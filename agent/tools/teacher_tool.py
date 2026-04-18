import importlib
import json
import re
from json.decoder import JSONDecoder
from typing import Any, Optional, cast

from langchain_core.tools import tool

from agent.utils.llm_client import call_with_retry, get_llm_client

# Average adult reading speed for explanatory prose (words per minute)
_TEACH_READ_WPM = 200


def _estimate_read_minutes(explanation: str) -> int:
    if not (explanation or "").strip():
        return 1
    words = len(re.findall(r"\w+", explanation))
    mins = max(1, round(words / _TEACH_READ_WPM))
    return min(mins, 45)


def _strip_code_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\s*```\s*$", "", t)
    return t.strip()


def _normalize_takeaways(raw: Any) -> list[str]:
    items: list[str] = []
    if isinstance(raw, list):
        for t in raw:
            if isinstance(t, str) and (s := t.strip()):
                items.append(s)
    elif isinstance(raw, str) and raw.strip():
        items.append(raw.strip())
    out: list[str] = []
    for s in items:
        line = re.sub(r"\s+", " ", s).strip()
        if line:
            out.append(line[:280])
        if len(out) >= 4:
            break
    return out


_json_decoder = JSONDecoder()
# CPython exposes py_scanstring on json.decoder; typeshed omits it (mypy attr-defined).
_json_py_scanstring: Any = getattr(importlib.import_module("json.decoder"), "py_scanstring")


def _repair_triple_quoted_explanation(text: str) -> str | None:
    r"""
    Models sometimes emit invalid JSON: an "explanation" value opened with
    three double-quotes and closed with three double-quotes (not valid JSON).
    Repair by turning that segment into a normal JSON string.
    """
    m = re.search(r'("explanation"\s*:\s*)"""', text)
    if not m:
        return None
    inner_start = m.end()
    close = text.find('"""', inner_start)
    if close < 0:
        return None
    inner = text[inner_start:close]
    suffix = text[close + 3 :]
    return text[: m.start(1)] + m.group(1) + json.dumps(inner) + suffix


def _maybe_unwrap_nested_json_explanation(expl: str) -> str:
    """If explanation is itself a JSON object with an explanation field, unwrap once."""
    s = expl.strip()
    if not s.startswith("{"):
        return expl
    head = s[: min(240, len(s))]
    if '"explanation"' not in head and "'explanation'" not in head:
        return expl
    candidate = _repair_triple_quoted_explanation(s) or s
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        return expl
    if isinstance(data, dict):
        inner = data.get("explanation")
        if isinstance(inner, str) and inner.strip():
            return inner.strip()
    return expl


def _loose_parse_explanation_and_takeaways(text: str) -> dict[str, Any] | None:
    """
    When json.loads fails, try to salvage a quoted "explanation" value via the stdlib
    JSON string scanner (handles escapes/newlines). Optionally parse "takeaways" array.
    """
    m = re.search(r'"explanation"\s*:\s*"', text)
    if not m:
        return None
    try:
        # py_scanstring expects the index of the opening " of the JSON string value
        expl, _end = cast(tuple[str, int], _json_py_scanstring(text, m.end() - 1, False))
    except (json.JSONDecodeError, ValueError):
        return None

    takeaways: list[str] = []
    tm = re.search(r'"takeaways"\s*:\s*\[', text)
    if tm:
        try:
            raw_tw, _ = _json_decoder.raw_decode(text, tm.end() - 1)
            takeaways = _normalize_takeaways(raw_tw)
        except (json.JSONDecodeError, ValueError):
            takeaways = []

    return {
        "explanation": expl.strip(),
        "takeaways": takeaways,
        "estimated_read_minutes": _estimate_read_minutes(expl),
    }


def _parse_teach_json_response(content: str) -> dict[str, Any]:
    """Parse model JSON; on failure try repairs, then loose extraction, else plain markdown."""
    stripped = _strip_code_fence(content)
    candidate = _repair_triple_quoted_explanation(stripped) or stripped

    data: dict[str, Any] | None = None
    try:
        parsed = json.loads(candidate)
        data = parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        data = None

    if data is None:
        loose = _loose_parse_explanation_and_takeaways(candidate)
        if loose is not None:
            return loose
        loose2 = _loose_parse_explanation_and_takeaways(stripped)
        if loose2 is not None:
            return loose2
        return {
            "explanation": stripped.strip(),
            "takeaways": [],
            "estimated_read_minutes": _estimate_read_minutes(stripped),
        }

    expl = data.get("explanation")
    expl = expl.strip() if isinstance(expl, str) else ""
    if not expl:
        expl = stripped.strip() or content.strip()
    expl = _maybe_unwrap_nested_json_explanation(expl)

    takeaways = _normalize_takeaways(data.get("takeaways"))

    return {
        "explanation": expl,
        "takeaways": takeaways,
        "estimated_read_minutes": _estimate_read_minutes(expl),
    }


def _build_teach_prompt(
    concept_name: str,
    difficulty_level: str,
    context: str,
    source_material: str,
    retry_attempt: Optional[int],
    alternative_strategy: Optional[str],
) -> str:
    difficulty_guide = {
        "beginner": {
            "vocabulary": "simple, everyday language",
            "examples": "real-world analogies and simple code examples",
            "depth": "surface-level understanding, focus on practical use",
            "technical_terms": "define all technical terms when first used",
        },
        "intermediate": {
            "vocabulary": "balanced mix of technical and accessible language",
            "examples": "practical code examples with some context",
            "depth": "moderate depth with explanations of why things work",
            "technical_terms": "assume some familiarity with common terms",
        },
        "advanced": {
            "vocabulary": "technical, precise terminology",
            "examples": "sophisticated code examples and edge cases",
            "depth": "deep understanding with underlying mechanisms",
            "technical_terms": "assume familiarity with domain terminology",
        },
    }

    guide = difficulty_guide.get(difficulty_level.lower(), difficulty_guide["beginner"])

    material_block = ""
    if source_material.strip():
        material_block = f"""
--- BEGIN USER-UPLOADED STUDY MATERIAL ---
{source_material[:3000]}
--- END USER-UPLOADED STUDY MATERIAL ---

IMPORTANT: Base your explanation primarily on the study material above.
Use the material's own examples, terminology, and structure where possible.
"""

    retry_instructions = ""
    if retry_attempt is not None:
        retry_instructions = f"\n\nIMPORTANT - This is RETRY ATTEMPT {retry_attempt}:"
        if retry_attempt == 1:
            retry_instructions += """
- Use SIMPLER language than before
- Provide MORE examples and analogies
- Break down the concept into smaller steps
- Use everyday analogies to explain technical concepts
- Avoid jargon unless absolutely necessary"""
        elif retry_attempt == 2:
            retry_instructions += """
- Try a COMPLETELY DIFFERENT teaching approach
- Use visual examples and step-by-step breakdowns
- Focus on practical applications rather than theory
- Use concrete examples before abstract concepts
- Consider using diagrams or structured formats"""
        elif retry_attempt >= 3:
            retry_instructions += """
- Use the SIMPLEST possible explanation
- Focus only on the core, essential understanding
- Use multiple analogies and real-world examples
- Break into very small, digestible pieces
- Ensure every step is clear before moving to the next"""

        if alternative_strategy:
            if alternative_strategy == "simplify_explanation":
                retry_instructions += "\n- Simplify every aspect of the explanation"
                retry_instructions += "\n- Use the simplest vocabulary possible"
                retry_instructions += "\n- Add more visual/analogy-based examples"
            elif alternative_strategy == "alternative_approach":
                retry_instructions += "\n- Take a completely different angle to explain this"
                retry_instructions += "\n- If previously theoretical, now be practical (or vice versa)"
                retry_instructions += "\n- Use different examples than what might have been used before"

    ctx_line = f"Context from the learner or prior steps: {context}\n" if context else ""

    return f"""Create a clear lesson for the concept "{concept_name}" at {difficulty_level} level.

Difficulty Level Guidelines:
- Vocabulary: {guide["vocabulary"]}
- Examples: {guide["examples"]}
- Depth: {guide["depth"]}
- Technical Terms: {guide["technical_terms"]}

{ctx_line}{material_block}{retry_instructions}

Respond with ONLY a valid JSON object (no markdown code fences, no commentary before or after). Use exactly these keys:
- "explanation": one string containing GitHub-flavored Markdown. Structure with ## headings such as Introduction, Core Explanation, and Examples. Match depth to {difficulty_level}.
- "takeaways": JSON array of 2 to 4 short strings. Each is a single memorable bullet (no markdown, no numbering prefix, under 180 characters). These are the "what mattered" hooks for the learner.

Rules:
- Do not repeat the takeaways verbatim as a list inside "explanation"; the lesson body teaches, the takeaways compress.
- Ground the lesson in the study material when it is provided above.
- Use standard JSON only for "explanation": one double-quoted string with \\n for newlines. Never use triple quotes (\"\"\") or Python-style string syntax.
- Output must be parseable by json.loads.
"""


def teach_concept_payload(
    concept_name: str,
    difficulty_level: str = "beginner",
    context: str = "",
    retry_attempt: Optional[int] = None,
    alternative_strategy: Optional[str] = None,
    source_material: str = "",
) -> dict[str, Any]:
    """
    Full teach result for HTTP API: explanation, takeaways, estimated_read_minutes.
    On failure returns {{"error": "[error:code] message"}} only.
    """
    llm = get_llm_client()
    prompt = _build_teach_prompt(
        concept_name,
        difficulty_level,
        context,
        source_material,
        retry_attempt,
        alternative_strategy,
    )

    try:
        response = call_with_retry(llm.invoke, prompt)
    except Exception as exc:
        error_msg = str(exc)
        if any(s in error_msg.lower() for s in ("rate limit", "429", "ratelimit")):
            return {"error": "[error:rate_limit] The LLM is currently rate-limited. Please wait a moment and try again."}
        return {"error": f"[error:llm_error] Could not generate explanation: {error_msg}"}

    content = str(response.content).strip()
    if content.startswith("[error:"):
        return {"error": content}

    parsed = _parse_teach_json_response(content)
    return parsed


@tool
def teach_concept(
    concept_name: str,
    difficulty_level: str = "beginner",
    context: str = "",
    retry_attempt: Optional[int] = None,
    alternative_strategy: Optional[str] = None,
    source_material: str = "",
) -> str:
    """
    Generates a clear, structured explanation of a concept at an appropriate difficulty level.

    This tool creates teaching content that explains a concept in a way that matches
    the learner's current difficulty level. It adapts vocabulary, examples, depth,
    and complexity based on the difficulty setting. Supports retry attempts with
    alternative teaching strategies.

    When source_material is provided (from user-uploaded content), the explanation
    is grounded in the actual material the learner is studying.

    Returns:
        Markdown explanation string (same as the "explanation" field in the JSON model output).
    """
    out = teach_concept_payload(
        concept_name=concept_name,
        difficulty_level=difficulty_level,
        context=context,
        retry_attempt=retry_attempt,
        alternative_strategy=alternative_strategy,
        source_material=source_material,
    )
    if out.get("error"):
        return str(out["error"])
    return str(out["explanation"])
