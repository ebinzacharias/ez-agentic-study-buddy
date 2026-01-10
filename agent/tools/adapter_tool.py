from typing import Any, Dict, Optional

from langchain_core.tools import tool


@tool
def adapt_difficulty(
    concept_name: str,
    current_difficulty: str,
    quiz_score: Optional[float] = None,
    retry_count: Optional[int] = None,
    average_score: Optional[float] = None,
    performance_history: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Adapts the difficulty level of a concept based on learner performance metrics.
    
    This tool analyzes performance metrics (quiz scores, retry counts, average scores)
    and adjusts the difficulty level up or down to optimize learning.
    
    Args:
        concept_name: Name of the concept to adapt difficulty for
        current_difficulty: Current difficulty level (beginner, intermediate, advanced)
        quiz_score: Most recent quiz score (0.0 to 1.0, where 1.0 is perfect)
        retry_count: Number of times the concept has been retried
        average_score: Average score across all quizzes for this concept (0.0 to 1.0)
        performance_history: JSON string with performance history (optional)
    
    Returns:
        Dictionary with:
            - concept_name: Name of the concept
            - old_difficulty: Previous difficulty level
            - new_difficulty: New difficulty level
            - reason: Explanation of why difficulty was adjusted
            - metrics_analyzed: Dictionary of metrics used for decision
    """
    difficulty_levels = ["beginner", "intermediate", "advanced"]
    
    if current_difficulty not in difficulty_levels:
        return {
            "error": f"Invalid difficulty level: {current_difficulty}",
            "concept_name": concept_name,
        }
    
    current_index = difficulty_levels.index(current_difficulty)
    old_difficulty = current_difficulty
    new_difficulty = current_difficulty
    reason_parts = []
    metrics = {}
    
    if quiz_score is not None:
        metrics["quiz_score"] = quiz_score
        if quiz_score < 0.0 or quiz_score > 1.0:
            return {
                "error": f"Invalid quiz_score: {quiz_score}. Must be between 0.0 and 1.0",
                "concept_name": concept_name,
            }
    
    if retry_count is not None:
        metrics["retry_count"] = retry_count
        if retry_count < 0:
            return {
                "error": f"Invalid retry_count: {retry_count}. Must be non-negative",
                "concept_name": concept_name,
            }
    
    if average_score is not None:
        metrics["average_score"] = average_score
        if average_score < 0.0 or average_score > 1.0:
            return {
                "error": f"Invalid average_score: {average_score}. Must be between 0.0 and 1.0",
                "concept_name": concept_name,
            }
    
    if performance_history:
        try:
            import json
            history = json.loads(performance_history) if isinstance(performance_history, str) else performance_history
            metrics["performance_history"] = history
        except (json.JSONDecodeError, TypeError):
            pass
    
    if not metrics:
        return {
            "error": "No performance metrics provided. At least one metric (quiz_score, retry_count, or average_score) is required.",
            "concept_name": concept_name,
        }
    
    adaptation_decision = _determine_adaptation(
        current_difficulty=current_difficulty,
        quiz_score=quiz_score,
        retry_count=retry_count,
        average_score=average_score,
    )
    
    new_difficulty = adaptation_decision["new_difficulty"]
    reason_parts.append(adaptation_decision["reason"])
    
    if new_difficulty != current_difficulty:
        new_index = difficulty_levels.index(new_difficulty)
        direction = "increased" if new_index > current_index else "decreased"
        reason_parts.append(f"Difficulty {direction} from {current_difficulty} to {new_difficulty}")
    else:
        reason_parts.append(f"Difficulty maintained at {current_difficulty}")
    
    return {
        "concept_name": concept_name,
        "old_difficulty": old_difficulty,
        "new_difficulty": new_difficulty,
        "reason": ". ".join(reason_parts) + ".",
        "metrics_analyzed": metrics,
        "adaptation_applied": new_difficulty != current_difficulty,
    }


def _determine_adaptation(
    current_difficulty: str,
    quiz_score: Optional[float] = None,
    retry_count: Optional[int] = None,
    average_score: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Determines how to adapt difficulty based on performance metrics.
    
    Rules:
    - If quiz_score < 0.5 or average_score < 0.5: Decrease difficulty (unless already beginner)
    - If quiz_score >= 0.8 or average_score >= 0.8: Increase difficulty (unless already advanced)
    - If retry_count >= 3: Decrease difficulty (unless already beginner)
    - If retry_count == 0 and quiz_score >= 0.7: Can increase difficulty
    - Otherwise: Maintain current difficulty
    """
    difficulty_levels = ["beginner", "intermediate", "advanced"]
    current_index = difficulty_levels.index(current_difficulty)
    
    decrease_reasons = []
    increase_reasons = []
    
    if quiz_score is not None:
        if quiz_score < 0.5:
            decrease_reasons.append(f"Low quiz score ({quiz_score:.2f} < 0.5)")
        elif quiz_score >= 0.8:
            increase_reasons.append(f"High quiz score ({quiz_score:.2f} >= 0.8)")
    
    if average_score is not None:
        if average_score < 0.5:
            decrease_reasons.append(f"Low average score ({average_score:.2f} < 0.5)")
        elif average_score >= 0.8:
            increase_reasons.append(f"High average score ({average_score:.2f} >= 0.8)")
    
    if retry_count is not None:
        if retry_count >= 3:
            decrease_reasons.append(f"High retry count ({retry_count} >= 3)")
        elif retry_count == 0 and quiz_score is not None and quiz_score >= 0.7:
            increase_reasons.append(f"No retries needed and good performance (score {quiz_score:.2f})")
    
    if decrease_reasons:
        if current_index > 0:
            new_index = current_index - 1
            new_difficulty = difficulty_levels[new_index]
            return {
                "new_difficulty": new_difficulty,
                "reason": f"Decreasing difficulty: {', '.join(decrease_reasons)}",
            }
    
    if increase_reasons:
        if current_index < len(difficulty_levels) - 1:
            new_index = current_index + 1
            new_difficulty = difficulty_levels[new_index]
            return {
                "new_difficulty": new_difficulty,
                "reason": f"Increasing difficulty: {', '.join(increase_reasons)}",
            }
    
    return {
        "new_difficulty": current_difficulty,
        "reason": "Maintaining difficulty based on current performance metrics",
    }

