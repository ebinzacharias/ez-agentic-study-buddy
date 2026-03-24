# Essential Design Patterns for AI Systems

## Introduction

This note covers essential design patterns for AI systems, focusing on LLM workflow patterns and their implementation using LangGraph. The patterns discussed include sequential (prompt chaining), routing, parallelization, the orchestrator pattern, and the evaluator-optimizer pattern. Each pattern is explained with its structure, use case, and execution flow.

---

## 1. Sequential Pattern (Prompt Chaining)

**Description:**
- The simplest workflow pattern.
- Passes the output of one LLM (or agent) directly as input to the next.
- Breaks complex problems into manageable steps, allowing specialized agents to handle each step.

**Example Use Case:**
- Writing a cover letter based on a job description.
  - Step 1: Technical expert agent generates a resume summary.
  - Step 2: Professional writer agent crafts the cover letter using the summary and job description.

**LangGraph Implementation:**
- Define a chain state object with fields for job description, resume summary, and cover letter.
- Create nodes for each agent (e.g., generate_resume_summary, generate_cover_letter).
- Connect nodes sequentially in the workflow graph.
- State variables are updated at each step and passed along the chain.

---

## 2. Routing Pattern

**Description:**
- Uses a router agent to analyze input and decide which specialized agent should handle the task.
- Enables intelligent selection and dynamic workflow branching.

**Example Use Case:**
- A system that can either summarize or translate input based on user request.

**LangGraph Implementation:**
- Define a router state with fields for user input, task type, and output.
- Create a router node that determines the task type (summarize or translate).
- Add conditional edges to route to the appropriate agent node.
- Each specialized node (summarize, translate) processes the input and updates the output field.

---

## 3. Parallelization Pattern

**Description:**
- Runs multiple LLM tasks simultaneously, increasing speed and throughput.
- Useful for splitting a problem into independent parts and merging results.

**Example Use Case:**
- Translating a sentence into multiple languages at once, then combining the results.

**LangGraph Implementation:**
- Define a state container with fields for the original input, each translation, and a combined output.
- Create translation nodes for each target language.
- Add an aggregator node to merge all translations.
- Connect translation nodes to run in parallel, then feed results to the aggregator.

---

## 4. Orchestrator Design Pattern

**Description:**
- Manages dynamic workflows where the number and type of tasks are not known in advance.
- A central orchestrator assigns tasks to specialized worker agents and coordinates parallel execution.
- A synthesizer node merges all worker outputs into a unified result.

**Example Use Case:**
- A party planner (orchestrator) receives a request for a multi-themed dinner, assigns chefs (workers) for each cuisine, and combines their dishes into a menu.

**LangGraph Implementation:**
- Use state variables for shared context (e.g., meals, sections, completed_menu, final_meal_guide).
- Worker state variables hold task-specific details for each worker.
- The orchestrator node breaks down the request and assigns tasks using the `send` function.
- Worker nodes process their assigned tasks in parallel, updating the shared state.
- The synthesizer node combines all outputs into the final result.

---

## 5. Evaluator-Optimizer Design Pattern

**Description:**
- Refines LLM outputs through iterative feedback loops until they meet target criteria.
- Connects generator, evaluator, and feedback nodes in a reflection loop.

**Example Use Case:**
- Multi-agent investment advisor:
  - Generator (e.g., Kathy Wood persona) creates an investment plan.
  - Evaluator (e.g., Warren Buffett persona) grades and provides feedback.
  - If rejected, feedback is used to refine the plan (e.g., Ray Dalio persona).
  - Loop continues until the plan meets the target risk grade or iteration limit is reached.

**LangGraph Implementation:**
- State variables track investor profile, investment plan, risk grades, feedback, and iteration count.
- Nodes for grading, generation, evaluation, and feedback routing.
- Conditional edges implement the reflection loop, routing back to the generator if needed.
- Workflow stops when criteria are met or iteration limit is reached.

---

## Summary Table

| Pattern                | Description                                      | Use Case Example                        |
|------------------------|--------------------------------------------------|-----------------------------------------|
| Sequential (Chaining)  | Passes output of one agent to the next           | Cover letter generation                 |
| Routing                | Directs input to the right agent based on intent | Summarize or translate user input       |
| Parallelization        | Runs tasks in parallel, merges results           | Multi-language translation              |
| Orchestrator           | Dynamically assigns and coordinates tasks        | Multi-themed dinner planning            |
| Evaluator-Optimizer    | Iterative feedback/refinement loop               | Investment plan refinement              |

---

## Key Concepts
- **State Variables:** Track workflow data and context, passed between nodes.
- **Nodes:** Represent agents or processing steps in the workflow.
- **Edges:** Define execution flow and conditional routing.
- **Worker State:** Used in orchestrator pattern for task-specific context.
- **Reflection Loop:** Used in evaluator-optimizer pattern for iterative improvement.

LangGraph enables structured, flexible, and scalable AI workflows by combining these patterns with state management and directed graphs.
