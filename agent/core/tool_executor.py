from typing import Any, Dict, List, Union

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from agent.tools.planner_tool import plan_learning_path


class ToolExecutor:
    def __init__(self, llm: Union[ChatGroq, ChatOpenAI]):
        self.llm = llm
        self.tools = [plan_learning_path]
        self.tool_map: Dict[str, BaseTool] = {
            tool.name: tool for tool in self.tools
        }
        self.llm_with_tools = self.llm.bind_tools(self.tools)
    
    def extract_tool_calls(self, response: Any) -> List[Dict[str, Any]]:
        tool_calls = []
        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_calls = response.tool_calls
        return tool_calls
    
    def execute_tool(self, tool_name: str, tool_args: Dict[str, Any], tool_call_id: str) -> ToolMessage:
        if tool_name not in self.tool_map:
            raise ValueError(f"Tool '{tool_name}' not found in tool_map")
        
        tool = self.tool_map[tool_name]
        tool_result = tool.invoke(tool_args)
        
        tool_message = ToolMessage(
            content=str(tool_result),
            tool_call_id=tool_call_id,
        )
        
        return tool_message
    
    def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[ToolMessage]:
        tool_messages = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_call_id = tool_call.get("id")
            tool_args = tool_call.get("args", {})
            
            tool_message = self.execute_tool(tool_name, tool_args, tool_call_id)
            tool_messages.append(tool_message)
        
        return tool_messages

