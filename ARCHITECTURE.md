# EZ Agentic Study Buddy - Architecture

## System Overview

```mermaid
flowchart TD
    style Web fill:#DBEAFE,stroke:#3B82F6,stroke-width:2px,color:#1E3A5F
    style Core fill:#D1FAE5,stroke:#10B981,stroke-width:2px,color:#064E3B

    linkStyle default stroke:#6366F1,stroke-width:2px

    subgraph Web[Web Layer]
        UI[React UI + Vite]
        API[FastAPI Backend]
        CL[Content Loader]
    end

    subgraph Core[Agent Core]
        Agent[StudyBuddyAgent]
        ReAct[ReAct Loop]
        Agent --> ReAct
    end
    
    LLM[LLM Client — Groq / OpenAI]
    State[State Manager]
    ToolExec[ToolExecutor]
    Tools[Planner / Teacher / Quizzer / Evaluator / Adapter]
    
    UI --> API
    API --> CL
    API --> Agent
    Agent --> LLM
    Agent --> State
    Agent --> ToolExec
    ToolExec --> LLM
    ToolExec --> Tools
```

## Component Architecture

```mermaid
classDiagram
    class StudyBuddyAgent {
        -llm: ChatGroq | ChatOpenAI
        -state: StudySessionState
        -decision_rules: DecisionRules
        -tool_executor: ToolExecutor
        -max_iterations: int
        -iteration_count: int
        -history: List[Dict]
        +observe() dict
        +decide(observation) dict
        +act(decision) dict
        +step() dict
        +run() dict
        +is_complete() bool
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
    
    class ToolExecutor {
        -llm: ChatGroq | ChatOpenAI
        -state: StudySessionState
        -tools: List[BaseTool]
        -tool_map: Dict[str, BaseTool]
        -llm_with_tools: LLM
        +extract_tool_calls(response) List[Dict]
        +execute_tool(name, args, call_id) ToolMessage
        +execute_tool_calls(tool_calls) List[ToolMessage]
        -_update_state_after_tool(name, args, result) None
    }
    
    class DecisionRules {
        -state: StudySessionState
        -retry_manager: RetryManager
        +decide_next_action(observation) dict
    }
    
    class RetryManager {
        -state: StudySessionState
        +MAX_RETRIES: int = 3
        +should_retry(concept_name, quiz_score) bool
        +can_retry(concept_name) bool
        +mark_for_retry(concept_name, quiz_score) dict
        +get_retry_strategy(concept_name) dict
        +get_reteaching_context(concept_name) str
    }
    
    class QuizWorkflow {
        -state: StudySessionState
        -current_quiz: Optional[Dict]
        +generate_quiz_for_concept(...) dict
        +evaluate_learner_answers(...) dict
        +complete_quiz_flow(...) dict
        +get_quiz_status(concept_name) dict
    }
    
    class PlannerTool {
        +plan_learning_path(topic, difficulty_level, max_concepts) List[dict]
    }
    
    class TeacherTool {
        +teach_concept(concept_name, difficulty_level, context, retry_attempt, alternative_strategy) str
    }
    
    class QuizzerTool {
        +generate_quiz(concept_name, difficulty_level, num_questions, question_types) dict
    }
    
    class EvaluatorTool {
        +evaluate_response(quiz_data, learner_answers) dict
    }
    
    class AdapterTool {
        +adapt_difficulty(concept_name, current_difficulty, quiz_score, retry_count, average_score) dict
    }
    
    StudyBuddyAgent --> StudySessionState : uses
    StudyBuddyAgent --> DecisionRules : uses
    StudyBuddyAgent --> ToolExecutor : uses
    StudyBuddyAgent --> LLMClient : uses
    DecisionRules --> StudySessionState : reads
    DecisionRules --> RetryManager : uses
    RetryManager --> StudySessionState : manages
    ToolExecutor --> StudySessionState : updates
    ToolExecutor --> LLMClient : uses
    ToolExecutor --> PlannerTool : executes
    ToolExecutor --> TeacherTool : executes
    ToolExecutor --> QuizzerTool : executes
    ToolExecutor --> EvaluatorTool : executes
    ToolExecutor --> AdapterTool : executes
    StudySessionState --> ConceptProgress : contains many
    QuizWorkflow --> StudySessionState : uses
```

### Core Components

#### 0. Web Layer

##### FastAPI Backend (`webapi/main.py`)
- **Role**: HTTP interface between the React UI and the agent core
- **Responsibilities**:
  - In-memory session management (`SESSIONS` dict keyed by UUID)
  - File upload parsing via Content Loader
  - Topic auto-suggestion from uploaded content (`_suggest_topic`)
  - Error classification for user-friendly messages (`_classify_error`)
  - Next-action recommendation after each step (`_get_next_action`)
  - Session expiry detection with clear HTTP 404 responses

##### Content Loader (`agent/utils/content_loader.py`)
- **Role**: Parse uploaded files into structured content for the agent
- **Supported formats**: `.txt`, `.md`, `.json`, `.pdf` (optional, requires PyMuPDF)
- **Output**: `LoadedContent` Pydantic model with `ContentSection` items
- **Features**:
  - Markdown heading-based section splitting
  - JSON key-value and nested structure parsing
  - Word count and summary context helpers
  - File validation (existence, extension, size)

##### React Frontend (`webui/`)
- **Role**: Upload-first study interface
- **Stack**: React + Vite
- **Flow**: Upload file → auto-create session → plan → teach → quiz → evaluate

##### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/` | Health check |
| `GET`  | `/ping` | Liveness probe |
| `POST` | `/upload` | Upload & parse a single file |
| `POST` | `/session/from-upload` | Upload file(s) → create session with auto-suggested topic |
| `POST` | `/session` | Create session from previously uploaded content |
| `GET`  | `/session/{id}` | Get session state |
| `POST` | `/session/{id}/upload` | Upload additional file to existing session |
| `POST` | `/session/{id}/plan` | Generate learning path |
| `POST` | `/session/{id}/teach` | Teach a concept |
| `POST` | `/session/{id}/quiz` | Generate a quiz |
| `POST` | `/session/{id}/evaluate` | Evaluate quiz answers |
| `GET`  | `/session/{id}/next-action` | Recommended next step |

#### 1. StudyBuddyAgent (`agent/core/agent.py`)
- **Role**: Main orchestrator
- **Responsibilities**:
  - Manages ReAct loop using LCEL chains (observe → decide → act)
  - Coordinates between LLM, state, decision rules, and tools
  - Executes learning flow with iteration limits
  - Tracks session history and completion status

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

#### 4. DecisionRules (`agent/core/decision_rules.py`)
- **Role**: Rule-based decision making for autonomous actions
- **Responsibilities**:
  - Analyzes current state to determine next action
  - Uses explicit if/then logic (not LLM-based decisions)
  - Considers concepts taught, quizzed, retry needs, scores
  - Returns structured decisions with tool information
  - Integrates with RetryManager for retry strategies

#### 5. RetryManager (`agent/core/retry_manager.py`)
- **Role**: Manages retry logic and alternative teaching strategies
- **Responsibilities**:
  - Tracks retry counts (MAX_RETRIES = 3)
  - Determines retry strategies based on attempt number
  - Generates context for re-teaching
  - Handles difficulty adaptation after max retries
  - Prevents infinite retry loops

#### 6. QuizWorkflow (`agent/core/quiz_workflow.py`)
- **Role**: Orchestrates quiz generation and evaluation workflow
- **Responsibilities**:
  - Generates quizzes for concepts
  - Evaluates learner answers
  - Updates state with quiz scores
  - Provides complete quiz flow (generate → evaluate → update)
  - Tracks quiz status and retry eligibility

#### 7. ToolExecutor (`agent/core/tool_executor.py`)
- **Role**: Manages tool binding and execution with state integration
- **Responsibilities**:
  - Binds tools to LLM using `llm.bind_tools()`
  - Extracts tool calls from LLM responses
  - Executes tools and creates ToolMessages
  - Maps tool names to tool instances
  - Automatically updates state after tool execution
  - Maintains state consistency across tool calls
  - Integrates with RetryManager for quiz evaluation

#### 8. Tools (`agent/tools/`)
- **Planner Tool** (`planner_tool.py`): ✅ Implemented
  - Breaks down topics into ordered learning concepts
  - Returns structured concept list with difficulty and order
  - Updates state: adds concepts to StudySessionState
- **Teacher Tool** (`teacher_tool.py`): ✅ Implemented
  - Generates explanations at appropriate difficulty levels
  - Adapts vocabulary, examples, and depth based on difficulty
  - Supports retry attempts with alternative strategies
  - Returns structured teaching content
  - Updates state: marks concepts as taught
- **Quizzer Tool** (`quizzer_tool.py`): ✅ Implemented
  - Generates quizzes based on concept and difficulty
  - Supports multiple question types (multiple choice, short answer, true/false)
  - Returns structured JSON with questions, options, answers, explanations
  - Updates state: adds concepts if not present
- **Evaluator Tool** (`evaluator_tool.py`): ✅ Implemented
  - Evaluates learner responses using explicit, rule-based scoring
  - Handles multiple question types with keyword matching
  - Provides partial credit for partial answers
  - Returns scores, feedback, and detailed results
  - Updates state: marks concepts as quizzed with scores
- **Adapter Tool** (`adapter_tool.py`): ✅ Implemented
  - Adjusts difficulty level based on performance metrics
  - Analyzes quiz scores, retry counts, average scores
  - Uses explicit rules (not LLM judgment)
  - Handles edge cases (min/max difficulty boundaries)
  - Updates state: adjusts concept difficulty level

#### 9. LCEL Chains (`agent/chains/decision_chain.py`)
- **Role**: Declarative chain composition for ReAct loop
- **Components**:
  - `create_observe_chain()`: Observes current state
  - `create_decide_chain()`: Makes decisions based on state
  - `create_act_chain()`: Executes actions using tools
  - `create_step_chain()`: Composes all chains together
- **Benefits**:
  - Cleaner, more declarative code
  - Better separation of concerns
  - Easier to test and maintain
  - Composable with pipe operator (|)

## ReAct Pattern Flow

```mermaid
flowchart LR
    style Observe fill:#DBEAFE,stroke:#3B82F6,stroke-width:2px,color:#1E3A5F
    style Decide fill:#FEF3C7,stroke:#F59E0B,stroke-width:2px,color:#78350F
    style Act fill:#D1FAE5,stroke:#10B981,stroke-width:2px,color:#064E3B
    style UpdateState fill:#EDE9FE,stroke:#8B5CF6,stroke-width:2px,color:#4C1D95

    linkStyle default stroke:#6366F1,stroke-width:2px

    Start([Start Session]) --> Observe[OBSERVE]
    
    Observe --> Decide[DECIDE]
    
    Decide --> Plan[Plan Path]
    Decide --> Teach[Teach Concept]
    Decide --> Quiz[Quiz Concept]
    Decide --> Evaluate[Evaluate Response]
    Decide --> Adapt[Retry / Adapt]
    
    Plan --> Act[ACT]
    Teach --> Act
    Quiz --> Act
    Evaluate --> Act
    Adapt --> Act
    
    Act --> UpdateState[Update State]
    UpdateState --> CheckComplete{Complete?}
    
    CheckComplete -->|No| Observe
    CheckComplete -->|Yes| End([End Session])
```

## Tool Integration

```mermaid
flowchart TD
    style ToolLayer fill:#FEF3C7,stroke:#F59E0B,stroke-width:2px,color:#78350F

    linkStyle default stroke:#6366F1,stroke-width:2px

    Agent[StudyBuddyAgent] --> ToolExec[ToolExecutor]
    
    subgraph ToolLayer[Tool Layer]
        Planner[Planner Tool]
        Teacher[Teacher Tool]
        Quizzer[Quizzer Tool]
        Evaluator[Evaluator Tool]
        Adapter[Adapter Tool]
    end

    ToolExec --> Planner
    ToolExec --> Teacher
    ToolExec --> Quizzer
    ToolExec --> Evaluator
    ToolExec --> Adapter
    
    Planner --> State[State Manager]
    Teacher --> State
    Quizzer --> State
    Evaluator --> State
    Adapter --> State
    
    Planner --> LLM[LLM Client]
    Teacher --> LLM
    Quizzer --> LLM
```

## Data Flow

```mermaid
sequenceDiagram
    participant Browser as React UI
    participant API as FastAPI Backend
    participant CL as Content Loader
    participant Agent as StudyBuddyAgent
    participant State as StudySessionState
    participant DecisionRules
    participant RetryManager
    participant ToolExec as ToolExecutor
    participant Tools as Agent Tools
    participant LLM

    Browser->>API: POST /session/from-upload (file)
    API->>CL: Parse file
    CL-->>API: LoadedContent
    API->>API: _suggest_topic(content)
    API->>State: Create Session State
    API-->>Browser: { session_id, topic, content_preview }

    Browser->>API: POST /session/{id}/plan
    API->>Agent: plan(topic, content)
    
    loop ReAct Loop
        Agent->>State: OBSERVE: Read State
        State-->>Agent: Current Progress Data
        
        Agent->>DecisionRules: DECIDE: Analyze State
        DecisionRules->>RetryManager: Check Retry Needs (if applicable)
        RetryManager-->>DecisionRules: Retry Strategy
        DecisionRules-->>Agent: Decision (action, tool_name, tool_args)
        
        Agent->>ToolExec: ACT: Execute Tool
        ToolExec->>Tools: Execute Tool (Planner/Teacher/Quizzer/Evaluator/Adapter)
        Tools->>LLM: Generate Content (if needed)
        LLM-->>Tools: Content Response
        Tools->>State: Update Progress
        Tools->>RetryManager: Update Retry Count (if quiz evaluation)
        Tools-->>ToolExec: Tool Result
        ToolExec-->>Agent: ToolMessage with Result
        
        Agent->>Agent: Check Completion
        
        alt Session Complete
            Agent-->>API: Return Final State
            API->>API: _get_next_action(state)
            API-->>Browser: { result, next_action }
        end
    end
```

## Key Design Patterns

1. **ReAct Pattern**: Reasoning + Acting loop for autonomous decision-making
   - Observe → Decide → Act → Repeat until completion
   - Implemented using LCEL chains for cleaner composition

2. **State Management**: Centralized state tracking with Pydantic models
   - StudySessionState for overall session tracking
   - ConceptProgress for individual concept status
   - Automatic state updates after tool execution

3. **Rule-Based Decisions**: Explicit if/then logic for decision making
   - DecisionRules class analyzes state and returns actions
   - Not LLM-based decisions (uses explicit rules)
   - Considers taught status, quiz scores, retry counts

4. **Retry Mechanisms**: Adaptive retry with alternative strategies
   - MAX_RETRIES = 3 limit prevents infinite loops
   - Different strategies per retry attempt (simplify, alternative approach, adapt difficulty)
   - Automatic difficulty adaptation after max retries

5. **LCEL Chains**: LangChain Expression Language for declarative composition
   - RunnablePassthrough for state management
   - Pipe operator (|) for chain composition
   - Better separation of concerns and testability

6. **Dependency Injection**: LLM and state can be provided or auto-created
   - Flexible initialization with optional parameters
   - Easy testing with mock objects

7. **Tool-Based Architecture**: Extensible tool system with ToolExecutor
   - Planner, Teacher, Quizzer, Evaluator, Adapter tools
   - Automatic tool binding to LLM
   - State updates after tool execution

8. **Explicit Scoring**: Rule-based evaluation logic
   - EvaluatorTool uses explicit keyword matching, not LLM judgment
   - Consistent, predictable scoring
   - Supports partial credit scenarios

9. **Error Handling**: Comprehensive error handling with clear messages
   - Input validation with helpful error messages
   - Structured error responses in action results
   - Edge case handling throughout the system

## LCEL Chain Architecture

```mermaid
flowchart LR
    style Observe fill:#DBEAFE,stroke:#3B82F6,stroke-width:2px,color:#1E3A5F
    style Decide fill:#FEF3C7,stroke:#F59E0B,stroke-width:2px,color:#78350F
    style Act fill:#D1FAE5,stroke:#10B981,stroke-width:2px,color:#064E3B
    style Output fill:#EDE9FE,stroke:#8B5CF6,stroke-width:2px,color:#4C1D95

    linkStyle default stroke:#6366F1,stroke-width:2px

    Input[Input State] --> Observe[Observe Chain]
    Observe --> Decide[Decide Chain]
    Decide --> Act[Act Chain]
    Act --> Output[Output State]
```

**Chain Composition**:
```python
step_chain = (
    observe_chain
    | decide_chain
    | act_chain
)
```

## Current Status

### ✅ Implemented Components

- **Web Layer**: FastAPI backend with session management, content loading, upload-first UX
- **React Frontend**: Vite-based upload → plan → teach → quiz → evaluate UI
- **Content Loader**: Parses `.txt`, `.md`, `.json`, optional `.pdf`
- **Core Agent**: StudyBuddyAgent with ReAct loop using LCEL chains
- **State Management**: Complete state tracking with Pydantic models
- **Decision Rules**: Rule-based decision making with explicit logic and next-action guidance
- **Retry Manager**: Retry mechanisms with alternative strategies
- **Quiz Workflow**: Complete quiz generation and evaluation workflow
- **All Tools**: Planner, Teacher, Quizzer, Evaluator, Adapter
- **LCEL Chains**: Declarative chain composition for ReAct loop
- **Error Handling**: Comprehensive error handling, session expiry detection, and edge cases
- **Testing**: 19 test files — end-to-end, unit, schema validation, workflow interaction tests
- **CI Pipeline**: GitHub Actions with ruff, mypy, and pytest

### 🔄 Learning Flow

1. **Planning Phase**: Planner tool creates learning path
2. **Teaching Phase**: Teacher tool explains concepts (with retry support)
3. **Assessment Phase**: Quizzer tool generates quizzes
4. **Evaluation Phase**: Evaluator tool scores responses (explicit logic)
5. **Adaptation Phase**: Adapter tool adjusts difficulty based on performance
6. **Retry Phase**: RetryManager handles retries with alternative strategies

### 📊 State Tracking

- Concepts planned, taught, quizzed, mastered
- Quiz scores and retry counts
- Difficulty levels and adaptation history
- Progress percentage and average scores
- Session history and iteration tracking

## Environment Configuration

```
.env file:
├─> LLM_PROVIDER=groq
├─> LLM_MODEL=llama-3.1-8b-instant
├─> LLM_TEMPERATURE=0.7
├─> GROQ_API_KEY=your_key
└─> (Optional: OPENAI_API_KEY)
```


