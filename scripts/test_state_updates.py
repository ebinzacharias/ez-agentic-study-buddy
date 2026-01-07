import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.core.state import StudySessionState
from agent.core.tool_executor import ToolExecutor
from agent.utils.llm_client import get_llm_client


def test_state_updates():
    print("Testing State Updates After Tool Execution")
    print("=" * 60)
    
    llm = get_llm_client()
    state = StudySessionState(session_id="test-123", topic="Python Basics")
    executor = ToolExecutor(llm, state)
    
    print("\n1. Initial State:")
    print(f"   Concepts: {list(state.concepts.keys())}")
    print(f"   Taught: {state.get_taught_concepts()}")
    print(f"   Progress: {state.get_progress_percentage():.0%}")
    
    print("\n2. Testing plan_learning_path - State Update:")
    tool_call_plan = {
        "name": "plan_learning_path",
        "id": "call-1",
        "args": {
            "topic": "Python Basics",
            "difficulty_level": "beginner",
            "max_concepts": 3
        }
    }
    
    tool_messages = executor.execute_tool_calls([tool_call_plan])
    print(f"   ✓ Tool executed")
    print(f"   Concepts in state: {list(state.concepts.keys())}")
    print(f"   Concepts planned: {state.concepts_planned}")
    print(f"   Total concepts: {len(state.concepts)}")
    
    print("\n3. Testing teach_concept - State Update:")
    concept_to_teach = state.concepts_planned[0] if state.concepts_planned else "Variables and Data Types"
    print(f"   Teaching: {concept_to_teach}")
    
    if concept_to_teach not in state.concepts:
        state.add_concept(concept_to_teach)
    
    tool_call_teach = {
        "name": "teach_concept",
        "id": "call-2",
        "args": {
            "concept_name": concept_to_teach,
            "difficulty_level": "beginner"
        }
    }
    
    tool_messages = executor.execute_tool_calls([tool_call_teach])
    print(f"   ✓ Tool executed")
    
    concept_progress = state.get_concept_progress(concept_to_teach)
    if concept_progress:
        print(f"   Concept status: {concept_progress.status.value}")
        print(f"   Taught at: {concept_progress.taught_at}")
    
    print("\n4. Final State:")
    print(f"   Concepts: {list(state.concepts.keys())}")
    print(f"   Taught: {state.get_taught_concepts()}")
    print(f"   Progress: {state.get_progress_percentage():.0%}")
    
    print("\n5. Verifying State Persistence:")
    taught_concepts = state.get_taught_concepts()
    assert concept_to_teach in taught_concepts, f"Concept {concept_to_teach} not marked as taught"
    print(f"   ✓ Concept '{concept_to_teach}' is marked as taught")
    
    concept_progress = state.get_concept_progress(concept_to_teach)
    assert concept_progress is not None, "Concept progress not found"
    assert concept_progress.taught_at is not None, "Concept taught_at timestamp not set"
    print(f"   ✓ State persists correctly")
    
    print("\n✓ State update test passed!")
    return True


if __name__ == "__main__":
    try:
        test_state_updates()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

