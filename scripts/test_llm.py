import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.utils.llm_client import get_llm_client


def test_llm_connection():
    print("Testing LLM connection...")
    
    try:
        llm = get_llm_client()
        print(f"✓ LLM client initialized: {type(llm).__name__}")
        
        response = llm.invoke("Say 'Hello, I am working!' in one sentence.")
        print(f"✓ LLM response: {response.content}")
        
        print("\n✅ LLM connection test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ LLM connection test failed: {e}")
        return False


if __name__ == "__main__":
    test_llm_connection()

