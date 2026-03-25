# Web UI (React)

Minimal UI to upload a file and view parsed section titles + content preview.

Also supports:
- upload-first session creation (topic is auto-suggested from your file)
- planning a learning path
- teaching a selected concept

## Run

```powershell
cd webui
npm install
npm run dev
```

The UI expects the API at `http://localhost:8000`.

Optional: override with an env var:

```powershell
$env:VITE_API_URL = "http://localhost:8000"
npm run dev
```

Note: Plan/Teach use an LLM; ensure your API environment has `GROQ_API_KEY` set.
