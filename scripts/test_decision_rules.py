import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.core.decision_rules import DecisionRules
from agent.core.state import ConceptStatus, DifficultyLevel, StudySessionState


def test_decision_rules():
    print("Testing Decision Rules")
    print("=" * 60)
    
    def setup_no_concepts():
        return StudySessionState(session_id="test-1", topic="Python Basics")
    
    def setup_not_taught():
        state = StudySessionState(session_id="test-2", topic="Python Basics")
        state.concepts_planned.extend(["Variables", "Functions"])
        state.add_concept("Variables", DifficultyLevel.BEGINNER)
        state.set_current_concept("Variables")
        return state
    
    def setup_taught_not_quizzed():
        state = StudySessionState(session_id="test-3", topic="Python Basics")
        state.concepts_planned.extend(["Variables", "Functions"])
        state.add_concept("Variables", DifficultyLevel.BEGINNER)
        state.set_current_concept("Variables")
        state.mark_concept_taught("Variables")
        return state
    
    def setup_low_score():
        state = StudySessionState(session_id="test-4", topic="Python Basics")
        state.concepts_planned.extend(["Variables", "Functions"])
        state.add_concept("Variables", DifficultyLevel.BEGINNER)
        state.set_current_concept("Variables")
        state.mark_concept_taught("Variables")
        state.mark_concept_quizzed("Variables", 0.5)
        return state
    
    def setup_mastered():
        state = StudySessionState(session_id="test-5", topic="Python Basics")
        state.concepts_planned.extend(["Variables", "Functions"])
        state.add_concept("Variables", DifficultyLevel.BEGINNER)
        state.add_concept("Functions", DifficultyLevel.BEGINNER)
        state.set_current_concept("Variables")
        state.mark_concept_taught("Variables")
        state.mark_concept_quizzed("Variables", 0.85)
        return state
    
    def setup_needs_retry():
        state = StudySessionState(session_id="test-6", topic="Python Basics")
        state.concepts_planned.extend(["Variables"])
        state.add_concept("Variables", DifficultyLevel.BEGINNER)
        state.set_current_concept("Variables")
        state.mark_concept_taught("Variables")
        state.mark_concept_quizzed("Variables", 0.4)
        return state
    
    test_cases = [
        {
            "name": "No concepts planned",
            "setup": setup_no_concepts,
            "expected_action": "plan_learning_path",
        },
        {
            "name": "Concept not taught",
            "setup": setup_not_taught,
            "expected_action": "teach_concept",
        },
        {
            "name": "Concept taught, not quizzed",
            "setup": setup_taught_not_quizzed,
            "expected_action": "generate_quiz",
        },
        {
            "name": "Concept quizzed with low score",
            "setup": setup_low_score,
            "expected_action": "teach_concept",
        },
        {
            "name": "Concept mastered, move to next",
            "setup": setup_mastered,
            "expected_action": "set_current_concept",
        },
        {
            "name": "Concept needs retry",
            "setup": setup_needs_retry,
            "expected_action": "teach_concept",
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['name']}")
        print("-" * 60)
        
        try:
            state = test_case["setup"]()
            rules = DecisionRules(state)
            decision = rules.decide_next_action()
            
            action = decision.get("action")
            reason = decision.get("reason", "")
            
            print(f"  Decision: {action}")
            print(f"  Reason: {reason}")
            
            if action == test_case["expected_action"]:
                print(f"  ✓ Correct action")
                passed += 1
            else:
                print(f"  ✗ Expected: {test_case['expected_action']}, Got: {action}")
                failed += 1
            
            if "tool_name" in decision:
                print(f"  Tool: {decision.get('tool_name')}")
                print(f"  Args: {decision.get('tool_args', {})}")
        
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All decision rule tests passed!")
        return True
    else:
        print("✗ Some tests failed")
        return False


if __name__ == "__main__":
    test_decision_rules()

