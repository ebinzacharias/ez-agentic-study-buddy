# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Reproducible Python env**: `uv.lock` is committed; `.gitignore` no longer excludes it. Use `uv sync --locked` (CI uses `uv sync --extra web --group dev --locked`).
- **Dev dependencies**: `[dependency-groups].dev` pins **ruff 0.11.7** (matches pre-commit **v0.11.7**), plus mypy and pytest; CI no longer installs tools with unversioned `uv pip install`.
- **CI**: Python syntax check fails the workflow on compile errors; **mypy** stricter defaults (`ignore_missing_imports = false`) with a narrow ignore for optional `fitz`.
- **Docs**: README / CONTRIBUTING security notes for `.env` and key rotation; npm lockfile only under `webui/`.

### Added
- **FastAPI Web Backend** (`webapi/main.py`)
  - Upload-first UX: upload file(s) → auto-create session with suggested topic
  - Session management with in-memory `SESSIONS` dict (keyed by UUID)
  - Endpoints: `/upload`, `/session/from-upload`, `/session`, `/session/{id}`,
    `/session/{id}/upload`, `/session/{id}/plan`, `/session/{id}/teach`,
    `/session/{id}/quiz`, `/session/{id}/evaluate`, `/session/{id}/next-action`
  - Topic auto-suggestion from uploaded content (`_suggest_topic`)
  - Next-action recommendation engine (`_get_next_action`) — Option B agent-guidance
  - Error classification for user-friendly messages (`_classify_error`)
  - Session expiry detection with clear HTTP 404 responses
  - Corporate proxy / SSL compatibility (optional `SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`)
- **Content Loader** (`agent/utils/content_loader.py`)
  - Parses `.txt`, `.md`, `.json`, and optionally `.pdf` (PyMuPDF) into structured `LoadedContent`
  - Markdown heading-based section splitting
  - JSON key-value and nested structure parsing
  - File validation, word count, and summary context helpers
- **React Frontend** (`webui/`)
  - Vite-based React app for the upload → plan → teach → quiz → evaluate flow
- **Agent classes** (`agent/agents/`)
  - `PlannerAgent`, `TeacherAgent`, `QuizzerAgent`, `AdapterAgent`
- **Quiz schema enforcement** — multiple-choice only, grounded in uploaded content
- **Test suite expansion**
  - `test_agent_workflow_interactions.py` — API workflow interaction tests
  - `test_topic_suggestion.py` — topic auto-suggestion regression tests
  - `test_quizzer_schema_validation.py` — quiz schema validation tests
  - `test_content_loader.py` — content loader tests
  - Total: 19 test files under `scripts/`
- **CI pipeline** (`.github/workflows/ci.yml`)
  - GitHub Actions: ruff lint, mypy type check, pytest
  - Uses `uv sync --extra web --group dev --locked` for dependencies and pinned tooling
  - `pytest.importorskip("fastapi")` guards for web-dependent tests
  - `pytest.mark.skipif(not GROQ_API_KEY)` for LLM-dependent tests

### Fixed
- Topic suggestion temp-name bug — broadened `_TEMP_STEM_RE` regex to match all temp file patterns
- mypy duplicate module discovery — added `webapi/__init__.py` package marker
- mypy type errors on optional `UploadFile.filename` — normalized with `file.filename or "uploaded_file"`
- Pytest `PytestReturnNotNoneWarning` in 8+ test files — replaced `return True/False` with `pytest.fail()`
- Ruff E402 import-order errors after `pytest.importorskip()` guards — added `# noqa: E402`
- Malformed quiz output handling — fallback parsing for non-JSON LLM responses
- Session expiry handling — clear error messages when session no longer exists

### Changed
- CI workflow: `uv sync` → `uv sync --extra web` to include FastAPI/uvicorn/python-multipart
- All documentation updated to reflect web UI workflow and current project structure

### Previous (pre-web)
- Minimal multi-agent architecture foundation:
  - Base agent class (`AgentBase`) with state, messaging, and reasoning loop
  - PlannerAgent and TeacherAgent as independent agent subclasses
  - Orchestrator for agent instantiation and message passing
- Decision Rules system with explicit if/then logic for state-driven decisions
- ReAct loop implementation in StudyBuddyAgent with Observe → Decide → Act pattern
- Quiz workflow integration connecting quiz generation and evaluation
- Main agent run loop with completion detection and history tracking
- Adapter Tool (`adapt_difficulty`)
  - Analyzes performance metrics (quiz scores, retry counts, average scores)
  - Adjusts difficulty level up or down based on explicit rules
  - Handles edge cases (min/max difficulty boundaries)
  - Updates state automatically after adaptation
  - Integrated with ToolExecutor and agent loop
- Retry Mechanisms (`RetryManager`)
  - Retry counting with MAX_RETRIES limit (3 attempts)
  - Re-explanation logic with alternative strategies per retry attempt
  - Low score handling (automatically triggers retry for scores < 0.6)
  - Alternative explanation strategies (simplify_explanation, alternative_approach, adapt_difficulty)
  - Loop prevention through retry limits and difficulty adaptation
  - Enhanced teacher tool with retry-specific instructions
  - Integrated with DecisionRules and ToolExecutor for automatic retry handling
- LCEL Refactoring
  - Refactored agent to use LangChain Expression Language (LCEL) for chain composition
  - Created LCEL chains for observe, decide, and act steps
  - Uses RunnablePassthrough for state management throughout chains
  - Composes chains with pipe operator (|) for declarative flow
  - Maintains backward compatibility with original methods
  - Better separation of concerns and code maintainability
- Testing and Edge Case Handling
  - Comprehensive end-to-end testing with full learning flow validation
  - Edge case handling for empty topics, no concepts, max iterations, invalid states
  - Improved error handling with clear, contextual error messages
  - System robustness testing with multiple topics and scenarios
  - Usage documentation (USAGE.md) with examples, best practices, and troubleshooting
  - Updated README with quick start guide
  - Validates inputs and handles exceptions gracefully throughout the system
- State Management System with Pydantic models
  - `ConceptProgress` model for tracking individual concept status
  - `StudySessionState` model for tracking overall session state
  - Methods for updating progress and querying state
- LLM Client setup with multi-provider support
  - Groq integration (default, free online)
  - OpenAI integration (optional)
  - Environment variable configuration via `.env`
- Core Agent skeleton (`StudyBuddyAgent`)
  - ReAct pattern structure (observe, decide, act)
  - State and LLM integration
  - Basic agent methods and initialization
- Planner Tool (`plan_learning_path`)
  - LangChain `@tool` decorator implementation
  - Breaks down topics into ordered learning concepts
  - Returns structured concept list with difficulty and order
- Teacher Tool (`teach_concept`)
  - Generates explanations at appropriate difficulty levels
  - Adapts vocabulary, examples, and depth based on difficulty
  - Returns structured teaching content with introduction, explanation, examples, and takeaways
- ToolExecutor (`agent/core/tool_executor.py`)
  - Tool binding to LLM using `llm.bind_tools()`
  - Tool call extraction from LLM responses
  - Manual tool execution and ToolMessage creation
  - Automatic state updates after tool execution
  - Integrates with StudySessionState for progress tracking
- State Update Integration
  - Automatic state updates after planning (adds concepts to state)
  - Automatic state updates after teaching (marks concepts as taught)
  - State persistence across tool calls
- Test scripts
  - LLM connection verification (`test_llm.py`)
  - Planner tool testing (`test_planner.py`)
  - Manual tool calling demonstration (`test_manual_tool_calling.py`)
  - Teacher tool testing (`test_teacher.py`)
  - State updates testing (`test_state_updates.py`)
- GitHub Actions CI workflow
  - Runs on PRs to main and pushes to main/develop
  - Validates imports and Python syntax
  - Uses uv for dependency management
- Architecture documentation with Mermaid diagrams
  - System overview diagram (updated with ToolExecutor)
  - Component architecture diagram (updated with tools)
  - ReAct pattern flow diagram
  - Tool integration diagram (updated with current status)
  - Data flow sequence diagram (updated with ToolExecutor)
- Learning documentation for each completed step
  - Step 1: State Management
  - Step 2: LLM Client Setup
  - Step 3: Core Agent Skeleton
  - Step 4: Planner Tool
  - Step 5: Manual Tool Calling
  - Step 6: Teacher Tool
  - Step 7: State Updates
- Project setup
  - MIT License
  - `.gitignore` for Python projects
  - `pyproject.toml` with dependencies
  - `.env.example` template
  - `ARCHITECTURE.md` with comprehensive diagrams
  - `CHANGELOG.md` for version tracking

## [0.1.0] - 2026-01-XX

### Added
- Initial project setup
- Basic project structure
- Repository initialization

[Unreleased]: https://github.com/ebinzacharias/ez-agentic-study-buddy/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ebinzacharias/ez-agentic-study-buddy/releases/tag/v0.1.0

