import React from "react";
import ReactMarkdown from "react-markdown";

export default function TeachStep({
  selectedConcept,
  teachResult,
  loading,
  completed,
  onStartQuiz,
  onMarkComplete,
}) {

  if (!selectedConcept) {
    return (
      <div className="learn-environment learn-environment--empty">
        <div className="learn-empty-state">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M9 18V5l12-2v13" />
            <circle cx="6" cy="18" r="3" />
            <circle cx="18" cy="16" r="3" />
          </svg>
          <p className="learn-empty-state__text">
            Select a concept from the sidebar to start learning.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="learn-environment">
      {/* Lesson card */}
      {loading ? (
        <div className="learn-loading">
          <div className="learn-loading__ring" aria-hidden="true" />
          <p className="learn-loading__label">Loading lesson for <strong>{selectedConcept}</strong>…</p>
        </div>
      ) : teachResult ? (
        <div className="result result--teach learn-environment__notes-card">
          <h2 className="result__title">{teachResult.concept_name}</h2>
          <article className="teach-explanation" aria-label="Lesson explanation">
            <ReactMarkdown
              components={{
                a: ({ node, ...props }) => (
                  <a {...props} target="_blank" rel="noopener noreferrer" />
                ),
              }}
            >
              {teachResult.explanation || "_No explanation text was returned._"}
            </ReactMarkdown>
          </article>

          {/* Card footer — actions */}
          <div className="lesson-footer">
            {onMarkComplete && (
              <button
                type="button"
                className={`lesson-footer__complete-btn ${completed ? "lesson-footer__complete-btn--done" : ""}`}
                onClick={onMarkComplete}
                disabled={loading}
                aria-pressed={completed}
                aria-label={
                  completed
                    ? "Mark this concept as incomplete"
                    : "Mark this concept as complete"
                }
                title={completed ? "Undo if you marked this by mistake" : undefined}
              >
                {completed ? (
                  <>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                      <path d="M20 6L9 17l-5-5" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    Mark incomplete
                  </>
                ) : (
                  "Mark as complete"
                )}
              </button>
            )}
            {onStartQuiz && (
              <button
                type="button"
                className="lesson-footer__quiz-cta"
                onClick={onStartQuiz}
                disabled={loading}
              >
                Test your knowledge
                <svg width="13" height="13" viewBox="0 0 12 12" fill="none" aria-hidden="true">
                  <path d="M2 6h8M7 3l3 3-3 3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="learn-empty-state">
          <p className="learn-empty-state__text">
            Click <strong>Study</strong> on a concept card, or select one in the sidebar.
          </p>
        </div>
      )}
    </div>
  );
}
