import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.tools.evaluator_tool import evaluate_response


def test_evaluator():
    print("Testing Evaluator Tool...")
    print("-" * 60)
    
    quiz_data = {
        "concept_name": "Variables and Data Types",
        "difficulty_level": "beginner",
        "questions": [
            {
                "question_number": 1,
                "question_type": "multiple_choice",
                "question": "What is a variable in Python?",
                "options": ["A labeled storage location", "A function", "A loop", "A comment"],
                "correct_answer": "A labeled storage location",
                "explanation": "Variables store values in memory"
            },
            {
                "question_number": 2,
                "question_type": "short_answer",
                "question": "What keyword is used to create a variable in Python?",
                "options": None,
                "correct_answer": "No keyword needed, just assign",
                "explanation": "Python variables are created by assignment"
            },
            {
                "question_number": 3,
                "question_type": "true_false",
                "question": "Variables in Python must be declared before use.",
                "options": None,
                "correct_answer": "False",
                "explanation": "Python variables don't need declaration"
            }
        ],
        "total_questions": 3
    }
    
    test_cases = [
        {
            "name": "All Correct",
            "answers": [
                {"question_number": 1, "answer": "A labeled storage location"},
                {"question_number": 2, "answer": "No keyword needed, just assign"},
                {"question_number": 3, "answer": "False"}
            ]
        },
        {
            "name": "Partial Correct",
            "answers": [
                {"question_number": 1, "answer": "A labeled storage location"},
                {"question_number": 2, "answer": "No keyword"},
                {"question_number": 3, "answer": "True"}
            ]
        },
        {
            "name": "All Incorrect",
            "answers": [
                {"question_number": 1, "answer": "A function"},
                {"question_number": 2, "answer": "var"},
                {"question_number": 3, "answer": "True"}
            ]
        },
        {
            "name": "Missing Answer",
            "answers": [
                {"question_number": 1, "answer": "A labeled storage location"},
                {"question_number": 2, "answer": ""}
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['name']}")
        print("-" * 60)
        
        learner_answers = {"answers": test_case["answers"]}
        
        try:
            result = evaluate_response.invoke({
                "quiz_data": json.dumps(quiz_data),
                "learner_answers": json.dumps(learner_answers)
            })
            
            print(f"✓ Tool executed successfully")
            print(f"\nResults:")
            print(f"  Total Questions: {result.get('total_questions', 0)}")
            print(f"  Questions Evaluated: {result.get('questions_evaluated', 0)}")
            print(f"  Total Score: {result.get('total_score', 0.0)}")
            print(f"  Average Score: {result.get('average_score', 0.0):.2f}")
            print(f"  Overall Percentage: {result.get('overall_percentage', 0.0):.1f}%")
            
            scores = result.get('scores', [])
            print(f"\n  Individual Scores:")
            for score in scores:
                status = "✓" if score.get('is_correct', False) else "✗"
                print(f"    {status} Q{score.get('question_number', '?')}: "
                      f"{score.get('score', 0.0):.2f} - {score.get('feedback', 'N/A')}")
            
        except Exception as e:
            print(f"✗ Tool execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n✓ Evaluator Tool test passed!")
    return True


if __name__ == "__main__":
    test_evaluator()

