import React from "react";

export default function TeachStep({
  selectedConcept,
  teachContext,
  teachResult,
  planResult,
  loading,
  onConceptChange,
  onContextChange,
  onTeach,
}) {
  return (
    <>
      <div className="card">
        <div className="row">
          <div className="field">
            <label>Concept</label>
            {planResult ? (
              <select
                value={selectedConcept}
                onChange={(e) => onConceptChange(e.target.value)}
              >
                <option value="">Select a concept</option>
                {planResult.concepts.map((c) => (
                  <option key={c.concept_name} value={c.concept_name}>
                    {c.concept_name}
                  </option>
                ))}
              </select>
            ) : (
              <input
                value={selectedConcept}
                onChange={(e) => onConceptChange(e.target.value)}
                placeholder="e.g., LangGraph Nodes"
              />
            )}
          </div>
          <div className="field actions">
            <label>&nbsp;</label>
            <button
              type="button"
              onClick={onTeach}
              disabled={!selectedConcept.trim() || loading}
            >
              Teach
            </button>
          </div>
        </div>
        <div className="field">
          <label>Context (optional)</label>
          <textarea
            value={teachContext}
            onChange={(e) => onContextChange(e.target.value)}
            placeholder="What do you already know? Where did you get stuck?"
          />
        </div>
      </div>

      {teachResult && (
        <div className="result">
          <h2>Teaching: {teachResult.concept_name}</h2>
          <pre className="preview">{teachResult.explanation}</pre>
        </div>
      )}
    </>
  );
}
