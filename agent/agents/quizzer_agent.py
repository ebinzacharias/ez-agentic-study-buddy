from agent.core.agent_base import AgentBase
from agent.tools.quizzer_tool import generate_quiz
from typing import Dict, Any

class QuizzerAgent(AgentBase):
    """
    Agent responsible for generating quizzes and questions for concepts.
    """
    def handle_message(self, message: Dict[str, Any], agent_registry):
        print(f"[QuizzerAgent] Received message: {message}")
        if message.get('type') == 'quiz_request':
            concept = message.get('concept_name', '')
            difficulty = message.get('difficulty_level', 'beginner')
            num_questions = message.get('num_questions', 3)
            quiz = generate_quiz(concept_name=concept, difficulty_level=difficulty, num_questions=num_questions)
            # Send quiz back to requester (if specified)
            if 'from' in message:
                self.send(message['from'], {'type': 'quiz_response', 'quiz': quiz}, agent_registry)
