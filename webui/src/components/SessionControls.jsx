import React, { useMemo, useState } from "react";
import SourcePreviewModal from "./SourcePreviewModal";

function norm(s) {
  return (s || "").trim().toLowerCase();
}

export default function SessionControls({
  sessionId,
  apiBaseUrl,
  uploadResult,
  topic,
  suggestedTopic,
  difficulty,
  loading,
  onDifficultyChange,
  onReset,
}) {
  const [sourceOpen, setSourceOpen] = useState(false);

  const suggestedDiffers =
    suggestedTopic &&
    norm(suggestedTopic) !== norm(topic);

  const fileLabel = useMemo(() => {
    const names = uploadResult?.materials
      ?.map((m) => m.filename)
      .filter(Boolean);
    if (!names?.length) return "";
    return names.join(", ");
  }, [uploadResult]);

  return (
    <section className="session-workspace-hero" aria-label="Current session">
      <div className="session-workspace-hero__inner">
        <div className="session-hero-banner">
          <p className="session-hero-summary sr-only">
            Session topic and difficulty. View extracted source text or start a new upload.
          </p>
          <div className="session-hero-banner__actions" role="group" aria-label="Session actions">
            <button
              type="button"
              className="btn-session-source"
              onClick={() => setSourceOpen(true)}
              disabled={loading || !sessionId}
            >
              View source
            </button>
            <button
              type="button"
              className="btn-session-reset-top"
              onClick={onReset}
              disabled={loading}
            >
              New upload &amp; reset session
            </button>
          </div>
        </div>

        <div className="session-metadata-card session-metadata-card--hero">
          <div className="row row--stack-sm session-metadata-card__fields">
            <div className="field">
              <label htmlFor="session-topic-display">Topic</label>
              <p id="session-topic-hint" className="session-field-hint">
                Auto: PDF/embedded title, filename, or first substantive heading — page numbers and
                footers are skipped.
              </p>
              <div
                id="session-topic-display"
                className="session-topic-readonly"
                aria-describedby="session-topic-hint"
              >
                {topic.trim() ? topic : "—"}
              </div>
            </div>
            <div className="field">
              <label htmlFor="session-difficulty">Difficulty</label>
              <p id="session-difficulty-hint" className="session-field-hint">
                Applied to Plan, Learn, and Quiz calls from this session.
              </p>
              <select
                id="session-difficulty"
                className="input-lab session-field-control"
                value={difficulty}
                onChange={(e) => onDifficultyChange(e.target.value)}
                aria-describedby="session-difficulty-hint"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
          </div>

          {suggestedDiffers ? (
            <p className="rail-meta session-metadata-card__suggested">
              <span className="rail-meta-label">Model suggestion</span>
              <span className="rail-meta-value">{suggestedTopic}</span>
            </p>
          ) : null}
        </div>
      </div>

      <SourcePreviewModal
        open={sourceOpen}
        onClose={() => setSourceOpen(false)}
        apiBaseUrl={apiBaseUrl}
        sessionId={sessionId}
        fileLabel={fileLabel}
      />
    </section>
  );
}
