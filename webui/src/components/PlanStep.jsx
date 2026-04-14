import React, { useEffect, useRef, useState } from "react";

function clampConcepts(n) {
  return Math.min(25, Math.max(1, n));
}

function TuneIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path
        d="M2 4h12M5 8h6M7 12h2"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

function ArrowIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path
        d="M3 8h10M9 4l4 4-4 4"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function SkeletonCard({ delay }) {
  return (
    <div className="concept-skeleton" style={{ "--delay": `${delay}ms` }}>
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
    if (!Number.isNaN(n)) onMaxConceptsChange(clampConcepts(n));
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

  const runGenerate = () => {
    const parsed = parseInt(String(draft).trim(), 10);
    const m = Number.isNaN(parsed) ? clampConcepts(maxConcepts) : clampConcepts(parsed);
    setDraft(String(m));
    onMaxConceptsChange(m);
    onPlan(m);
  };

  const [tuneOpen, setTuneOpen] = useState(false);
  const tuneRef = useRef(null);

  useEffect(() => {
    if (!tuneOpen) return;
    const handleOutside = (e) => {
      if (tuneRef.current && !tuneRef.current.contains(e.target)) {
        setTuneOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, [tuneOpen]);

  const hasPath = Boolean(planResult?.concepts?.length);
  const isAutoScanning = loading && !hasPath;

  return (
    <div className="plan-env">
      <div className="plan-env__header">
        <div className="plan-env__header-left">
          <h3 className="plan-env__title">
            {isAutoScanning ? "Scanning document…" : hasPath ? "Learning Path" : "Learning Path"}
          </h3>
          {hasPath && (
            <p className="plan-env__meta">
              {planResult.concepts.length} concepts &mdash; tap any card to start studying
            </p>
          )}
          {isAutoScanning && (
            <p className="plan-env__meta plan-env__meta--scanning">
              Extracting ordered concepts from your file
            </p>
          )}
          {!isAutoScanning && !hasPath && (
            <p className="plan-env__meta">
              Concept extraction didn&apos;t run automatically. Use Tune to generate.
            </p>
          )}
        </div>

        <div className="plan-tune" ref={tuneRef}>
          <button
            type="button"
            className={`plan-tune__trigger${tuneOpen ? " is-open" : ""}`}
            aria-expanded={tuneOpen}
            aria-haspopup="true"
            onClick={() => setTuneOpen((v) => !v)}
          >
            <TuneIcon />
            Tune
          </button>
          {tuneOpen && (
            <div className="plan-tune__panel" role="dialog" aria-label="Tune learning path">
              <p className="plan-tune__hint">
                Regenerating replaces the path and clears any downstream Learn / Quiz results.
              </p>
              <div className="plan-tune__row">
                <label htmlFor="plan-max-concepts-tune" className="plan-tune__label">
                  Concepts
                </label>
                <input
                  id="plan-max-concepts-tune"
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  className="plan-tune__input"
                  autoComplete="off"
                  value={draft}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  aria-label="Max concepts, 1 to 25"
                />
                <button
                  type="button"
                  className="plan-tune__run"
                  onClick={() => { runGenerate(); setTuneOpen(false); }}
                  disabled={disabled || loading}
                >
                  {loading ? "Running…" : "Regenerate"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Shimmer skeleton while auto-scanning */}
      {isAutoScanning && (
        <div className="concept-skeleton-grid" aria-label="Loading concepts" aria-busy="true">
          {[0, 60, 120, 180, 240, 300, 360, 420].map((delay, i) => (
            <SkeletonCard key={i} delay={delay} />
          ))}
        </div>
      )}

      {/* Bento concept cards */}
      {hasPath && (
        <ol className="concept-grid" aria-label="Learning path">
          {planResult.concepts.map((c, i) => (
            <li
              key={`${c.order}-${c.concept_name}`}
              className="concept-card"
              style={{ "--i": i }}
            >
              <span className="concept-card__num" aria-hidden="true">
                {String(c.order).padStart(2, "0")}
              </span>
              <div className="concept-card__body">
                <h4 className="concept-card__name">{c.concept_name}</h4>
                {c.difficulty && (
                  <span className="concept-card__diff">{c.difficulty}</span>
                )}
              </div>
              {onPickConcept && (
                <button
                  type="button"
                  className="concept-card__cta"
                  onClick={() => onPickConcept(c.concept_name)}
                  aria-label={`Study ${c.concept_name}`}
                >
                  <span>Study</span>
                  <ArrowIcon />
                </button>
              )}
            </li>
          ))}
        </ol>
      )}

      {/* Empty state — plan failed silently */}
      {!isAutoScanning && !hasPath && (
        <div className="plan-env__empty">
          <p className="plan-env__empty-text">
            Open <strong>Tune</strong> above to generate your learning path.
          </p>
        </div>
      )}
    </div>
  );
}
