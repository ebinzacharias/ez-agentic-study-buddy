# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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

