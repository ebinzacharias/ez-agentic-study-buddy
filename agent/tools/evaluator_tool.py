import json
import re
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool


def normalize_text(text: str) -> str:
    return re.sub(r'[^\w\s]', '', text.lower().strip())


def check_keyword_match(answer: str, correct_answer: str, required_keywords: Optional[List[str]] = None) -> bool:
    answer_normalized = normalize_text(answer)
    correct_normalized = normalize_text(correct_answer)
    
    if answer_normalized == correct_normalized:
        return True
    
    if required_keywords:
        answer_lower = answer.lower()
        return all(keyword.lower() in answer_lower for keyword in required_keywords)
    
    return False


def score_multiple_choice(learner_answer: str, correct_answer: str, options: Optional[List[str]] = None) -> float:
    learner_normalized = normalize_text(learner_answer)
    correct_normalized = normalize_text(correct_answer)
    
    if learner_normalized == correct_normalized:
        return 1.0
    
    if options:
        learner_matches = [opt for opt in options if normalize_text(opt) == learner_normalized]
        correct_matches = [opt for opt in options if normalize_text(opt) == correct_normalized]
        
        if learner_matches and correct_matches:
            if learner_matches[0] == correct_matches[0]:
                return 1.0
    
    if correct_normalized in learner_normalized or learner_normalized in correct_normalized:
        return 0.5
    
    return 0.0


def score_short_answer(learner_answer: str, correct_answer: str) -> float:
    learner_normalized = normalize_text(learner_answer)
    correct_normalized = normalize_text(correct_answer)
    
    if learner_normalized == correct_normalized:
        return 1.0
    
    if learner_normalized in correct_normalized or correct_normalized in learner_normalized:
        return 0.7
    
    words_correct = normalize_text(correct_answer).split()
    words_learner = learner_normalized.split()
    
    if not words_correct:
        return 0.0
    
    matching_words = sum(1 for word in words_correct if word in learner_normalized)
    partial_score = matching_words / len(words_correct)
    
    if partial_score >= 0.6:
        return 0.6
    elif partial_score >= 0.4:
        return 0.4
    elif partial_score >= 0.2:
        return 0.2
    
    return 0.0


def extract_keywords_from_answer(correct_answer: str) -> List[str]:
    words = normalize_text(correct_answer).split()
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'we', 'us', 'you', 'he', 'she', 'him', 'her'}
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    return keywords[:5]


@tool
def evaluate_response(
    quiz_data: str,
    learner_answers: str,
) -> Dict[str, Any]:
    """
    Evaluates learner responses to a quiz using explicit, rule-based scoring logic.
    
    This tool scores learner answers using explicit rules including keyword matching,
    exact matches, partial credit for keyword presence, and question-type-specific logic.
    The scoring is deterministic and consistent, not relying solely on LLM judgment.
    
    Args:
        quiz_data: JSON string containing the quiz data with questions, correct answers, and question types
        learner_answers: JSON string containing learner answers in format:
          {
            "answers": [
              {"question_number": 1, "answer": "learner answer here"},
              {"question_number": 2, "answer": "another answer"}
            ]
          }
    
    Returns:
        A dictionary containing:
        - total_questions: Total number of questions
        - questions_evaluated: Number of questions with answers
        - scores: List of score dictionaries, each containing:
          - question_number: Question number
          - score: Numeric score (0.0 to 1.0)
          - is_correct: Boolean indicating if answer is correct (score >= 0.8)
          - feedback: Brief feedback string
        - total_score: Sum of all scores
        - average_score: Average score across all questions (0.0 to 1.0)
        - overall_percentage: Overall score as percentage (0 to 100)
    
    Example:
        >>> quiz = '{"questions": [{"question_number": 1, "question_type": "multiple_choice", ...}]}'
        >>> answers = '{"answers": [{"question_number": 1, "answer": "Option A"}]}'
        >>> evaluate_response(quiz, answers)
        {
            "total_questions": 3,
            "questions_evaluated": 1,
            "scores": [{"question_number": 1, "score": 1.0, "is_correct": True, "feedback": "Correct!"}],
            "total_score": 1.0,
            "average_score": 1.0,
            "overall_percentage": 100.0
        }
    """
    try:
        quiz_dict = json.loads(quiz_data) if isinstance(quiz_data, str) else quiz_data
        answers_dict = json.loads(learner_answers) if isinstance(learner_answers, str) else learner_answers
    except (json.JSONDecodeError, TypeError) as e:
        return {
            "error": f"Invalid JSON format: {str(e)}",
            "total_questions": 0,
            "questions_evaluated": 0,
            "scores": [],
            "total_score": 0.0,
            "average_score": 0.0,
            "overall_percentage": 0.0,
        }
    
    questions = quiz_dict.get("questions", [])
    learner_answers_list = answers_dict.get("answers", [])
    
    answer_map = {ans.get("question_number"): ans.get("answer", "") for ans in learner_answers_list}
    
    scores = []
    total_score = 0.0
    
    for question in questions:
        question_num = question.get("question_number")
        question_type = question.get("question_type", "").lower()
        correct_answer = question.get("correct_answer", "")
        learner_answer = answer_map.get(question_num, "")
        
        if not learner_answer:
            scores.append({
                "question_number": question_num,
                "score": 0.0,
                "is_correct": False,
                "feedback": "No answer provided",
            })
            continue
        
        score = 0.0
        
        if question_type == "multiple_choice":
            options = question.get("options")
            score = score_multiple_choice(learner_answer, correct_answer, options)
        
        elif question_type == "short_answer":
            score = score_short_answer(learner_answer, correct_answer)
            
            if score < 1.0 and score > 0.0:
                keywords = extract_keywords_from_answer(correct_answer)
                if keywords and check_keyword_match(learner_answer, correct_answer, keywords):
                    score = max(score, 0.8)
        
        elif question_type == "true_false":
            learner_normalized = normalize_text(learner_answer)
            correct_normalized = normalize_text(correct_answer)
            score = 1.0 if learner_normalized == correct_normalized else 0.0
        
        else:
            learner_normalized = normalize_text(learner_answer)
            correct_normalized = normalize_text(correct_answer)
            score = 1.0 if learner_normalized == correct_normalized else 0.0
        
        score = max(0.0, min(1.0, score))
        
        is_correct = score >= 0.8
        
        if score >= 0.8:
            feedback = "Correct!"
        elif score >= 0.6:
            feedback = "Mostly correct, but could be more precise"
        elif score >= 0.4:
            feedback = "Partially correct, missing some key points"
        elif score > 0.0:
            feedback = "Incorrect, but shows some understanding"
        else:
            feedback = "Incorrect"
        
        scores.append({
            "question_number": question_num,
            "score": round(score, 2),
            "is_correct": is_correct,
            "feedback": feedback,
        })
        
        total_score += score
    
    total_questions = len(questions)
    questions_evaluated = len([s for s in scores if answer_map.get(s["question_number"])])
    average_score = total_score / total_questions if total_questions > 0 else 0.0
    overall_percentage = average_score * 100.0
    
    return {
        "total_questions": total_questions,
        "questions_evaluated": questions_evaluated,
        "scores": scores,
        "total_score": round(total_score, 2),
        "average_score": round(average_score, 2),
        "overall_percentage": round(overall_percentage, 2),
    }

