# Step 11: Decision Rules

## What Was Done

Created explicit decision rules in `agent/core/decision_rules.py`:

1. **DecisionRules Class**: Implements rule-based decision making using explicit if/then logic:
   - Analyzes current state
   - Returns appropriate action based on state conditions
   - Handles all learning flow scenarios

2. **Decision Logic**: Implements explicit rules for:
   - **Plan Learning Path**: If no concepts planned
   - **Add Concept**: If concepts planned but not in state
   - **Teach Concept**: If concept not taught or needs retry
   - **Generate Quiz**: If concept taught but not quizzed
   - **Re-teach**: If quiz score is low (< 0.6)
   - **Move to Next**: If concept mastered or quizzed with good score
   - **Adapt Difficulty**: If concept failed 3+ times
   - **Session Complete**: If all concepts mastered

3. **State Analysis**: Considers:
   - Concepts planned vs concepts in state
   - Current concept status (not_started, in_progress, taught, quizzed, mastered, needs_retry)
   - Quiz scores and retry counts
   - Overall progress

4. **Action Structure**: Returns structured action dictionary with:
   - `action`: Action type (plan_learning_path, teach_concept, generate_quiz, etc.)
   - `tool_name`: Tool to use (if applicable)
   - `tool_args`: Arguments for tool (if applicable)
   - `reason`: Explanation of why this action was chosen

5. **Edge Case Handling**:
   - Handles missing concepts
   - Handles concepts not in planned list
   - Handles retry scenarios
   - Handles session completion

6. **Helper Methods**:
   - `_get_observation()`: Gets current state observation
   - `_get_next_untaught_concept()`: Finds next concept to teach
   - `_get_teaching_context()`: Builds context for teaching

## Why This Is Required

Explicit decision rules are essential because:

1. **Deterministic Decisions**: Explicit rules ensure the same state always leads to the same decision, making behavior predictable and testable.

2. **Transparency**: Clear if/then logic makes it easy to understand why a particular action was chosen.

3. **Maintainability**: Explicit rules are easier to modify and debug than LLM-based decisions.

4. **Reliability**: Rule-based decisions don't depend on LLM availability or model behavior.

5. **Performance**: Rule-based decisions are instant, no API calls needed.

6. **Testability**: Explicit logic can be unit tested with different state scenarios.

7. **Foundation for Agent**: The agent's `decide()` method can use these rules to make autonomous decisions.

8. **Control Flow**: Provides clear control flow for the learning process (teach → quiz → evaluate → adapt → repeat).

Without explicit decision rules, the agent would rely solely on LLM judgment, which is inconsistent and unpredictable.

