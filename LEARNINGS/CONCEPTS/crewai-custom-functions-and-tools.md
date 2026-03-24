# Extending CrewAI with Custom Functions

## Introduction
This note explains how to extend CrewAI with custom functions (tools), assign them to agents or tasks, and design both agent-centric and task-centric workflows for greater flexibility and control.

---

## Custom Functions (Tools) in CrewAI
- **Purpose:** Enhance agent capabilities and enable domain-specific, task-specific behavior.
- **How to Create:**
  - Use the `@tool` decorator from `crewai.tools` to register a function as a tool.
  - Example: Define `add_numbers` and `multiply_numbers` tools for a calculator agent.
  - Each tool should have a docstring describing its purpose.
- **Assignment:**
  - Tools can be assigned to agents or tasks, depending on workflow needs.

---

## Example: Calculator Agent with Custom Tools
- **Tools:**
  - `add_numbers`: Adds numbers extracted from input.
  - `multiply_numbers`: Multiplies numbers extracted from input.
- **Agent:**
  - Role: Calculator
  - Goal: Extract, add, or multiply numbers from instructions.
  - Backstory: Interprets numeric instructions.
  - Tools: Assigned both `add_numbers` and `multiply_numbers`.
- **Workflow:**
  - Task input: e.g., "Add 7 and 8, also 9, don't forget 10."
  - Agent parses input, selects the appropriate tool, and returns the result.

---

## Assigning Tools: Agent-Centric vs Task-Centric

### Agent-Centric Approach
- **Tools are assigned directly to the agent.**
- Agent decides which tool to use based on the query.
- Example: Daily Dish Assistant agent with access to both PDF Search Tool and SerperDevTool.
- Agent analyzes the query and chooses the appropriate tool.
- Flexible, allows agent reasoning and tool selection.

### Task-Centric Approach
- **Tools are assigned to individual tasks, not the agent.**
- Agent follows a guided, step-by-step process using the tool specified by each task.
- Example: Customer Service Specialist agent with two tasks:
  - FAQ search (uses PDF Search Tool)
  - Response drafting (uses FAQ results)
- Each task manages its own tool, ensuring isolation and traceability.
- Useful for workflows requiring strict process control.

---

## Example: Q&A Bot for Daily Dish
- **Agent-Centric:**
  - Inquiry Specialist agent with access to FAQ PDF and web search tools.
  - Agent chooses tool based on question.
- **Task-Centric:**
  - Customer Service Specialist agent with tasks for FAQ search and response drafting.
  - Tools are attached to tasks, not the agent.
  - Workflow is sequential and guided.

---

## Key Takeaways
- Custom functions (tools) in CrewAI enable domain-specific actions and greater workflow flexibility.
- Tools can be assigned to agents (agent-centric) or tasks (task-centric), depending on the desired control and reasoning.
- Agent-centric workflows allow agents to choose tools dynamically.
- Task-centric workflows guide agents through a fixed process, with tools attached to each step.
- CrewAI supports both approaches for building robust, adaptable multi-agent systems.
