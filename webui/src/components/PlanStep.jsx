import React from "react";

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
  planResult,
  loading,
  disabled,
  completedConcepts,
  onPickConcept,
}) {
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
              ? `We identified ${planResult.concepts.length} key concept${planResult.concepts.length !== 1 ? "s" : ""}. Click a concept to start learning.`
              : "Upload a document to generate your learning path."}
          </p>
        </div>
      </div>

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
              className={`concept-card${loading ? " concept-card--busy" : ""}${completedConcepts?.has(c.concept_name) ? " concept-card--completed" : ""}`}
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
                {completedConcepts?.has(c.concept_name) ? (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-label="Completed">
                    <path d="M20 6L9 17l-5-5" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                ) : (
                  String(c.order).padStart(2, "0")
                )}
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
