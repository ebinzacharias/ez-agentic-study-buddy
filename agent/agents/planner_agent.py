from agent.core.agent_base import AgentBase
from typing import Dict, Any

class PlannerAgent(AgentBase):
    """
    Agent responsible for planning study sessions or learning paths.
    """
    def handle_message(self, message: Dict[str, Any]):
        print(f"[PlannerAgent] Received message: {message}")
        # Example: respond to a 'plan_request' message
        if message.get('type') == 'plan_request':
            plan = {'type': 'plan_response', 'plan': 'Study Chapter 1: Introduction to Multi-Agent Systems'}
            if 'from' in message:
                self.send(message['from'], plan)
