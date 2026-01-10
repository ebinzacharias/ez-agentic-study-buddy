from typing import Any, Dict, List, Optional

from agent.core.state import ConceptProgress, ConceptStatus, DifficultyLevel, StudySessionState


class RetryManager:
    MAX_RETRIES = 3
    LOW_SCORE_THRESHOLD = 0.6
    EXCELLENT_SCORE_THRESHOLD = 0.8
    
    def __init__(self, state: StudySessionState):
        self.state = state
    
    def should_retry(self, concept_name: str, quiz_score: Optional[float] = None) -> bool:
        """
        Determines if a concept should be retried based on quiz score.
        
        Args:
            concept_name: Name of the concept to check
            quiz_score: Quiz score (0.0 to 1.0). If None, uses concept's stored score.
        
        Returns:
            True if concept should be retried, False otherwise
        """
        concept_progress = self.state.get_concept_progress(concept_name)
        if not concept_progress:
            return False
        
        score = quiz_score if quiz_score is not None else concept_progress.score
        if score is None:
            return False
        
        if score < self.LOW_SCORE_THRESHOLD:
            if concept_progress.retry_count < self.MAX_RETRIES:
                return True
        
        return False
    
    def can_retry(self, concept_name: str) -> bool:
        """
        Checks if a concept can still be retried (hasn't exceeded max retries).
        
        Args:
            concept_name: Name of the concept to check
        
        Returns:
            True if retries are still available, False if max retries exceeded
        """
        concept_progress = self.state.get_concept_progress(concept_name)
        if not concept_progress:
            return False
        
        return concept_progress.retry_count < self.MAX_RETRIES
    
    def mark_for_retry(self, concept_name: str, quiz_score: float) -> Dict[str, Any]:
        """
        Marks a concept for retry and increments retry count.
        
        Args:
            concept_name: Name of the concept to mark for retry
            quiz_score: Quiz score that triggered the retry
        
        Returns:
            Dictionary with retry information
        """
        concept_progress = self.state.get_concept_progress(concept_name)
        if not concept_progress:
            return {
                "error": f"Concept '{concept_name}' not found in state",
                "can_retry": False,
            }
        
        if quiz_score >= self.LOW_SCORE_THRESHOLD:
            return {
                "error": f"Score {quiz_score:.2f} is above retry threshold {self.LOW_SCORE_THRESHOLD}",
                "can_retry": False,
            }
        
        if concept_progress.retry_count >= self.MAX_RETRIES:
            return {
                "error": f"Max retries ({self.MAX_RETRIES}) exceeded for '{concept_name}'",
                "can_retry": False,
                "retry_count": concept_progress.retry_count,
                "max_retries": self.MAX_RETRIES,
            }
        
        concept_progress.quiz_taken = True
        concept_progress.score = quiz_score
        from datetime import datetime
        concept_progress.quizzed_at = datetime.now()
        concept_progress.increment_retry()
        
        return {
            "concept_name": concept_name,
            "retry_count": concept_progress.retry_count,
            "max_retries": self.MAX_RETRIES,
            "can_retry": concept_progress.retry_count < self.MAX_RETRIES,
            "quiz_score": quiz_score,
            "status": concept_progress.status.value,
        }
    
    def get_retry_strategy(self, concept_name: str) -> Dict[str, Any]:
        """
        Determines the retry strategy for a concept based on retry count and performance.
        
        Args:
            concept_name: Name of the concept
        
        Returns:
            Dictionary with retry strategy information
        """
        concept_progress = self.state.get_concept_progress(concept_name)
        if not concept_progress:
            return {
                "error": f"Concept '{concept_name}' not found",
                "strategy": None,
            }
        
        retry_count = concept_progress.retry_count
        score = concept_progress.score or 0.0
        difficulty = concept_progress.difficulty_level
        
        if retry_count >= self.MAX_RETRIES:
            return {
                "strategy": "adapt_difficulty",
                "reason": f"Max retries exceeded ({retry_count} >= {self.MAX_RETRIES})",
                "action": "decrease_difficulty",
                "concept_name": concept_name,
            }
        
        strategies = [
            {
                "retry_count": 1,
                "strategy": "simplify_explanation",
                "approach": "Use simpler language, more examples, analogies",
                "difficulty_adjustment": None,
            },
            {
                "retry_count": 2,
                "strategy": "alternative_approach",
                "approach": "Try different teaching method, visual examples, step-by-step breakdown",
                "difficulty_adjustment": "consider_decreasing",
            },
            {
                "retry_count": 3,
                "strategy": "adapt_difficulty",
                "approach": "Decrease difficulty level before final retry",
                "difficulty_adjustment": "decrease",
            },
        ]
        
        strategy_info = strategies[min(retry_count - 1, len(strategies) - 1)] if retry_count > 0 else strategies[0]
        
        context_notes = []
        if score < 0.4:
            context_notes.append("Very low score, need fundamental explanation")
        elif score < 0.5:
            context_notes.append("Low score, focus on basics")
        else:
            context_notes.append("Moderate score, clarify specific misunderstandings")
        
        if retry_count > 1:
            context_notes.append(f"Previous attempts ({retry_count}) were unsuccessful")
        
        return {
            "strategy": strategy_info["strategy"],
            "approach": strategy_info["approach"],
            "retry_count": retry_count,
            "difficulty_adjustment": strategy_info.get("difficulty_adjustment"),
            "current_difficulty": difficulty.value,
            "current_score": score,
            "context_notes": context_notes,
            "concept_name": concept_name,
        }
    
    def get_reteaching_context(self, concept_name: str) -> str:
        """
        Generates context string for re-teaching a concept based on retry history.
        
        Args:
            concept_name: Name of the concept
        
        Returns:
            Context string for teaching tool
        """
        strategy = self.get_retry_strategy(concept_name)
        
        if "error" in strategy:
            return f"Re-teaching concept: {concept_name}"
        
        context_parts = [
            f"Re-teaching attempt {strategy['retry_count']}",
            f"Strategy: {strategy['strategy']}",
            f"Approach: {strategy['approach']}",
        ]
        
        if strategy.get("context_notes"):
            context_parts.extend(strategy["context_notes"])
        
        if strategy.get("current_score") is not None:
            context_parts.append(f"Previous score: {strategy['current_score']:.2f}")
        
        return ". ".join(context_parts) + "."
    
    def should_adapt_difficulty(self, concept_name: str) -> bool:
        """
        Determines if difficulty should be adapted instead of retrying.
        
        Args:
            concept_name: Name of the concept
        
        Returns:
            True if difficulty should be adapted, False otherwise
        """
        concept_progress = self.state.get_concept_progress(concept_name)
        if not concept_progress:
            return False
        
        return concept_progress.retry_count >= self.MAX_RETRIES
    
    def get_concepts_exceeding_retries(self) -> List[str]:
        """
        Returns list of concept names that have exceeded max retries.
        
        Returns:
            List of concept names
        """
        concepts_exceeding = []
        for concept_name, progress in self.state.concepts.items():
            if progress.retry_count >= self.MAX_RETRIES:
                concepts_exceeding.append(concept_name)
        return concepts_exceeding
    
    def reset_retry_for_concept(self, concept_name: str) -> bool:
        """
        Resets retry count for a concept (e.g., after successful adaptation).
        
        Args:
            concept_name: Name of the concept
        
        Returns:
            True if reset successful, False otherwise
        """
        concept_progress = self.state.get_concept_progress(concept_name)
        if not concept_progress:
            return False
        
        concept_progress.retry_count = 0
        return True

