from pathlib import Path
import sys
from agent.tools.planner_tool import plan_learning_path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_planner():
    print("Testing Planner Tool...")
    print("-" * 50)
    
    try:
        result = plan_learning_path.invoke({
            "topic": "Python Basics",
            "difficulty_level": "beginner",
            "max_concepts": 5
        })
        
        print("✓ Tool executed successfully")
        print(f"\nLearning Path ({len(result)} concepts):")
        print("-" * 50)
        
        for concept in result:
            print(f"{concept['order']}. {concept['concept_name']} ({concept['difficulty']})")
        
        print("\n✓ Planner Tool test passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Planner Tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_planner()

