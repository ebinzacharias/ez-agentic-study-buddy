import React from "react";

export default function NextActionBanner({ nextAction, loading, onFollow }) {
  if (!nextAction) return null;

  if (nextAction.action === "session_complete") {
    return (
      <div className="next-action-banner next-action-complete">
        <span className="next-action-icon">&#x1F3C6;</span>
        <div className="next-action-reason">
          {nextAction.reason || "All concepts mastered! Great work."}
        </div>
      </div>
    );
  }

  return (
    <div className="next-action-banner">
      <div className="next-action-body">
        <span className="next-action-icon">&#x1F916;</span>
        <div>
          <div className="next-action-reason">{nextAction.reason}</div>
          {nextAction.concept && (
            <div className="next-action-concept">{nextAction.concept}</div>
          )}
        </div>
      </div>
      <button
        type="button"
        className="btn-secondary"
        onClick={onFollow}
        disabled={loading}
      >
        {nextAction.label} &rarr;
      </button>
    </div>
  );
}
