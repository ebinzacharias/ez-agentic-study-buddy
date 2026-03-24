from agent.core.agent_base import AgentBase
from typing import Dict, Any

class TeacherAgent(AgentBase):
    """
    Agent responsible for teaching or delivering content.
    """
    def handle_message(self, message: Dict[str, Any], agent_registry: Dict[str, AgentBase]):
        print(f"[TeacherAgent] Received message: {message}")
        # Example: respond to a 'plan_response' message
        if message.get('type') == 'plan_response':
            print(f"[TeacherAgent] Ready to teach: {message.get('plan')}")
