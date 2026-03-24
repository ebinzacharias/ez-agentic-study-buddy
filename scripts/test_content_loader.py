"""
Test script for the Content Loader utility.

Tests loading .txt, .md, and .json files, auto-detection,
error handling, and state integration.
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.utils.content_loader import (  # noqa: E402
    ContentSection,
    LoadedContent,
    SUPPORTED_EXTENSIONS,
    load_content,
    load_json_file,
    load_markdown_file,
    load_text_file,
)
from agent.core.state import StudySessionState  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures — tiny temp files
# ---------------------------------------------------------------------------

def _create_temp(content: str, suffix: str) -> str:
    """Write *content* to a temp file and return its path."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.write(fd, content.encode("utf-8"))
    os.close(fd)
    return path


SAMPLE_TXT = """\
Introduction to Python

Python is a high-level, interpreted programming language known for its
readability and simplicity.  It was created by Guido van Rossum and first
released in 1991.

Variables and Data Types

Variables in Python do not need explicit declaration.  Python supports
several built-in data types including int, float, str, list, dict, and bool.

Control Flow

Python uses if/elif/else for conditional execution and for/while for loops.
Indentation is significant in Python and defines code blocks.
"""

SAMPLE_MD = """\
# Machine Learning Fundamentals

An overview of core ML concepts.

## Supervised Learning

Supervised learning uses labelled data to train models.  Common algorithms
include linear regression, decision trees, and support vector machines.

## Unsupervised Learning

Unsupervised learning finds patterns in unlabelled data.  Clustering and
dimensionality reduction are typical tasks.

### K-Means Clustering

K-Means partitions data into K clusters by minimising intra-cluster variance.
"""

SAMPLE_JSON = json.dumps({
    "title": "Data Structures 101",
    "sections": [
        {"title": "Arrays", "body": "An array stores elements in contiguous memory locations."},
        {"title": "Linked Lists", "body": "A linked list stores elements as nodes with pointers."},
        {"title": "Hash Tables", "body": "Hash tables map keys to values via a hash function."},
    ],
})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_load_text_file() -> None:
    path = _create_temp(SAMPLE_TXT, ".txt")
    try:
        content = load_text_file(path)
        assert isinstance(content, LoadedContent)
        assert content.metadata["format"] == "text"
        assert content.total_word_count() > 0
        assert len(content.sections) >= 1
        print(f"  [PASS] load_text_file -> {len(content.sections)} sections, "
              f"{content.total_word_count()} words")
    finally:
        os.unlink(path)


def test_load_markdown_file() -> None:
    path = _create_temp(SAMPLE_MD, ".md")
    try:
        content = load_markdown_file(path)
        assert isinstance(content, LoadedContent)
        assert content.metadata["format"] == "markdown"
        titles = content.get_section_titles()
        assert "Supervised Learning" in titles
        assert "Unsupervised Learning" in titles
        print(f"  [PASS] load_markdown_file -> {len(content.sections)} sections, "
              f"titles: {titles}")
    finally:
        os.unlink(path)


def test_load_json_file() -> None:
    path = _create_temp(SAMPLE_JSON, ".json")
    try:
        content = load_json_file(path)
        assert isinstance(content, LoadedContent)
        assert content.title == "Data Structures 101"
        assert len(content.sections) == 3
        assert content.sections[0].title == "Arrays"
        print(f"  [PASS] load_json_file -> {len(content.sections)} sections, "
              f"title: {content.title}")
    finally:
        os.unlink(path)


def test_auto_detect_loader() -> None:
    """load_content() should pick the right loader based on extension."""
    path = _create_temp(SAMPLE_MD, ".md")
    try:
        content = load_content(path)
        assert content.metadata["format"] == "markdown"
        print(f"  [PASS] load_content auto-detect (.md) -> format={content.metadata['format']}")
    finally:
        os.unlink(path)


def test_unsupported_extension() -> None:
    path = _create_temp("hello", ".xyz")
    try:
        try:
            load_content(path)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unsupported file type" in str(e)
            print(f"  [PASS] Unsupported extension raises ValueError: {e}")
    finally:
        os.unlink(path)


def test_file_not_found() -> None:
    try:
        load_content("/nonexistent/path/file.txt")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        print("  [PASS] Missing file raises FileNotFoundError")


def test_content_section_model() -> None:
    section = ContentSection(
        title="Test",
        body="This is a test section with several words in it.",
        source_file="test.txt",
        section_index=0,
    )
    assert section.word_count() == 10
    print(f"  [PASS] ContentSection word_count = {section.word_count()}")


def test_loaded_content_summary_truncation() -> None:
    long_text = "word " * 1000
    content = LoadedContent(
        title="Long",
        source_file="long.txt",
        raw_text=long_text,
    )
    summary = content.get_summary_context(max_chars=100)
    assert len(summary) < len(long_text)
    assert summary.endswith("[... content truncated ...]")
    print(f"  [PASS] get_summary_context truncates at max_chars "
          f"({len(summary)} < {len(long_text)})")


def test_state_integration() -> None:
    """StudySessionState can store and query loaded content."""
    path = _create_temp(SAMPLE_TXT, ".txt")
    try:
        content = load_content(path)
        state = StudySessionState(session_id="test-1", topic="Python")

        assert not state.has_loaded_content()

        state.set_loaded_content(content.model_dump())

        assert state.has_loaded_content()
        ctx = state.get_content_context(max_chars=200)
        assert len(ctx) > 0
        print(f"  [PASS] State integration: has_loaded_content={state.has_loaded_content()}, "
              f"context preview={ctx[:60]}...")
    finally:
        os.unlink(path)


def test_supported_extensions_constant() -> None:
    assert ".txt" in SUPPORTED_EXTENSIONS
    assert ".md" in SUPPORTED_EXTENSIONS
    assert ".pdf" in SUPPORTED_EXTENSIONS
    assert ".json" in SUPPORTED_EXTENSIONS
    print(f"  [PASS] SUPPORTED_EXTENSIONS = {sorted(SUPPORTED_EXTENSIONS)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Content Loader — Test Suite")
    print("=" * 60)

    tests = [
        test_load_text_file,
        test_load_markdown_file,
        test_load_json_file,
        test_auto_detect_loader,
        test_unsupported_extension,
        test_file_not_found,
        test_content_section_model,
        test_loaded_content_summary_truncation,
        test_state_integration,
        test_supported_extensions_constant,
    ]

    passed = 0
    failed = 0
    for fn in tests:
        print(f"\n>> {fn.__name__}")
        try:
            fn()
            passed += 1
        except Exception as exc:
            failed += 1
            print(f"  [FAIL] {exc}")

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    print("=" * 60)
