# Step 4: Planner Tool

## What Was Done

Created the Planner Tool in `agent/tools/planner_tool.py`:

1. **LangChain Tool Decorator**: Used `@tool` decorator from `langchain_core.tools` to create a callable tool that LLMs can understand and invoke.

2. **Comprehensive Docstring**: Added detailed docstring that explains:
   - Tool purpose and functionality
   - Parameters with descriptions
   - Return value structure
   - Example usage
   - This docstring is critical as LLMs use it to understand when and how to call the tool

3. **Type Annotations**: Added proper type hints:
   - Function parameters with default values
   - Return type `List[dict]` for structured concept data

4. **Implementation Logic**:
   - Uses LLM to analyze topic and break it into concepts
   - Parses numbered list response from LLM
   - Maps concepts to ordered list with difficulty levels
   - Respects max_concepts parameter to limit output

5. **Structured Return**: Returns list of dictionaries with:
   - `concept_name`: Name of the concept
   - `difficulty`: Difficulty level (beginner/intermediate/advanced)
   - `order`: Sequential order in learning path

## Why This Is Required

The Planner Tool is essential because:

1. **Autonomous Learning Path Creation**: The agent needs to break down any topic into teachable concepts without manual intervention.

2. **LangChain Tool Integration**: Using `@tool` decorator makes the function callable by LLMs through tool calling, enabling the agent to autonomously decide when to create a learning path.

3. **LLM Understanding**: The detailed docstring allows the LLM to understand:
   - When this tool should be used
   - What parameters it needs
   - What it will return
   - How to interpret the results

4. **Structured Output**: Returning structured data allows the agent to programmatically add concepts to state and manage the learning sequence.

5. **Foundation for Teaching Flow**: Once concepts are planned, the agent can systematically teach each one in order.

6. **Prerequisite for ReAct Loop**: This tool will be invoked in the DECIDE phase when the agent observes that no learning path exists yet.

Without the Planner Tool, the agent cannot autonomously create learning paths and must rely on manually provided concepts.

