import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.tools.adapter_tool import adapt_difficulty


def test_adapter_tool():
    print("Testing Adapt Difficulty Tool")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Decrease difficulty - low quiz score",
            "args": {
                "concept_name": "Variables",
                "current_difficulty": "intermediate",
                "quiz_score": 0.4,
            },
            "expected_change": True,
            "expected_direction": "decrease",
        },
        {
            "name": "Increase difficulty - high quiz score",
            "args": {
                "concept_name": "Variables",
                "current_difficulty": "beginner",
                "quiz_score": 0.85,
            },
            "expected_change": True,
            "expected_direction": "increase",
        },
        {
            "name": "Decrease difficulty - high retry count",
            "args": {
                "concept_name": "Functions",
                "current_difficulty": "advanced",
                "retry_count": 3,
            },
            "expected_change": True,
            "expected_direction": "decrease",
        },
        {
            "name": "Maintain difficulty - medium performance",
            "args": {
                "concept_name": "Loops",
                "current_difficulty": "intermediate",
                "quiz_score": 0.65,
                "retry_count": 1,
            },
            "expected_change": False,
        },
        {
            "name": "Cannot decrease - already beginner",
            "args": {
                "concept_name": "Basics",
                "current_difficulty": "beginner",
                "quiz_score": 0.3,
                "retry_count": 4,
            },
            "expected_change": False,
            "expected_difficulty": "beginner",
        },
        {
            "name": "Cannot increase - already advanced",
            "args": {
                "concept_name": "Advanced",
                "current_difficulty": "advanced",
                "quiz_score": 0.95,
                "average_score": 0.9,
            },
            "expected_change": False,
            "expected_difficulty": "advanced",
        },
        {
            "name": "Increase based on average score",
            "args": {
                "concept_name": "Classes",
                "current_difficulty": "intermediate",
                "average_score": 0.85,
            },
            "expected_change": True,
            "expected_direction": "increase",
        },
        {
            "name": "Decrease based on average score",
            "args": {
                "concept_name": "Generators",
                "current_difficulty": "advanced",
                "average_score": 0.45,
            },
            "expected_change": True,
            "expected_direction": "decrease",
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['name']}")
        print("-" * 60)
        
        try:
            result = adapt_difficulty.invoke(test_case["args"])
            
            if "error" in result:
                print(f"  ✗ Error: {result['error']}")
                failed += 1
                continue
            
            old_difficulty = result.get("old_difficulty")
            new_difficulty = result.get("new_difficulty")
            reason = result.get("reason", "")
            adaptation_applied = result.get("adaptation_applied", False)
            
            print(f"  Old Difficulty: {old_difficulty}")
            print(f"  New Difficulty: {new_difficulty}")
            print(f"  Adaptation Applied: {adaptation_applied}")
            print(f"  Reason: {reason}")
            
            if test_case.get("expected_change") is False:
                if not adaptation_applied and old_difficulty == new_difficulty:
                    if "expected_difficulty" not in test_case or new_difficulty == test_case["expected_difficulty"]:
                        print(f"  ✓ Correctly maintained difficulty")
                        passed += 1
                    else:
                        print(f"  ✗ Expected difficulty {test_case['expected_difficulty']}, got {new_difficulty}")
                        failed += 1
                else:
                    print(f"  ✗ Expected no change, but difficulty was changed")
                    failed += 1
            else:
                if adaptation_applied:
                    difficulty_levels = ["beginner", "intermediate", "advanced"]
                    old_index = difficulty_levels.index(old_difficulty)
                    new_index = difficulty_levels.index(new_difficulty)
                    direction = "increase" if new_index > old_index else "decrease"
                    
                    expected_direction = test_case.get("expected_direction")
                    if expected_direction and direction == expected_direction:
                        print(f"  ✓ Correctly {direction}d difficulty")
                        passed += 1
                    elif expected_direction:
                        print(f"  ✗ Expected {expected_direction}, got {direction}")
                        failed += 1
                    else:
                        print(f"  ✓ Correctly adapted difficulty")
                        passed += 1
                else:
                    print(f"  ✗ Expected change, but difficulty was maintained")
                    failed += 1
        
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All adapter tool tests passed!")
        return True
    else:
        print("✗ Some tests failed")
        return False


def test_edge_cases():
    print("\n" + "=" * 60)
    print("Testing Edge Cases")
    print("=" * 60)
    
    edge_cases = [
        {
            "name": "Invalid difficulty level",
            "args": {
                "concept_name": "Test",
                "current_difficulty": "invalid",
                "quiz_score": 0.5,
            },
            "should_error": True,
        },
        {
            "name": "Invalid quiz score (too high)",
            "args": {
                "concept_name": "Test",
                "current_difficulty": "beginner",
                "quiz_score": 1.5,
            },
            "should_error": True,
        },
        {
            "name": "Invalid quiz score (too low)",
            "args": {
                "concept_name": "Test",
                "current_difficulty": "beginner",
                "quiz_score": -0.5,
            },
            "should_error": True,
        },
        {
            "name": "Invalid retry count (negative)",
            "args": {
                "concept_name": "Test",
                "current_difficulty": "beginner",
                "retry_count": -1,
            },
            "should_error": True,
        },
        {
            "name": "No metrics provided",
            "args": {
                "concept_name": "Test",
                "current_difficulty": "beginner",
            },
            "should_error": True,
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\nEdge Case {i}: {test_case['name']}")
        print("-" * 60)
        
        try:
            result = adapt_difficulty.invoke(test_case["args"])
            
            if test_case.get("should_error"):
                if "error" in result:
                    print(f"  ✓ Correctly returned error: {result['error']}")
                    passed += 1
                else:
                    print(f"  ✗ Expected error, but got result: {result}")
                    failed += 1
            else:
                if "error" not in result:
                    print(f"  ✓ No error (as expected)")
                    passed += 1
                else:
                    print(f"  ✗ Unexpected error: {result['error']}")
                    failed += 1
        
        except Exception as e:
            if test_case.get("should_error"):
                print(f"  ✓ Correctly raised exception: {e}")
                passed += 1
            else:
                print(f"  ✗ Unexpected exception: {e}")
                failed += 1
    
    print("\n" + "=" * 60)
    print(f"Edge Case Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    test_adapter_tool()
    test_edge_cases()

