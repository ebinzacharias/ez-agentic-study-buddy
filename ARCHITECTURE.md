# EZ Agentic Study Buddy - Architecture

## System Overview

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

## Component Architecture

```mermaid
classDiagram
    class StudyBuddyAgent {
        -llm: ChatGroq | ChatOpenAI
        -state: StudySessionState
        +observe() dict
        +decide(observation) str
        +act(action) dict
        +step() dict
        +run() None
    }
    
    class StudySessionState {
        +session_id: str
        +topic: str
        +concepts: dict[str, ConceptProgress]
        +current_concept: str
        +overall_difficulty: DifficultyLevel
        +add_concept(name, difficulty)
        +set_current_concept(name)
        +mark_concept_taught(name)
        +mark_concept_quizzed(name, score)
        +get_progress_percentage() float
        +get_average_score() float
    }
    
    class ConceptProgress {
        +concept_name: str
        +status: ConceptStatus
        +quiz_taken: bool
        +score: float
        +retry_count: int
        +difficulty_level: DifficultyLevel
        +mark_taught()
        +mark_quizzed(score)
        +increment_retry()
    }
    
    class LLMClient {
        +initialize_llm(provider, model, temperature)
        +get_llm_client() ChatGroq | ChatOpenAI
    }
    
    StudyBuddyAgent --> StudySessionState : uses
    StudyBuddyAgent --> LLMClient : uses
    StudySessionState --> ConceptProgress : contains many
```

### Core Components

#### 1. StudyBuddyAgent (`agent/core/agent.py`)
- **Role**: Main orchestrator
- **Responsibilities**:
  - Manages ReAct loop (observe → decide → act)
  - Coordinates between LLM and state
  - Executes learning flow

#### 2. State Management (`agent/core/state.py`)
- **StudySessionState**: Overall session tracking
  - Session metadata (topic, ID, start time)
  - Dictionary of concepts and their progress
  - Methods to query progress (taught, mastered, needs retry)
  
- **ConceptProgress**: Individual concept tracking
  - Status (not_started, in_progress, taught, quizzed, mastered, needs_retry)
  - Quiz scores and retry counts
  - Difficulty level

#### 3. LLM Client (`agent/utils/llm_client.py`)
- **Role**: Language model interface
- **Supports**: Groq (default, free) and OpenAI
- **Configuration**: Environment variables (.env)

## ReAct Pattern Flow

```mermaid
flowchart LR
    Start([Start Session]) --> Observe[OBSERVE<br/>Read Current State]
    
    Observe --> ObserveData{State Information}
    ObserveData --> Current[Current Concept]
    ObserveData --> Progress[Progress %]
    ObserveData --> Taught[Concepts Taught]
    ObserveData --> Retry[Needs Retry]
    
    Current --> Decide
    Progress --> Decide
    Taught --> Decide
    Retry --> Decide
    
    Decide[DECIDE<br/>Choose Action<br/>Using LLM + State]
    
    Decide --> ActionDecision{What to do?}
    
    ActionDecision -->|No concepts| Plan[Plan Learning Path]
    ActionDecision -->|Not taught| Teach[Teach Concept]
    ActionDecision -->|Not quizzed| Quiz[Quiz Concept]
    ActionDecision -->|Quiz taken| Evaluate[Evaluate Response]
    ActionDecision -->|Needs retry| Adapt[Retry/Adapt]
    
    Plan --> Act
    Teach --> Act
    Quiz --> Act
    Evaluate --> Act
    Adapt --> Act
    
    Act[ACT<br/>Execute Action]
    
    Act --> UpdateState[Update State]
    UpdateState --> CheckComplete{Session<br/>Complete?}
    
    CheckComplete -->|No| Observe
    CheckComplete -->|Yes| End([End Session])
    
    style Observe fill:#e3f2fd
    style Decide fill:#fff3e0
    style Act fill:#e8f5e9
    style UpdateState fill:#f3e5f5
```

## Future Tool Integration

```mermaid
graph TD
    Agent[StudyBuddyAgent] --> Tools{Tool Selection}
    
    Tools -->|Initial Setup| Planner[Planner Tool<br/>Generate Learning Path]
    Tools -->|Teaching Phase| Teacher[Teacher Tool<br/>Teach Concepts]
    Tools -->|Assessment Phase| Quizzer[Quizzer Tool<br/>Create Quizzes]
    Tools -->|Evaluation Phase| Evaluator[Evaluator Tool<br/>Evaluate Responses]
    Tools -->|Adaptation| Adapter[Adapter Tool<br/>Adjust Difficulty]
    
    Planner --> State
    Teacher --> State
    Quizzer --> State
    Evaluator --> State
    Adapter --> State
    
    State[State Manager<br/>Updates Progress]
    
    LLM[LLM Client<br/>Powers All Tools]
    
    Planner --> LLM
    Teacher --> LLM
    Quizzer --> LLM
    Evaluator --> LLM
    Adapter --> LLM
    
    style Agent fill:#e1f5ff
    style Planner fill:#e8f5e9
    style Teacher fill:#fff3e0
    style Quizzer fill:#fce4ec
    style Evaluator fill:#e0f2f1
    style Adapter fill:#f3e5f5
    style LLM fill:#fff9c4
    style State fill:#e8eaf6
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Agent as StudyBuddyAgent
    participant State as StudySessionState
    participant LLM
    participant Tools as Agent Tools
    
    User->>Agent: Initialize with Topic
    Agent->>State: Create Session State
    Agent->>LLM: Initialize LLM Client
    
    loop ReAct Loop
        Agent->>State: OBSERVE: Read State
        State-->>Agent: Current Progress Data
        
        Agent->>LLM: DECIDE: Analyze State
        LLM-->>Agent: Recommended Action
        
        Agent->>Tools: ACT: Execute Tool
        Tools->>LLM: Generate Content
        LLM-->>Tools: Content Response
        Tools->>State: Update Progress
        Tools-->>Agent: Action Result
        
        Agent->>Agent: Check Completion
        
        alt Session Complete
            Agent->>User: Return Final State
        end
    end
```

## Key Design Patterns

1. **ReAct Pattern**: Reasoning + Acting loop for autonomous decision-making
2. **State Management**: Centralized state tracking with Pydantic models
3. **Dependency Injection**: LLM and state can be provided or auto-created
4. **Tool-Based Architecture**: Extensible tool system (to be implemented)

## Environment Configuration

```
.env file:
├─> LLM_PROVIDER=groq
├─> LLM_MODEL=llama-3.1-8b-instant
├─> GROQ_API_KEY=your_key
└─> (Optional: OPENAI_API_KEY)
```

## Current Status

✅ State Management System
✅ LLM Client Setup
✅ Core Agent Skeleton
⏳ Tool Definitions (Planner, Teacher, Quizzer, Evaluator)
⏳ Decision Logic Implementation
⏳ Main Agent Loop

