# Web UI (React + Vite)

Frontend for **EZ Agentic Study Buddy**: upload-first session, learning path planning, teaching, quizzes, evaluation, and next-action hints from the API.

For environment setup (Python `uv`, `.env`, `GROQ_API_KEY`), use the [repository root README](../README.md). The **npm lockfile** for this app is **`webui/package-lock.json` only** (there is no root `package.json` / lockfile).

## Prerequisites

- Node.js 18+
- FastAPI backend running (see [webapi README](../webapi/README.md) or root README)

## Run

From **repo root**:

```bash
cd webui
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The UI calls the API at **http://localhost:8000** by default.

### API base URL

**Bash / zsh:**

```bash
export VITE_API_URL=http://127.0.0.1:8000
npm run dev
```

**PowerShell:**

```powershell
cd webui
$env:VITE_API_URL = "http://127.0.0.1:8000"
npm run dev
```

### Optional header badge (“Local · Groq”)

Shown only when `VITE_SHOW_RUNTIME_BADGE=true` is set at build/dev time (e.g. `VITE_SHOW_RUNTIME_BADGE=true npm run dev`).

## Features (UI flow)

1. Upload material → session created, topic suggested from content  
2. Plan → ordered concepts from the planner  
3. Teach → explanations grounded in uploaded text  
4. Quiz → multiple-choice from the quizzer  
5. Evaluate → rule-based scoring via the API  
6. Next-action banner → driven by `GET /session/{id}/next-action`

Plan, teach, quiz, and evaluate require a valid **`GROQ_API_KEY`** (or configured provider) on the **backend** process.
