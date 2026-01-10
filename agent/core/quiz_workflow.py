import json
from typing import Any, Dict, List, Optional

from agent.core.state import StudySessionState
from agent.tools.evaluator_tool import evaluate_response
from agent.tools.quizzer_tool import generate_quiz


class QuizWorkflow:
    def __init__(self, state: StudySessionState):
        self.state = state
        self.current_quiz: Optional[Dict[str, Any]] = None
    
    def generate_quiz_for_concept(
        self,
        concept_name: str,
        difficulty_level: Optional[str] = None,
        num_questions: int = 3,
        question_types: str = "multiple_choice,short_answer",
    ) -> Dict[str, Any]:
        if difficulty_level is None:
            concept_progress = self.state.get_concept_progress(concept_name)
            if concept_progress:
                difficulty_level = concept_progress.difficulty_level.value
            else:
                difficulty_level = self.state.overall_difficulty.value
        
        quiz_result = generate_quiz.invoke({
            "concept_name": concept_name,
            "difficulty_level": difficulty_level,
            "num_questions": num_questions,
            "question_types": question_types,
        })
        
        if isinstance(quiz_result, dict) and "error" not in quiz_result:
            self.current_quiz = quiz_result
            if concept_name not in self.state.concepts:
                from agent.core.state import DifficultyLevel
                difficulty = DifficultyLevel.BEGINNER
                if difficulty_level == "intermediate":
                    difficulty = DifficultyLevel.INTERMEDIATE
                elif difficulty_level == "advanced":
                    difficulty = DifficultyLevel.ADVANCED
                self.state.add_concept(concept_name, difficulty)
        
        return quiz_result
    
    def evaluate_learner_answers(
        self,
        learner_answers: List[Dict[str, Any]],
        concept_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.current_quiz:
            if concept_name:
                quiz_result = self.generate_quiz_for_concept(concept_name)
                if "error" in quiz_result:
                    return {
                        "error": "Failed to generate quiz",
                        "quiz_result": quiz_result,
                    }
            else:
                return {
                    "error": "No quiz available. Generate a quiz first or provide concept_name.",
                }
        
        quiz_data_str = json.dumps(self.current_quiz)
        answers_data = {"answers": learner_answers}
        answers_data_str = json.dumps(answers_data)
        
        evaluation_result = evaluate_response.invoke({
            "quiz_data": quiz_data_str,
            "learner_answers": answers_data_str,
        })
        
        if isinstance(evaluation_result, dict) and "error" not in evaluation_result:
            average_score = evaluation_result.get("average_score")
            if average_score is not None and concept_name:
                if concept_name in self.state.concepts:
                    self.state.mark_concept_quizzed(concept_name, float(average_score))
            elif average_score is not None and not concept_name:
                concept_name_from_quiz = self.current_quiz.get("concept_name")
                if concept_name_from_quiz and concept_name_from_quiz in self.state.concepts:
                    self.state.mark_concept_quizzed(concept_name_from_quiz, float(average_score))
        
        return evaluation_result
    
    def complete_quiz_flow(
        self,
        concept_name: str,
        learner_answers: List[Dict[str, Any]],
        difficulty_level: Optional[str] = None,
        num_questions: int = 3,
        question_types: str = "multiple_choice,short_answer",
    ) -> Dict[str, Any]:
        quiz_result = self.generate_quiz_for_concept(
            concept_name=concept_name,
            difficulty_level=difficulty_level,
            num_questions=num_questions,
            question_types=question_types,
        )
        
        if "error" in quiz_result:
            return {
                "error": "Quiz generation failed",
                "quiz_result": quiz_result,
            }
        
        evaluation_result = self.evaluate_learner_answers(
            learner_answers=learner_answers,
            concept_name=concept_name,
        )
        
        return {
            "quiz": quiz_result,
            "evaluation": evaluation_result,
            "concept_name": concept_name,
            "concept_status": self.state.get_concept_progress(concept_name).status.value if concept_name in self.state.concepts else None,
        }
    
    def get_quiz_status(self, concept_name: str) -> Dict[str, Any]:
        concept_progress = self.state.get_concept_progress(concept_name)
        if not concept_progress:
            return {
                "concept_name": concept_name,
                "quiz_taken": False,
                "score": None,
                "status": "not_started",
            }
        
        return {
            "concept_name": concept_name,
            "quiz_taken": concept_progress.quiz_taken,
            "score": concept_progress.score,
            "status": concept_progress.status.value,
            "retry_count": concept_progress.retry_count,
            "quizzed_at": concept_progress.quizzed_at.isoformat() if concept_progress.quizzed_at else None,
        }
    
    def can_retry_quiz(self, concept_name: str) -> bool:
        concept_progress = self.state.get_concept_progress(concept_name)
        if not concept_progress:
            return False
        
        return concept_progress.status.value == "needs_retry"

