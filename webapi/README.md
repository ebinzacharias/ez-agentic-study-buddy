# Web API (FastAPI)

Minimal backend to upload a file and parse it using `agent.utils.content_loader`.

## Run

```powershell
# from repo root
.venv\Scripts\python.exe -m pip install -e ".[web]"
.venv\Scripts\python.exe -m uvicorn webapi.main:app --reload --port 8000
```

## Endpoints

- `GET /ping` → `{ "status": "ok" }`
- `POST /upload` (multipart form-data `file`) → parsed section titles + preview
