from typing import Any, Dict, List, Optional

from agent.core.retry_manager import RetryManager
from agent.core.state import ConceptStatus, StudySessionState


class DecisionRules:
    def __init__(self, state: StudySessionState):
        self.state = state
        self.retry_manager = RetryManager(state)
    
    def decide_next_action(self, observation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if observation is None:
            observation = self._get_observation()
        
        concepts_planned = self.state.concepts_planned
        concepts = self.state.concepts
        current_concept = self.state.current_concept
        
        if not concepts_planned and not concepts:
            return {
                "action": "plan_learning_path",
                "tool_name": "plan_learning_path",
                "tool_args": {
                    "topic": self.state.topic,
                    "difficulty_level": self.state.overall_difficulty.value,
                    "max_concepts": 10,
                },
                "reason": "No learning path planned yet",
            }
        
        if concepts_planned and not concepts:
            first_concept = concepts_planned[0]
            return {
                "action": "add_concept",
                "concept_name": first_concept,
                "reason": f"Adding first concept: {first_concept}",
            }
        
        concepts_needing_retry = self.state.get_concepts_needing_retry()
        if concepts_needing_retry:
            retry_concept = concepts_needing_retry[0]
            concept_progress = self.state.get_concept_progress(retry_concept)
            
            if not concept_progress:
                next_concept = self._get_next_untaught_concept()
                if next_concept:
                    return {
                        "action": "set_current_concept",
                        "concept_name": next_concept,
                        "reason": f"Skipping invalid retry concept, moving to: {next_concept}",
                    }
            
            if self.retry_manager.should_adapt_difficulty(retry_concept):
                return {
                    "action": "adapt_difficulty",
                    "concept_name": retry_concept,
                    "reason": f"Concept {retry_concept} exceeded max retries ({RetryManager.MAX_RETRIES}), adapting difficulty",
                }
            
            if not self.retry_manager.can_retry(retry_concept):
                concepts_exceeding = self.retry_manager.get_concepts_exceeding_retries()
                if retry_concept in concepts_exceeding:
                    return {
                        "action": "adapt_difficulty",
                        "concept_name": retry_concept,
                        "reason": f"Concept {retry_concept} cannot be retried further, adapting difficulty",
                    }
            
            retry_strategy = self.retry_manager.get_retry_strategy(retry_concept)
            retry_context = self.retry_manager.get_reteaching_context(retry_concept)
            
            current_retry_count = concept_progress.retry_count if concept_progress else 0
            difficulty_level = concept_progress.difficulty_level.value if concept_progress else "beginner"
            
            tool_args = {
                "concept_name": retry_concept,
                "difficulty_level": difficulty_level,
                "context": retry_context,
            }
            
            if "error" not in retry_strategy:
                if retry_strategy.get("retry_count"):
                    tool_args["retry_attempt"] = retry_strategy.get("retry_count")
                if retry_strategy.get("strategy"):
                    tool_args["alternative_strategy"] = retry_strategy.get("strategy")
            
            strategy_name = retry_strategy.get("strategy", "standard") if "error" not in retry_strategy else "standard"
            
            return {
                "action": "teach_concept",
                "tool_name": "teach_concept",
                "tool_args": tool_args,
                "reason": f"Retrying concept: {retry_concept} (attempt {current_retry_count + 1}/{RetryManager.MAX_RETRIES}, strategy: {strategy_name})",
            }
        
        if not current_concept:
            next_concept = self._get_next_untaught_concept()
            if next_concept:
                return {
                    "action": "set_current_concept",
                    "concept_name": next_concept,
                    "reason": f"Setting current concept to: {next_concept}",
                }
        
        if current_concept:
            concept_progress = self.state.get_concept_progress(current_concept)
            
            if not concept_progress:
                return {
                    "action": "add_concept",
                    "concept_name": current_concept,
                    "reason": f"Adding current concept: {current_concept}",
                }
            
            status = concept_progress.status
            
            if status == ConceptStatus.NOT_STARTED or status == ConceptStatus.IN_PROGRESS:
                return {
                    "action": "teach_concept",
                    "tool_name": "teach_concept",
                    "tool_args": {
                        "concept_name": current_concept,
                        "difficulty_level": concept_progress.difficulty_level.value,
                        "context": self._get_teaching_context(),
                    },
                    "reason": f"Teaching concept: {current_concept}",
                }
            
            if status == ConceptStatus.TAUGHT:
                return {
                    "action": "generate_quiz",
                    "tool_name": "generate_quiz",
                    "tool_args": {
                        "concept_name": current_concept,
                        "difficulty_level": concept_progress.difficulty_level.value,
                        "num_questions": 3,
                        "question_types": "multiple_choice,short_answer",
                    },
                    "reason": f"Generating quiz for: {current_concept}",
                }
            
            if status == ConceptStatus.QUIZZED:
                if concept_progress.score is not None and concept_progress.score < 0.6:
                    return {
                        "action": "teach_concept",
                        "tool_name": "teach_concept",
                        "tool_args": {
                            "concept_name": current_concept,
                            "difficulty_level": concept_progress.difficulty_level.value,
                            "context": f"Re-teaching after low quiz score ({concept_progress.score:.2f})",
                        },
                        "reason": f"Re-teaching {current_concept} due to low score",
                    }
                else:
                    next_concept = self._get_next_untaught_concept()
                    if next_concept:
                        return {
                            "action": "set_current_concept",
                            "concept_name": next_concept,
                            "reason": f"Moving to next concept: {next_concept}",
                        }
            
            if status == ConceptStatus.MASTERED:
                next_concept = self._get_next_untaught_concept()
                if next_concept:
                    return {
                        "action": "set_current_concept",
                        "concept_name": next_concept,
                        "reason": f"Concept mastered, moving to: {next_concept}",
                    }
                else:
                    return {
                        "action": "session_complete",
                        "reason": "All concepts mastered",
                    }
        
        next_concept = self._get_next_untaught_concept()
        if next_concept:
            return {
                "action": "set_current_concept",
                "concept_name": next_concept,
                "reason": f"Moving to next concept: {next_concept}",
            }
        
        return {
            "action": "session_complete",
            "reason": "No more concepts to teach",
        }
    
    def _get_observation(self) -> Dict:
        return {
            "session_id": self.state.session_id,
            "topic": self.state.topic,
            "current_concept": self.state.current_concept,
            "concepts_planned": self.state.concepts_planned,
            "concepts_taught": self.state.get_taught_concepts(),
            "concepts_mastered": self.state.get_mastered_concepts(),
            "concepts_needing_retry": self.state.get_concepts_needing_retry(),
            "progress_percentage": self.state.get_progress_percentage(),
            "average_score": self.state.get_average_score(),
            "overall_difficulty": self.state.overall_difficulty.value,
        }
    
    def _get_next_untaught_concept(self) -> Optional[str]:
        for concept_name in self.state.concepts_planned:
            concept_progress = self.state.get_concept_progress(concept_name)
            if not concept_progress or concept_progress.status not in [
                ConceptStatus.MASTERED,
            ]:
                return concept_name
        
        for concept_name, progress in self.state.concepts.items():
            if progress.status not in [ConceptStatus.MASTERED]:
                return concept_name
        
        return None
    
    def _get_teaching_context(self) -> str:
        taught_concepts = self.state.get_taught_concepts()
        if taught_concepts:
            return f"Learner has already learned: {', '.join(taught_concepts[:3])}"
        return ""

