import logging
import os
import re
import tempfile
import traceback
import uuid
from typing import Any

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from agent.utils.content_loader import SUPPORTED_EXTENSIONS, load_content
from agent.core.decision_rules import DecisionRules
from agent.core.state import DifficultyLevel, StudySessionState
from agent.tools.evaluator_tool import evaluate_response
from agent.tools.planner_tool import plan_learning_path
from agent.tools.quizzer_tool import generate_quiz
from agent.tools.teacher_tool import teach_concept

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
    max_concepts: int = 10


SESSIONS: dict[str, StudySessionState] = {}


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


def _first_heading_from_text(text: str) -> str:
    """Try to extract the first meaningful heading or line from raw text."""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Strip leading markdown heading markers
        clean = re.sub(r"^#{1,6}\s*", "", line).strip()
        # Skip very short or very long lines
        if 3 < len(clean) < 120:
            return clean
    return ""


def _suggest_topic(
    titles: list[str],
    filenames: list[str],
    raw_texts: list[str] | None = None,
) -> str:
    # 1. Use titles that are NOT temp-file stems
    cleaned_titles = [t.strip() for t in titles if t and t.strip() and not _looks_like_temp_stem(t)]
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
    ext = os.path.splitext(file.filename)[1].lower()
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
        for file in files:
            filenames.append(file.filename)
            ext = os.path.splitext(file.filename)[1].lower()
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
                temp_paths.append(tmp_path)

            loaded = load_content(tmp_path)
            loaded_list.append(
                {
                    "filename": file.filename,
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
        return JSONResponse(status_code=500, content={"error": str(e)})
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


@app.post("/session/{session_id}/upload")
async def upload_to_session(session_id: str, file: UploadFile = File(...)) -> dict[str, Any]:
    state = SESSIONS.get(session_id)
    if state is None:
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    ext = os.path.splitext(file.filename)[1].lower()
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
        loaded = load_content(tmp_path)
        state.set_loaded_content(loaded.model_dump())
        if (loaded_title := loaded.title.strip()):
            state.topic = loaded_title

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
    max_concepts = req.max_concepts

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
        explanation = teach_concept.invoke(
            {
                "concept_name": concept,
                "difficulty_level": difficulty,
                "context": req.context,
                "source_material": state.get_content_context(max_chars=3000),
            }
        )
        state.add_concept(concept)
        state.mark_concept_taught(concept)
        # Check if tool returned an error string (prefixed with [error:...])
        if isinstance(explanation, str) and explanation.startswith("[error:"):
            code = explanation.split("]")[0].replace("[error:", "")
            msg = explanation.split("] ", 1)[-1]
            return JSONResponse(
                status_code=503,
                content={"error": msg, "error_code": code},
            )
        return {
            "session_id": state.session_id,
            "concept_name": concept,
            "difficulty_level": difficulty,
            "explanation": explanation,
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
        try:
            quiz_meta = _json.loads(req.quiz_data) if isinstance(req.quiz_data, str) else req.quiz_data
            concept_name = quiz_meta.get("concept_name", "").strip()
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
        return {"session_id": session_id, **result, "next_action": _get_next_action(state)}
    except Exception as e:
        error_code, user_msg = _classify_error(e)
        logger.error("Evaluate endpoint error: %s", e)
        return JSONResponse(
            status_code=500,
            content={"error": user_msg, "error_code": error_code, "detail": str(e)},
        )
