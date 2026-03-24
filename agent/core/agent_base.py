from typing import Any, Dict, Optional

class AgentBase:
    """
    Minimal base class for agents in a multi-agent system.
    Handles state, messaging, and a simple reasoning loop.
    """
    def __init__(self, name: str, state: Optional[Dict[str, Any]] = None):
        self.name = name
        self.state = state or {}
        self.inbox = []  # List of incoming messages
        self.outbox = []  # List of outgoing messages

    def receive(self, message: Dict[str, Any]):
        """Receive a message (append to inbox)."""
        self.inbox.append(message)

    def send(self, recipient: 'AgentBase', message: Dict[str, Any]):
        """Send a message to another agent (append to their inbox)."""
        recipient.receive({**message, 'from': self.name})
        self.outbox.append({'to': recipient.name, **message})

    def step(self):
        """Process one message from the inbox (to be implemented by subclasses)."""
        if self.inbox:
            message = self.inbox.pop(0)
            self.handle_message(message)

    def handle_message(self, message: Dict[str, Any]):
        """Handle an incoming message (override in subclass)."""
        raise NotImplementedError("handle_message must be implemented by subclasses.")
