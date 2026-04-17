"""Extended offline tests for DecisionRules.

Covers decision paths not in the original test_decision_rules.py:
add_concept trigger, adapt_difficulty, session_complete, retry
strategy rotation, and quizzed-with-passing-score transitions.
"""

from agent.core.decision_rules import DecisionRules
from agent.core.state import StudySessionState


def _state(topic: str = "Python") -> StudySessionState:
    return StudySessionState(session_id="test", topic=topic)


class TestPlanningPhase:
    def test_empty_state_triggers_plan(self):
        state = _state()
        decision = DecisionRules(state).decide_next_action()
        assert decision["action"] == "plan_learning_path"

    def test_planned_but_no_concepts_dict_triggers_add(self):
        """Concepts in planned list but not yet added to state dict."""
        state = _state()
        state.concepts_planned = ["Variables", "Functions"]
        decision = DecisionRules(state).decide_next_action()
        assert decision["action"] == "add_concept"
        assert decision["concept_name"] == "Variables"


class TestTeachQuizCycle:
    def test_untaught_concept_triggers_teach(self):
        state = _state()
        state.concepts_planned = ["Variables"]
        state.add_concept("Variables")
        state.set_current_concept("Variables")
        decision = DecisionRules(state).decide_next_action()
        assert decision["action"] == "teach_concept"

    def test_taught_concept_triggers_quiz(self):
        state = _state()
        state.concepts_planned = ["Variables"]
        state.add_concept("Variables")
        state.set_current_concept("Variables")
        state.mark_concept_taught("Variables")
        decision = DecisionRules(state).decide_next_action()
        assert decision["action"] == "generate_quiz"

    def test_quizzed_passing_moves_to_next(self):
        """Score >= 0.6 but < 0.8: should move to next concept."""
        state = _state()
        state.concepts_planned = ["Variables", "Functions"]
        state.add_concept("Variables")
        state.add_concept("Functions")
        state.set_current_concept("Variables")
        state.mark_concept_taught("Variables")
        state.mark_concept_quizzed("Variables", 0.7)
        decision = DecisionRules(state).decide_next_action()
        assert decision["action"] == "set_current_concept"
        assert decision["concept_name"] == "Functions"

    def test_quizzed_low_score_reteaches(self):
        state = _state()
        state.concepts_planned = ["Variables"]
        state.add_concept("Variables")
        state.set_current_concept("Variables")
        state.mark_concept_taught("Variables")
        state.mark_concept_quizzed("Variables", 0.5)
        # Score < 0.6 -> NEEDS_RETRY -> should reteach
        decision = DecisionRules(state).decide_next_action()
        assert decision["action"] == "teach_concept"


class TestSessionCompletion:
    def test_all_mastered_completes_session(self):
        state = _state()
        state.concepts_planned = ["Variables"]
        state.add_concept("Variables")
        state.set_current_concept("Variables")
        state.mark_concept_taught("Variables")
        state.mark_concept_quizzed("Variables", 0.9)
        decision = DecisionRules(state).decide_next_action()
        assert decision["action"] == "session_complete"

    def test_last_concept_mastered_no_more_to_teach(self):
        state = _state()
        state.concepts_planned = ["A", "B"]
        state.add_concept("A")
        state.add_concept("B")
        state.mark_concept_quizzed("A", 0.9)
        state.mark_concept_quizzed("B", 0.85)
        state.current_concept = "B"
        decision = DecisionRules(state).decide_next_action()
        assert decision["action"] == "session_complete"


class TestRetryAndAdaptation:
    def test_max_retries_triggers_adapt_difficulty(self):
        state = _state()
        state.concepts_planned = ["Variables"]
        state.add_concept("Variables")
        state.set_current_concept("Variables")
        state.mark_concept_taught("Variables")
        # Simulate 3 failed retries
        cp = state.concepts["Variables"]
        cp.mark_quizzed(0.3)       # retry_count = 1, status = NEEDS_RETRY
        cp.retry_count = 3         # Force to max
        decision = DecisionRules(state).decide_next_action()
        assert decision["action"] == "adapt_difficulty"
        assert decision["concept_name"] == "Variables"

    def test_retry_with_available_attempts_reteaches(self):
        state = _state()
        state.concepts_planned = ["Variables"]
        state.add_concept("Variables")
        state.set_current_concept("Variables")
        state.mark_concept_taught("Variables")
        cp = state.concepts["Variables"]
        cp.mark_quizzed(0.3)  # retry_count = 1, NEEDS_RETRY
        decision = DecisionRules(state).decide_next_action()
        assert decision["action"] == "teach_concept"
        assert "retry" in decision["reason"].lower() or "Retrying" in decision["reason"]


class TestNoCurrentConcept:
    def test_no_current_picks_next_untaught(self):
        state = _state()
        state.concepts_planned = ["A", "B"]
        state.add_concept("A")
        state.add_concept("B")
        state.mark_concept_quizzed("A", 0.9)
        # No current_concept set, B is untaught
        state.current_concept = None
        decision = DecisionRules(state).decide_next_action()
        assert decision["action"] == "set_current_concept"
        assert decision["concept_name"] == "B"
