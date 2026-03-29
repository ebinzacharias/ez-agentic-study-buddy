import React from "react";
import ReactMarkdown from "react-markdown";
import MaterialPreview from "./MaterialPreview";

export default function TeachStep({
  selectedConcept,
  teachContext,
  teachResult,
  planResult,
  uploadResult,
  loading,
  onConceptChange,
  onContextChange,
  onTeach,
}) {
  return (
    <div className="learn-environment">
      <header className="learn-environment__intro">
        <h3 className="learn-environment__heading">Learn</h3>
        <p className="learn-environment__lede text-muted text-sm">
          Deep focus: structured notes alongside your original material.
        </p>
      </header>

      <div className="card card--stage learn-environment__toolbar">
        <div className="row">
          <div className="field">
            <label htmlFor="teach-concept">Concept</label>
            {planResult ? (
              <select
                id="teach-concept"
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
                id="teach-concept"
                value={selectedConcept}
                onChange={(e) => onConceptChange(e.target.value)}
                placeholder="e.g., LangGraph Nodes"
              />
            )}
          </div>
          <div className="field actions field--primary-action">
            <label>&nbsp;</label>
            <button
              type="button"
              onClick={onTeach}
              disabled={!selectedConcept.trim() || loading}
            >
              Learn concept
            </button>
          </div>
        </div>
        <div className="field">
          <label htmlFor="teach-context">Context (optional)</label>
          <textarea
            id="teach-context"
            value={teachContext}
            onChange={(e) => onContextChange(e.target.value)}
            placeholder="What do you already know? Where did you get stuck?"
          />
        </div>
      </div>

      <div className="learn-environment__split">
        <div className="learn-environment__notes">
          {teachResult ? (
            <div className="result result--teach learn-environment__notes-card">
              <h2 className="result__title">Notes · {teachResult.concept_name}</h2>
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
            </div>
          ) : (
            <div className="learn-environment__placeholder card card--stage">
              <p className="text-muted">
                Choose a concept and select <strong>Learn concept</strong> to see AI-generated
                notes here. Your source file stays on the right for cross-reference.
              </p>
            </div>
          )}
        </div>
        <div className="learn-environment__source">
          {uploadResult ? (
            <MaterialPreview
              uploadResult={uploadResult}
              variant="sourcePanel"
              className="learn-environment__material"
            />
          ) : (
            <div className="learn-environment__placeholder card card--stage">
              <p className="text-muted text-sm">No material preview available.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
