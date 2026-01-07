import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.tools.teacher_tool import teach_concept


def test_teacher():
    print("Testing Teacher Tool...")
    print("-" * 60)
    
    test_cases = [
        {
            "concept_name": "Variables and Data Types",
            "difficulty_level": "beginner",
            "context": "",
        },
        {
            "concept_name": "Functions",
            "difficulty_level": "intermediate",
            "context": "Learner knows variables and control structures",
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"  Concept: {test_case['concept_name']}")
        print(f"  Difficulty: {test_case['difficulty_level']}")
        if test_case['context']:
            print(f"  Context: {test_case['context']}")
        print("-" * 60)
        
        try:
            result = teach_concept.invoke(test_case)
            print(f"✓ Tool executed successfully")
            print(f"\nTeaching Content ({len(result)} chars):")
            print(result[:300] + "..." if len(result) > 300 else result)
            print()
            
        except Exception as e:
            print(f"✗ Tool execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("✓ Teacher Tool test passed!")
    return True


if __name__ == "__main__":
    test_teacher()

