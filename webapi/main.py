import os
import tempfile

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agent.utils.content_loader import SUPPORTED_EXTENSIONS, load_content

app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "EZ-Agentic Content Loader API",
        "docs": "http://127.0.0.1:8000/docs",
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={
                "error": f"Unsupported file type: {ext}",
                "supported": sorted(SUPPORTED_EXTENSIONS),
            },
        )
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        content = load_content(tmp_path)
        return {
            "section_titles": content.get_section_titles(),
            "preview": content.get_summary_context(1200),
            "metadata": content.metadata,
            "title": content.title,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        os.unlink(tmp_path)

@app.get("/ping")
def ping():
    return {"status": "ok"}
