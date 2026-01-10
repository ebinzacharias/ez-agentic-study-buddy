from typing import Optional

from langchain_core.tools import tool

from agent.core.state import DifficultyLevel
from agent.utils.llm_client import get_llm_client


@tool
def teach_concept(
    concept_name: str,
    difficulty_level: str = "beginner",
    context: str = "",
    retry_attempt: Optional[int] = None,
    alternative_strategy: Optional[str] = None,
) -> str:
    """
    Generates a clear, structured explanation of a concept at an appropriate difficulty level.
    
    This tool creates teaching content that explains a concept in a way that matches
    the learner's current difficulty level. It adapts vocabulary, examples, depth,
    and complexity based on the difficulty setting. Supports retry attempts with
    alternative teaching strategies.
    
    Args:
        concept_name: The name of the concept to teach (e.g., "Variables and Data Types", "Functions")
        difficulty_level: The difficulty level for the explanation ("beginner", "intermediate", or "advanced")
        context: Optional context about what the learner already knows or what concepts were taught before
        retry_attempt: Optional retry attempt number (1, 2, 3). If provided, uses alternative teaching strategies.
        alternative_strategy: Optional strategy name ("simplify_explanation", "alternative_approach"). If provided, uses specific alternative approach.
    
    Returns:
        A formatted teaching explanation string containing:
        - Introduction to the concept
        - Core explanation adapted to difficulty level
        - Practical examples
        - Key takeaways
    
    Example:
        >>> teach_concept("Variables", "beginner")
        "Variables are like labeled boxes where you can store information..."
        
        >>> teach_concept("Functions", "intermediate", retry_attempt=2, alternative_strategy="alternative_approach")
        "Let's try a different way to understand functions..."
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
    
    prompt = f"""Create a clear, structured explanation of the concept "{concept_name}" at {difficulty_level} level.

Difficulty Level Guidelines:
- Vocabulary: {guide['vocabulary']}
- Examples: {guide['examples']}
- Depth: {guide['depth']}
- Technical Terms: {guide['technical_terms']}

{f'Context: {context}' if context else ''}
{retry_instructions}

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

