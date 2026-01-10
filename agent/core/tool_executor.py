from typing import Any, Dict, List, Optional, Union

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from agent.core.state import DifficultyLevel, StudySessionState
from agent.tools.adapter_tool import adapt_difficulty
from agent.tools.evaluator_tool import evaluate_response
from agent.tools.planner_tool import plan_learning_path
from agent.tools.quizzer_tool import generate_quiz
from agent.tools.teacher_tool import teach_concept


class ToolExecutor:
    def __init__(
        self,
        llm: Union[ChatGroq, ChatOpenAI],
        state: Optional[StudySessionState] = None,
    ):
        self.llm = llm
        self.state = state
        self.tools = [plan_learning_path, teach_concept, generate_quiz, evaluate_response, adapt_difficulty]
        self.tool_map: Dict[str, BaseTool] = {
            tool.name: tool for tool in self.tools
        }
        self.llm_with_tools = self.llm.bind_tools(self.tools)
    
    def extract_tool_calls(self, response: Any) -> List[Dict[str, Any]]:
        tool_calls = []
        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_calls = response.tool_calls
        return tool_calls
    
    def _update_state_after_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        tool_result: Any,
    ) -> None:
        if not self.state:
            return
        
        if tool_name == "plan_learning_path":
            if isinstance(tool_result, list):
                for concept_data in tool_result:
                    if isinstance(concept_data, dict):
                        concept_name = concept_data.get("concept_name")
                        difficulty_str = concept_data.get("difficulty", "beginner")
                        if concept_name:
                            from agent.core.state import DifficultyLevel
                            difficulty = DifficultyLevel.BEGINNER
                            if difficulty_str == "intermediate":
                                difficulty = DifficultyLevel.INTERMEDIATE
                            elif difficulty_str == "advanced":
                                difficulty = DifficultyLevel.ADVANCED
                            self.state.add_concept(concept_name, difficulty)
                self.state.concepts_planned = [
                    c.get("concept_name") for c in tool_result
                    if isinstance(c, dict) and c.get("concept_name")
                ]
        
        elif tool_name == "teach_concept":
            concept_name = tool_args.get("concept_name")
            if concept_name and concept_name in self.state.concepts:
                self.state.mark_concept_taught(concept_name)
        
        elif tool_name == "evaluate_response":
            import json
            from agent.core.retry_manager import RetryManager
            
            evaluation_result = tool_result
            if isinstance(evaluation_result, str):
                try:
                    evaluation_result = json.loads(evaluation_result)
                except json.JSONDecodeError:
                    return
            
            if isinstance(evaluation_result, dict):
                average_score = evaluation_result.get("average_score")
                if average_score is not None:
                    concept_name_from_quiz = tool_args.get("concept_name")
                    if not concept_name_from_quiz:
                        quiz_data_str = tool_args.get("quiz_data", "{}")
                        try:
                            quiz_data = json.loads(quiz_data_str) if isinstance(quiz_data_str, str) else quiz_data_str
                            concept_name_from_quiz = quiz_data.get("concept_name")
                        except (json.JSONDecodeError, TypeError):
                            pass
                    
                    if concept_name_from_quiz and concept_name_from_quiz in self.state.concepts:
                        retry_manager = RetryManager(self.state)
                        if retry_manager.should_retry(concept_name_from_quiz, float(average_score)):
                            retry_manager.mark_for_retry(concept_name_from_quiz, float(average_score))
                        else:
                            self.state.mark_concept_quizzed(concept_name_from_quiz, float(average_score))
        
        elif tool_name == "adapt_difficulty":
            if isinstance(tool_result, dict) and "error" not in tool_result:
                concept_name = tool_result.get("concept_name")
                new_difficulty_str = tool_result.get("new_difficulty")
                adaptation_applied = tool_result.get("adaptation_applied", False)
                
                if concept_name and new_difficulty_str and adaptation_applied:
                    new_difficulty = DifficultyLevel.BEGINNER
                    if new_difficulty_str == "intermediate":
                        new_difficulty = DifficultyLevel.INTERMEDIATE
                    elif new_difficulty_str == "advanced":
                        new_difficulty = DifficultyLevel.ADVANCED
                    
                    if concept_name in self.state.concepts:
                        self.state.update_difficulty(concept_name, new_difficulty)
    
    def execute_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        tool_call_id: str,
    ) -> ToolMessage:
        if tool_name not in self.tool_map:
            raise ValueError(f"Tool '{tool_name}' not found in tool_map")
        
        tool = self.tool_map[tool_name]
        tool_result = tool.invoke(tool_args)
        
        self._update_state_after_tool(tool_name, tool_args, tool_result)
        
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

