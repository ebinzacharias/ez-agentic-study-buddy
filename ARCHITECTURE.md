# System Architecture

## Overview

The system has three layers: a web interface, an agent core, and a set of tools. The web layer handles file uploads and session management.

**Two ways to run the same building blocks:**

1. **HTTP path (default product):** FastAPI handlers update `StudySessionState` and call tools or teacher/quiz helpers **directly** per endpoint (for example `plan_learning_path.invoke(...)`, `teach_concept_payload`, quiz generation, evaluation). The UI advances the workflow one REST call at a time.
2. **Library path:** `StudyBuddyAgent` runs a **ReAct-style** LCEL loop (**observe → decide → act**) each `step()`, using **DecisionRules** and **ToolExecutor** over the same tools and state. This is used for **programmatic runs and tests**, not as the internal driver for every browser action.

All decision-making about _what to do next_ (for **DecisionRules** and `/next-action`) uses explicit rules, not LLM inference. The LLM is used for **content generation** inside planner, teacher, and quizzer paths (and related invocations).

## Components

### Web Layer

**FastAPI Backend** (`webapi/main.py`)
- In-memory session management keyed by UUID.
- File upload parsing via Content Loader.
- Topic auto-suggestion from uploaded content.
- Endpoints invoke tools or structured helpers **directly**; they do **not** call `StudyBuddyAgent` per request.
- Next-action recommendation via **DecisionRules** on current state (`GET /session/{id}/next-action`).
- Error classification for user-facing messages.

**Content Loader** (`agent/utils/content_loader.py`)
- Parses `.txt`, `.md`, `.json`, `.pdf` into structured `LoadedContent`.
- Markdown heading-based section splitting.
- JSON key-value and nested structure parsing.
- File validation (existence, extension, size).

**React Frontend** (`webui/`)
- Upload-first interface built with React and Vite.
- Components: UploadStep, PlanStep, TeachStep, QuizStep, ModeSwitcher, SessionControls, QuizProgressTracker, MaterialPreview, SourcePreviewModal.
- Flow: upload file, create session, plan, teach, quiz, evaluate.

### Agent Core

**StudyBuddyAgent** (`agent/core/agent.py`)
- Runs the ReAct loop using LCEL chains (observe, decide, act) for **`step()` / `run()`** in Python.
- Coordinates LLM, state, decision rules, and tools via **ToolExecutor**.
- Enforces iteration limits. Tracks session history.
- **Not** wired as the default executor inside FastAPI route handlers (see Overview).

**StudySessionState** (`agent/core/state.py`)
- Pydantic model tracking session metadata, concepts, and progress.
- ConceptProgress tracks individual concept status, quiz scores, retry counts, and difficulty.
- Methods: `get_progress_percentage()`, `get_average_score()`, `get_concepts_needing_retry()`.

**DecisionRules** (`agent/core/decision_rules.py`)
- Determines the next action using explicit if/then logic.
- Considers: concepts taught, quizzed, retry needs, scores.
- Returns structured decisions with tool name and arguments.

**RetryManager** (`agent/core/retry_manager.py`)
- Tracks retry counts per concept (max 3).
- Selects retry strategy based on attempt number: simplify, alternative approach, adapt difficulty.
- Prevents infinite retry loops.

**QuizWorkflow** (`agent/core/quiz_workflow.py`)
- Orchestrates quiz generation, answer evaluation, and state updates.
- Tracks quiz status and retry eligibility per concept.

**ToolExecutor** (`agent/core/tool_executor.py`)
- Binds tools to LLM using `llm.bind_tools()`.
- Extracts and executes tool calls from LLM responses.
- Updates state automatically after each tool execution.

### Tools

All tools live in `agent/tools/`. Each accepts structured input and returns structured output.

| Tool | File | Responsibility |
|------|------|----------------|
| Planner | `planner_tool.py` | Break topic into ordered concepts with difficulty levels |
| Teacher | `teacher_tool.py` | Generate explanations adapted to difficulty, with retry support |
| Quizzer | `quizzer_tool.py` | Generate multiple-choice questions from concept content |
| Evaluator | `evaluator_tool.py` | Score answers using keyword matching (not LLM judgment) |
| Adapter | `adapter_tool.py` | Adjust difficulty based on quiz scores and retry count |

### LCEL Chains

**Decision Chain** (`agent/chains/decision_chain.py`)
- Composes the ReAct loop as: `observe_chain | decide_chain | act_chain`.
- Each chain is a `RunnablePassthrough` that adds its result to the state dict.

### LLM Client

**LLM Client** (`agent/utils/llm_client.py`)
- Supports Groq (default) and OpenAI.
- Configured via environment variables.

## Data Flow

### Typical web request path

```mermaid
sequenceDiagram
    participant UI as React UI
    participant API as FastAPI
    participant CL as Content Loader
    participant State as StudySessionState
    participant Rules as DecisionRules
    participant Tools as LangChain tools
    participant LLM as LLM

    UI->>API: POST /session/from-upload (file)
    API->>CL: load_content
    CL-->>API: LoadedContent
    API->>State: Create session, set topic
    API-->>UI: session_id, topic

    UI->>API: POST /session/{id}/plan
    API->>Tools: plan_learning_path.invoke(...)
    Tools->>LLM: Generate learning path
    LLM-->>Tools: Structured concepts
    Tools-->>API: concept list
    API->>State: concepts_planned / topic
    API-->>UI: JSON response

    UI->>API: GET /session/{id}/next-action
    API->>State: Read state
    API->>Rules: decide_next_action()
    Rules-->>API: action, args, reason
    API-->>UI: Recommendation
```

### Library agent loop (`StudyBuddyAgent`)

For **`agent.run()`** or repeated **`agent.step()`**, the same **DecisionRules** and **ToolExecutor** run an **observe → decide → act** LCEL chain each iteration (see `agent/chains/decision_chain.py`). The LLM is invoked from tools as needed inside the **Act** phase.

## Architecture Diagram

```mermaid
flowchart TD
    classDef layer fill:#EEF2FF,stroke:#6366F1,stroke-width:2px,color:#1E293B,font-weight:bold

    subgraph UserLayer[User Layer]
        direction TB
        Browser[React + Vite]
    end

    subgraph ServiceLayer[Service Layer]
        direction TB
        API[FastAPI Backend]
        CL[Content Loader]
    end

    subgraph AgentLayer[Agent Layer]
        direction TB
        SA[StudyBuddyAgent<br/>library / tests]
        TE[ToolExecutor]
        DR[DecisionRules]
        RM[RetryManager]
        SM[StudySessionState]
    end

    subgraph ToolLayer[Tool Layer]
        direction TB
        PT[Planner Tool]
        TT[Teacher Tool]
        QT[Quizzer Tool]
        ET[Evaluator Tool]
        AT[Adapter Tool]
    end

    subgraph InfraLayer[Infrastructure]
        direction TB
        LLM[LLM - Groq / OpenAI]
    end

    Browser ==> API
    API --> CL
    API --> SM
    API --> ToolLayer
    API -.->|/next-action| DR
    SA --> DR
    SA --> SM
    DR --> SM
    DR -.-> RM
    SA ==> TE
    TE ==> ToolLayer
    PT --> LLM
    TT --> LLM
    QT --> LLM

    class UserLayer,ServiceLayer,AgentLayer,ToolLayer,InfraLayer layer
```

## ReAct Loop

**In `StudyBuddyAgent`**, each `step()` runs three phases:

1. **Observe** - Read current session state (concepts planned, taught, quizzed, scores).
2. **Decide** - DecisionRules analyzes state and returns the next action using explicit logic.
3. **Act** - ToolExecutor runs the selected tool and updates state.

The loop continues until all concepts are mastered or the iteration limit is reached.

In the **web app**, the **user and UI** advance the workflow; each **POST** performs one slice of this flow (plan, teach, quiz, evaluate) without entering `StudyBuddyAgent` unless you call it from Python yourself.

```mermaid
flowchart LR
    classDef phase fill:#EEF2FF,stroke:#6366F1,stroke-width:2px,color:#1E293B,font-weight:bold

    Start([Start]) ==> Observe[Observe]
    Observe ==> Decide[Decide]
    Decide ==> Act[Act]
    Act ==> Check{Done?}
    Check -->|No| Observe
    Check ==>|Yes| End([End])

    class Observe,Decide,Act phase
```

## Design Decisions

- **Rule-based decisions over LLM decisions.** DecisionRules uses explicit if/then logic to determine the next action. This makes behavior predictable and testable. The LLM is only used for content generation.

- **State-driven flow.** The agent does not maintain a conversation history for decision-making. It reads the current state each iteration. This avoids context window issues and makes the system stateless between iterations.

- **Explicit scoring.** The Evaluator uses keyword matching, not LLM judgment. This ensures consistent, reproducible quiz scores.

- **Retry with strategy variation.** Each retry attempt uses a different teaching strategy (simplify, alternative approach, difficulty adaptation). After 3 retries, the system adapts difficulty and moves on.

- **LCEL composition.** The ReAct loop is composed as a chain (`observe | decide | act`). This keeps each phase isolated and testable.

## Environment Configuration

```
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
LLM_TEMPERATURE=0.7
GROQ_API_KEY=your_key
OPENAI_API_KEY=optional
```

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/ping` | Liveness probe |
| `POST` | `/upload` | Upload and parse a file |
| `POST` | `/session/from-upload` | Upload file, create session |
| `POST` | `/session` | Create session from uploaded content |
| `GET` | `/session/{id}` | Get session state |
| `POST` | `/session/{id}/plan` | Generate learning path |
| `POST` | `/session/{id}/teach` | Teach a concept |
| `POST` | `/session/{id}/quiz` | Generate a quiz |
| `POST` | `/session/{id}/evaluate` | Evaluate quiz answers |
| `GET` | `/session/{id}/next-action` | Recommended next step |


