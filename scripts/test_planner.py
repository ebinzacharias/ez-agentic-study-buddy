import os
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.tools.planner_tool import plan_learning_path  # noqa: E402

pytestmark = pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set — skipping LLM-dependent tests",
)


def test_planner():
    print("Testing Planner Tool...")
    print("-" * 50)
    
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


if __name__ == "__main__":
    test_planner()

