from typing import Any, Dict

from langchain_core.tools import tool

from agent.utils.llm_client import call_with_retry, get_llm_client


@tool
def generate_quiz(
    concept_name: str,
    difficulty_level: str = "beginner",
    num_questions: int = 3,
    question_types: str = "multiple_choice",
    source_material: str = "",
) -> Dict[str, Any]:
    """
    Generates a quiz to test understanding of a concept at an appropriate difficulty level.
    When source_material is provided, questions are grounded in the actual uploaded content.

    Args:
        concept_name: The concept to quiz on. Use the document topic for a full-document quiz.
        difficulty_level: "beginner", "intermediate", or "advanced"
        num_questions: Number of questions to generate (default: 3)
        question_types: Comma-separated question types (currently only "multiple_choice" supported)
        source_material: Optional text from uploaded study material. When provided, all
            questions MUST be grounded in this content, not general knowledge.
    """
    llm = get_llm_client()
    
    difficulty_guide = {
        "beginner": {
            "complexity": "simple, fundamental questions",
            "depth": "surface-level understanding",
            "examples": "basic application questions",
        },
        "intermediate": {
            "complexity": "moderately challenging questions",
            "depth": "deeper understanding with some application",
            "examples": "practical application questions",
        },
        "advanced": {
            "complexity": "complex, nuanced questions",
            "depth": "deep understanding with edge cases",
            "examples": "sophisticated application and analysis questions",
        },
    }
    
    guide = difficulty_guide.get(difficulty_level.lower(), difficulty_guide["beginner"])

    material_block = ""
    if source_material.strip():
        material_block = f"""
--- BEGIN UPLOADED STUDY MATERIAL ---
{source_material[:4000]}
--- END UPLOADED STUDY MATERIAL ---

IMPORTANT: Every question MUST be based strictly on the study material above.
Do NOT use general knowledge. Only ask about content present in the material.
"""

    prompt = f"""Create a quiz with {num_questions} questions about "{concept_name}" at {difficulty_level} level.
{material_block}

Difficulty Level Guidelines:
- Question Complexity: {guide['complexity']}
- Depth: {guide['depth']}
- Examples: {guide['examples']}

Question Types to Include: multiple_choice

Requirements:
- Each question should test understanding of {concept_name}
- Questions should be appropriate for {difficulty_level} level
- Every question MUST be multiple_choice
- For every multiple choice question, provide exactly 4 options as full text strings (NOT letters like A/B/C/D)
- The correct_answer field MUST be the FULL option text (e.g. "Generating Human-Like Text"), NOT a letter
- Include brief explanation for each answer

Return the quiz in this EXACT JSON format:
{{
    "concept_name": "{concept_name}",
    "difficulty_level": "{difficulty_level}",
    "questions": [
        {{
            "question_number": 1,
            "question_type": "multiple_choice",
            "question": "Question text here?",
            "options": ["Full text of option 1", "Full text of option 2", "Full text of option 3", "Full text of option 4"],
            "correct_answer": "Full text of option 1",
            "explanation": "Brief explanation here"
        }},
        {{
            "question_number": 2,
            "question_type": "multiple_choice",
            "question": "Question text here?",
            "options": ["Full text of option 1", "Full text of option 2", "Full text of option 3", "Full text of option 4"],
            "correct_answer": "Full text of option 2",
            "explanation": "Brief explanation here"
        }}
    ],
    "total_questions": {num_questions}
}}

IMPORTANT: correct_answer for multiple_choice MUST be the exact full text of one of the options, never a letter.
Return ONLY valid JSON, no additional text before or after."""

    def _extract_valid_mc_questions(raw: str) -> list[dict[str, Any]]:
        import json

        json_start = raw.find("{")
        json_end = raw.rfind("}") + 1
        if json_start == -1 or json_end <= json_start:
            return []
        parsed = json.loads(raw[json_start:json_end])
        questions = parsed.get("questions") or []
        valid_questions: list[dict[str, Any]] = []

        for question in questions:
            options = question.get("options")
            correct_answer = question.get("correct_answer")
            if question.get("question_type") != "multiple_choice":
                continue
            if not isinstance(options, list) or len(options) != 4:
                continue
            if any(not isinstance(option, str) or not option.strip() for option in options):
                continue
            normalized_options = [option.strip() for option in options]
            if not isinstance(correct_answer, str) or correct_answer.strip() not in normalized_options:
                continue

            valid_questions.append(
                {
                    "question_number": len(valid_questions) + 1,
                    "question_type": "multiple_choice",
                    "question": str(question.get("question", "")).strip(),
                    "options": normalized_options,
                    "correct_answer": correct_answer.strip(),
                    "explanation": str(question.get("explanation", "")).strip(),
                }
            )

        return valid_questions

    try:
        response = call_with_retry(llm.invoke, prompt)
    except Exception as exc:
        error_msg = str(exc)
        error_code = "rate_limit" if any(s in error_msg.lower() for s in ("rate limit", "429", "ratelimit")) else "llm_error"
        return {
            "concept_name": concept_name,
            "difficulty_level": difficulty_level,
            "questions": [],
            "total_questions": 0,
            "error": error_msg,
            "error_code": error_code,
        }

    content = str(response.content).strip()
    last_raw = content
    valid_questions = _extract_valid_mc_questions(content)

    if len(valid_questions) < num_questions:
        # Try up to two stricter regeneration attempts if model returned invalid question shapes
        strict_prompt = (
            prompt
            + "\n\nCRITICAL VALIDATION RULES:"
            + "\n- Output ONLY multiple_choice questions"
            + "\n- Each question MUST include exactly 4 non-empty string options"
            + "\n- correct_answer MUST exactly match one option"
            + "\n- Do not output null options"
        )
        for _ in range(2):
            try:
                retry_response = call_with_retry(llm.invoke, strict_prompt, max_attempts=2)
                retry_content = str(retry_response.content).strip()
                last_raw = retry_content
                retry_questions = _extract_valid_mc_questions(retry_content)
                if len(retry_questions) >= len(valid_questions):
                    valid_questions = retry_questions
                if len(valid_questions) >= num_questions:
                    break
            except Exception:
                break

    if valid_questions:
        final_questions = valid_questions[:num_questions]
        return {
            "concept_name": concept_name,
            "difficulty_level": difficulty_level,
            "questions": final_questions,
            "total_questions": len(final_questions),
        }

    return {
        "concept_name": concept_name,
        "difficulty_level": difficulty_level,
        "questions": [],
        "total_questions": 0,
        "error": "Failed to generate valid multiple-choice questions with options.",
        "error_code": "invalid_quiz_format",
        "raw_response": last_raw[:500],
    }

