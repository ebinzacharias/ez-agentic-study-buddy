from typing import List

from langchain_core.tools import tool

from agent.core.state import DifficultyLevel
from agent.utils.llm_client import call_with_retry, get_llm_client


@tool
def plan_learning_path(
    topic: str,
    difficulty_level: str = "beginner",
    max_concepts: int = 10,
    source_material: str = "",
) -> List[dict]:
    """
    Breaks down a learning topic into an ordered list of concepts to teach.
    
    This tool analyzes a topic and creates a structured learning path by identifying
    the key concepts that should be taught in sequence. It considers prerequisites
    and logical ordering to ensure concepts build upon each other.

    When source_material is provided (from user-uploaded content), the learning path
    is derived from the actual material rather than general knowledge.
    
    Args:
        topic: The main topic or subject to create a learning path for (e.g., "Python Basics", "Machine Learning")
        difficulty_level: Overall difficulty level for the path ("beginner", "intermediate", or "advanced")
        max_concepts: Maximum number of concepts to include in the learning path (default: 10)
        source_material: Optional text extracted from user-uploaded study materials.
            When provided, concepts are grounded in the actual content.
    
    Returns:
        A list of dictionaries, each containing:
        - concept_name: Name of the concept to teach
        - difficulty: Difficulty level for this specific concept
        - order: Sequential order in the learning path (1, 2, 3, ...)
    
    Example:
        >>> plan_learning_path("Python Basics", "beginner", 5)
        [
            {"concept_name": "Variables and Data Types", "difficulty": "beginner", "order": 1},
            {"concept_name": "Control Structures", "difficulty": "beginner", "order": 2},
            ...
        ]
    """
    llm = get_llm_client()

    if source_material.strip():
        material_section = f"""
--- BEGIN UPLOADED STUDY MATERIAL ---
{source_material[:3000]}
--- END UPLOADED STUDY MATERIAL ---"""
        source_instruction = f"""
You are building a learning path STRICTLY from the uploaded material above.

Step 1 — Identify every distinct concept present in the material.
Step 2 — Rank them by importance to understanding the material (most central ideas first).
Step 3 — Select the most important concepts. Use as many as the material naturally supports, up to {max_concepts} maximum. If the material covers only one idea, return one concept. Do not pad or split artificially.
Step 4 — Re-order the selected concepts into a logical learning sequence (prerequisites first).

Rules:
- Every concept MUST come directly from the uploaded material. Do NOT invent or add outside knowledge.
- Return only as many concepts as the material genuinely contains. Do NOT force {max_concepts} concepts.
- Concept names must be concise (2–6 words) and reflect the actual content of the material.
- Overall difficulty level: {difficulty_level}
"""
    else:
        material_section = ""
        source_instruction = f"""
Break down the topic "{topic}" into up to {max_concepts} key concepts.

Requirements:
- Create a logical learning sequence where each concept builds on the previous ones
- Overall difficulty level: {difficulty_level}
- Order from fundamental to advanced, considering prerequisites
- Each concept should be specific and focused
"""

    prompt = f"""Task: produce a numbered learning-path list.
{material_section}
{source_instruction}
Return ONLY a numbered list of concept names, one per line. No explanations, no headers.
Format:
1. Concept Name
2. Concept Name
..."""

    try:
        response = call_with_retry(llm.invoke, prompt)
    except Exception as exc:
        return [{"error": str(exc), "error_code": "llm_error", "concept_name": topic, "difficulty": difficulty_level, "order": 1}]

    content = str(response.content).strip()
    
    concepts = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line[0].isdigit():
            parts = line.split('.', 1)
            if len(parts) == 2:
                order = int(parts[0].strip())
                concept_name = parts[1].strip()
                
                difficulty = DifficultyLevel.BEGINNER
                if difficulty_level.lower() == "intermediate":
                    difficulty = DifficultyLevel.INTERMEDIATE
                elif difficulty_level.lower() == "advanced":
                    difficulty = DifficultyLevel.ADVANCED
                
                concepts.append({
                    "concept_name": concept_name,
                    "difficulty": difficulty.value,
                    "order": order
                })
        
        if len(concepts) >= max_concepts:
            break
    
    return concepts

