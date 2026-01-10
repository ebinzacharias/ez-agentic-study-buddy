import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.core.agent import StudyBuddyAgent


def test_lcel_step():
    print("Testing LCEL Chain Integration")
    print("=" * 60)
    
    agent = StudyBuddyAgent(topic="Python Variables", max_iterations=3)
    
    print("\n1. Testing LCEL step() method")
    print("-" * 60)
    
    step_result = agent.step()
    
    print(f"  Iteration: {step_result.get('iteration', 'N/A')}")
    print(f"  Observation keys: {list(step_result.get('observation', {}).keys())}")
    print(f"  Decision action: {step_result.get('decision', {}).get('action', 'N/A')}")
    print(f"  Action result success: {step_result.get('action_result', {}).get('success', 'N/A')}")
    
    assert "iteration" in step_result, "Step result should have iteration"
    assert "observation" in step_result, "Step result should have observation"
    assert "decision" in step_result, "Step result should have decision"
    assert "action_result" in step_result, "Step result should have action_result"
    
    print("  ✓ LCEL step structure is correct")
    
    print("\n2. Testing multiple steps")
    print("-" * 60)
    
    for i in range(3):
        step_result = agent.step()
        decision = step_result.get("decision", {})
        action = decision.get("action", "N/A")
        print(f"  Step {i+1}: Action = {action}")
        
        if agent.is_complete():
            print(f"  Session completed at step {i+1}")
            break
    
    print("\n3. Testing backward compatibility")
    print("-" * 60)
    
    observation = agent.observe()
    print(f"  observe() returns: {list(observation.keys())}")
    assert "session_id" in observation, "Observation should have session_id"
    
    decision = agent.decide(observation)
    print(f"  decide() returns action: {decision.get('action', 'N/A')}")
    assert "action" in decision, "Decision should have action"
    
    action_result = agent.act(decision)
    print(f"  act() returns success: {action_result.get('success', 'N/A')}")
    assert "success" in action_result, "Action result should have success"
    
    print("  ✓ Backward compatibility maintained")
    
    print("\n✓ All LCEL chain tests passed!")
    return True


if __name__ == "__main__":
    try:
        test_lcel_step()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

