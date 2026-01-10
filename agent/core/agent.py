import uuid
from typing import Any, Dict, List, Optional, Union

from langchain_core.messages import ToolMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from agent.core.decision_rules import DecisionRules
from agent.core.state import DifficultyLevel, StudySessionState
from agent.core.tool_executor import ToolExecutor


class StudyBuddyAgent:
    def __init__(
        self,
        llm: Optional[Union[ChatGroq, ChatOpenAI]] = None,
        session_state: Optional[StudySessionState] = None,
        topic: Optional[str] = None,
        max_iterations: int = 50,
    ):
        if llm is None:
            from agent.utils.llm_client import get_llm_client
            llm = get_llm_client()
        
        self.llm = llm
        
        if session_state is None:
            if topic is None:
                raise ValueError("Either session_state or topic must be provided")
            session_id = str(uuid.uuid4())
            session_state = StudySessionState(
                session_id=session_id,
                topic=topic,
            )
        
        self.state = session_state
        self.decision_rules = DecisionRules(self.state)
        self.tool_executor = ToolExecutor(self.llm, self.state)
        self.max_iterations = max_iterations
        self.iteration_count = 0
        self.history: List[Dict[str, Any]] = []
    
    def observe(self) -> Dict[str, Any]:
        return {
            "session_id": self.state.session_id,
            "topic": self.state.topic,
            "current_concept": self.state.current_concept,
            "concepts_planned": self.state.concepts_planned,
            "concepts_taught": self.state.get_taught_concepts(),
            "concepts_mastered": self.state.get_mastered_concepts(),
            "concepts_needing_retry": self.state.get_concepts_needing_retry(),
            "progress_percentage": self.state.get_progress_percentage(),
            "average_score": self.state.get_average_score(),
            "overall_difficulty": self.state.overall_difficulty.value,
        }
    
    def decide(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        decision = self.decision_rules.decide_next_action(observation)
        return decision
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        action = decision.get("action")
        result: Dict[str, Any] = {
            "action": action,
            "success": False,
            "result": None,
            "error": None,
        }
        
        try:
            if action == "plan_learning_path":
                tool_name = decision.get("tool_name")
                tool_args = decision.get("tool_args", {})
                tool_call_id = f"plan_{self.iteration_count}"
                
                tool_message = self.tool_executor.execute_tool(
                    tool_name=tool_name,
                    tool_args=tool_args,
                    tool_call_id=tool_call_id,
                )
                result["success"] = True
                result["result"] = tool_message.content
            
            elif action == "add_concept":
                concept_name = decision.get("concept_name")
                if concept_name:
                    if concept_name not in self.state.concepts:
                        difficulty = DifficultyLevel.BEGINNER
                        if self.state.concepts_planned:
                            concept_progress = self.state.get_concept_progress(concept_name)
                            if concept_progress:
                                difficulty = concept_progress.difficulty_level
                        self.state.add_concept(concept_name, difficulty)
                    result["success"] = True
                    result["result"] = f"Concept '{concept_name}' added"
            
            elif action == "set_current_concept":
                concept_name = decision.get("concept_name")
                if concept_name:
                    self.state.set_current_concept(concept_name)
                    result["success"] = True
                    result["result"] = f"Current concept set to: {concept_name}"
            
            elif action == "teach_concept":
                tool_name = decision.get("tool_name")
                tool_args = decision.get("tool_args", {})
                tool_call_id = f"teach_{self.iteration_count}"
                
                tool_message = self.tool_executor.execute_tool(
                    tool_name=tool_name,
                    tool_args=tool_args,
                    tool_call_id=tool_call_id,
                )
                result["success"] = True
                result["result"] = tool_message.content
            
            elif action == "generate_quiz":
                tool_name = decision.get("tool_name")
                tool_args = decision.get("tool_args", {})
                tool_call_id = f"quiz_{self.iteration_count}"
                
                tool_message = self.tool_executor.execute_tool(
                    tool_name=tool_name,
                    tool_args=tool_args,
                    tool_call_id=tool_call_id,
                )
                result["success"] = True
                result["result"] = tool_message.content
            
            elif action == "adapt_difficulty":
                concept_name = decision.get("concept_name")
                if concept_name:
                    concept_progress = self.state.get_concept_progress(concept_name)
                    if concept_progress:
                        tool_args = {
                            "concept_name": concept_name,
                            "current_difficulty": concept_progress.difficulty_level.value,
                            "quiz_score": concept_progress.score if concept_progress.score is not None else None,
                            "retry_count": concept_progress.retry_count,
                            "average_score": concept_progress.score if concept_progress.score is not None else None,
                        }
                        tool_call_id = f"adapt_{self.iteration_count}"
                        
                        tool_message = self.tool_executor.execute_tool(
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
    
    def step(self) -> Dict[str, Any]:
        observation = self.observe()
        decision = self.decide(observation)
        action_result = self.act(decision)
        
        step_result = {
            "iteration": self.iteration_count,
            "observation": observation,
            "decision": decision,
            "action_result": action_result,
        }
        
        self.history.append(step_result)
        self.iteration_count += 1
        
        return step_result
    
    def is_complete(self) -> bool:
        if self.iteration_count >= self.max_iterations:
            return True
        
        observation = self.observe()
        decision = self.decision_rules.decide_next_action(observation)
        
        if decision.get("action") == "session_complete":
            return True
        
        concepts_planned = self.state.concepts_planned
        concepts_mastered = self.state.get_mastered_concepts()
        
        if concepts_planned and len(concepts_mastered) >= len(concepts_planned):
            return True
        
        return False
    
    def run(self) -> Dict[str, Any]:
        print(f"Starting learning session for topic: {self.state.topic}")
        print(f"Session ID: {self.state.session_id}")
        print("=" * 60)
        
        while not self.is_complete():
            step_result = self.step()
            
            decision = step_result["decision"]
            action = decision.get("action")
            reason = decision.get("reason", "")
            action_result = step_result["action_result"]
            
            print(f"\n[Iteration {self.iteration_count}]")
            print(f"Action: {action}")
            print(f"Reason: {reason}")
            
            if action_result.get("success"):
                result_preview = str(action_result.get("result", ""))[:100]
                if len(str(action_result.get("result", ""))) > 100:
                    result_preview += "..."
                print(f"Result: {result_preview}")
            else:
                error = action_result.get("error", "Unknown error")
                print(f"Error: {error}")
            
            observation = step_result["observation"]
            progress = observation.get("progress_percentage", 0)
            print(f"Progress: {progress:.1f}%")
        
        print("\n" + "=" * 60)
        print("Learning session completed!")
        print(f"Total iterations: {self.iteration_count}")
        print(f"Concepts taught: {len(self.state.get_taught_concepts())}")
        print(f"Concepts mastered: {len(self.state.get_mastered_concepts())}")
        print(f"Final progress: {self.state.get_progress_percentage():.1f}%")
        print(f"Average score: {self.state.get_average_score():.2f}")
        
        return {
            "session_id": self.state.session_id,
            "topic": self.state.topic,
            "iterations": self.iteration_count,
            "concepts_taught": self.state.get_taught_concepts(),
            "concepts_mastered": self.state.get_mastered_concepts(),
            "progress_percentage": self.state.get_progress_percentage(),
            "average_score": self.state.get_average_score(),
            "history": self.history,
        }

