from typing import Dict, List

from langchain_core.tools import tool

from agent.utils.llm_client import get_llm_client


@tool
def generate_quiz(
    concept_name: str,
    difficulty_level: str = "beginner",
    num_questions: int = 3,
    question_types: str = "multiple_choice,short_answer",
) -> Dict[str, any]:
    """
    Generates a quiz to test understanding of a concept at an appropriate difficulty level.
    
    This tool creates questions that assess the learner's understanding of a concept.
    Questions are adapted to the difficulty level and can include multiple choice,
    short answer, and other question types.
    
    Args:
        concept_name: The name of the concept to create a quiz for (e.g., "Variables and Data Types", "Functions")
        difficulty_level: The difficulty level for the quiz ("beginner", "intermediate", or "advanced")
        num_questions: Number of questions to generate (default: 3)
        question_types: Comma-separated list of question types (e.g., "multiple_choice,short_answer" or "true_false,multiple_choice")
    
    Returns:
        A dictionary containing:
        - concept_name: Name of the concept being quizzed
        - difficulty_level: Difficulty level of the quiz
        - questions: List of question dictionaries, each containing:
          - question_number: Sequential number (1, 2, 3, ...)
          - question_type: Type of question (multiple_choice, short_answer, true_false, etc.)
          - question: The question text
          - options: List of options (for multiple choice), None for other types
          - correct_answer: The correct answer or answer key
          - explanation: Brief explanation of the correct answer
        - total_questions: Total number of questions generated
    
    Example:
        >>> generate_quiz("Variables", "beginner", 2, "multiple_choice")
        {
            "concept_name": "Variables",
            "difficulty_level": "beginner",
            "questions": [
                {
                    "question_number": 1,
                    "question_type": "multiple_choice",
                    "question": "What is a variable in Python?",
                    "options": ["A labeled storage location", ...],
                    "correct_answer": "A labeled storage location",
                    "explanation": "Variables store values..."
                },
                ...
            ],
            "total_questions": 2
        }
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
    
    prompt = f"""Create a quiz with {num_questions} questions about "{concept_name}" at {difficulty_level} level.

Difficulty Level Guidelines:
- Question Complexity: {guide['complexity']}
- Depth: {guide['depth']}
- Examples: {guide['examples']}

Question Types to Include: {', '.join(types_list)}

Requirements:
- Each question should test understanding of {concept_name}
- Questions should be appropriate for {difficulty_level} level
- Include a mix of question types if multiple types specified
- For multiple choice questions, provide 4 options (A, B, C, D)
- For short answer questions, provide clear correct answer
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
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
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

Return ONLY valid JSON, no additional text before or after."""

    response = llm.invoke(prompt)
    content = response.content.strip()
    
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

