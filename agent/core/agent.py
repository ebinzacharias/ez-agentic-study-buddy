import uuid
from typing import Optional, Union

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from agent.core.state import StudySessionState


class StudyBuddyAgent:
    def __init__(
        self,
        llm: Optional[Union[ChatGroq, ChatOpenAI]] = None,
        session_state: Optional[StudySessionState] = None,
        topic: Optional[str] = None,
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
    
    def observe(self) -> dict:
        return {
            "session_id": self.state.session_id,
            "topic": self.state.topic,
            "current_concept": self.state.current_concept,
            "concepts_taught": self.state.get_taught_concepts(),
            "concepts_mastered": self.state.get_mastered_concepts(),
            "concepts_needing_retry": self.state.get_concepts_needing_retry(),
            "progress_percentage": self.state.get_progress_percentage(),
            "average_score": self.state.get_average_score(),
            "overall_difficulty": self.state.overall_difficulty.value,
        }
    
    def decide(self, observation: dict) -> str:
        pass
    
    def act(self, action: str) -> dict:
        pass
    
    def step(self) -> dict:
        observation = self.observe()
        action = self.decide(observation)
        result = self.act(action)
        return {
            "observation": observation,
            "action": action,
            "result": result,
        }
    
    def run(self) -> None:
        pass

