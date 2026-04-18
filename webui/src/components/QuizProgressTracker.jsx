import React from "react";

function questionStatus(q, quizAnswers, quizCheckByQuestion, scoreFor) {
  const answered = !!(quizAnswers[q.question_number] || "").trim();
  const scored = scoreFor(q.question_number);
  const checkedLocal = quizCheckByQuestion[q.question_number];

  if (scored) {
    return {
      statusClass: scored.is_correct ? "is-correct" : "is-incorrect",
      statusLabel: scored.is_correct ? "Correct" : "Review",
    };
  }
  if (checkedLocal === true) {
    return { statusClass: "is-correct", statusLabel: "Correct" };
  }
  if (checkedLocal === false) {
    return { statusClass: "is-incorrect", statusLabel: "Incorrect" };
  }
  if (answered) {
    return { statusClass: "is-answered", statusLabel: "Answered" };
  }
  return { statusClass: "is-pending", statusLabel: "Open" };
}

export default function QuizProgressTracker({
  quizResult,
  quizAnswers,
  quizCheckByQuestion = {},
  evalResult,
  currentQuestionIndex = 0,
  onSelectQuestion,
}) {
  const total = quizResult?.questions?.length ?? 0;
  const answeredCount = quizResult
    ? quizResult.questions.filter(
        (q) => (quizAnswers[q.question_number] || "").trim() !== ""
      ).length
    : 0;
  const remaining = total > 0 ? Math.max(0, total - answeredCount) : null;

  const scoreFor = (qNum) =>
    evalResult?.scores?.find((s) => s.question_number === qNum);

  const canNavigate = !!quizResult && !evalResult && typeof onSelectQuestion === "function";

  return (
    <div className="quiz-progress-tracker card card--rail">
      <h2 className="quiz-progress-tracker__title">Progress</h2>
      {!quizResult ? (
        <p className="quiz-progress-tracker__empty text-muted text-sm">
          After you generate a quiz, this panel tracks each question. Right now: configure
          and press <strong>Generate quiz</strong>.
        </p>
      ) : (
        <>
          <p className="quiz-progress-tracker__summary">
            <strong>
              {evalResult
                ? "Graded"
                : remaining === 0
                  ? "All answered"
                  : `${remaining} left`}
            </strong>
            <span className="text-muted text-sm">
              {" "}
              · {answeredCount} / {total} selected
            </span>
          </p>
          {canNavigate ? (
            <p className="quiz-progress-tracker__hint text-muted text-sm">
              Tap a question to jump back or review before you submit. Green / red after{" "}
              <strong>Check answer</strong>.
            </p>
          ) : null}
          <ol className="quiz-progress-tracker__list" aria-label="Questions">
            {quizResult.questions.map((q, idx) => {
              const { statusClass, statusLabel } = questionStatus(
                q,
                quizAnswers,
                quizCheckByQuestion,
                scoreFor
              );
              const isCurrent = idx === currentQuestionIndex;

              if (!canNavigate) {
                return (
                  <li
                    key={q.question_number}
                    className={`quiz-progress-tracker__item ${statusClass}${
                      isCurrent ? " is-current" : ""
                    }`}
                  >
                    <span className="quiz-progress-tracker__qnum">
                      Q{q.question_number}
                    </span>
                    <span className="quiz-progress-tracker__status">{statusLabel}</span>
                  </li>
                );
              }

              return (
                <li key={q.question_number} className="quiz-progress-tracker__li">
                  <button
                    type="button"
                    className={`quiz-progress-tracker__btn ${statusClass}${
                      isCurrent ? " is-current" : ""
                    }`}
                    aria-current={isCurrent ? "step" : undefined}
                    aria-label={`Question ${q.question_number}, ${statusLabel}`}
                    onClick={() => onSelectQuestion(idx)}
                  >
                    <span className="quiz-progress-tracker__qnum">
                      Q{q.question_number}
                    </span>
                    <span className="quiz-progress-tracker__status">{statusLabel}</span>
                  </button>
                </li>
              );
            })}
          </ol>
        </>
      )}
    </div>
  );
}
