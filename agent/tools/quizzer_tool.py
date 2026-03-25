from typing import Any, Dict

from langchain_core.tools import tool

from agent.utils.llm_client import get_llm_client


@tool
def generate_quiz(
    concept_name: str,
    difficulty_level: str = "beginner",
    num_questions: int = 3,
    question_types: str = "multiple_choice,short_answer",
    source_material: str = "",
) -> Dict[str, Any]:
    """
    Generates a quiz to test understanding of a concept at an appropriate difficulty level.
    When source_material is provided, questions are grounded in the actual uploaded content.

    Args:
        concept_name: The concept to quiz on. Use the document topic for a full-document quiz.
        difficulty_level: "beginner", "intermediate", or "advanced"
        num_questions: Number of questions to generate (default: 3)
        question_types: Comma-separated question types (e.g. "multiple_choice,short_answer")
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
    types_list = [t.strip() for t in question_types.split(",")]

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

Question Types to Include: {', '.join(types_list)}

Requirements:
- Each question should test understanding of {concept_name}
- Questions should be appropriate for {difficulty_level} level
- Include a mix of question types if multiple types specified
- For multiple choice questions, provide 4 options as full text strings (NOT letters like A/B/C/D)
- The correct_answer field MUST be the FULL option text (e.g. "Generating Human-Like Text"), NOT a letter
- For short answer questions, provide a clear, concise correct answer
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
            "question_type": "short_answer",
            "question": "Question text here?",
            "options": null,
            "correct_answer": "Correct answer here",
            "explanation": "Brief explanation here"
        }}
    ],
    "total_questions": {num_questions}
}}

IMPORTANT: correct_answer for multiple_choice MUST be the exact full text of one of the options, never a letter.
Return ONLY valid JSON, no additional text before or after."""

    response = llm.invoke(prompt)
    content = str(response.content).strip()
    
    import json
    
    json_start = content.find("{")
    json_end = content.rfind("}") + 1
    
    if json_start != -1 and json_end > json_start:
        json_content = content[json_start:json_end]
        try:
            quiz_data = json.loads(json_content)
            return quiz_data
        except json.JSONDecodeError as e:
            return {
                "concept_name": concept_name,
                "difficulty_level": difficulty_level,
                "questions": [],
                "total_questions": 0,
                "error": f"Failed to parse JSON: {str(e)}",
                "raw_response": content[:500],
            }
    
    return {
        "concept_name": concept_name,
        "difficulty_level": difficulty_level,
        "questions": [],
        "total_questions": 0,
        "error": "No valid JSON found in response",
        "raw_response": content[:500],
    }

