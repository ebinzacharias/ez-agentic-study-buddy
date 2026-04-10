import React, { useEffect, useState } from "react";

function clampConcepts(n) {
  return Math.min(25, Math.max(1, n));
}

export default function PlanStep({
  maxConcepts,
  planResult,
  loading,
  disabled,
  onMaxConceptsChange,
  onPlan,
  onPickConcept,
}) {
  const [draft, setDraft] = useState(String(maxConcepts));

  useEffect(() => {
    setDraft(String(maxConcepts));
  }, [maxConcepts]);

  const handleChange = (e) => {
    const v = e.target.value;
    if (!/^\d*$/.test(v)) return;
    setDraft(v);
    if (v.trim() === "") return;
    const n = parseInt(v, 10);
    if (!Number.isNaN(n)) {
      onMaxConceptsChange(clampConcepts(n));
    }
  };

  const handleBlur = () => {
    const parsed = parseInt(String(draft).trim(), 10);
    if (Number.isNaN(parsed)) {
      const fallback = clampConcepts(maxConcepts);
      onMaxConceptsChange(fallback);
      setDraft(String(fallback));
      return;
    }
    const next = clampConcepts(parsed);
    onMaxConceptsChange(next);
    setDraft(String(next));
  };

  const resolveMaxFromDraft = () => {
    const parsed = parseInt(String(draft).trim(), 10);
    return Number.isNaN(parsed)
      ? clampConcepts(maxConcepts)
      : clampConcepts(parsed);
  };

  const runGenerate = () => {
    const m = resolveMaxFromDraft();
    setDraft(String(m));
    onMaxConceptsChange(m);
    onPlan(m);
  };

  const hasPath = Boolean(planResult?.concepts?.length);

  return (
    <div className="plan-environment">
      <header className="plan-environment__intro">
        <h3 className="plan-environment__heading">Learning path</h3>
        <p className="plan-environment__lede">
          {hasPath
            ? "Your concepts are ordered below. Pick one to study, or regenerate with a different size."
            : "One action builds the ordered list from your upload. The Path tab is navigation only — it does not call the model by itself."}
        </p>
      </header>

      {hasPath ? (
        <section
          className="plan-result card card--stage"
          aria-label="Generated learning path"
        >
          <h4 className="plan-result__title">Concepts ({planResult.concepts.length})</h4>
          <ol className="plan-result__list">
            {planResult.concepts.map((c) => (
              <li key={`${c.order}-${c.concept_name}`} className="plan-result__item">
                <span className="plan-result__order">{c.order}</span>
                <div className="plan-result__body">
                  <span className="plan-result__name">{c.concept_name}</span>
                  {c.difficulty ? (
                    <span className="plan-result__difficulty text-muted text-sm">
                      {c.difficulty}
                    </span>
                  ) : null}
                </div>
                {onPickConcept ? (
                  <button
                    type="button"
                    className="btn-secondary plan-result__learn-btn"
                    onClick={() => onPickConcept(c.concept_name)}
                  >
                    Learn this
                  </button>
                ) : null}
              </li>
            ))}
          </ol>
          <p className="plan-result__rail-note text-muted text-sm">
            The sidebar mirrors this list for quick jumps while you stay in other modes.
          </p>
        </section>
      ) : null}

      {!hasPath ? (
        <div className="card card--stage card--lab-stage plan-environment__generate-card">
          <div className="row">
            <div className="field">
              <label htmlFor="plan-max-concepts">Max concepts</label>
              <input
                id="plan-max-concepts"
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                className="input-lab"
                autoComplete="off"
                aria-describedby="plan-max-concepts-hint"
                value={draft}
                onChange={handleChange}
                onBlur={handleBlur}
              />
              <span id="plan-max-concepts-hint" className="sr-only">
                Whole number from 1 to 25
              </span>
            </div>
            <div className="field actions field--primary-action">
              <label>&nbsp;</label>
              <button
                type="button"
                className="btn-plan-path"
                onClick={runGenerate}
                disabled={disabled || loading}
              >
                {loading ? "Generating…" : "Generate learning path"}
              </button>
            </div>
          </div>
          <p className="plan-step-hint">
            Requires <code>GROQ_API_KEY</code> on the API. Uses your session topic and difficulty.
          </p>
        </div>
      ) : (
        <details className="plan-regenerate card card--stage">
          <summary className="plan-regenerate__summary">
            Change concept count or run again
          </summary>
          <div className="plan-regenerate__body">
            <div className="row">
              <div className="field">
                <label htmlFor="plan-max-concepts-regen">Max concepts</label>
                <input
                  id="plan-max-concepts-regen"
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  className="input-lab"
                  value={draft}
                  onChange={handleChange}
                  onBlur={handleBlur}
                />
              </div>
              <div className="field actions field--primary-action">
                <label>&nbsp;</label>
                <button
                  type="button"
                  className="btn-plan-path"
                  onClick={runGenerate}
                  disabled={disabled || loading}
                >
                  {loading ? "Regenerating…" : "Regenerate path"}
                </button>
              </div>
            </div>
            <p className="plan-step-hint">
              Regenerating replaces the path and clears downstream Learn / Quiz results for this
              session.
            </p>
          </div>
        </details>
      )}
    </div>
  );
}
