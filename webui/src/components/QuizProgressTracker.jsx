import React from "react";

export default function QuizProgressTracker({
  quizResult,
  quizAnswers,
  evalResult,
  numQuestions,
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
          <ol className="quiz-progress-tracker__list" aria-label="Questions">
            {quizResult.questions.map((q) => {
              const answered = !!(quizAnswers[q.question_number] || "").trim();
              const scored = scoreFor(q.question_number);
              let statusClass = "is-pending";
              if (scored) {
                statusClass = scored.is_correct ? "is-correct" : "is-incorrect";
              } else if (answered) {
                statusClass = "is-answered";
              }
              return (
                <li
                  key={q.question_number}
                  className={`quiz-progress-tracker__item ${statusClass}`}
                >
                  <span className="quiz-progress-tracker__qnum">
                    Q{q.question_number}
                  </span>
                  <span className="quiz-progress-tracker__status">
                    {scored
                      ? scored.is_correct
                        ? "Correct"
                        : "Review"
                      : answered
                        ? "Answered"
                        : "Open"}
                  </span>
                </li>
              );
            })}
          </ol>
        </>
      )}
    </div>
  );
}
