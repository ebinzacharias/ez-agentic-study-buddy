"""Unit tests for teach response JSON parsing (no LLM)."""

import json

from agent.tools.teacher_tool import _parse_teach_json_response


def test_valid_json_round_trip() -> None:
    raw = (
        '{"explanation": "## Hi\\n\\nBody.", '
        '"takeaways": ["One", "Two"], "ignored": true}'
    )
    out = _parse_teach_json_response(raw)
    assert out["explanation"] == "## Hi\n\nBody."
    assert out["takeaways"] == ["One", "Two"]


def test_triple_quoted_explanation_repair() -> None:
    raw = (
        '{\n  "explanation": """## Title\n\nSome **markdown** here.\n""",\n'
        '  "takeaways": ["Alpha", "Beta"]\n}'
    )
    out = _parse_teach_json_response(raw)
    assert out["explanation"].startswith("## Title")
    assert "markdown" in out["explanation"]
    assert not out["explanation"].lstrip().startswith("{")
    assert out["takeaways"] == ["Alpha", "Beta"]


def test_loose_parse_when_trailing_garbage() -> None:
    raw = '{"explanation": "Plain lesson text", "takeaways": ["x"]} trailing junk'
    out = _parse_teach_json_response(raw)
    assert "trailing" not in out["explanation"]
    assert out["takeaways"] == ["x"]


def test_nested_json_string_explanation() -> None:
    inner = '{"explanation": "## Inner\\n\\nOK", "takeaways": []}'
    wrapped = json.dumps({"explanation": inner, "takeaways": ["Keep"]})
    out = _parse_teach_json_response(wrapped)
    assert out["explanation"].startswith("## Inner")
    assert out["takeaways"] == ["Keep"]
