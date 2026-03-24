# CrewAI with Structured Outputs, YAML, and CrewBase Classes

## Introduction
This note covers how to build a multi-agent meal planning system using CrewAI, focusing on structured outputs with Pydantic, YAML-based configuration, and the use of CrewBase classes for flexible, maintainable workflows.

---

## System Overview
- **Agents:** Specialized for meal planning, shopping organization, budgeting, leftovers management, and summary generation.
- **Workflow:** Tasks run sequentially; each agent's output becomes the next agent's input.
- **Shared LLM:** All agents use a common LLM (e.g., Granite on WatsonX) for consistent reasoning.
- **External Tools:** Some agents use tools like SERPER web search for real-time data.

---

## Structured Outputs with Pydantic
- **Purpose:** Ensures agent outputs are clean, validated, and reusable.
- **Key Models:**
  - `GroceryItem`: name, quantity, estimated price, store category.
  - `MealPlan`: meal name, cooking difficulty, servings, list of ingredients.
  - `ShoppingCategory`: section name, list of grocery items, total estimated cost.
  - `GroceryShoppingPlan`: total_budget, list of MealPlan objects, ShoppingCategory sections, shopping tips.
- **Benefits:**
  - Automatic validation and serialization.
  - Consistent data exchange between agents and tasks.
  - Supports budget tracking and structured reporting.

---

## Defining Agents and Tasks in YAML
- **Why YAML?**
  - Separates configuration from code for easier updates.
  - Allows non-developers to modify agent/task definitions.
- **How:**
  - Define agent roles, goals, backstories, and tasks in YAML files.
  - Example: The leftovers agent and its task are defined in YAML for easy updates.

---

## Using CrewBase Classes
- **@CrewBase Decorator:**
  - Marks a class as a crew container.
  - Methods with @Agent or @Task return agent/task objects, loaded from YAML if specified.
  - CrewBase locates the config folder automatically.
- **Workflow:**
  - Import the CrewBase class and instantiate it with the shared LLM.
  - Access YAML-defined agents/tasks as methods.
  - Combine all agents and tasks (Python and YAML) into a complete crew.
  - Run the workflow sequentially with `.kickoff()`.

---

## Example Workflow Steps
1. **MealPlanner Agent:**
   - Finds recipes matching budget and dietary needs.
   - Uses SERPER Web Search Tool.
   - Outputs a structured `MealPlan`.
2. **ShoppingOrganizer Agent:**
   - Turns meal ingredients into a shopping list.
   - Groups items by store section, estimates quantities, considers budget/diet.
   - Outputs a `GroceryShoppingPlan`.
3. **BudgetAdvisor Agent:**
   - Ensures plan stays within budget, suggests savings.
   - Uses SERPER for price estimates.
   - Outputs markdown guide.
4. **LeftoverManager Agent (YAML):**
   - Handles leftover management, defined in YAML for easy updates.
5. **Summary Agent:**
   - Compiles all outputs into a final meal planning guide.

---

## Key Takeaways
- CrewAI enables multi-agent workflows with clear roles, goals, and tasks.
- Pydantic models ensure structured, validated data exchange.
- YAML configuration separates logic from code, making updates easier.
- CrewBase classes allow seamless integration of YAML-defined agents/tasks.
- Outputs can be stored in various formats (JSON, Markdown) as needed.
- The full workflow produces a comprehensive, structured meal planning guide.
