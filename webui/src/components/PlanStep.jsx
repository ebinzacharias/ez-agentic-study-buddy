import React from "react";

export default function PlanStep({
  maxConcepts,
  planResult,
  loading,
  disabled,
  onMaxConceptsChange,
  onPlan,
}) {
  return (
    <div className="card card--stage">
      <div className="row">
        <div className="field">
          <label>Max concepts</label>
          <input
            type="number"
            min="1"
            max="25"
            value={maxConcepts}
            onChange={(e) => onMaxConceptsChange(Number(e.target.value) || 10)}
          />
        </div>
        <div className="field actions field--primary-action">
          <label>&nbsp;</label>
          <button type="button" onClick={onPlan} disabled={disabled || loading}>
            Plan Learning Path
          </button>
        </div>
      </div>
      <div className="hint">
        Uses an LLM &mdash; ensure <code>GROQ_API_KEY</code> is set on the API server.
      </div>
      {planResult && (
        <p className="plan-status" role="status">
          <strong>Path ready.</strong>{" "}
          {planResult.concepts?.length ?? 0} concepts in order — choose one in the
          session panel to teach or quiz.
        </p>
      )}
    </div>
  );
}
