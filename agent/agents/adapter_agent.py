from agent.core.agent_base import AgentBase
from agent.tools.adapter_tool import adapt_difficulty
from typing import Dict, Any

class AdapterAgent(AgentBase):
    """
    Agent responsible for adjusting difficulty and adapting learning based on performance.
    """
    def handle_message(self, message: Dict[str, Any], agent_registry):
        print(f"[AdapterAgent] Received message: {message}")
        if message.get('type') == 'adapt_request':
            concept = message.get('concept_name', '')
            current_difficulty = message.get('current_difficulty', 'beginner')
            quiz_score = message.get('quiz_score')
            retry_count = message.get('retry_count')
            average_score = message.get('average_score')
            performance_history = message.get('performance_history')
            result = adapt_difficulty(
                concept_name=concept,
                current_difficulty=current_difficulty,
                quiz_score=quiz_score,
                retry_count=retry_count,
                average_score=average_score,
                performance_history=performance_history
            )
            # Send adaptation result back to requester (if specified)
            if 'from' in message:
                self.send(message['from'], {'type': 'adapt_response', 'adaptation': result}, agent_registry)
