from typing import Any, Dict

from langchain_core.runnables import RunnablePassthrough

from agent.core.decision_rules import DecisionRules


def create_observe_chain(state_manager: Any) -> RunnablePassthrough:
    """
    Creates an LCEL chain for the observe step.
    
    Args:
        state_manager: Object with state attribute and observe() method
    
    Returns:
        RunnablePassthrough chain that observes state
    """
    def observe_state(input_dict: Dict[str, Any]) -> Dict[str, Any]:
        observation = state_manager.observe()
        return observation
    
    return RunnablePassthrough.assign(observation=observe_state)


def create_decide_chain(decision_rules: DecisionRules) -> RunnablePassthrough:
    """
    Creates an LCEL chain for the decide step.
    
    Args:
        decision_rules: DecisionRules instance
    
    Returns:
        RunnablePassthrough chain that decides next action
    """
    def decide_action(input_dict: Dict[str, Any]) -> Dict[str, Any]:
        observation = input_dict.get("observation", {})
        decision = decision_rules.decide_next_action(observation)
        return decision
    
    return RunnablePassthrough.assign(decision=decide_action)


def create_act_chain(tool_executor: Any, iteration_count: int) -> RunnablePassthrough:
    """
    Creates an LCEL chain for the act step.
    
    Args:
        tool_executor: ToolExecutor instance
        iteration_count: Current iteration count
    
    Returns:
        RunnablePassthrough chain that executes actions
    """
    def execute_action(input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action based on decision."""
        decision = input_dict.get("decision", {})
        action = decision.get("action")
        
        result: Dict[str, Any] = {
            "action": action,
            "success": False,
            "result": None,
            "error": None,
        }
        
        try:
            from agent.core.state import DifficultyLevel
            
            if action == "plan_learning_path":
                tool_name = decision.get("tool_name")
                tool_args = decision.get("tool_args", {})
                tool_call_id = f"plan_{iteration_count}"
                
                tool_message = tool_executor.execute_tool(
                    tool_name=tool_name,
                    tool_args=tool_args,
                    tool_call_id=tool_call_id,
                )
                result["success"] = True
                result["result"] = tool_message.content
            
            elif action == "add_concept":
                concept_name = decision.get("concept_name")
                if concept_name:
                    state = tool_executor.state
                    if concept_name not in state.concepts:
                        difficulty = DifficultyLevel.BEGINNER
                        if state.concepts_planned:
                            concept_progress = state.get_concept_progress(concept_name)
                            if concept_progress:
                                difficulty = concept_progress.difficulty_level
                        state.add_concept(concept_name, difficulty)
                    result["success"] = True
                    result["result"] = f"Concept '{concept_name}' added"
            
            elif action == "set_current_concept":
                concept_name = decision.get("concept_name")
                if concept_name:
                    tool_executor.state.set_current_concept(concept_name)
                    result["success"] = True
                    result["result"] = f"Current concept set to: {concept_name}"
            
            elif action == "teach_concept":
                tool_name = decision.get("tool_name")
                tool_args = decision.get("tool_args", {})
                tool_call_id = f"teach_{iteration_count}"
                
                tool_message = tool_executor.execute_tool(
                    tool_name=tool_name,
                    tool_args=tool_args,
                    tool_call_id=tool_call_id,
                )
                result["success"] = True
                result["result"] = tool_message.content
            
            elif action == "generate_quiz":
                tool_name = decision.get("tool_name")
                tool_args = decision.get("tool_args", {})
                tool_call_id = f"quiz_{iteration_count}"
                
                tool_message = tool_executor.execute_tool(
                    tool_name=tool_name,
                    tool_args=tool_args,
                    tool_call_id=tool_call_id,
                )
                result["success"] = True
                result["result"] = tool_message.content
            
            elif action == "adapt_difficulty":
                concept_name = decision.get("concept_name")
                if concept_name:
                    state = tool_executor.state
                    concept_progress = state.get_concept_progress(concept_name)
                    if concept_progress:
                        tool_args = {
                            "concept_name": concept_name,
                            "current_difficulty": concept_progress.difficulty_level.value,
                            "quiz_score": concept_progress.score if concept_progress.score is not None else None,
                            "retry_count": concept_progress.retry_count,
                            "average_score": concept_progress.score if concept_progress.score is not None else None,
                        }
                        tool_call_id = f"adapt_{iteration_count}"
                        
                        tool_message = tool_executor.execute_tool(
                            tool_name="adapt_difficulty",
                            tool_args=tool_args,
                            tool_call_id=tool_call_id,
                        )
                        
                        import json
                        try:
                            tool_result = json.loads(tool_message.content) if isinstance(tool_message.content, str) else tool_message.content
                            if isinstance(tool_result, dict) and "error" not in tool_result:
                                result["success"] = True
                                result["result"] = tool_message.content
                            else:
                                result["error"] = tool_result.get("error", "Unknown error in adaptation")
                        except (json.JSONDecodeError, TypeError):
                            result["success"] = True
                            result["result"] = tool_message.content
                    else:
                        result["error"] = f"Concept '{concept_name}' not found in state"
                else:
                    result["error"] = "No concept_name provided for adaptation"
            
            elif action == "session_complete":
                result["success"] = True
                result["result"] = "Learning session completed"
            
            else:
                result["error"] = f"Unknown action: {action}"
        
        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
        
        return result
    
    return RunnablePassthrough.assign(action_result=execute_action)


def create_step_chain(
    state_manager: Any,
    decision_rules: DecisionRules,
    tool_executor: Any,
    iteration_count: int,
) -> Any:
    """
    Creates a complete LCEL chain for one ReAct step (Observe → Decide → Act).
    
    Args:
        state_manager: Object with state attribute and observe() method
        decision_rules: DecisionRules instance
        tool_executor: ToolExecutor instance
        iteration_count: Current iteration count
    
    Returns:
        Composed LCEL chain
    """
    observe_chain = create_observe_chain(state_manager)
    decide_chain = create_decide_chain(decision_rules)
    act_chain = create_act_chain(tool_executor, iteration_count)
    
    step_chain = (
        observe_chain
        | decide_chain
        | act_chain
    )
    
    return step_chain

