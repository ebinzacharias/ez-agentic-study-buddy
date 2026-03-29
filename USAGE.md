# Usage Guide

## Web UI (Recommended)

The easiest way to use EZ Agentic Study Buddy is through the web interface.

### Start the Backend

```bash
uv sync --extra web --locked
uv run uvicorn webapi.main:app --reload --port 8000
```

### Start the Frontend

```bash
cd webui
npm install
npm run dev
```

### Study Workflow

1. **Upload** — Open [http://localhost:5173](http://localhost:5173) and drop a file (PDF, Markdown, plain text, or JSON).
2. **Session Created** — A session is created automatically. The system suggests a topic from your content.
3. **Plan** — Click "Plan" to generate a learning path of ordered concepts.
4. **Teach** — Step through each concept. The Teacher generates grounded explanations from your material.
5. **Quiz** — Take a multiple-choice quiz on each concept.
6. **Evaluate** — Get instant feedback with scores and next-action recommendations.
7. **Adapt** — Difficulty adjusts automatically based on your quiz performance.

### Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Plain text | `.txt` | Split into sections by blank lines |
| Markdown | `.md` | Split by headings (`#`, `##`, etc.) |
| JSON | `.json` | Key-value pairs or nested objects |
| PDF | `.pdf` | Loaded via **pymupdf** (included in `pyproject.toml`; run `uv sync`) |

### API Usage (curl)

Replace `SESSION_ID` with the `session_id` value from `/session/from-upload` (or export it: `export SESSION_ID=...`).

```bash
# Upload a file and create a session (multipart field must be "files")
curl -s -X POST http://localhost:8000/session/from-upload \
  -F "files=@my-notes.md"

# Plan learning path (JSON body — empty topic uses session topic)
curl -s -X POST "http://localhost:8000/session/${SESSION_ID}/plan" \
  -H "Content-Type: application/json" \
  -d '{"topic":"","difficulty_level":"beginner","max_concepts":10}'

# Teach a concept (concept_name is required)
curl -s -X POST "http://localhost:8000/session/${SESSION_ID}/teach" \
  -H "Content-Type: application/json" \
  -d '{"concept_name":"Your concept name","difficulty_level":"beginner","context":""}'

# Generate a quiz for a concept
curl -s -X POST "http://localhost:8000/session/${SESSION_ID}/quiz" \
  -H "Content-Type: application/json" \
  -d '{"concept_name":"Your concept name","difficulty_level":"beginner","num_questions":3,"question_types":"multiple_choice"}' \
  -o quiz-response.json

# Evaluate answers: the API expects quiz_data and learner_answers as JSON *strings*.
# Easiest: save the /quiz JSON to quiz-response.json, write learner answers, combine with jq.
echo '{"answers":[{"question_number":1,"answer":"A"}]}' > learner-answers.json
# Use the same question_number values as in quiz-response.json; for MC, answer can be A/B/C/D or full option text.
jq -n --rawfile q quiz-response.json --rawfile la learner-answers.json \
  '{quiz_data: $q, learner_answers: $la}' | \
curl -s -X POST "http://localhost:8000/session/${SESSION_ID}/evaluate" \
  -H "Content-Type: application/json" \
  -d @-

# Get next recommended action
curl -s "http://localhost:8000/session/${SESSION_ID}/next-action"
```

The **`jq`** step is optional if you build the outer JSON yourself; keep `quiz_data` and `learner_answers` as string values whose contents are valid JSON. See `POST /session/{session_id}/evaluate` in [http://localhost:8000/docs](http://localhost:8000/docs) when the server is running.

---

## Programmatic Usage

### Quick Start

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

### Run All Tests

```bash
# Full suite (LLM-dependent tests require GROQ_API_KEY)
uv run python -m pytest -q

# Verbose output
uv run python -m pytest -v
```

### Offline Tests (No API Key)

```bash
uv run python -m pytest scripts/test_decision_rules.py scripts/test_quizzer_schema_validation.py -q
```

### Run Specific Test Categories

```bash
# Decision rules (offline)
uv run python -m pytest scripts/test_decision_rules.py -v

# Quiz schema validation (offline)
uv run python -m pytest scripts/test_quizzer_schema_validation.py -v

# End-to-end (requires GROQ_API_KEY)
uv run python -m pytest scripts/test_end_to_end.py -v

# LCEL chains
uv run python -m pytest scripts/test_lcel_chains.py -v

# Retry mechanisms
uv run python -m pytest scripts/test_retry_mechanisms.py -v

# Web API workflow interactions (requires fastapi extra)
uv run python -m pytest scripts/test_agent_workflow_interactions.py -v
```

> **Note:** Tests that require `GROQ_API_KEY` or `fastapi` will skip automatically when those dependencies are unavailable.

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

See the `scripts/` directory for test examples:

| File | Description |
|------|-------------|
| `test_end_to_end.py` | Complete system flow |
| `test_planner.py` | Learning path planning |
| `test_teacher.py` | Concept teaching |
| `test_quizzer.py` | Quiz generation |
| `test_evaluator.py` | Answer evaluation |
| `test_retry_mechanisms.py` | Retry handling |
| `test_decision_rules.py` | Decision rule logic (offline) |
| `test_quizzer_schema_validation.py` | Quiz schema validation (offline) |
| `test_agent_workflow_interactions.py` | Web API workflow interactions |
| `test_topic_suggestion.py` | Topic auto-suggestion |

