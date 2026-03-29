"""Smoke test for the FastAPI session endpoints.

This test avoids LLM calls (plan/teach) so it can run without GROQ_API_KEY.
It validates:
- create session
- upload text material to session

Run:
    .venv/Scripts/python.exe scripts/test_webapi_sessions.py

Requires the API running at http://127.0.0.1:8000
"""

from __future__ import annotations

import json
import urllib.request


API_BASE = "http://127.0.0.1:8000"


def http_json(method: str, url: str, body: dict | None = None) -> dict:
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_multipart_upload(url: str, field_name: str, filename: str, content: bytes) -> dict:
    # Quick + simple approach: write to temp and use curl if available is messy.
    # Instead, use requests-like multipart manually.
    boundary = "----ezagenticboundary"
    crlf = "\r\n"

    payload = (
        f"--{boundary}{crlf}"
        f"Content-Disposition: form-data; name=\"{field_name}\"; filename=\"{filename}\"{crlf}"
        f"Content-Type: application/octet-stream{crlf}{crlf}"
    ).encode("utf-8") + content + crlf.encode("utf-8") + f"--{boundary}--{crlf}".encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    print("== Web API Session Smoke Test ==")

    ping = http_json("GET", f"{API_BASE}/ping")
    assert ping.get("status") == "ok"
    print("[PASS] /ping")

    sample = b"Intro\n\nThis is a test document about Python variables.\n\n# Heading\nMore text."
    upload = http_multipart_upload(
        f"{API_BASE}/session/from-upload",
        field_name="files",
        filename="sample.txt",
        content=sample,
    )
    sid = upload["session_id"]
    assert "preview" in upload
    print(f"[PASS] upload-first created session: {sid}")

    sess = http_json("GET", f"{API_BASE}/session/{sid}")
    assert sess.get("has_loaded_content") is True
    print("[PASS] session reflects loaded content")

    source = http_json("GET", f"{API_BASE}/session/{sid}/source")
    assert "text" in source
    assert "Python variables" in source["text"]
    assert source.get("filenames") == ["sample.txt"]
    assert source.get("pdf_available") is False
    print("[PASS] session source text")

    print("All OK")


if __name__ == "__main__":
    main()
