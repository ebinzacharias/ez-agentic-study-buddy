# Web API (FastAPI)

Session state and study flow endpoints for **EZ Agentic Study Buddy**. Parses uploads via `agent.utils.content_loader` and invokes planner, teacher, quizzer, and evaluator tools.

Full setup (`.env`, API keys) is in the [repository root README](../README.md).

## Run

From **repository root** (recommended — uses `uv` like the rest of the project):

```bash
uv sync --extra web
cp .env.example .env   # once: set GROQ_API_KEY
uv run uvicorn webapi.main:app --reload --host 127.0.0.1 --port 8000
```

Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Short message + docs link |
| `GET` | `/ping` | `{ "status": "ok" }` |
| `POST` | `/upload` | Multipart `file` — parse only, no session |
| `POST` | `/session/from-upload` | Multipart `files` — create session + load content, optional `topic`, `difficulty_level` |
| `POST` | `/session` | JSON body: `topic`, `difficulty_level` — empty session (add content via `/session/{id}/upload`) |
| `GET` | `/session/{session_id}` | Session metadata |
| `POST` | `/session/{session_id}/upload` | Multipart `file` — attach content to session |
| `POST` | `/session/{session_id}/plan` | JSON: `topic`, `difficulty_level`, `max_concepts` — learning path |
| `POST` | `/session/{session_id}/teach` | JSON: `concept_name`, optional `difficulty_level`, `context` |
| `POST` | `/session/{session_id}/quiz` | JSON: `concept_name`, optional `difficulty_level`, `num_questions`, `question_types` |
| `POST` | `/session/{session_id}/evaluate` | JSON: **`quiz_data`** and **`learner_answers`** as JSON **strings** (see [USAGE.md](../USAGE.md)) |
| `GET` | `/session/{session_id}/next-action` | Rule-based recommended next step |

Sessions live **in memory**; restart clears the server store.

## Related

- [Web UI README](../webui/README.md) — Vite dev server and `VITE_API_URL`  
- [USAGE.md](../USAGE.md) — curl examples and full workflow
