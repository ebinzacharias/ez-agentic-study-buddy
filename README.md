# EZ Agentic Study Buddy

A single-agent AI tutor that autonomously guides learners through topics using the ReAct (Reasoning + Acting) pattern.

**Started:** January 2026

## Overview

An AI agent that makes autonomous decisions about learning flow:
- Plans learning paths from topics
- Teaches concepts step-by-step
- Tests understanding with quizzes
- Evaluates responses and adapts difficulty
- Tracks progress throughout the session

## Core Architecture

```mermaid
graph TB
    subgraph "StudyBuddyAgent"
        Agent[StudyBuddyAgent]
        ReAct[ReAct Loop<br/>observe → decide → act]
        Agent --> ReAct
    end
    
    LLM[LLM Client<br/>Groq/OpenAI]
    State[State Manager<br/>StudySessionState<br/>ConceptProgress]
    
    Agent --> LLM
    Agent --> State
    
    style Agent fill:#e1f5ff
    style ReAct fill:#fff4e1
    style LLM fill:#e8f5e9
    style State fill:#f3e5f5
```

### ReAct Pattern

The agent continuously loops through three phases:

```mermaid
flowchart LR
    O[OBSERVE<br/>Read State] --> D[DECIDE<br/>Choose Action]
    D --> A[ACT<br/>Execute]
    A --> O
    
    style O fill:#e3f2fd
    style D fill:#fff3e0
    style A fill:#e8f5e9
```

1. **OBSERVE**: Reads current state (progress, scores, concepts taught)
2. **DECIDE**: Uses LLM to analyze state and choose next action
3. **ACT**: Executes chosen action and updates state

### Components

- **StudyBuddyAgent**: Main orchestrator managing the ReAct loop
- **LLM Client**: Interface to language models (Groq default, OpenAI optional)
- **State Manager**: Tracks session progress using Pydantic models

For detailed architecture, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Groq API key ([console.groq.com](https://console.groq.com) - free)

### Setup

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Test setup
uv run python scripts/test_llm.py
```

### Usage

```python
from agent.core.agent import StudyBuddyAgent

agent = StudyBuddyAgent(topic="Python Basics")
observation = agent.observe()
result = agent.step()
```

## Project Structure

```
agent/
├── core/
│   ├── agent.py          # StudyBuddyAgent class
│   └── state.py          # State models
└── utils/
    └── llm_client.py     # LLM initialization
```

## Documentation

- [Architecture](./ARCHITECTURE.md) - System design and diagrams
- [Learning Notes](./LEARNINGS/) - Step-by-step implementation guide
- [Changelog](./CHANGELOG.md) - Version history

## License

MIT - See [LICENSE](./LICENSE) for details
