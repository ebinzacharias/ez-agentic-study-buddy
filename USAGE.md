# Usage Guide

## Quick Start

### Basic Usage

```python
from agent.core.agent import StudyBuddyAgent

# Create an agent with a topic
agent = StudyBuddyAgent(topic="Python Basics", max_iterations=50)

# Run the learning session
result = agent.run()

# Access results
print(f"Concepts taught: {result['concepts_taught']}")
print(f"Progress: {result['progress_percentage']:.1f}%")
print(f"Average score: {result['average_score']:.2f}")
```

### Step-by-Step Usage

```python
from agent.core.agent import StudyBuddyAgent

# Initialize agent
agent = StudyBuddyAgent(topic="Machine Learning Fundamentals", max_iterations=30)

# Run step by step
while not agent.is_complete():
    step_result = agent.step()
    
    decision = step_result["decision"]
    action = decision.get("action")
    reason = decision.get("reason")
    
    print(f"Action: {action}")
    print(f"Reason: {reason}")
    
    observation = step_result["observation"]
    print(f"Progress: {observation['progress_percentage']:.1f}%")

# Get final results
final_result = {
    "session_id": agent.state.session_id,
    "iterations": agent.iteration_count,
    "concepts_taught": agent.state.get_taught_concepts(),
    "concepts_mastered": agent.state.get_mastered_concepts(),
    "progress_percentage": agent.state.get_progress_percentage(),
    "average_score": agent.state.get_average_score(),
}
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# LLM Provider (groq or openai)
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
LLM_TEMPERATURE=0.7

# API Keys
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### Agent Parameters

```python
agent = StudyBuddyAgent(
    topic="Your Topic",           # Required: Learning topic
    max_iterations=50,            # Optional: Max iterations (default: 50)
    llm=None,                     # Optional: Custom LLM instance
    session_state=None,           # Optional: Existing session state
)
```

## Advanced Usage

### Using Custom Session State

```python
from agent.core.state import StudySessionState, DifficultyLevel

# Create custom session state
state = StudySessionState(
    session_id="custom-session-123",
    topic="Advanced Python",
)

# Add concepts manually
state.add_concept("Decorators", DifficultyLevel.INTERMEDIATE)
state.add_concept("Generators", DifficultyLevel.ADVANCED)

# Use with agent
agent = StudyBuddyAgent(session_state=state)
```

### Accessing Individual Methods

```python
agent = StudyBuddyAgent(topic="Python Basics")

# Observe current state
observation = agent.observe()
print(f"Current concept: {observation['current_concept']}")
print(f"Progress: {observation['progress_percentage']:.1f}%")

# Make decision
decision = agent.decide(observation)
print(f"Next action: {decision['action']}")

# Execute action
action_result = agent.act(decision)
print(f"Success: {action_result['success']}")
```

### Using LCEL Chains Directly

```python
from agent.chains.decision_chain import create_step_chain
from agent.core.decision_rules import DecisionRules
from agent.core.tool_executor import ToolExecutor
from agent.core.agent import StudyBuddyAgent

agent = StudyBuddyAgent(topic="Python Basics")

# Create LCEL chain
step_chain = create_step_chain(
    state_manager=agent,
    decision_rules=agent.decision_rules,
    tool_executor=agent.tool_executor,
    iteration_count=agent.iteration_count,
)

# Invoke chain
result = step_chain.invoke({})
print(f"Observation: {result.get('observation')}")
print(f"Decision: {result.get('decision')}")
print(f"Action Result: {result.get('action_result')}")
```

## Error Handling

### Common Errors

**ValueError: Topic required**
```python
try:
    agent = StudyBuddyAgent(topic="")
except ValueError as e:
    print(f"Error: {e}")
    # Output: Topic must be a non-empty string
```

**RuntimeError: Session completed**
```python
agent = StudyBuddyAgent(topic="Test", max_iterations=2)
agent.run()

try:
    agent.step()  # Will raise RuntimeError
except RuntimeError as e:
    print(f"Error: {e}")
    # Output: Session already completed...
```

**Tool Execution Errors**
```python
step_result = agent.step()
action_result = step_result.get("action_result", {})

if not action_result.get("success"):
    error = action_result.get("error", "Unknown error")
    print(f"Action failed: {error}")
```

## Best Practices

### 1. Set Appropriate Max Iterations

```python
# For simple topics
agent = StudyBuddyAgent(topic="Simple Topic", max_iterations=20)

# For complex topics
agent = StudyBuddyAgent(topic="Complex Topic", max_iterations=100)
```

### 2. Monitor Progress

```python
agent = StudyBuddyAgent(topic="Python Basics", max_iterations=50)

while not agent.is_complete():
    step_result = agent.step()
    
    observation = step_result["observation"]
    progress = observation["progress_percentage"]
    
    if progress >= 100.0:
        print("All concepts mastered!")
        break
    
    print(f"Progress: {progress:.1f}%")
```

### 3. Handle Edge Cases

```python
# Check if concepts exist
agent = StudyBuddyAgent(topic="Topic", max_iterations=10)

step_result = agent.step()
observation = step_result["observation"]

if not observation.get("concepts_planned"):
    print("No concepts planned yet")
elif len(observation.get("concepts_planned", [])) == 0:
    print("Learning path planning in progress")
```

### 4. Save Session History

```python
agent = StudyBuddyAgent(topic="Python Basics", max_iterations=50)
result = agent.run()

# Access history
history = result["history"]

# Save to file
import json
with open("session_history.json", "w") as f:
    json.dump(history, f, indent=2, default=str)
```

## Testing

### Run End-to-End Tests

```bash
uv run python scripts/test_end_to_end.py
```

### Run Specific Tests

```bash
# Test LCEL chains
uv run python scripts/test_lcel_chains.py

# Test retry mechanisms
uv run python scripts/test_retry_mechanisms.py

# Test decision rules
uv run python scripts/test_decision_rules.py
```

## Troubleshooting

### Issue: LLM Connection Failed

**Solution**: Check your API keys in `.env` file:
```bash
# Verify keys are set
echo $GROQ_API_KEY
echo $OPENAI_API_KEY
```

### Issue: Agent Stuck in Loop

**Solution**: Check max_iterations and completion conditions:
```python
agent = StudyBuddyAgent(topic="Topic", max_iterations=50)

# Monitor iterations
while not agent.is_complete():
    step_result = agent.step()
    if agent.iteration_count >= agent.max_iterations:
        print("Reached max iterations")
        break
```

### Issue: No Concepts Planned

**Solution**: Wait for learning path planning to complete:
```python
agent = StudyBuddyAgent(topic="Topic", max_iterations=10)

# First step should plan learning path
step_result = agent.step()
decision = step_result["decision"]

if decision.get("action") == "plan_learning_path":
    print("Planning learning path...")
    # Continue with next steps
```

## Examples

See the `scripts/` directory for more examples:
- `test_end_to_end.py`: Complete system testing
- `test_planner.py`: Learning path planning
- `test_teacher.py`: Concept teaching
- `test_quizzer.py`: Quiz generation
- `test_evaluator.py`: Answer evaluation
- `test_retry_mechanisms.py`: Retry handling

