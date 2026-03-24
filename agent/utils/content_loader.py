"""
Content Loader Utility

Loads and parses user-uploaded study materials (text, PDF, Markdown)
into structured content the agent can use for teaching and quiz generation.
"""

import json
import re
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


class ContentSection(BaseModel):
    """A single section extracted from uploaded content."""

    title: str = ""
    body: str = ""
    source_file: str = ""
    page_number: Optional[int] = None
    section_index: int = 0

    def word_count(self) -> int:
        return len(self.body.split())


class LoadedContent(BaseModel):
    """Structured representation of all loaded study materials."""

    title: str = ""
    source_file: str = ""
    sections: list[ContentSection] = Field(default_factory=list)
    raw_text: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    def total_word_count(self) -> int:
        return sum(s.word_count() for s in self.sections)

    def get_section_titles(self) -> list[str]:
        return [s.title for s in self.sections if s.title]

    def get_full_text(self) -> str:
        """Return all section bodies joined together."""
        if self.sections:
            return "\n\n".join(s.body for s in self.sections if s.body)
        return self.raw_text

    def get_summary_context(self, max_chars: int = 2000) -> str:
        """Return a truncated version suitable for LLM context."""
        full = self.get_full_text()
        if len(full) <= max_chars:
            return full
        return full[:max_chars] + "\n\n[... content truncated ...]"


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def load_text_file(file_path: str) -> LoadedContent:
    """Load a plain .txt file."""
    path = Path(file_path)
    _validate_file(path, {".txt"})

    text = path.read_text(encoding="utf-8")
    sections = _split_into_sections(text, source_file=path.name)

    return LoadedContent(
        title=path.stem,
        source_file=path.name,
        sections=sections,
        raw_text=text,
        metadata={"format": "text", "size_bytes": path.stat().st_size},
    )


def load_markdown_file(file_path: str) -> LoadedContent:
    """Load a Markdown (.md) file, splitting on headings."""
    path = Path(file_path)
    _validate_file(path, {".md", ".markdown"})

    text = path.read_text(encoding="utf-8")
    sections = _parse_markdown_sections(text, source_file=path.name)

    title = path.stem
    if sections and sections[0].title:
        title = sections[0].title

    return LoadedContent(
        title=title,
        source_file=path.name,
        sections=sections,
        raw_text=text,
        metadata={"format": "markdown", "size_bytes": path.stat().st_size},
    )


def load_pdf_file(file_path: str) -> LoadedContent:
    """
    Load a PDF file. Requires the ``pymupdf`` (fitz) package.

    Falls back to a helpful error if pymupdf is not installed.
    """
    path = Path(file_path)
    _validate_file(path, {".pdf"})

    try:
        import fitz  # pymupdf
    except ImportError:
        raise ImportError(
            "pymupdf is required to load PDF files. "
            "Install it with: pip install pymupdf"
        )

    doc = fitz.open(str(path))
    sections: list[ContentSection] = []
    all_text_parts: list[str] = []

    for page_num, page in enumerate(doc, start=1):
        page_text = page.get_text()  # type: ignore[union-attr]
        if page_text.strip():
            sections.append(
                ContentSection(
                    title=f"Page {page_num}",
                    body=page_text.strip(),
                    source_file=path.name,
                    page_number=page_num,
                    section_index=page_num - 1,
                )
            )
            all_text_parts.append(page_text.strip())

    doc.close()

    return LoadedContent(
        title=path.stem,
        source_file=path.name,
        sections=sections,
        raw_text="\n\n".join(all_text_parts),
        metadata={
            "format": "pdf",
            "size_bytes": path.stat().st_size,
            "page_count": len(sections),
        },
    )


def load_json_file(file_path: str) -> LoadedContent:
    """Load a structured JSON study-material file.

    Expected shape (flexible):
        { "title": "...", "sections": [ {"title": "...", "body": "..."}, ... ] }
    or a plain list of strings.
    """
    path = Path(file_path)
    _validate_file(path, {".json"})

    data = json.loads(path.read_text(encoding="utf-8"))
    sections: list[ContentSection] = []

    if isinstance(data, dict):
        title = data.get("title", path.stem)
        for idx, sec in enumerate(data.get("sections", [])):
            if isinstance(sec, dict):
                sections.append(
                    ContentSection(
                        title=str(sec.get("title", "")),
                        body=str(sec.get("body") or sec.get("content") or ""),
                        source_file=path.name,
                        section_index=idx,
                    )
                )
            elif isinstance(sec, str):
                sections.append(
                    ContentSection(
                        body=sec,
                        source_file=path.name,
                        section_index=idx,
                    )
                )
    elif isinstance(data, list):
        title = path.stem
        for idx, item in enumerate(data):
            body = item if isinstance(item, str) else json.dumps(item)
            sections.append(
                ContentSection(
                    body=body,
                    source_file=path.name,
                    section_index=idx,
                )
            )
    else:
        title = path.stem
        sections.append(
            ContentSection(
                body=str(data),
                source_file=path.name,
                section_index=0,
            )
        )

    raw_text = "\n\n".join(s.body for s in sections)

    return LoadedContent(
        title=title,
        source_file=path.name,
        sections=sections,
        raw_text=raw_text,
        metadata={"format": "json", "size_bytes": path.stat().st_size},
    )


# ---------------------------------------------------------------------------
# Auto-detect loader
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".pdf", ".json"}

_LOADERS = {
    ".txt": load_text_file,
    ".md": load_markdown_file,
    ".markdown": load_markdown_file,
    ".pdf": load_pdf_file,
    ".json": load_json_file,
}


def load_content(file_path: str) -> LoadedContent:
    """Auto-detect file type and load content.

    Args:
        file_path: Path to the study material file.

    Returns:
        LoadedContent with parsed sections.

    Raises:
        ValueError: If the file type is not supported.
        FileNotFoundError: If the file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()
    loader = _LOADERS.get(ext)
    if loader is None:
        raise ValueError(
            f"Unsupported file type: '{ext}'. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    return loader(file_path)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _validate_file(path: Path, allowed_suffixes: set[str]) -> None:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() not in allowed_suffixes:
        raise ValueError(
            f"Expected one of {allowed_suffixes}, got '{path.suffix}'"
        )


def _split_into_sections(
    text: str,
    source_file: str = "",
    min_section_length: int = 50,
) -> list[ContentSection]:
    """Split plain text into sections by blank-line-separated paragraphs."""
    paragraphs = re.split(r"\n\s*\n", text.strip())
    sections: list[ContentSection] = []

    for idx, para in enumerate(paragraphs):
        para = para.strip()
        if not para:
            continue

        # Treat a short first line as a heading
        lines = para.split("\n", 1)
        if len(lines) == 2 and len(lines[0]) < 80:
            title = lines[0].strip()
            body = lines[1].strip()
        else:
            title = ""
            body = para

        if len(body) < min_section_length and idx > 0 and sections:
            # Merge tiny paragraphs into previous section
            sections[-1].body += "\n\n" + body
            continue

        sections.append(
            ContentSection(
                title=title,
                body=body,
                source_file=source_file,
                section_index=len(sections),
            )
        )

    return sections


def _parse_markdown_sections(
    text: str,
    source_file: str = "",
) -> list[ContentSection]:
    """Split Markdown into sections based on headings (# / ## / ###)."""
    heading_pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    matches = list(heading_pattern.finditer(text))

    if not matches:
        # No headings — treat as a single section
        return _split_into_sections(text, source_file)

    sections: list[ContentSection] = []

    # Content before the first heading
    pre_heading = text[: matches[0].start()].strip()
    if pre_heading:
        sections.append(
            ContentSection(
                title="Introduction",
                body=pre_heading,
                source_file=source_file,
                section_index=0,
            )
        )

    for i, match in enumerate(matches):
        title = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()

        sections.append(
            ContentSection(
                title=title,
                body=body,
                source_file=source_file,
                section_index=len(sections),
            )
        )

    return sections
