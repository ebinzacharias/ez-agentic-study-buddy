import logging
import os
import re
import tempfile
import traceback
import uuid
from typing import Any

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from agent.utils.content_loader import SUPPORTED_EXTENSIONS, load_content
from agent.core.decision_rules import DecisionRules
from agent.core.state import DifficultyLevel, StudySessionState
from agent.tools.adapter_tool import adapt_difficulty
from agent.tools.evaluator_tool import evaluate_response
from agent.tools.planner_tool import plan_learning_path
from agent.tools.quizzer_tool import generate_quiz
from agent.tools.teacher_tool import teach_concept_payload

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("webapi")

app = FastAPI()


class CreateSessionRequest(BaseModel):
    topic: str = Field(default="", description="Learning topic")
    difficulty_level: str = Field(default="beginner", description="beginner|intermediate|advanced")


class TeachRequest(BaseModel):
    concept_name: str
    difficulty_level: str = "beginner"
    context: str = ""


class QuizRequest(BaseModel):
    concept_name: str
    difficulty_level: str = "beginner"
    num_questions: int = 3
    question_types: str = "multiple_choice"


class EvaluateRequest(BaseModel):
    quiz_data: str  # JSON string of the quiz
    learner_answers: str  # JSON string of answers


class PlanRequest(BaseModel):
    topic: str = ""
    difficulty_level: str = "beginner"
    max_concepts: int = 0  # 0 = auto-infer from document size/complexity


SESSIONS: dict[str, StudySessionState] = {}
# Single-file PDF uploads only: original bytes for in-browser PDF preview (session bar → View source).
SESSION_ORIGINAL_BLOBS: dict[str, tuple[bytes, str, str]] = {}


_ACTION_LABELS: dict[str, str] = {
    "plan_learning_path": "Plan Learning Path",
    "teach_concept": "Teach Concept",
    "generate_quiz": "Generate Quiz",
    "adapt_difficulty": "Adapt Difficulty",
    "session_complete": "Session Complete",
    "set_current_concept": "Set Next Concept",
    "add_concept": "Add Concept",
}


def _get_next_action(state: StudySessionState) -> dict[str, Any]:
    """Run DecisionRules against current session state and return a UI-friendly recommendation."""
    rules = DecisionRules(state)
    decision = rules.decide_next_action()
    action = decision.get("action", "")
    concept = (
        decision.get("tool_args", {}).get("concept_name")
        or decision.get("concept_name")
        or ""
    )
    return {
        "action": action,
        "label": _ACTION_LABELS.get(action, action.replace("_", " ").title()),
        "concept": concept,
        "reason": decision.get("reason", ""),
    }


_RATE_LIMIT_HINTS = ("rate limit", "ratelimit", "429", "too many requests")
_TIMEOUT_HINTS = ("timeout", "timed out", "connection")
_AUTH_HINTS = ("api key", "authentication", "unauthorized", "401", "403")
_QUIZ_FORMAT_HINTS = ("invalid_quiz_format", "valid multiple-choice questions")


def _classify_error(exc: Exception) -> tuple[str, str]:
    """Return (error_code, user_message) for a caught exception."""
    msg = str(exc).lower()
    if any(s in msg for s in _RATE_LIMIT_HINTS):
        return "rate_limit", "The LLM is rate-limited. Please wait a moment and try again."
    if any(s in msg for s in _TIMEOUT_HINTS):
        return "timeout", "The request timed out. Check your network/proxy and retry."
    if any(s in msg for s in _AUTH_HINTS):
        return "auth_error", "API key error. Ensure GROQ_API_KEY is set correctly in .env."
    if any(s in msg for s in _QUIZ_FORMAT_HINTS):
        return "invalid_quiz_format", "Could not generate valid multiple-choice options. Please try again."
    return "llm_error", str(exc)


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... content truncated ...]"


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _normalize_difficulty(level: str) -> DifficultyLevel:
    value = (level or "").lower().strip()
    if value == "intermediate":
        return DifficultyLevel.INTERMEDIATE
    if value == "advanced":
        return DifficultyLevel.ADVANCED
    return DifficultyLevel.BEGINNER


_TEMP_STEM_RE = re.compile(r"^tmp[a-z0-9_-]{5,}$", re.IGNORECASE)


def _looks_like_temp_stem(s: str) -> bool:
    """Return True if a string looks like a generated temp-file name."""
    return bool(_TEMP_STEM_RE.match(s.strip()))


def _suggest_max_concepts(raw_text: str) -> int:
    """
    Estimate a sensible concept count from document length and structure.

    Signals used:
      - Word count  → depth / how much ground the document covers
      - Heading count (Markdown # lines) → explicit structural complexity

    Intentionally conservative: it is better to generate a tight, focused
    path and let the user request more via Tune than to overwhelm them with
    too many concepts on a short document.

    The result is clamped to [3, 15].
    """
    if not raw_text or not raw_text.strip():
        return 5

    words = len(raw_text.split())

    heading_count = sum(
        1 for line in raw_text.splitlines()
        if re.match(r"^#{1,6}\s+\S", line.strip())
    )

    # Base concept count — deliberately conservative
    if words < 300:
        base = 3
    elif words < 800:
        base = 4
    elif words < 2_000:
        base = 5
    elif words < 5_000:
        base = 7
    elif words < 10_000:
        base = 9
    elif words < 20_000:
        base = 12
    else:
        base = 15

    # Every 3 headings suggests one extra concept, capped at +3
    heading_boost = min(heading_count // 3, 3)

    return max(3, min(15, base + heading_boost))


def _letter_count(s: str) -> int:
    return sum(1 for c in s if c.isalpha())


def _is_low_signal_topic_line(s: str) -> bool:
    """Heuristic: page counters, footers, and other PDF/header noise — not a real topic."""
    t = (s or "").strip()
    if not t:
        return True
    tl = t.lower()
    # "1 von 2", "3 of 12", "12 / 30"
    if re.match(r"^\d{1,4}\s+von\s+\d{1,4}$", tl):
        return True
    if re.match(r"^\d{1,4}\s+of\s+\d{1,4}$", tl):
        return True
    if re.match(r"^\d{1,4}\s*/\s*\d{1,4}$", t):
        return True
    # "Page 1", "Seite 2 von 10", "Page 3 of 12"
    if re.match(r"^(?:page|seite)\s+\d{1,4}(?:\s*(?:of|von|,)\s*\d{1,4})?$", tl):
        return True
    if re.match(r"^(?:page|seite)\s+\d{1,4}\s*/\s*\d{1,4}$", tl):
        return True
    # Footer / legal one-liners
    if "all rights reserved" in tl or tl.startswith("©") or "copyright" in tl:
        return True
    # Only digits, spaces, and light punctuation (e.g. " - 1 - ")
    if _letter_count(t) == 0 and re.match(r"^[\d\s\-–—/|.,:]+$", t):
        return True
    return False


def _looks_substantive_topic(s: str) -> bool:
    """Enough letters to be a plausible human title (filters '1 von 2', '- 2 -', etc.)."""
    t = (s or "").strip()
    if len(t) < 4 or len(t) > 120:
        return False
    if _is_low_signal_topic_line(t):
        return False
    if _letter_count(t) < 4:
        return False
    return True


def _first_heading_from_text(text: str) -> str:
    """Prefer Markdown ATX headings, then the first substantive line (skip PDF page markers)."""
    if not (text or "").strip():
        return ""
    lines = text.splitlines()
    # Pass 1: explicit # headings (usually real document titles)
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^#{1,6}\s+(.+)$", line)
        if m:
            clean = m.group(1).strip()
            if _looks_substantive_topic(clean):
                return clean[:80]
    # Pass 2: first substantive line (strip stray # if present)
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        clean = re.sub(r"^#{1,6}\s*", "", line).strip()
        if _looks_substantive_topic(clean):
            return clean[:80]
    return ""


def _suggest_topic(
    titles: list[str],
    filenames: list[str],
    raw_texts: list[str] | None = None,
) -> str:
    # 1. Use loader titles that are not temp stems and not PDF/footer noise
    cleaned_titles: list[str] = []
    for t in titles:
        t = (t or "").strip()
        if not t or _looks_like_temp_stem(t):
            continue
        if not _looks_substantive_topic(t):
            continue
        cleaned_titles.append(t)
    if cleaned_titles:
        unique = _dedupe_preserve_order(cleaned_titles)
        if len(unique) == 1:
            return unique[0]
        joined = " / ".join(unique[:3])
        return joined[:80]

    # 2. Try the first heading / meaningful line from raw content
    if raw_texts:
        for text in raw_texts:
            heading = _first_heading_from_text(text)
            if heading:
                return heading[:80]

    # 3. Fall back to the original (non-temp) filename stem
    stems = []
    for f in filenames:
        if not f:
            continue
        stem = os.path.splitext(os.path.basename(f))[0].strip()
        # Replace hyphens/underscores with spaces and title-case
        stem = re.sub(r"[-_]+", " ", stem).strip()
        if stem and not _looks_like_temp_stem(stem):
            stems.append(stem.title())
    if stems:
        unique_stems = _dedupe_preserve_order(stems)
        if len(unique_stems) == 1:
            return unique_stems[0]
        joined = " / ".join(unique_stems[:3])
        return joined[:80]

    return "Uploaded Materials"

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "EZ-Agentic Content Loader API",
        "docs": "http://127.0.0.1:8000/docs",
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename or "uploaded_file"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={
                "error": f"Unsupported file type: {ext}",
                "supported": sorted(SUPPORTED_EXTENSIONS),
            },
        )
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        content = load_content(tmp_path)
        return {
            "section_titles": content.get_section_titles(),
            "preview": content.get_summary_context(1200),
            "metadata": content.metadata,
            "title": content.title,
            "raw_text": content.raw_text,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        os.unlink(tmp_path)

@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.post("/session/from-upload")
async def create_session_from_upload(
    files: list[UploadFile] = File(...),
    difficulty_level: str = "beginner",
    topic: str = "",
) -> dict[str, Any]:
    if not files:
        return JSONResponse(status_code=400, content={"error": "No files provided"})

    temp_paths: list[str] = []
    loaded_list: list[dict[str, Any]] = []
    all_section_titles: list[str] = []
    all_titles: list[str] = []
    filenames: list[str] = []
    raw_text_parts: list[str] = []

    try:
        last_file_bytes: bytes = b""
        for file in files:
            filename = file.filename or "uploaded_file"
            filenames.append(filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": f"Unsupported file type: {ext}",
                        "supported": sorted(SUPPORTED_EXTENSIONS),
                    },
                )

            last_file_bytes = await file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(last_file_bytes)
                tmp_path = tmp.name
            temp_paths.append(tmp_path)

            loaded = load_content(tmp_path)
            loaded_list.append(
                {
                    "filename": filename,
                    "title": loaded.title,
                    "metadata": loaded.metadata,
                }
            )
            all_section_titles.extend(loaded.get_section_titles())
            all_titles.append(loaded.title)
            if loaded.raw_text.strip():
                raw_text_parts.append(loaded.raw_text.strip())

        merged_raw_text = "\n\n".join(raw_text_parts)
        merged_loaded_content = {
            "title": _suggest_topic(all_titles, filenames, raw_text_parts),
            "source_file": "multiple" if len(filenames) > 1 else (filenames[0] if filenames else ""),
            "sections": [],
            "raw_text": merged_raw_text,
            "metadata": {
                "format": "mixed" if len(filenames) > 1 else (loaded_list[0].get("metadata", {}).get("format", "unknown") if loaded_list else "unknown"),
                "sources": loaded_list,
            },
        }

        session_id = str(uuid.uuid4())
        suggested_topic = _suggest_topic(all_titles, filenames, raw_text_parts)
        final_topic = topic.strip() or suggested_topic

        state = StudySessionState(session_id=session_id, topic=final_topic)
        state.overall_difficulty = _normalize_difficulty(difficulty_level)
        state.set_loaded_content(merged_loaded_content)
        SESSIONS[session_id] = state

        # Retain one original PDF for native preview (multi-file or non-PDF → text-only modal).
        if len(filenames) == 1:
            sole = filenames[0]
            sole_ext = os.path.splitext(sole)[1].lower()
            if sole_ext == ".pdf" and last_file_bytes:
                SESSION_ORIGINAL_BLOBS[session_id] = (
                    last_file_bytes,
                    "application/pdf",
                    os.path.basename(sole) or "document.pdf",
                )
            else:
                SESSION_ORIGINAL_BLOBS.pop(session_id, None)
        else:
            SESSION_ORIGINAL_BLOBS.pop(session_id, None)

        section_titles = _dedupe_preserve_order([t for t in all_section_titles if t and t.strip()])

        return {
            "session_id": state.session_id,
            "topic": state.topic,
            "suggested_topic": suggested_topic,
            "overall_difficulty": state.overall_difficulty.value,
            "materials": loaded_list,
            "section_titles": section_titles,
            "preview": _truncate(merged_raw_text, 1200),
        }
    except Exception as e:
        logger.error(f"Error in /session/from-upload: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e), "type": type(e).__name__})
    finally:
        for p in temp_paths:
            try:
                os.unlink(p)
            except OSError:
                pass


@app.post("/session")
def create_session(req: CreateSessionRequest) -> dict[str, Any]:
    session_id = str(uuid.uuid4())
    topic = req.topic.strip() or "Untitled"
    state = StudySessionState(session_id=session_id, topic=topic)

    state.overall_difficulty = _normalize_difficulty(req.difficulty_level)

    SESSIONS[session_id] = state
    return {
        "session_id": session_id,
        "topic": state.topic,
        "overall_difficulty": state.overall_difficulty.value,
    }


@app.get("/session/{session_id}")
def get_session(session_id: str) -> dict[str, Any]:
    state = SESSIONS.get(session_id)
    if state is None:
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    return {
        "session_id": state.session_id,
        "topic": state.topic,
        "overall_difficulty": state.overall_difficulty.value,
        "has_loaded_content": state.has_loaded_content(),
        "concepts_planned": state.concepts_planned,
        "progress": state.get_progress_percentage(),
    }


@app.get("/session/{session_id}/source")
def get_session_source(session_id: str) -> dict[str, Any]:
    """Return extracted plain text for the material stored on this session (full document)."""
    state = SESSIONS.get(session_id)
    if state is None:
        return JSONResponse(status_code=404, content={"error": "Session not found"})
    if not state.has_loaded_content() or state.loaded_content is None:
        return JSONResponse(
            status_code=400,
            content={"error": "No content uploaded for this session"},
        )
    lc = state.loaded_content
    raw = str(lc.get("raw_text") or "")
    meta = lc.get("metadata") or {}
    sources = meta.get("sources") or []
    filenames: list[str] = []
    for item in sources:
        if isinstance(item, dict) and item.get("filename"):
            filenames.append(str(item["filename"]))
    pdf_available = session_id in SESSION_ORIGINAL_BLOBS
    out: dict[str, Any] = {
        "text": raw,
        "filenames": filenames,
        "pdf_available": pdf_available,
    }
    if pdf_available:
        out["pdf_filename"] = SESSION_ORIGINAL_BLOBS[session_id][2]
    return out


@app.get("/session/{session_id}/source-file")
def get_session_source_file(session_id: str) -> Response:
    """Return the original uploaded PDF bytes (only when a single PDF was used to create the session)."""
    if session_id not in SESSIONS:
        return JSONResponse(status_code=404, content={"error": "Session not found"})
    blob = SESSION_ORIGINAL_BLOBS.get(session_id)
    if not blob:
        return JSONResponse(
            status_code=404,
            content={"error": "No original PDF is stored for this session"},
        )
    data, media_type, filename = blob
    safe_name = (os.path.basename(filename) or "document.pdf").replace('"', "").replace("\r", "")
    return Response(
        content=data,
        media_type=media_type,
        headers={
            "Content-Disposition": f'inline; filename="{safe_name}"',
            "Cache-Control": "private, max-age=300",
        },
    )


@app.post("/session/{session_id}/upload")
async def upload_to_session(session_id: str, file: UploadFile = File(...)) -> dict[str, Any]:
    state = SESSIONS.get(session_id)
    if state is None:
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    filename = file.filename or "uploaded_file"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={
                "error": f"Unsupported file type: {ext}",
                "supported": sorted(SUPPORTED_EXTENSIONS),
            },
        )

    file_bytes = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        loaded = load_content(tmp_path)
        state.set_loaded_content(loaded.model_dump())
        if (loaded_title := loaded.title.strip()):
            state.topic = loaded_title

        if ext == ".pdf" and file_bytes:
            SESSION_ORIGINAL_BLOBS[session_id] = (
                file_bytes,
                "application/pdf",
                os.path.basename(filename) or "document.pdf",
            )
        else:
            SESSION_ORIGINAL_BLOBS.pop(session_id, None)

        return {
            "session_id": state.session_id,
            "topic": state.topic,
            "overall_difficulty": state.overall_difficulty.value,
            "section_titles": loaded.get_section_titles(),
            "preview": loaded.get_summary_context(1200),
            "metadata": loaded.metadata,
            "title": loaded.title,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        os.unlink(tmp_path)


@app.post("/session/{session_id}/plan")
def session_plan(session_id: str, req: PlanRequest) -> dict[str, Any]:
    state = SESSIONS.get(session_id)
    if state is None:
        return JSONResponse(status_code=410, content={"error": "Session expired. Please re-upload your material.", "error_code": "session_expired"})
    if not state.has_loaded_content():
        return JSONResponse(status_code=400, content={"error": "No content uploaded for this session"})

    topic = (req.topic or state.topic).strip() or state.topic
    difficulty = (req.difficulty_level or state.overall_difficulty.value).strip()

    # Always compute the document's inherent ceiling so the UI can lock it in.
    raw_text = state.loaded_content.get("raw_text", "") if state.loaded_content else ""
    document_max = _suggest_max_concepts(raw_text)
    # Use the caller's requested count if supplied; otherwise default to the document ceiling.
    max_concepts = req.max_concepts if req.max_concepts > 0 else document_max

    state.topic = topic
    state.overall_difficulty = _normalize_difficulty(difficulty)

    try:
        concepts = plan_learning_path.invoke(
            {
                "topic": topic,
                "difficulty_level": difficulty,
                "max_concepts": max_concepts,
                "source_material": state.get_content_context(max_chars=3000),
            }
        )
        # Cache the planned concept names for UI convenience
        state.concepts_planned = [str(c.get("concept_name", "")).strip() for c in concepts if c.get("concept_name")]
        return {
            "session_id": state.session_id,
            "topic": topic,
            "difficulty_level": difficulty,
            "concepts": concepts,
            "suggested_max_concepts": document_max,  # always the document ceiling, never the requested count
        }
    except Exception as e:
        tb = traceback.format_exc()
        logger.error("Plan endpoint error:\n%s", tb)
        error_code, user_msg = _classify_error(e)
        return JSONResponse(
            status_code=500,
            content={
                "error": user_msg,
                "error_code": error_code,
                "detail": str(e),
            },
        )


@app.post("/session/{session_id}/teach")
def session_teach(session_id: str, req: TeachRequest) -> dict[str, Any]:
    state = SESSIONS.get(session_id)
    if state is None:
        return JSONResponse(status_code=410, content={"error": "Session expired. Please re-upload your material.", "error_code": "session_expired"})
    if not state.has_loaded_content():
        return JSONResponse(status_code=400, content={"error": "No content uploaded for this session"})

    concept = req.concept_name.strip()
    if not concept:
        return JSONResponse(status_code=400, content={"error": "concept_name is required"})

    difficulty = (req.difficulty_level or state.overall_difficulty.value).strip()
    state.overall_difficulty = _normalize_difficulty(difficulty)

    try:
        payload = teach_concept_payload(
            concept_name=concept,
            difficulty_level=difficulty,
            context=req.context or "",
            source_material=state.get_content_context(max_chars=3000),
        )
        state.add_concept(concept)
        state.mark_concept_taught(concept)
        state.current_concept = concept  # anchor state so next_action resolves correctly
        if payload.get("error"):
            err = str(payload["error"])
            if err.startswith("[error:"):
                code = err.split("]")[0].replace("[error:", "")
                msg = err.split("] ", 1)[-1]
                return JSONResponse(
                    status_code=503,
                    content={"error": msg, "error_code": code},
                )
            return JSONResponse(status_code=503, content={"error": err, "error_code": "unknown"})
        return {
            "session_id": state.session_id,
            "concept_name": concept,
            "difficulty_level": difficulty,
            "explanation": payload["explanation"],
            "takeaways": payload.get("takeaways") or [],
            "estimated_read_minutes": int(payload.get("estimated_read_minutes") or 1),
            "next_action": _get_next_action(state),
        }
    except Exception as e:
        error_code, user_msg = _classify_error(e)
        return JSONResponse(
            status_code=500,
            content={"error": user_msg, "error_code": error_code, "detail": str(e)},
        )


@app.post("/session/{session_id}/quiz")
def session_quiz(session_id: str, req: QuizRequest) -> dict[str, Any]:
    state = SESSIONS.get(session_id)
    if state is None:
        return JSONResponse(status_code=410, content={"error": "Session expired. Please re-upload your material.", "error_code": "session_expired"})

    concept = req.concept_name.strip()
    if not concept:
        return JSONResponse(status_code=400, content={"error": "concept_name is required"})

    try:
        quiz = generate_quiz.invoke(
            {
                "concept_name": concept,
                "difficulty_level": req.difficulty_level,
                "num_questions": req.num_questions,
                "question_types": req.question_types,
                "source_material": state.get_content_context(max_chars=4000) if state.has_loaded_content() else "",
            }
        )
        # Tool may return a dict with an error key if all retries failed
        if isinstance(quiz, dict) and "error" in quiz:
            error_code = quiz.get("error_code", "llm_error")
            _, user_msg = _classify_error(Exception(quiz["error"]))
            return JSONResponse(
                status_code=503,
                content={"error": user_msg, "error_code": error_code, "detail": quiz["error"]},
            )
        return {"session_id": session_id, **quiz}
    except Exception as e:
        error_code, user_msg = _classify_error(e)
        logger.error("Quiz endpoint error: %s", e)
        return JSONResponse(
            status_code=500,
            content={"error": user_msg, "error_code": error_code, "detail": str(e)},
        )


@app.get("/session/{session_id}/next-action")
def session_next_action(session_id: str) -> dict[str, Any]:
    """Return the next recommended action for the session based on current state."""
    state = SESSIONS.get(session_id)
    if state is None:
        return JSONResponse(status_code=404, content={"error": "Session not found"})
    return {"session_id": session_id, **_get_next_action(state)}


@app.post("/session/{session_id}/evaluate")
def session_evaluate(session_id: str, req: EvaluateRequest) -> dict[str, Any]:
    state = SESSIONS.get(session_id)
    if state is None:
        return JSONResponse(
            status_code=410,
            content={"error": "Session expired. Please re-upload your material to start a new session.", "error_code": "session_expired"},
        )

    try:
        import json as _json
        result = evaluate_response.invoke(
            {
                "quiz_data": req.quiz_data,
                "learner_answers": req.learner_answers,
            }
        )
        # Update session state with the quiz score so DecisionRules can act on it
        concept_name = ""
        score = 0.0
        try:
            quiz_meta = _json.loads(req.quiz_data) if isinstance(req.quiz_data, str) else req.quiz_data
            concept_name = (quiz_meta.get("concept_name") or "").strip()
            score_pct = result.get("overall_percentage", 0)
            score = score_pct / 100.0
            if concept_name and concept_name in state.concepts:
                state.mark_concept_quizzed(concept_name, score)
            elif concept_name:
                state.add_concept(concept_name)
                state.mark_concept_taught(concept_name)
                state.mark_concept_quizzed(concept_name, score)
        except Exception:
            pass

        # Rule-based difficulty adaptation (no LLM) — runs after quiz scoring
        difficulty_adaptation: dict[str, Any] | None = None
        if concept_name and concept_name in state.concepts:
            prog = state.get_concept_progress(concept_name)
            current_lvl = state.overall_difficulty.value
            retry_ct = prog.retry_count if prog else 0
            try:
                adapt = adapt_difficulty.invoke(
                    {
                        "concept_name": concept_name,
                        "current_difficulty": current_lvl,
                        "quiz_score": score,
                        "retry_count": retry_ct,
                    }
                )
            except Exception as adapt_exc:
                logger.warning("adapt_difficulty after evaluate failed: %s", adapt_exc)
                adapt = None

            if isinstance(adapt, dict) and "error" not in adapt:
                difficulty_adaptation = {
                    "adaptation_applied": bool(adapt.get("adaptation_applied", False)),
                    "old_difficulty": adapt.get("old_difficulty"),
                    "new_difficulty": adapt.get("new_difficulty"),
                    "reason": (adapt.get("reason") or "").strip(),
                    "concept_name": adapt.get("concept_name") or concept_name,
                }
                if difficulty_adaptation["adaptation_applied"]:
                    new_d = str(difficulty_adaptation["new_difficulty"] or "")
                    state.overall_difficulty = _normalize_difficulty(new_d)
                    if prog:
                        prog.update_difficulty(_normalize_difficulty(new_d))

        out: dict[str, Any] = {
            "session_id": session_id,
            **result,
            "next_action": _get_next_action(state),
        }
        if difficulty_adaptation is not None:
            out["difficulty_adaptation"] = difficulty_adaptation
        return out
    except Exception as e:
        error_code, user_msg = _classify_error(e)
        logger.error("Evaluate endpoint error: %s", e)
        return JSONResponse(
            status_code=500,
            content={"error": user_msg, "error_code": error_code, "detail": str(e)},
        )
