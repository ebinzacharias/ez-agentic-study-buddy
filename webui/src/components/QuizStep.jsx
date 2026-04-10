import React from "react";

export default function QuizStep({
  topic,
  quizConcept,
  selectedConcept,
  numQuestions,
  quizResult,
  quizAnswers,
  evalResult,
  planResult,
  loading,
  onQuizConceptChange,
  onNumQuestionsChange,
  onAnswerChange,
  onGenerateQuiz,
  onEvaluate,
  onSetQuizConcept,
  onStartNewQuiz,
}) {
  const phase =
    evalResult != null ? "results" : quizResult != null ? "active" : "setup";

  return (
    <div className="quiz-environment">
      <div className="quiz-environment__inner">
        {phase === "setup" ? (
          <header className="quiz-environment__intro">
            <h3 className="quiz-environment__heading">Quiz</h3>
            <p className="quiz-environment__lede text-muted text-sm">
              Choose scope and question count, then generate. After that, you&apos;ll answer here —
              no duplicate controls.
            </p>
          </header>
        ) : null}

        {phase === "active" ? (
          <header className="quiz-environment__intro quiz-environment__intro--tight">
            <h3 className="quiz-environment__heading">Answer the questions</h3>
            <p className="quiz-environment__lede text-muted text-sm">
              Submit when ready. Use <strong>Change quiz</strong> to pick different settings.
            </p>
          </header>
        ) : null}

        {phase === "results" ? (
          <header className="quiz-environment__intro quiz-environment__intro--tight">
            <h3 className="quiz-environment__heading">Results</h3>
            <p className="quiz-environment__lede text-muted text-sm">
              Review feedback below. Start a new quiz when you&apos;re ready.
            </p>
          </header>
        ) : null}

        {phase === "setup" ? (
          <div className="card card--stage quiz-environment__setup">
            <div className="row">
              <div className="field">
                <label htmlFor="quiz-concept">Quiz concept</label>
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
              <div className="field">
                <label htmlFor="quiz-numq">Questions</label>
                <input
                  id="quiz-numq"
                  type="number"
                  min="1"
                  max="10"
                  value={numQuestions}
                  onChange={(e) => onNumQuestionsChange(Number(e.target.value) || 3)}
                />
              </div>
              <div className="field actions field--primary-action">
                <label className="label-placeholder">&nbsp;</label>
                <button
                  type="button"
                  onClick={onGenerateQuiz}
                  disabled={
                    !(quizConcept.trim() || selectedConcept.trim()) || loading
                  }
                >
                  Generate quiz
                </button>
              </div>
            </div>
            <div className="row row--tight">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => onSetQuizConcept(topic)}
                disabled={!topic || loading}
              >
                Quiz entire document
              </button>
            </div>
            <div className="hint">
              Questions are grounded in your uploaded material. Use{" "}
              <strong>Quiz entire document</strong> to quiz across all content.
            </div>
          </div>
        ) : null}

        {phase === "active" && quizResult ? (
          <div className="quiz-environment__context-bar card card--stage">
            <div className="quiz-environment__context-meta">
              <span className="quiz-environment__context-label">Quiz</span>
              <strong className="quiz-environment__context-value">
                {quizResult.concept_name}
              </strong>
              <span className="quiz-environment__context-sep" aria-hidden>
                ·
              </span>
              <span className="text-muted text-sm">
                {quizResult.questions?.length ?? 0} questions
              </span>
            </div>
            <button
              type="button"
              className="btn-secondary quiz-environment__context-action"
              onClick={onStartNewQuiz}
              disabled={loading}
            >
              Change quiz
            </button>
          </div>
        ) : null}

        {phase === "active" && quizResult ? (
          <div className="result result--quiz quiz-environment__assessment">
            <h2 className="result__title quiz-environment__assessment-title sr-only">
              Questions · {quizResult.concept_name}
            </h2>
            {quizResult.questions?.map((q) => (
              <div key={q.question_number} className="quiz-question-card">
                <p className="quiz-question-card__prompt">
                  <span className="quiz-question-card__num">Q{q.question_number}</span>
                  {q.question}
                </p>
                {q.options ? (
                  <div
                    className="quiz-options"
                    role="radiogroup"
                    aria-label={`Question ${q.question_number}`}
                  >
                    {q.options.map((opt, i) => (
                      <label key={i} className="quiz-option">
                        <input
                          type="radio"
                          name={`q${q.question_number}`}
                          value={opt}
                          checked={quizAnswers[q.question_number] === opt}
                          onChange={() => onAnswerChange(q.question_number, opt)}
                        />
                        {opt}
                      </label>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted text-sm">
                    No options available for this question.
                  </p>
                )}
              </div>
            ))}
            <button
              type="button"
              onClick={onEvaluate}
              disabled={loading}
              className="btn-touch quiz-submit-desktop quiz-environment__submit"
            >
              {loading ? "Evaluating…" : "Submit and evaluate"}
            </button>
          </div>
        ) : null}

        {phase === "results" && evalResult ? (
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
            <div
              className="score-bar"
              role="progressbar"
              aria-valuenow={evalResult.overall_percentage}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label="Score"
            >
              <div
                className="score-fill"
                style={{ width: `${evalResult.overall_percentage}%` }}
              />
            </div>
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
                  <strong>Q{s.question_number}</strong> — {s.feedback} (
                  {Math.round(s.score * 100)}%)
                  {!s.is_correct && q?.correct_answer && (
                    <div className="correct-answer">
                      Correct answer: <em>{q.correct_answer}</em>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : null}
      </div>
    </div>
  );
}
