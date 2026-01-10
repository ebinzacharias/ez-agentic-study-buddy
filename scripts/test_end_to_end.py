import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.core.agent import StudyBuddyAgent
from agent.core.state import StudySessionState


def test_full_learning_flow():
    print("=" * 60)
    print("Testing Full Learning Flow (End-to-End)")
    print("=" * 60)
    
    try:
        agent = StudyBuddyAgent(topic="Python Variables", max_iterations=10)
        
        print(f"\n✓ Agent initialized with topic: {agent.state.topic}")
        print(f"  Session ID: {agent.state.session_id}")
        print(f"  Max iterations: {agent.max_iterations}")
        
        print("\n--- Running Learning Session ---")
        iterations = 0
        
        while not agent.is_complete() and iterations < 10:
            step_result = agent.step()
            iterations += 1
            
            decision = step_result.get("decision", {})
            action = decision.get("action", "unknown")
            
            print(f"\n[Iteration {iterations}]")
            print(f"  Action: {action}")
            print(f"  Reason: {decision.get('reason', 'N/A')[:60]}...")
            
            action_result = step_result.get("action_result", {})
            if action_result.get("success"):
                print(f"  ✓ Success")
            else:
                error = action_result.get("error", "Unknown error")
                print(f"  ✗ Error: {error}")
                break
            
            observation = step_result.get("observation", {})
            progress = observation.get("progress_percentage", 0)
            print(f"  Progress: {progress:.1f}%")
        
        print("\n--- Session Summary ---")
        print(f"  Total iterations: {agent.iteration_count}")
        print(f"  Concepts taught: {len(agent.state.get_taught_concepts())}")
        print(f"  Concepts mastered: {len(agent.state.get_mastered_concepts())}")
        print(f"  Final progress: {agent.state.get_progress_percentage():.1f}%")
        print(f"  Average score: {agent.state.get_average_score() or 0.0:.2f}")
        
        print("\n✓ Full learning flow test completed")
        return True
    
    except Exception as e:
        print(f"\n✗ Full learning flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_case_empty_topic():
    print("\n" + "=" * 60)
    print("Testing Edge Case: Empty Topic")
    print("=" * 60)
    
    try:
        agent = StudyBuddyAgent(topic="")
        print("✗ Should have raised ValueError for empty topic")
        return False
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {e}")
        return True
    except Exception as e:
        print(f"✗ Unexpected exception: {e}")
        return False


def test_edge_case_none_topic():
    print("\n" + "=" * 60)
    print("Testing Edge Case: None Topic")
    print("=" * 60)
    
    try:
        agent = StudyBuddyAgent(topic=None)
        print("✗ Should have raised ValueError for None topic")
        return False
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {e}")
        return True
    except Exception as e:
        print(f"✗ Unexpected exception: {e}")
        return False


def test_edge_case_max_iterations():
    print("\n" + "=" * 60)
    print("Testing Edge Case: Max Iterations")
    print("=" * 60)
    
    try:
        agent = StudyBuddyAgent(topic="Test Topic", max_iterations=2)
        
        for i in range(3):
            if agent.is_complete():
                print(f"✓ Session completed at iteration {i} (as expected)")
                break
            agent.step()
        
        if agent.iteration_count >= 2:
            print(f"✓ Max iterations respected: {agent.iteration_count} >= 2")
        else:
            print(f"✗ Max iterations not respected: {agent.iteration_count} < 2")
            return False
        
        if agent.is_complete():
            print("✓ is_complete() returns True after max iterations")
        else:
            print("✗ is_complete() should return True after max iterations")
            return False
        
        return True
    
    except Exception as e:
        print(f"✗ Max iterations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_case_no_concepts():
    print("\n" + "=" * 60)
    print("Testing Edge Case: No Concepts Planned")
    print("=" * 60)
    
    try:
        agent = StudyBuddyAgent(topic="Very Specific Niche Topic XYZ123", max_iterations=5)
        
        step_result = agent.step()
        decision = step_result.get("decision", {})
        action = decision.get("action")
        
        print(f"  First action: {action}")
        
        if action == "plan_learning_path":
            print("✓ Correctly attempts to plan learning path when no concepts")
        else:
            print(f"✗ Expected 'plan_learning_path', got '{action}'")
            return False
        
        return True
    
    except Exception as e:
        print(f"✗ No concepts test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_case_invalid_state():
    print("\n" + "=" * 60)
    print("Testing Edge Case: Invalid State Operations")
    print("=" * 60)
    
    try:
        state = StudySessionState(session_id="test", topic="Test")
        
        progress = state.get_concept_progress("NonExistentConcept")
        if progress is None:
            print("✓ get_concept_progress returns None for non-existent concept")
        else:
            print("✗ get_concept_progress should return None for non-existent concept")
            return False
        
        taught = state.get_taught_concepts()
        if taught == []:
            print("✓ get_taught_concepts returns empty list for new state")
        else:
            print(f"✗ get_taught_concepts should return empty list, got: {taught}")
            return False
        
        progress_pct = state.get_progress_percentage()
        if progress_pct == 0.0:
            print(f"✓ get_progress_percentage returns 0.0 for new state: {progress_pct}")
        else:
            print(f"✗ get_progress_percentage should return 0.0, got: {progress_pct}")
            return False
        
        avg_score = state.get_average_score()
        if avg_score is None:
            print("✓ get_average_score returns None for new state")
        else:
            print(f"✗ get_average_score should return None, got: {avg_score}")
            return False
        
        return True
    
    except Exception as e:
        print(f"✗ Invalid state test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    print("\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)
    
    try:
        agent = StudyBuddyAgent(topic="Test", max_iterations=3)
        
        observation = agent.observe()
        decision = agent.decide(observation)
        
        invalid_decision = {"action": "invalid_action_xyz"}
        action_result = agent.act(invalid_decision)
        
        if not action_result.get("success"):
            error = action_result.get("error", "")
            if "Unknown action" in error:
                print(f"✓ Correctly handles unknown action: {error}")
            else:
                print(f"✗ Expected 'Unknown action' error, got: {error}")
                return False
        else:
            print("✗ Should have failed for unknown action")
            return False
        
        return True
    
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_robustness():
    print("\n" + "=" * 60)
    print("Testing System Robustness")
    print("=" * 60)
    
    test_cases = [
        ("Python Basics", 5),
        ("Machine Learning Fundamentals", 3),
        ("Data Structures", 4),
    ]
    
    passed = 0
    failed = 0
    
    for topic, max_iter in test_cases:
        try:
            agent = StudyBuddyAgent(topic=topic, max_iterations=max_iter)
            
            for _ in range(max_iter):
                if agent.is_complete():
                    break
                step_result = agent.step()
                
                if "observation" not in step_result:
                    print(f"  ✗ Missing 'observation' in step result for topic: {topic}")
                    failed += 1
                    break
                if "decision" not in step_result:
                    print(f"  ✗ Missing 'decision' in step result for topic: {topic}")
                    failed += 1
                    break
                if "action_result" not in step_result:
                    print(f"  ✗ Missing 'action_result' in step result for topic: {topic}")
                    failed += 1
                    break
            else:
                print(f"  ✓ Topic '{topic}' handled robustly")
                passed += 1
        
        except Exception as e:
            print(f"  ✗ Topic '{topic}' failed: {e}")
            failed += 1
    
    print(f"\n  Robustness: {passed} passed, {failed} failed")
    return failed == 0


def run_all_tests():
    print("\n" + "=" * 60)
    print("COMPREHENSIVE SYSTEM TESTING")
    print("=" * 60)
    
    tests = [
        ("Full Learning Flow", test_full_learning_flow),
        ("Edge Case: Empty Topic", test_edge_case_empty_topic),
        ("Edge Case: None Topic", test_edge_case_none_topic),
        ("Edge Case: Max Iterations", test_edge_case_max_iterations),
        ("Edge Case: No Concepts", test_edge_case_no_concepts),
        ("Edge Case: Invalid State", test_edge_case_invalid_state),
        ("Error Handling", test_error_handling),
        ("System Robustness", test_robustness),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} raised exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed out of {len(results)} tests")
    
    if failed == 0:
        print("\n✓ All tests passed!")
        return True
    else:
        print("\n✗ Some tests failed")
        return False


if __name__ == "__main__":
    run_all_tests()

