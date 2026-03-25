import os
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.utils.llm_client import get_llm_client  # noqa: E402

pytestmark = pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set — skipping LLM-dependent tests",
)


def test_llm_connection():
    print("Testing LLM connection...")
    
    llm = get_llm_client()
    print(f"✓ LLM client initialized: {type(llm).__name__}")
    
    response = llm.invoke("Say 'Hello, I am working!' in one sentence.")
    print(f"✓ LLM response: {response.content}")
    
    print("\n✅ LLM connection test passed!")


if __name__ == "__main__":
    test_llm_connection()

