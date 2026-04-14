import React, { useEffect, useRef, useState } from "react";

function clampConcepts(n, max = 15) {
  return Math.min(max, Math.max(1, n));
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

  // 0 means "auto" — show empty draft until backend resolves the count
  const [draft, setDraft] = useState(maxConcepts > 0 ? String(maxConcepts) : "");

  useEffect(() => {
    setDraft(maxConcepts > 0 ? String(maxConcepts) : "");
  }, [maxConcepts]);

  const handleChange = (e) => {
    const v = e.target.value;
    if (!/^\d*$/.test(v)) return;
    setDraft(v);
    if (v.trim() === "") return;
    const n = parseInt(v, 10);
    if (!Number.isNaN(n)) onMaxConceptsChange(clampConcepts(n, ceiling));
  };

  const handleBlur = () => {
    const trimmed = String(draft).trim();
    if (trimmed === "") {
      // Blank resets to the document's suggested ceiling
      const fallback = ceiling;
      onMaxConceptsChange(fallback);
      setDraft(String(fallback));
      return;
    }
    const parsed = parseInt(trimmed, 10);
    if (Number.isNaN(parsed) || parsed <= 0) {
      onMaxConceptsChange(ceiling);
      setDraft(String(ceiling));
      return;
    }
    const next = clampConcepts(parsed, ceiling);
    onMaxConceptsChange(next);
    setDraft(String(next));
  };

  const runGenerate = () => {
    const parsed = parseInt(String(draft).trim(), 10);
    const m = Number.isNaN(parsed) || parsed <= 0 ? ceiling : clampConcepts(parsed, ceiling);
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
              {planResult.concepts.length}{maxAllowed > 0 ? ` / ${maxAllowed}` : ""} concepts &mdash; tap any card to start studying
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
                {maxAllowed > 0
                  ? `The document supports up to ${maxAllowed} concepts. Reduce the count to focus on fewer topics.`
                  : "Regenerating replaces the path and clears any downstream Learn / Quiz results."}
              </p>
              <div className="plan-tune__body">
                <div className="plan-tune__row">
                  <label htmlFor="plan-max-concepts-tune" className="plan-tune__label">
                    Concepts
                  </label>
                  <input
                    id="plan-max-concepts-tune"
                    type="number"
                    min={1}
                    max={ceiling}
                    className="plan-tune__input"
                    autoComplete="off"
                    placeholder={String(ceiling)}
                    value={draft}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    aria-label={`Number of concepts, 1 to ${ceiling}`}
                  />
                  <span className="plan-tune__cap">/ {ceiling}</span>
                </div>
                <div className="plan-tune__row">
                  <label htmlFor="plan-difficulty" className="plan-tune__label">
                    Difficulty
                  </label>
                  <select
                    id="plan-difficulty"
                    className="plan-tune__select"
                    value={difficulty}
                    onChange={(e) => onDifficultyChange(e.target.value)}
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
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
              className={`concept-card${loading ? " concept-card--busy" : ""}`}
              style={{ "--i": i }}
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
