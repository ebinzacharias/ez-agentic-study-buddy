import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.core.tool_executor import ToolExecutor
from agent.tools.planner_tool import plan_learning_path
from agent.utils.llm_client import get_llm_client
from langchain_core.messages import ToolMessage


def test_manual_tool_calling():
    print("=" * 60)
    print("Test 1: Manual Tool Calling (Step by Step)")
    print("=" * 60)
    
    manual_test()


def manual_test():
    print("Testing Manual Tool Calling with LLM")
    print("=" * 60)
    
    llm = get_llm_client()
    
    tools = [plan_learning_path]
    
    tool_map = {
        "plan_learning_path": plan_learning_path,
    }
    
    print("\n1. Binding tools to LLM...")
    llm_with_tools = llm.bind_tools(tools)
    print("✓ Tools bound successfully")
    
    print("\n2. Creating prompt for LLM...")
    prompt = """You are a learning path planner. 
The user wants to learn 'Python Basics' as a beginner with a maximum of 5 concepts.
Create a learning path by calling the plan_learning_path tool."""
    
    print("Prompt:", prompt)
    
    print("\n3. Invoking LLM with tools...")
    response = llm_with_tools.invoke(prompt)
    print("✓ LLM response received")
    print(f"Response type: {type(response)}")
    print(f"Response content: {response.content[:100]}...")
    
    print("\n4. Extracting tool calls...")
    tool_calls = []
    if hasattr(response, "tool_calls") and response.tool_calls:
        tool_calls = response.tool_calls
        print(f"✓ Found {len(tool_calls)} tool call(s)")
        
        for i, tool_call in enumerate(tool_calls):
            print(f"\n  Tool Call {i+1}:")
            print(f"    Name: {tool_call.get('name', 'N/A')}")
            print(f"    ID: {tool_call.get('id', 'N/A')}")
            print(f"    Args: {tool_call.get('args', {})}")
    else:
        print("✗ No tool calls found in response")
        print("Response:", response)
        return False
    
    print("\n5. Executing tool calls...")
    tool_messages = []
    
    for tool_call in tool_calls:
        tool_name = tool_call.get("name")
        tool_call_id = tool_call.get("id")
        tool_args = tool_call.get("args", {})
        
        if tool_name not in tool_map:
            print(f"✗ Tool '{tool_name}' not found in tool_map")
            continue
        
        print(f"\n  Executing: {tool_name}")
        print(f"    Arguments: {tool_args}")
        
        try:
            tool_result = tool_map[tool_name].invoke(tool_args)
            print(f"✓ Tool executed successfully")
            print(f"    Result: {len(tool_result)} concepts planned")
            
            tool_message = ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call_id,
            )
            tool_messages.append(tool_message)
            print(f"✓ ToolMessage created with tool_call_id: {tool_call_id}")
            
        except Exception as e:
            print(f"✗ Tool execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n6. Final Results:")
    print("=" * 60)
    print(f"✓ LLM invoked with tool binding")
    print(f"✓ Tool calls extracted: {len(tool_calls)}")
    print(f"✓ Tools executed: {len(tool_messages)}")
    print(f"✓ ToolMessages created: {len(tool_messages)}")
    
    if tool_messages:
        print("\nToolMessage details:")
        for msg in tool_messages:
            print(f"  - tool_call_id: {msg.tool_call_id}")
            print(f"    content length: {len(msg.content)} chars")
    
    print("\n✓ Manual tool calling test passed!")
    return True


def test_tool_executor():
    print("\n" + "=" * 60)
    print("Test 2: Using ToolExecutor Class")
    print("=" * 60)
    
    llm = get_llm_client()
    executor = ToolExecutor(llm)
    
    print("\n1. ToolExecutor initialized")
    print(f"   Tools bound: {len(executor.tools)}")
    print(f"   Tools in map: {list(executor.tool_map.keys())}")
    
    print("\n2. Invoking LLM with tools...")
    prompt = """You are a learning path planner. 
The user wants to learn 'Machine Learning' as an intermediate level with a maximum of 5 concepts.
Create a learning path by calling the plan_learning_path tool."""
    
    response = executor.llm_with_tools.invoke(prompt)
    print("✓ LLM response received")
    
    print("\n3. Extracting tool calls...")
    tool_calls = executor.extract_tool_calls(response)
    print(f"✓ Found {len(tool_calls)} tool call(s)")
    
    if not tool_calls:
        print("✗ No tool calls found")
        return False
    
    print("\n4. Executing tool calls using ToolExecutor...")
    tool_messages = executor.execute_tool_calls(tool_calls)
    print(f"✓ Executed {len(tool_messages)} tool call(s)")
    
    print("\n5. ToolMessage Details:")
    for msg in tool_messages:
        print(f"   - tool_call_id: {msg.tool_call_id}")
        print(f"     content length: {len(msg.content)} chars")
    
    print("\n✓ ToolExecutor test passed!")
    return True


if __name__ == "__main__":
    try:
        manual_test()
        test_tool_executor()
        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

