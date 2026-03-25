# Web API (FastAPI)

Minimal backend to upload a file and parse it using `agent.utils.content_loader`.

## Run

```powershell
# from repo root
.venv\Scripts\python.exe -m pip install -e ".[web]"
.venv\Scripts\python.exe -m uvicorn webapi.main:app --reload --port 8000
```

## Endpoints

- `GET /` → basic API info + docs link
- `GET /ping` → `{ "status": "ok" }`
- `POST /upload` (multipart form-data `file`) → parse + preview (no session)

### Sessions

- `POST /session/from-upload` → upload file(s), create session, auto-suggest topic
- `POST /session` → create an in-memory session
- `GET /session/{session_id}` → session info
- `POST /session/{session_id}/upload` → parse + attach content to session
- `POST /session/{session_id}/plan` → plan a learning path (LLM required)
- `POST /session/{session_id}/teach` → teach a concept (LLM required)
