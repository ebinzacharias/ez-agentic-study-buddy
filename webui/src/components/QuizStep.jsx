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
}) {
  return (
    <>
      {/* Quiz controls */}
      <div className="card">
        <div className="row">
          <div className="field">
            <label>Quiz concept</label>
            {planResult ? (
              <select
                value={quizConcept}
                onChange={(e) => onQuizConceptChange(e.target.value)}
              >
                <option value="">— Same as teach concept —</option>
                <option value={topic}>{topic} (entire document)</option>
                {planResult.concepts.map((c) => (
                  <option key={c.concept_name} value={c.concept_name}>
                    {c.concept_name}
                  </option>
                ))}
              </select>
            ) : (
              <input
                value={quizConcept}
                onChange={(e) => onQuizConceptChange(e.target.value)}
                placeholder={selectedConcept || "e.g., LangGraph Nodes"}
              />
            )}
          </div>
          <div className="field">
            <label>Questions</label>
            <input
              type="number"
              min="1"
              max="10"
              value={numQuestions}
              onChange={(e) => onNumQuestionsChange(Number(e.target.value) || 3)}
            />
          </div>
          <div className="field actions">
            <label>&nbsp;</label>
            <button
              type="button"
              onClick={onGenerateQuiz}
              disabled={
                !(quizConcept.trim() || selectedConcept.trim()) || loading
              }
            >
              Generate Quiz
            </button>
          </div>
        </div>
        <div className="row" style={{ marginTop: "0.5rem" }}>
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

      {/* Quiz questions */}
      {quizResult && (
        <div className="result">
          <h2>Quiz: {quizResult.concept_name}</h2>
          {quizResult.questions?.map((q) => (
            <div key={q.question_number} className="quiz-question">
              <p>
                <strong>Q{q.question_number}.</strong> {q.question}
              </p>
              {q.options ? (
                <div className="quiz-options">
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
                <p className="muted" style={{ fontSize: "0.85em" }}>
                  No options available for this question.
                </p>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={onEvaluate}
            disabled={loading}
            style={{ marginTop: "1rem" }}
          >
            {loading ? "Evaluating..." : "Submit & Evaluate"}
          </button>
        </div>
      )}

      {/* Evaluation results */}
      {evalResult && (
        <div className="result">
          <h2>Results &mdash; {evalResult.overall_percentage}%</h2>
          <div className="score-bar">
            <div
              className="score-fill"
              style={{ width: `${evalResult.overall_percentage}%` }}
            />
          </div>
          <p className="muted">
            {evalResult.questions_evaluated} / {evalResult.total_questions}{" "}
            answered &middot; Score: {evalResult.total_score} /{" "}
            {evalResult.total_questions}
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
                <strong>Q{s.question_number}</strong> &mdash; {s.feedback} (
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
      )}
    </>
  );
}
