"""Offline tests for StudySessionState and ConceptProgress models.

No LLM or API key required. Validates state transitions, score
thresholds, progress tracking, and edge cases.
"""

import pytest

from agent.core.state import (
    ConceptProgress,
    ConceptStatus,
    DifficultyLevel,
    StudySessionState,
)


# -- ConceptProgress ---------------------------------------------------------


class TestConceptProgress:
    def test_initial_status_is_not_started(self):
        cp = ConceptProgress(concept_name="Variables")
        assert cp.status == ConceptStatus.NOT_STARTED
        assert cp.score is None
        assert cp.retry_count == 0
        assert cp.quiz_taken is False

    def test_mark_taught_sets_status_and_timestamp(self):
        cp = ConceptProgress(concept_name="Variables")
        cp.mark_taught()
        assert cp.status == ConceptStatus.TAUGHT
        assert cp.taught_at is not None

    def test_quiz_score_above_08_masters(self):
        cp = ConceptProgress(concept_name="Variables")
        cp.mark_taught()
        cp.mark_quizzed(0.85)
        assert cp.status == ConceptStatus.MASTERED
        assert cp.quiz_taken is True
        assert cp.score == 0.85

    def test_quiz_score_between_06_and_08_stays_quizzed(self):
        cp = ConceptProgress(concept_name="Variables")
        cp.mark_taught()
        cp.mark_quizzed(0.7)
        assert cp.status == ConceptStatus.QUIZZED
        assert cp.retry_count == 0

    def test_quiz_score_below_06_triggers_retry(self):
        cp = ConceptProgress(concept_name="Variables")
        cp.mark_taught()
        cp.mark_quizzed(0.4)
        assert cp.status == ConceptStatus.NEEDS_RETRY
        assert cp.retry_count == 1

    def test_reset_for_retry_clears_quiz_state(self):
        cp = ConceptProgress(concept_name="Variables")
        cp.mark_taught()
        cp.mark_quizzed(0.3)
        cp.reset_for_retry()
        assert cp.status == ConceptStatus.IN_PROGRESS
        assert cp.quiz_taken is False
        assert cp.score is None
        assert cp.quizzed_at is None

    def test_boundary_score_08_is_mastered(self):
        cp = ConceptProgress(concept_name="Variables")
        cp.mark_quizzed(0.8)
        assert cp.status == ConceptStatus.MASTERED

    def test_boundary_score_06_is_quizzed(self):
        cp = ConceptProgress(concept_name="Variables")
        cp.mark_quizzed(0.6)
        assert cp.status == ConceptStatus.QUIZZED

    def test_boundary_score_059_is_needs_retry(self):
        cp = ConceptProgress(concept_name="Variables")
        cp.mark_quizzed(0.59)
        assert cp.status == ConceptStatus.NEEDS_RETRY


# -- StudySessionState -------------------------------------------------------


class TestStudySessionState:
    def _make_state(self) -> StudySessionState:
        return StudySessionState(session_id="test-1", topic="Python Basics")

    def test_add_concept(self):
        state = self._make_state()
        state.add_concept("Variables", DifficultyLevel.BEGINNER)
        assert "Variables" in state.concepts
        assert state.concepts["Variables"].difficulty_level == DifficultyLevel.BEGINNER

    def test_add_concept_is_idempotent(self):
        state = self._make_state()
        state.add_concept("Variables", DifficultyLevel.BEGINNER)
        state.concepts["Variables"].mark_taught()
        state.add_concept("Variables", DifficultyLevel.ADVANCED)
        # Should not overwrite
        assert state.concepts["Variables"].status == ConceptStatus.TAUGHT
        assert state.concepts["Variables"].difficulty_level == DifficultyLevel.BEGINNER

    def test_set_current_concept_sets_in_progress(self):
        state = self._make_state()
        state.add_concept("Variables")
        state.set_current_concept("Variables")
        assert state.current_concept == "Variables"
        assert state.concepts["Variables"].status == ConceptStatus.IN_PROGRESS

    def test_set_current_concept_unknown_is_noop(self):
        state = self._make_state()
        state.set_current_concept("Unknown")
        assert state.current_concept is None

    def test_progress_percentage_empty(self):
        state = self._make_state()
        assert state.get_progress_percentage() == 0.0

    def test_progress_percentage_partial(self):
        state = self._make_state()
        state.add_concept("A")
        state.add_concept("B")
        state.mark_concept_quizzed("A", 0.9)
        assert state.get_progress_percentage() == pytest.approx(0.5)

    def test_progress_percentage_all_mastered(self):
        state = self._make_state()
        state.add_concept("A")
        state.add_concept("B")
        state.mark_concept_quizzed("A", 0.9)
        state.mark_concept_quizzed("B", 0.85)
        assert state.get_progress_percentage() == pytest.approx(1.0)

    def test_get_average_score(self):
        state = self._make_state()
        state.add_concept("A")
        state.add_concept("B")
        state.mark_concept_quizzed("A", 0.8)
        state.mark_concept_quizzed("B", 0.6)
        assert state.get_average_score() == pytest.approx(0.7)

    def test_get_average_score_none_when_no_quizzes(self):
        state = self._make_state()
        state.add_concept("A")
        assert state.get_average_score() is None

    def test_concepts_needing_retry(self):
        state = self._make_state()
        state.add_concept("A")
        state.add_concept("B")
        state.mark_concept_quizzed("A", 0.3)
        state.mark_concept_quizzed("B", 0.9)
        assert state.get_concepts_needing_retry() == ["A"]

    def test_content_context_truncation(self):
        state = self._make_state()
        long_text = "x" * 5000
        state.set_loaded_content({"raw_text": long_text})
        context = state.get_content_context(max_chars=100)
        assert len(context) <= 100
