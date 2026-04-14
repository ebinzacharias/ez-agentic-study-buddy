import React, { useEffect, useState } from "react";

function clampConcepts(n, max = 15) {
  return Math.min(max, Math.max(1, n));
}

function SkeletonCard() {
  return (
    <div className="concept-skeleton">
      <div className="concept-skeleton__num" />
      <div className="concept-skeleton__body">
        <div className="concept-skeleton__line concept-skeleton__line--title" />
        <div className="concept-skeleton__line concept-skeleton__line--sub" />
      </div>
    </div>
  );
}

export default function PlanStep({
  maxConcepts,
  maxAllowed,
  difficulty,
  planResult,
  loading,
  disabled,
  onMaxConceptsChange,
  onDifficultyChange,
  onPlan,
  onPickConcept,
}) {
  const ceiling = maxAllowed > 0 ? maxAllowed : 15;
  const [count, setCount] = useState(maxConcepts > 0 ? maxConcepts : ceiling);

  useEffect(() => {
    if (maxConcepts > 0) setCount(maxConcepts);
    else if (ceiling > 0) setCount(ceiling);
  }, [maxConcepts, ceiling]);

  const step = (delta) => {
    const next = clampConcepts(count + delta, ceiling);
    setCount(next);
    onMaxConceptsChange(next);
    onPlan(next);
  };

  const hasPath = Boolean(planResult?.concepts?.length);
  const isAutoScanning = loading && !hasPath;

  return (
    <div className="plan-env">
      {/* ── Header ─────────────────────────── */}
      <div className="plan-env__header">
        <div className="plan-env__header-left">
          <h3 className="plan-env__title">
            {isAutoScanning ? "Scanning document…" : "Study Plan"}
          </h3>
          <p className="plan-env__meta">
            {isAutoScanning
              ? "Extracting ordered concepts from your file"
              : hasPath
              ? `We identified ${planResult.concepts.length} key concept${planResult.concepts.length !== 1 ? "s" : ""}. Adjust the count or click a concept to start learning.`
              : "Upload a document to generate your learning path."}
          </p>
        </div>
      </div>

      {/* ── Concept stepper ────────────────── */}
      {(hasPath || maxAllowed > 0) && !isAutoScanning && (
        <div className="plan-stepper-row">
          <span className="plan-stepper__label">Concepts:</span>
          <div className="plan-stepper">
            <button
              type="button"
              className="plan-stepper__btn"
              aria-label="Fewer concepts"
              disabled={disabled || loading || count <= 1}
              onClick={() => step(-1)}
            >
              −
            </button>
            <span className="plan-stepper__count" aria-live="polite" aria-label={`${count} concepts`}>
              {count}
            </span>
            <button
              type="button"
              className="plan-stepper__btn"
              aria-label="More concepts"
              disabled={disabled || loading || count >= ceiling}
              onClick={() => step(+1)}
            >
              +
            </button>
          </div>
          {maxAllowed > 0 && (
            <span className="plan-stepper__cap">of {ceiling} max</span>
          )}

          {/* Difficulty inline */}
          <div className="plan-stepper__difficulty">
            <label htmlFor="plan-difficulty-inline" className="plan-stepper__diff-label">
              Level
            </label>
            <select
              id="plan-difficulty-inline"
              className="plan-stepper__diff-select"
              value={difficulty}
              onChange={(e) => {
                onDifficultyChange(e.target.value);
                onPlan(count);
              }}
              disabled={disabled || loading}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>
      )}

      {/* ── Skeleton ───────────────────────── */}
      {isAutoScanning && (
        <div className="concept-skeleton-grid" aria-label="Loading concepts" aria-busy="true">
          {Array.from({ length: 8 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      )}

      {/* ── Concept cards ──────────────────── */}
      {hasPath && (
        <ol className="concept-grid" aria-label="Learning path">
          {planResult.concepts.map((c) => (
            <li
              key={`${c.order}-${c.concept_name}`}
              className={`concept-card${loading ? " concept-card--busy" : ""}`}
              role={onPickConcept ? "button" : undefined}
              tabIndex={onPickConcept ? 0 : undefined}
              aria-label={onPickConcept ? `Learn ${c.concept_name}` : undefined}
              onClick={() => !loading && onPickConcept?.(c.concept_name)}
              onKeyDown={(e) => {
                if (!loading && (e.key === "Enter" || e.key === " ")) {
                  e.preventDefault();
                  onPickConcept?.(c.concept_name);
                }
              }}
            >
              <span className="concept-card__num" aria-hidden="true">
                {String(c.order).padStart(2, "0")}
              </span>
              <div className="concept-card__body">
                <h4 className="concept-card__name">{c.concept_name}</h4>
              </div>
              <span className="concept-card__learn-hint" aria-hidden="true">
                Learn
                <svg width="11" height="11" viewBox="0 0 12 12" fill="none">
                  <path d="M2 6h8M7 3l3 3-3 3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
            </li>
          ))}
        </ol>
      )}

      {/* ── Empty state ────────────────────── */}
      {!isAutoScanning && !hasPath && (
        <div className="plan-env__empty">
          <p className="plan-env__empty-text">
            Upload a document above to generate your study plan.
          </p>
        </div>
      )}
    </div>
  );
}
