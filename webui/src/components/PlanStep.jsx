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
    <div className="card card--stage card--lab-stage">
      <div className="row">
        <div className="field">
          <label>Max concepts</label>
          <input
            type="number"
            className="input-lab"
            min="1"
            max="25"
            value={maxConcepts}
            onChange={(e) => onMaxConceptsChange(Number(e.target.value) || 10)}
          />
        </div>
        <div className="field actions field--primary-action">
          <label>&nbsp;</label>
          <button
            type="button"
            className="btn-plan-path"
            onClick={onPlan}
            disabled={disabled || loading}
          >
            Plan Learning Path
          </button>
        </div>
      </div>
      <p className="plan-step-hint">
        Uses an LLM &mdash; ensure <code>GROQ_API_KEY</code> is set on the API
        server.
      </p>
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
