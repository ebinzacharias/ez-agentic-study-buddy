from __future__ import annotations

import json
from types import SimpleNamespace

from agent.tools import quizzer_tool


class _FakeLLM:
    def __init__(self, responses: list[str]):
        self._responses = responses
        self._idx = 0

    def invoke(self, prompt: str):
        if self._idx >= len(self._responses):
            payload = self._responses[-1]
        else:
            payload = self._responses[self._idx]
        self._idx += 1
        return SimpleNamespace(content=payload)


def test_generate_quiz_recovers_from_invalid_first_response(monkeypatch) -> None:
    invalid = json.dumps(
        {
            "concept_name": "Agent Basics",
            "difficulty_level": "beginner",
            "questions": [
                {
                    "question_number": 1,
                    "question_type": "multiple_choice",
                    "question": "What is an agent?",
                    "options": None,
                    "correct_answer": "Autonomous entity",
                    "explanation": "",
                }
            ],
            "total_questions": 1,
        }
    )
    valid = json.dumps(
        {
            "concept_name": "Agent Basics",
            "difficulty_level": "beginner",
            "questions": [
                {
                    "question_number": 1,
                    "question_type": "multiple_choice",
                    "question": "What is an agent?",
                    "options": ["A tool", "An autonomous system", "A UI", "A file"],
                    "correct_answer": "An autonomous system",
                    "explanation": "",
                },
                {
                    "question_number": 2,
                    "question_type": "multiple_choice",
                    "question": "What does an orchestrator do?",
                    "options": ["Stores files", "Coordinates steps", "Renders CSS", "Compiles code"],
                    "correct_answer": "Coordinates steps",
                    "explanation": "",
                },
            ],
            "total_questions": 2,
        }
    )

    fake_llm = _FakeLLM([invalid, valid])
    monkeypatch.setattr(quizzer_tool, "get_llm_client", lambda: fake_llm)
    monkeypatch.setattr(quizzer_tool, "call_with_retry", lambda fn, *a, **k: fn(*a))

    result = quizzer_tool.generate_quiz.invoke(
        {
            "concept_name": "Agent Basics",
            "difficulty_level": "beginner",
            "num_questions": 2,
            "question_types": "multiple_choice",
            "source_material": "Agent = autonomous system that decides and acts.",
        }
    )

    assert "error" not in result
    assert result["total_questions"] == 2
    assert len(result["questions"]) == 2
    for question in result["questions"]:
        assert question["question_type"] == "multiple_choice"
        assert isinstance(question["options"], list)
        assert len(question["options"]) == 4
        assert question["correct_answer"] in question["options"]


def test_generate_quiz_returns_invalid_format_error_when_all_attempts_bad(monkeypatch) -> None:
    always_bad = json.dumps(
        {
            "concept_name": "Agent Basics",
            "difficulty_level": "beginner",
            "questions": [
                {
                    "question_number": 1,
                    "question_type": "short_answer",
                    "question": "Explain agent.",
                    "options": None,
                    "correct_answer": "An autonomous system",
                    "explanation": "",
                }
            ],
            "total_questions": 1,
        }
    )

    fake_llm = _FakeLLM([always_bad, always_bad, always_bad])
    monkeypatch.setattr(quizzer_tool, "get_llm_client", lambda: fake_llm)
    monkeypatch.setattr(quizzer_tool, "call_with_retry", lambda fn, *a, **k: fn(*a))

    result = quizzer_tool.generate_quiz.invoke(
        {
            "concept_name": "Agent Basics",
            "difficulty_level": "beginner",
            "num_questions": 2,
            "question_types": "multiple_choice",
            "source_material": "Agent basics",
        }
    )

    assert result["total_questions"] == 0
    assert result["error_code"] == "invalid_quiz_format"
    assert "valid multiple-choice" in result["error"].lower()

