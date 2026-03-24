from typing import List

from langchain_core.tools import tool

from agent.core.state import DifficultyLevel
from agent.utils.llm_client import get_llm_client


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

    material_block = ""
    if source_material.strip():
        material_block = f"""
--- BEGIN USER-UPLOADED STUDY MATERIAL ---
{source_material[:3000]}
--- END USER-UPLOADED STUDY MATERIAL ---

IMPORTANT: Derive the concepts primarily from the study material above.
Only add general-knowledge concepts if the material is insufficient.
"""
    
    prompt = f"""Break down the topic "{topic}" into {max_concepts} key concepts to teach.
{material_block}
Requirements:
- Create a logical learning sequence where each concept builds on previous ones
- Overall difficulty level: {difficulty_level}
- Each concept should be specific and focused
- Order concepts from fundamental to advanced
- Consider prerequisites between concepts

Return ONLY a numbered list of concept names, one per line, in the order they should be taught.
Format:
1. Concept Name 1
2. Concept Name 2
3. Concept Name 3
..."""

    response = llm.invoke(prompt)
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

