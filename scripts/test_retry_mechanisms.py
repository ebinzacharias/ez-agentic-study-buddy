import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.core.retry_manager import RetryManager
from agent.core.state import ConceptStatus, DifficultyLevel, StudySessionState


def test_retry_manager():
    print("Testing Retry Mechanisms")
    print("=" * 60)
    
    state = StudySessionState(session_id="test-retry", topic="Python Basics")
    state.add_concept("Variables", DifficultyLevel.BEGINNER)
    state.mark_concept_taught("Variables")
    
    retry_manager = RetryManager(state)
    
    print("\n1. Testing should_retry()")
    print("-" * 60)
    
    should_retry_low = retry_manager.should_retry("Variables", quiz_score=0.4)
    should_retry_high = retry_manager.should_retry("Variables", quiz_score=0.7)
    should_retry_no_score = retry_manager.should_retry("Variables")
    
    print(f"  Low score (0.4): {should_retry_low} (expected: True)")
    print(f"  High score (0.7): {should_retry_high} (expected: False)")
    print(f"  No score: {should_retry_no_score} (expected: False)")
    
    assert should_retry_low == True, "Should retry for low score"
    assert should_retry_high == False, "Should not retry for high score"
    
    print("\n2. Testing mark_for_retry()")
    print("-" * 60)
    
    retry_result = retry_manager.mark_for_retry("Variables", quiz_score=0.45)
    print(f"  Retry Result: {retry_result}")
    concept_progress = state.get_concept_progress("Variables")
    print(f"  Retry Count: {concept_progress.retry_count}")
    print(f"  Status: {concept_progress.status.value}")
    print(f"  Score: {concept_progress.score}")
    
    assert concept_progress.retry_count == 1, "Retry count should be 1"
    assert concept_progress.status == ConceptStatus.NEEDS_RETRY, "Status should be NEEDS_RETRY"
    assert concept_progress.score == 0.45, "Score should be 0.45"
    
    print("\n3. Testing can_retry()")
    print("-" * 60)
    
    can_retry_1 = retry_manager.can_retry("Variables")
    print(f"  After 1 retry: {can_retry_1} (expected: True)")
    assert can_retry_1 == True, "Should be able to retry after 1 attempt"
    
    retry_manager.mark_for_retry("Variables", quiz_score=0.4)
    can_retry_2 = retry_manager.can_retry("Variables")
    print(f"  After 2 retries: {can_retry_2} (expected: True)")
    assert can_retry_2 == True, "Should be able to retry after 2 attempts"
    
    retry_manager.mark_for_retry("Variables", quiz_score=0.3)
    can_retry_3 = retry_manager.can_retry("Variables")
    print(f"  After 3 retries: {can_retry_3} (expected: False)")
    assert can_retry_3 == False, "Should not be able to retry after 3 attempts"
    
    print("\n4. Testing get_retry_strategy()")
    print("-" * 60)
    
    state2 = StudySessionState(session_id="test-2", topic="Functions")
    state2.add_concept("Functions", DifficultyLevel.INTERMEDIATE)
    state2.mark_concept_taught("Functions")
    
    retry_manager2 = RetryManager(state2)
    
    retry_manager2.mark_for_retry("Functions", quiz_score=0.4)
    strategy_1 = retry_manager2.get_retry_strategy("Functions")
    print(f"  Strategy after 1 retry: {strategy_1['strategy']}")
    print(f"  Approach: {strategy_1['approach']}")
    assert strategy_1['strategy'] == "simplify_explanation", "Should use simplify_explanation for retry 1"
    
    retry_manager2.mark_for_retry("Functions", quiz_score=0.35)
    strategy_2 = retry_manager2.get_retry_strategy("Functions")
    print(f"  Strategy after 2 retries: {strategy_2['strategy']}")
    print(f"  Approach: {strategy_2['approach']}")
    assert strategy_2['strategy'] == "alternative_approach", "Should use alternative_approach for retry 2"
    
    retry_manager2.mark_for_retry("Functions", quiz_score=0.3)
    strategy_3 = retry_manager2.get_retry_strategy("Functions")
    print(f"  Strategy after 3 retries: {strategy_3['strategy']}")
    print(f"  Approach: {strategy_3['approach']}")
    assert strategy_3['strategy'] == "adapt_difficulty", "Should use adapt_difficulty for retry 3"
    
    print("\n5. Testing get_reteaching_context()")
    print("-" * 60)
    
    context = retry_manager2.get_reteaching_context("Functions")
    print(f"  Context: {context[:100]}...")
    assert "retry" in context.lower() or "re-teaching" in context.lower(), "Context should mention retry"
    
    print("\n6. Testing should_adapt_difficulty()")
    print("-" * 60)
    
    should_adapt = retry_manager2.should_adapt_difficulty("Functions")
    print(f"  Should adapt after 3 retries: {should_adapt} (expected: True)")
    assert should_adapt == True, "Should adapt difficulty after 3 retries"
    
    print("\n7. Testing max retries limit")
    print("-" * 60)
    
    state3 = StudySessionState(session_id="test-3", topic="Loops")
    state3.add_concept("Loops", DifficultyLevel.BEGINNER)
    state3.mark_concept_taught("Loops")
    
    retry_manager3 = RetryManager(state3)
    
    for i in range(3):
        result = retry_manager3.mark_for_retry("Loops", quiz_score=0.3 + i * 0.01)
        print(f"  Retry {i+1}: {result.get('can_retry', False)}")
    
    result_4 = retry_manager3.mark_for_retry("Loops", quiz_score=0.33)
    print(f"  Retry 4 (exceeds max): {result_4.get('error', 'No error')}")
    assert "error" in result_4, "Should return error after max retries"
    assert "Max retries" in result_4.get("error", ""), "Error should mention max retries"
    
    print("\n8. Testing get_concepts_exceeding_retries()")
    print("-" * 60)
    
    exceeding = retry_manager2.get_concepts_exceeding_retries()
    print(f"  Concepts exceeding retries: {exceeding}")
    assert "Functions" in exceeding, "Functions should be in exceeding list"
    
    print("\n✓ All retry mechanism tests passed!")
    return True


if __name__ == "__main__":
    try:
        test_retry_manager()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

