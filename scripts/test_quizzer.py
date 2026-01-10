import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.tools.quizzer_tool import generate_quiz


def test_quizzer():
    print("Testing Quizzer Tool...")
    print("-" * 60)
    
    test_cases = [
        {
            "concept_name": "Variables and Data Types",
            "difficulty_level": "beginner",
            "num_questions": 3,
            "question_types": "multiple_choice,short_answer",
        },
        {
            "concept_name": "Functions",
            "difficulty_level": "intermediate",
            "num_questions": 2,
            "question_types": "multiple_choice",
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"  Concept: {test_case['concept_name']}")
        print(f"  Difficulty: {test_case['difficulty_level']}")
        print(f"  Questions: {test_case['num_questions']}")
        print(f"  Types: {test_case['question_types']}")
        print("-" * 60)
        
        try:
            result = generate_quiz.invoke(test_case)
            print(f"✓ Tool executed successfully")
            
            if "error" in result:
                print(f"⚠ Error: {result['error']}")
                if "raw_response" in result:
                    print(f"Raw response: {result['raw_response'][:200]}...")
                continue
            
            print(f"\nQuiz Generated:")
            print(f"  Concept: {result.get('concept_name', 'N/A')}")
            print(f"  Difficulty: {result.get('difficulty_level', 'N/A')}")
            print(f"  Total Questions: {result.get('total_questions', 0)}")
            
            questions = result.get('questions', [])
            if questions:
                print(f"\n  Questions ({len(questions)}):")
                for q in questions:
                    print(f"    Q{q.get('question_number', '?')}: {q.get('question_type', 'unknown')}")
                    print(f"      {q.get('question', 'N/A')[:80]}...")
                    if q.get('options'):
                        print(f"      Options: {len(q.get('options', []))} choices")
                    print(f"      Correct Answer: {q.get('correct_answer', 'N/A')[:50]}")
            else:
                print("  ⚠ No questions generated")
            
        except Exception as e:
            print(f"✗ Tool execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n✓ Quizzer Tool test passed!")
    return True


if __name__ == "__main__":
    test_quizzer()

