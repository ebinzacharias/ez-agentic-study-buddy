from agent.agents.planner_agent import PlannerAgent
from agent.agents.teacher_agent import TeacherAgent

class Orchestrator:
    """
    Minimal orchestrator to manage agent communication and run a demo interaction.
    """
    def __init__(self):
        self.planner = PlannerAgent(name="Planner")
        self.teacher = TeacherAgent(name="Teacher")
        # Register agents for message passing by name
        self.agents = {
            "Planner": self.planner,
            "Teacher": self.teacher
        }

    def run_demo(self):
        # Planner receives a plan request from the orchestrator
        plan_request = {'type': 'plan_request', 'from': 'Orchestrator'}
        self.planner.receive(plan_request)
        # Step 1: Planner processes the request and sends a plan to Teacher
        self.planner.send(self.agents["Teacher"], {'type': 'plan_response', 'plan': 'Study Chapter 1: Introduction to Multi-Agent Systems'})
        # Step 2: Teacher processes the plan
        self.teacher.step(self.agents)

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run_demo()
