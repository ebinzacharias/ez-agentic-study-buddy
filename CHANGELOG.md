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
- Test script for LLM connection verification
- Architecture documentation with Mermaid diagrams
  - System overview diagram
  - Component architecture diagram
  - ReAct pattern flow diagram
  - Future tool integration diagram
  - Data flow sequence diagram
- Learning documentation for each completed step
- Project setup
  - MIT License
  - `.gitignore` for Python projects
  - `pyproject.toml` with dependencies
  - `.env.example` template

## [0.1.0] - 2026-01-XX

### Added
- Initial project setup
- Basic project structure
- Repository initialization

[Unreleased]: https://github.com/ebinzacharias/ez-agentic-study-buddy/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ebinzacharias/ez-agentic-study-buddy/releases/tag/v0.1.0

