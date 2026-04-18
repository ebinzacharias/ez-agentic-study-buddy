import React, { useState, useEffect, useRef } from "react";

export default function QuizStep({
  topic,
  quizConcept,
  selectedConcept,
  numQuestions,
  difficulty,
  quizResult,
  quizAnswers,
  evalResult,
  planResult,
  loading,
  onQuizConceptChange,
  onNumQuestionsChange,
  onDifficultyChange,
  onAnswerChange,
  onGenerateQuiz,
  onEvaluate,
  onStartNewQuiz,
  currentQuestionIndex,
  onCurrentQuestionIndexChange,
  quizCheckByQuestion = {},
  onQuizCheckByQuestionChange,
}) {
  const phase =
    evalResult != null ? "results" : quizResult != null ? "active" : "setup";

  const MIN_Q = 5;
  const MAX_Q = 10;
  const stepQ = (delta) => {
    const next = Math.min(MAX_Q, Math.max(MIN_Q, numQuestions + delta));
    onNumQuestionsChange(next);
  };

  const [questionCountDraft, setQuestionCountDraft] = useState(null);

  useEffect(() => {
    setQuestionCountDraft(null);
  }, [numQuestions]);

  const questionCountDisplay =
    questionCountDraft !== null ? questionCountDraft : String(numQuestions);

  const commitQuestionCount = () => {
    const raw = questionCountDraft !== null ? questionCountDraft : String(numQuestions);
    const v = parseInt(raw, 10);
    const clamped = Math.min(
      MAX_Q,
      Math.max(MIN_Q, Number.isFinite(v) ? v : numQuestions)
    );
    onNumQuestionsChange(clamped);
    setQuestionCountDraft(null);
  };

  const currentQIdx = currentQuestionIndex ?? 0;
  const checked = quizCheckByQuestion;
  const [stepAnnouncement, setStepAnnouncement] = useState("");
  const nextBtnRef = useRef(null);

  const setCurrentQIdx = onCurrentQuestionIndexChange ?? (() => {});

  const questions = quizResult?.questions ?? [];
  const safeIdx = Math.min(Math.max(0, currentQIdx), Math.max(0, questions.length - 1));
  const currentQ = questions.length ? questions[safeIdx] : undefined;

  useEffect(() => {
    if (!onCurrentQuestionIndexChange || questions.length === 0) return;
    if (currentQIdx !== safeIdx) {
      onCurrentQuestionIndexChange(safeIdx);
    }
  }, [
    questions.length,
    currentQIdx,
    safeIdx,
    onCurrentQuestionIndexChange,
  ]);
  const isChecked = currentQ ? checked[currentQ.question_number] !== undefined : false;
  const isCorrectAnswer = currentQ ? checked[currentQ.question_number] === true : false;
  const hasAnswer = currentQ ? !!quizAnswers[currentQ.question_number] : false;
  const isLastQ = questions.length > 0 && safeIdx === questions.length - 1;

  const headingId = currentQ ? `quiz-active-heading-${currentQ.question_number}` : "";
  const promptId = currentQ ? `quiz-active-prompt-${currentQ.question_number}` : "";
  const radiogroupLabelledBy =
    headingId && promptId ? `${headingId} ${promptId}` : undefined;

  useEffect(() => {
    if (phase !== "active" || questions.length === 0) {
      setStepAnnouncement("");
      return;
    }
    setStepAnnouncement(`Question ${safeIdx + 1} of ${questions.length}`);
  }, [phase, safeIdx, questions.length]);

  // After "Check answer", move focus to the primary action (Next / See results).
  useEffect(() => {
    if (phase !== "active" || !currentQ || !isChecked) return;
    const id = window.requestAnimationFrame(() => {
      nextBtnRef.current?.focus({ preventScroll: true });
    });
    return () => window.cancelAnimationFrame(id);
  }, [phase, currentQ?.question_number, isChecked]);

  // After advancing to another question, move focus to the first choice.
  useEffect(() => {
    if (phase !== "active" || !currentQ) return;
    const id = window.requestAnimationFrame(() => {
      const first = document.querySelector(
        `input[type="radio"][name="q${currentQ.question_number}"]`
      );
      first?.focus({ preventScroll: true });
    });
    return () => window.cancelAnimationFrame(id);
  }, [phase, safeIdx, currentQ?.question_number]);

  const handleCheck = () => {
    if (!currentQ || !hasAnswer || !onQuizCheckByQuestionChange) return;
    const userAnswer = quizAnswers[currentQ.question_number];
    const correct = userAnswer === currentQ.correct_answer;
    onQuizCheckByQuestionChange((prev) => ({
      ...prev,
      [currentQ.question_number]: correct,
    }));
  };

  const handleNext = () => {
    if (isLastQ) {
      onEvaluate();
    } else {
      setCurrentQIdx(safeIdx + 1);
    }
  };

  return (
    <div className="quiz-environment">
      <div className="quiz-environment__inner">

        {/* ── Setup phase ── */}
        {phase === "setup" && (
          <div className="card card--stage quiz-environment__setup">
            <h3 className="quiz-environment__heading">Quiz</h3>

            <div className="quiz-setup">
              {/* Concept — full width */}
              <div className="quiz-setup__concept">
                <label htmlFor="quiz-concept">Concept</label>
                {planResult ? (
                  <select
                    id="quiz-concept"
                    value={quizConcept}
                    onChange={(e) => onQuizConceptChange(e.target.value)}
                  >
                    <option value="">— Same as in Learn —</option>
                    <option value={topic}>{topic} (entire document)</option>
                    {planResult.concepts.map((c) => (
                      <option key={c.concept_name} value={c.concept_name}>
                        {c.concept_name}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    id="quiz-concept"
                    value={quizConcept}
                    onChange={(e) => onQuizConceptChange(e.target.value)}
                    placeholder={selectedConcept || "e.g., LangGraph Nodes"}
                  />
                )}
              </div>

              {/* Questions + Depth — side by side */}
              <div className="quiz-setup__options">
                <div className="quiz-setup__field">
                  <label htmlFor="quiz-num-questions">
                    Questions
                    <span className="sr-only">
                      {" "}
                      ({MIN_Q}–{MAX_Q})
                    </span>
                  </label>
                  <div className="quiz-q-stepper">
                    <button
                      type="button"
                      className="quiz-q-stepper__btn"
                      aria-label="Fewer questions"
                      disabled={loading || numQuestions <= MIN_Q}
                      onClick={() => stepQ(-1)}
                    >
                      −
                    </button>
                    <input
                      id="quiz-num-questions"
                      className="quiz-q-stepper__value"
                      type="text"
                      inputMode="numeric"
                      autoComplete="off"
                      disabled={loading}
                      value={questionCountDisplay}
                      onChange={(e) =>
                        setQuestionCountDraft(e.target.value.replace(/[^\d]/g, ""))
                      }
                      onBlur={commitQuestionCount}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") e.currentTarget.blur();
                      }}
                    />
                    <button
                      type="button"
                      className="quiz-q-stepper__btn"
                      aria-label="More questions"
                      disabled={loading || numQuestions >= MAX_Q}
                      onClick={() => stepQ(+1)}
                    >
                      +
                    </button>
                  </div>
                </div>

                <div className="quiz-setup__field">
                  <label htmlFor="quiz-depth">Depth</label>
                  <select
                    id="quiz-depth"
                    value={difficulty}
                    onChange={(e) => onDifficultyChange(e.target.value)}
                    disabled={loading}
                  >
                    <option value="beginner">Essentials</option>
                    <option value="intermediate">In-depth</option>
                    <option value="advanced">Expert</option>
                  </select>
                </div>
              </div>

              {/* Generate button — full width */}
              <button
                type="button"
                className="quiz-setup__generate"
                onClick={onGenerateQuiz}
                disabled={!(quizConcept.trim() || selectedConcept.trim()) || loading}
              >
                {loading ? "Generating…" : "Generate quiz"}
              </button>
            </div>

            <div className="hint">
              Questions are grounded in your uploaded material.
            </div>
          </div>
        )}

        {/* ── Active phase — one question at a time ── */}
        {phase === "active" && currentQ && (
          <div className="quiz-one">
            <div className="sr-only" aria-live="polite" aria-atomic="true">
              {stepAnnouncement}
            </div>

            {/* Progress bar — dots + counter are visual only; step is announced via live region */}
            <div className="quiz-one__progress" aria-hidden="true">
              <div className="quiz-one__progress-dots">
                {questions.map((q, i) => (
                  <span
                    key={q.question_number}
                    className={`quiz-one__dot${i === safeIdx ? " quiz-one__dot--active" : ""}${checked[q.question_number] !== undefined ? (checked[q.question_number] ? " quiz-one__dot--correct" : " quiz-one__dot--wrong") : ""}`}
                    aria-hidden="true"
                  />
                ))}
              </div>
              <span className="quiz-one__counter">
                {safeIdx + 1} / {questions.length}
              </span>
            </div>

            {/* Question card */}
            <div className="quiz-question-card quiz-question-card--single">
              <h2 id={headingId} className="quiz-question-card__num">
                Question {safeIdx + 1} of {questions.length}
              </h2>
              <p id={promptId} className="quiz-question-card__prompt">
                {currentQ.question}
              </p>

              {currentQ.options && (
                <div
                  className="quiz-options"
                  role="radiogroup"
                  aria-labelledby={radiogroupLabelledBy}
                >
                  {currentQ.options.map((opt, i) => {
                    const isSelected = quizAnswers[currentQ.question_number] === opt;
                    const isCorrectOpt = opt === currentQ.correct_answer;
                    let cls = "quiz-option";
                    if (isChecked) {
                      if (isCorrectOpt) cls += " quiz-option--correct";
                      else if (isSelected) cls += " quiz-option--incorrect";
                      cls += " quiz-option--locked";
                    } else if (isSelected) {
                      cls += " quiz-option--selected";
                    }
                    return (
                      <label key={i} className={cls}>
                        <input
                          type="radio"
                          name={`q${currentQ.question_number}`}
                          value={opt}
                          checked={isSelected}
                          onChange={() => !isChecked && onAnswerChange(currentQ.question_number, opt)}
                          disabled={isChecked}
                        />
                        <span className="quiz-option__text">{opt}</span>
                        {isChecked && isCorrectOpt && (
                          <span className="quiz-option__badge quiz-option__badge--correct" aria-label="Correct answer">✓</span>
                        )}
                        {isChecked && isSelected && !isCorrectOpt && (
                          <span className="quiz-option__badge quiz-option__badge--wrong" aria-label="Wrong answer">✗</span>
                        )}
                      </label>
                    );
                  })}
                </div>
              )}

              {/* Immediate feedback after checking */}
              {isChecked && (
                <div
                  className={`quiz-feedback${isCorrectAnswer ? " quiz-feedback--correct" : " quiz-feedback--wrong"}`}
                  aria-live="polite"
                  aria-atomic="true"
                >
                  <p className="quiz-feedback__verdict">
                    {isCorrectAnswer ? "Correct!" : `Incorrect — correct answer: ${currentQ.correct_answer}`}
                  </p>
                  {currentQ.explanation && (
                    <p className="quiz-feedback__explanation">{currentQ.explanation}</p>
                  )}
                </div>
              )}

              {/* Action buttons */}
              <div className="quiz-one__actions">
                <button
                  type="button"
                  className="btn-secondary quiz-one__change"
                  onClick={onStartNewQuiz}
                  disabled={loading}
                >
                  Change quiz
                </button>
                {!isChecked ? (
                  <button
                    type="button"
                    className="quiz-one__check"
                    onClick={handleCheck}
                    disabled={!hasAnswer || loading}
                  >
                    Check answer
                  </button>
                ) : (
                  <button
                    ref={nextBtnRef}
                    type="button"
                    className="quiz-one__next"
                    onClick={handleNext}
                    disabled={loading}
                  >
                    {isLastQ ? (loading ? "Evaluating…" : "See results") : "Next question"}
                    <svg width="13" height="13" viewBox="0 0 12 12" fill="none" aria-hidden="true">
                      <path d="M2 6h8M7 3l3 3-3 3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ── Results phase ── */}
        {phase === "results" && evalResult && (
          <div className="result result--eval quiz-environment__eval">
            <div className="quiz-environment__eval-head">
              <h2 className="result__title">
                Score — {evalResult.overall_percentage}%
              </h2>
              <button
                type="button"
                className="btn-secondary quiz-environment__new-quiz-btn"
                onClick={onStartNewQuiz}
                disabled={loading}
              >
                New quiz
              </button>
            </div>
            <progress
              className="score-bar score-bar--progress"
              value={evalResult.overall_percentage}
              max={100}
              aria-label="Score"
            />
            <p className="text-muted text-sm">
              {evalResult.questions_evaluated} / {evalResult.total_questions} answered · Score:{" "}
              {evalResult.total_score} / {evalResult.total_questions}
            </p>
            {evalResult.scores?.map((s) => {
              const q = quizResult?.questions?.find(
                (qq) => qq.question_number === s.question_number
              );
              return (
                <div
                  key={s.question_number}
                  className={`eval-item ${s.is_correct ? "correct" : "incorrect"}`}
                >
                  <strong>Q{s.question_number}</strong> — {s.feedback}
                  {!s.is_correct && q?.correct_answer && (
                    <div className="correct-answer">
                      Correct answer: <em>{q.correct_answer}</em>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

      </div>
    </div>
  );
}
