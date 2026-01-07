from langchain_core.tools import tool

from agent.core.state import DifficultyLevel
from agent.utils.llm_client import get_llm_client


@tool
def teach_concept(
    concept_name: str,
    difficulty_level: str = "beginner",
    context: str = "",
) -> str:
    """
    Generates a clear, structured explanation of a concept at an appropriate difficulty level.
    
    This tool creates teaching content that explains a concept in a way that matches
    the learner's current difficulty level. It adapts vocabulary, examples, depth,
    and complexity based on the difficulty setting.
    
    Args:
        concept_name: The name of the concept to teach (e.g., "Variables and Data Types", "Functions")
        difficulty_level: The difficulty level for the explanation ("beginner", "intermediate", or "advanced")
        context: Optional context about what the learner already knows or what concepts were taught before
    
    Returns:
        A formatted teaching explanation string containing:
        - Introduction to the concept
        - Core explanation adapted to difficulty level
        - Practical examples
        - Key takeaways
    
    Example:
        >>> teach_concept("Variables", "beginner")
        "Variables are like labeled boxes where you can store information...
        
        For beginners, think of a variable like a labeled box..."
        
        >>> teach_concept("Closures", "advanced", context="Learner knows functions and scopes")
        "Closures are functions that capture variables from their enclosing scope..."
    """
    llm = get_llm_client()
    
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
    
    prompt = f"""Create a clear, structured explanation of the concept "{concept_name}" at {difficulty_level} level.

Difficulty Level Guidelines:
- Vocabulary: {guide['vocabulary']}
- Examples: {guide['examples']}
- Depth: {guide['depth']}
- Technical Terms: {guide['technical_terms']}

{f'Context: The learner already knows: {context}' if context else ''}

Structure your explanation as follows:
1. **Introduction**: Briefly introduce what {concept_name} is and why it matters
2. **Core Explanation**: Explain the concept clearly, adapting to {difficulty_level} level
3. **Examples**: Provide {guide['examples']} that illustrate the concept
4. **Key Takeaways**: Summarize the most important points

Make sure the explanation:
- Uses appropriate language for {difficulty_level} level
- Includes practical examples
- Is clear and easy to follow
- Builds understanding progressively
"""

    response = llm.invoke(prompt)
    content = response.content.strip()
    
    return content

