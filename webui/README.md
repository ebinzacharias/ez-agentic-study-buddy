# Web UI (React)

Minimal UI to upload a file and view parsed section titles + content preview.

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
