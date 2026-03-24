# BeeAI Core Concepts and Architecture

## Introduction
BeeAI is an open-source, production-ready platform for building AI agents and multi-agent systems, developed under the Linux Foundation AI and Data Program and backed by IBM Research. It is designed for real-world deployment with enterprise-grade stability, modularity, and observability.

---

## Core Capabilities & Architecture
- **Production-Ready Architecture:** Built-in caching, memory optimization, resource management, and open telemetry integration.
- **Provider-Agnostic Backend:** Supports 10+ LLM providers (OpenAI, WatsonX.ai, Grok, Ollama, Anthropic, etc.).
- **Advanced Agent Patterns:** Implements patterns like ReAct (Reasoning and Acting), systematic thinking, and multi-agent coordination.
- **Dual-Language Support:** Full feature parity between Python and TypeScript.

---

## Async & Await in BeeAI
- **Why Async/Await?**
  - Handles I/O operations (e.g., LLM calls) efficiently.
  - Enables concurrent execution for better performance, especially in multi-agent and tool-using scenarios.
  - `async def` defines a coroutine; `await` pauses execution until completion.

---

## Prompt Templates & Structured Outputs
- **Dynamic Prompt Templates:**
  - Use mustache-style syntax for reusable, consistent prompts.
  - Ensures uniformity and reduces bias in LLM interactions.
- **Structured Outputs with Pydantic:**
  - Define schemas using Pydantic models.
  - BeeAI returns typed, validated Python objects matching your schema.
  - Eliminates parsing errors and ensures data consistency.

---

## Memory Management
- **UnconstrainedMemory Class:**
  - Stores all messages without limits (full conversational history).
  - Async methods for adding, retrieving, and resetting memory.
  - Useful for maintaining context across interactions.

---

## Key Benefits of BeeAI
- **Modularity:** Swap components (models, memory, tools) independently.
- **Structured Outputs:** Guarantees typed, validated data.
- **Async Execution:** Responsive apps, even with slow APIs or many agents.
- **Multi-Agent Support:** Build workflows with specialized agent collaboration.
- **Standards Compliance:** Integrates with Model Context Protocol (MCP), Agent-to-Agent (A2A), etc.
- **Observability:** Open telemetry for debugging, monitoring, and optimization.

---

# Building Agents with the BeeAI Framework

## RequirementAgent Class
- **Purpose:** Build intelligent, controllable agents with persistent state, tool usage, and behavioral requirements.
- **Setup:**
  - Import RequirementAgent and UnconstrainedMemory.
  - Initialize LLM and memory.
  - Define system instructions for agent role.
  - Run agent asynchronously.

---

## Adding Tools & Reasoning
- **Tools:**
  - Add capabilities (e.g., WikipediaTool, ThinkTool).
  - Use `tools` parameter to assign tools to agents.
- **Requirements System:**
  - Fine-grained control over tool usage (e.g., max invocations, execution order).
  - `ConditionalRequirement`, `AskPermissionRequirement`, `ControlTrajectoryMiddleware`, etc.
- **ReAct Pattern:**
  - Combine ThinkTool and action tools.
  - Use requirements to enforce think-act cycles and control tool usage.

---

## Human-in-the-Loop & Security
- **AskPermissionRequirement:**
  - Adds human approval before agent actions.
  - Essential for compliance and risk management.

---

## Custom Tools
- **How to Build:**
  - Define input schema with Pydantic.
  - Create a Tool subclass with custom logic in `_run`.
  - Use in agents like any built-in tool.

---

## Multi-Agent Systems
- **HandoffTool:**
  - Enables agents to delegate tasks to other agents.
  - Coordinator agent uses HandoffTool and ThinkTool for orchestration.

---

## Summary
- BeeAI is a robust, modular, and production-ready framework for building advanced AI agents and multi-agent systems.
- Key features: async execution, structured outputs, memory management, advanced agent patterns, and observability.
- Supports both individual and collaborative agent workflows, with fine-grained control and standards compliance.
