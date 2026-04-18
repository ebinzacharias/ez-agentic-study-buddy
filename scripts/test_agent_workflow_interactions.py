from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

pytest.importorskip("fastapi", reason="fastapi not installed (web extras required)")

from fastapi.testclient import TestClient  # noqa: E402

from agent.core.state import DifficultyLevel, StudySessionState  # noqa: E402
from webapi import main as webmain  # noqa: E402


def _seed_session(session_id: str = "test-session") -> str:
    state = StudySessionState(session_id=session_id, topic="Agentic Frameworks")
    state.overall_difficulty = DifficultyLevel.BEGINNER
    state.set_loaded_content({"raw_text": "Agent, orchestrator, tools, evaluator."})
    state.concepts_planned = ["Agent Basics"]
    state.add_concept("Agent Basics", DifficultyLevel.BEGINNER)
    state.set_current_concept("Agent Basics")
    webmain.SESSIONS[session_id] = state
    return session_id


def _client() -> TestClient:
    return TestClient(webmain.app)


def test_teach_returns_next_action_generate_quiz(monkeypatch) -> None:
    webmain.SESSIONS.clear()
    sid = _seed_session("teach-next-action")

    monkeypatch.setattr(
        webmain,
        "teach_concept_payload",
        lambda **kwargs: {
            "explanation": "Teaching content",
            "takeaways": ["Takeaway one", "Takeaway two"],
            "estimated_read_minutes": 2,
        },
    )

    client = _client()
    resp = client.post(
        f"/session/{sid}/teach",
        json={
            "concept_name": "Agent Basics",
            "difficulty_level": "beginner",
            "context": "",
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["concept_name"] == "Agent Basics"
    assert data["explanation"] == "Teaching content"
    assert data["takeaways"] == ["Takeaway one", "Takeaway two"]
    assert data["estimated_read_minutes"] == 2
    assert "next_action" in data
    assert data["next_action"]["action"] == "generate_quiz"


def test_evaluate_low_score_recommends_reteach(monkeypatch) -> None:
    webmain.SESSIONS.clear()
    sid = _seed_session("evaluate-reteach")

    # Concept is taught before quiz evaluation path
    webmain.SESSIONS[sid].mark_concept_taught("Agent Basics")

    monkeypatch.setattr(
        webmain,
        "evaluate_response",
        SimpleNamespace(invoke=lambda payload: {
            "total_questions": 2,
            "questions_evaluated": 2,
            "scores": [],
            "total_score": 0.8,
            "average_score": 0.4,
            "overall_percentage": 40.0,
        }),
    )

    client = _client()
    quiz_data = {
        "concept_name": "Agent Basics",
        "questions": [
            {"question_number": 1, "question_type": "multiple_choice", "correct_answer": "A"},
            {"question_number": 2, "question_type": "multiple_choice", "correct_answer": "B"},
        ],
    }
    learner_answers = {"answers": [{"question_number": 1, "answer": "X"}]}

    resp = client.post(
        f"/session/{sid}/evaluate",
        json={
            "quiz_data": json.dumps(quiz_data),
            "learner_answers": json.dumps(learner_answers),
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_percentage"] == 40.0
    assert data["next_action"]["action"] == "teach_concept"


def test_session_expired_returns_410_with_error_code() -> None:
    webmain.SESSIONS.clear()
    client = _client()

    resp = client.post(
        "/session/missing-session/evaluate",
        json={"quiz_data": "{}", "learner_answers": "{}"},
    )

    assert resp.status_code == 410
    data = resp.json()
    assert data["error_code"] == "session_expired"


def test_quiz_invalid_format_surfaces_error_code(monkeypatch) -> None:
    webmain.SESSIONS.clear()
    sid = _seed_session("quiz-invalid-format")

    monkeypatch.setattr(
        webmain,
        "generate_quiz",
        SimpleNamespace(invoke=lambda payload: {
            "error": "Failed to generate valid multiple-choice questions with options.",
            "error_code": "invalid_quiz_format",
        }),
    )

    client = _client()
    resp = client.post(
        f"/session/{sid}/quiz",
        json={
            "concept_name": "Agent Basics",
            "difficulty_level": "beginner",
            "num_questions": 3,
            "question_types": "multiple_choice",
        },
    )

    assert resp.status_code == 503
    data = resp.json()
    assert data["error_code"] == "invalid_quiz_format"

