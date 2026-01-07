# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
- ToolExecutor (`agent/core/tool_executor.py`)
  - Tool binding to LLM using `llm.bind_tools()`
  - Tool call extraction from LLM responses
  - Manual tool execution and ToolMessage creation
- Test scripts
  - LLM connection verification (`test_llm.py`)
  - Planner tool testing (`test_planner.py`)
  - Manual tool calling demonstration (`test_manual_tool_calling.py`)
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

