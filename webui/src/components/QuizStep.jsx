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
      <div className="card card--stage">
        <div className="row">
          <div className="field">
            <label htmlFor="quiz-concept">Quiz concept</label>
            {planResult ? (
              <select
                id="quiz-concept"
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

      {quizResult && (
        <div className="result result--quiz">
          <h2 className="result__title">Quiz: {quizResult.concept_name}</h2>
          {quizResult.questions?.map((q) => (
            <div key={q.question_number} className="quiz-question">
              <p>
                <strong>Question {q.question_number}.</strong> {q.question}
              </p>
              {q.options ? (
                <div className="quiz-options" role="radiogroup" aria-label={`Question ${q.question_number}`}>
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
            className="btn-touch quiz-submit-desktop"
          >
            {loading ? "Evaluating…" : "Submit and evaluate"}
          </button>
        </div>
      )}

      {evalResult && (
        <div className="result result--eval">
          <h2 className="result__title">Results — {evalResult.overall_percentage}%</h2>
          <div className="score-bar" role="progressbar" aria-valuenow={evalResult.overall_percentage} aria-valuemin={0} aria-valuemax={100} aria-label="Score">
            <div
              className="score-fill"
              style={{ width: `${evalResult.overall_percentage}%` }}
            />
          </div>
          <p className="text-muted text-sm">
            {evalResult.questions_evaluated} / {evalResult.total_questions}{" "}
            answered · Score: {evalResult.total_score} /{" "}
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
      )}
    </>
  );
}
