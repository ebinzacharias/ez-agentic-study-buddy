import React from "react";

export default function NextActionBanner({ nextAction, loading, onFollow }) {
  if (!nextAction) return null;

  if (nextAction.action === "session_complete") {
    return (
      <aside className="next-action-banner next-action-complete" aria-live="polite">
        <span className="next-action-icon" aria-hidden="true">&#x1F3C6;</span>
        <span className="sr-only">Session complete. </span>
        <div className="next-action-reason">
          {nextAction.reason || "All concepts mastered. Great work."}
        </div>
      </aside>
    );
  }

  return (
    <aside className="next-action-banner" aria-live="polite">
      <div className="next-action-body">
        <div>
          <span className="sr-only">Suggested next step: </span>
          <div className="next-action-reason">{nextAction.reason}</div>
          {nextAction.concept && (
            <div className="next-action-concept">Concept: {nextAction.concept}</div>
          )}
        </div>
      </div>
      <button
        type="button"
        className="btn-secondary btn-touch"
        onClick={onFollow}
        disabled={loading}
      >
        {nextAction.label}
        <span aria-hidden="true"> →</span>
      </button>
    </aside>
  );
}
