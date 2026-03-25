from __future__ import annotations

import pytest

pytest.importorskip("fastapi", reason="fastapi not installed (web extras required)")

from webapi.main import _looks_like_temp_stem, _suggest_topic  # noqa: E402


def test_looks_like_temp_stem_handles_windows_style_tmp_names() -> None:
    assert _looks_like_temp_stem("tmp4g_qlrpo")
    assert _looks_like_temp_stem("tmpa1b2c3")
    assert _looks_like_temp_stem("tmp-abc123")
    assert not _looks_like_temp_stem("Agentic Frameworks")
    assert not _looks_like_temp_stem("Introduction_to_AI")


def test_suggest_topic_ignores_temp_titles_and_prefers_content_heading() -> None:
    suggested = _suggest_topic(
        titles=["tmp4g_qlrpo"],
        filenames=["real-notes.md"],
        raw_texts=["# Agentic Frameworks and Design\n\nAgents coordinate tools."],
    )
    assert suggested == "Agentic Frameworks and Design"


def test_suggest_topic_falls_back_to_original_filename_when_needed() -> None:
    suggested = _suggest_topic(
        titles=["tmp4g_qlrpo"],
        filenames=["agentic-framework-cheatsheet.pdf"],
        raw_texts=["\n\n"],
    )
    assert suggested == "Agentic Framework Cheatsheet"
