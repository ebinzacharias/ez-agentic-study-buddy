import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.core.quiz_workflow import QuizWorkflow
from agent.core.state import StudySessionState, DifficultyLevel


def test_complete_quiz_workflow():
    print("Testing Complete Quiz Workflow")
    print("=" * 60)
    
    state = StudySessionState(
        session_id="test-workflow-123",
        topic="Python Basics"
    )
    
    state.add_concept("Variables and Data Types", DifficultyLevel.BEGINNER)
    state.mark_concept_taught("Variables and Data Types")
    
    workflow = QuizWorkflow(state)
    
    concept_name = "Variables and Data Types"
    
    print("\n1. Initial State:")
    status = workflow.get_quiz_status(concept_name)
    print(f"   Concept: {status['concept_name']}")
    print(f"   Quiz Taken: {status['quiz_taken']}")
    print(f"   Score: {status['score']}")
    print(f"   Status: {status['status']}")
    
    print("\n2. Generating Quiz...")
    quiz_result = workflow.generate_quiz_for_concept(
        concept_name=concept_name,
        num_questions=3,
        question_types="multiple_choice,short_answer"
    )
    
    if "error" in quiz_result:
        print(f"   ✗ Failed to generate quiz: {quiz_result['error']}")
        return False
    
    print(f"   ✓ Quiz generated: {quiz_result.get('total_questions', 0)} questions")
    questions = quiz_result.get('questions', [])
    if questions:
        print(f"   Questions:")
        for q in questions:
            print(f"     Q{q.get('question_number', '?')}: {q.get('question_type', 'unknown')}")
    
    print("\n3. Simulating Learner Answers...")
    learner_answers = []
    for q in questions:
        if q.get('question_type') == 'multiple_choice' and q.get('options'):
            answer = q.get('options')[0]
        else:
            answer = q.get('correct_answer', 'test answer')
        learner_answers.append({
            "question_number": q.get('question_number'),
            "answer": answer
        })
        print(f"   Q{q.get('question_number')}: {answer[:50]}...")
    
    print("\n4. Evaluating Answers...")
    evaluation_result = workflow.evaluate_learner_answers(
        learner_answers=learner_answers,
        concept_name=concept_name
    )
    
    if "error" in evaluation_result:
        print(f"   ✗ Failed to evaluate: {evaluation_result['error']}")
        return False
    
    print(f"   ✓ Evaluation complete")
    print(f"   Total Questions: {evaluation_result.get('total_questions', 0)}")
    print(f"   Average Score: {evaluation_result.get('average_score', 0.0):.2f}")
    print(f"   Overall Percentage: {evaluation_result.get('overall_percentage', 0.0):.1f}%")
    
    print("\n5. Checking State Updates...")
    status_after = workflow.get_quiz_status(concept_name)
    print(f"   Quiz Taken: {status_after['quiz_taken']}")
    print(f"   Score: {status_after['score']}")
    print(f"   Status: {status_after['status']}")
    print(f"   Retry Count: {status_after.get('retry_count', 0)}")
    
    assert status_after['quiz_taken'] == True, "Quiz not marked as taken"
    assert status_after['score'] is not None, "Score not stored"
    assert status_after['score'] >= 0.0 and status_after['score'] <= 1.0, "Invalid score range"
    print("   ✓ State updated correctly")
    
    print("\n6. Testing Complete Flow...")
    state2 = StudySessionState(session_id="test-2", topic="Functions")
    state2.add_concept("Functions", DifficultyLevel.INTERMEDIATE)
    state2.mark_concept_taught("Functions")
    
    workflow2 = QuizWorkflow(state2)
    
    complete_result = workflow2.complete_quiz_flow(
        concept_name="Functions",
        learner_answers=[
            {"question_number": 1, "answer": "test answer 1"},
            {"question_number": 2, "answer": "test answer 2"}
        ],
        num_questions=2
    )
    
    if "error" in complete_result:
        print(f"   ⚠ Complete flow had error: {complete_result['error']}")
    else:
        print(f"   ✓ Complete flow executed successfully")
        print(f"   Quiz Status: {complete_result.get('concept_status', 'unknown')}")
    
    print("\n7. Testing Retry Logic...")
    can_retry = workflow2.can_retry_quiz("Functions")
    print(f"   Can Retry: {can_retry}")
    
    print("\n✓ Complete quiz workflow test passed!")
    return True


if __name__ == "__main__":
    try:
        test_complete_quiz_workflow()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

