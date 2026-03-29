from __future__ import annotations

import pytest

pytest.importorskip("fastapi", reason="fastapi not installed (web extras required)")

from webapi.main import (  # noqa: E402
    _is_low_signal_topic_line,
    _looks_like_temp_stem,
    _looks_substantive_topic,
    _suggest_topic,
)


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


def test_low_signal_page_markers_rejected() -> None:
    assert _is_low_signal_topic_line("1 von 2")
    assert _is_low_signal_topic_line("Page 3 of 12")
    assert _is_low_signal_topic_line("Seite 2 von 10")
    assert not _is_low_signal_topic_line("Agentic Frameworks Overview")
    assert _looks_substantive_topic("Agentic Frameworks Overview")
    assert not _looks_substantive_topic("1 von 2")


def test_suggest_topic_skips_pdf_page_counter_then_uses_next_line() -> None:
    suggested = _suggest_topic(
        titles=["tmpabc12345"],
        filenames=["kalman_filtering.pdf"],
        raw_texts=["1 von 2\n\nState Estimation and Kalman Filters\n\nIntro text here."],
    )
    assert suggested == "State Estimation and Kalman Filters"


def test_suggest_topic_rejects_junk_title_and_uses_body_or_filename() -> None:
    suggested = _suggest_topic(
        titles=["1 von 2"],
        filenames=["course_notes.pdf"],
        raw_texts=["Chapter One: Linear Algebra\n\nMore text."],
    )
    assert suggested == "Chapter One: Linear Algebra"


def test_suggest_topic_page_markers_only_falls_back_to_filename_stem() -> None:
    suggested = _suggest_topic(
        titles=["tmpabc12345"],
        filenames=["course_notes.pdf"],
        raw_texts=["1 von 2\n\n12 / 30\n\n---\n"],
    )
    assert suggested == "Course Notes"
