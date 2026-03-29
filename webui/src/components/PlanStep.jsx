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

  return (
    <div className="plan-environment">
      <header className="plan-environment__intro">
        <h3 className="plan-environment__heading">Plan</h3>
        <p className="plan-environment__lede">
          Configure and map your session — set how many concepts to extract and how deep the
          study path should go.
        </p>
      </header>

      <div className="card card--stage card--lab-stage">
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
              onClick={() => {
                const m = resolveMaxFromDraft();
                setDraft(String(m));
                onMaxConceptsChange(m);
                onPlan(m);
              }}
              disabled={disabled || loading}
            >
              Generate Study Path
            </button>
          </div>
        </div>
        <p className="plan-step-hint">
          Uses an LLM &mdash; ensure <code>GROQ_API_KEY</code> is set on the API server.
        </p>
        {planResult ? (
          <p className="plan-status" role="status">
            <strong>Study path ready.</strong>{" "}
            {planResult.concepts?.length ?? 0} concepts mapped — pick one in the sidebar, then
            switch to <strong>Learn</strong> or <strong>Quiz</strong>.
          </p>
        ) : null}
      </div>
    </div>
  );
}
