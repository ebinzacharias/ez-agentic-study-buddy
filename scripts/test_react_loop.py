import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.core.agent import StudyBuddyAgent


def test_react_loop():
    print("Testing ReAct Loop")
    print("=" * 60)
    
    agent = StudyBuddyAgent(topic="Python Variables", max_iterations=10)
    
    print("\nRunning agent for a few iterations...")
    print("-" * 60)
    
    for i in range(5):
        if agent.is_complete():
            print("\nSession completed early!")
            break
        
        step_result = agent.step()
        
        decision = step_result["decision"]
        action = decision.get("action")
        reason = decision.get("reason", "")
        action_result = step_result["action_result"]
        
        print(f"\n[Step {i + 1}]")
        print(f"  Action: {action}")
        print(f"  Reason: {reason}")
        print(f"  Success: {action_result.get('success')}")
        
        if action_result.get("error"):
            print(f"  Error: {action_result.get('error')}")
        
        observation = step_result["observation"]
        print(f"  Progress: {observation.get('progress_percentage', 0):.1f}%")
        print(f"  Current Concept: {observation.get('current_concept', 'None')}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print(f"Total iterations: {agent.iteration_count}")
    print(f"History length: {len(agent.history)}")
    
    return True


def test_full_run():
    print("\n" + "=" * 60)
    print("Testing Full Run (Limited Iterations)")
    print("=" * 60)
    
    agent = StudyBuddyAgent(topic="Python Basics", max_iterations=5)
    
    try:
        result = agent.run()
        print("\nRun completed successfully!")
        print(f"Session ID: {result['session_id']}")
        print(f"Iterations: {result['iterations']}")
        return True
    except Exception as e:
        print(f"\nRun failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_react_loop()
    test_full_run()

