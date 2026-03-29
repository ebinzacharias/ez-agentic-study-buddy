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
    <>
      <div className="card">
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
          <div className="field actions">
            <label>&nbsp;</label>
            <button type="button" onClick={onPlan} disabled={disabled || loading}>
              Plan Learning Path
            </button>
          </div>
        </div>
        <div className="hint">
          Uses an LLM &mdash; ensure <code>GROQ_API_KEY</code> is set.
        </div>
      </div>

      {planResult && (
        <div className="result">
          <h2>Learning Path</h2>
          <ul>
            {planResult.concepts?.map((c) => (
              <li key={`${c.order}-${c.concept_name}`}>
                {c.order}. {c.concept_name}
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}
