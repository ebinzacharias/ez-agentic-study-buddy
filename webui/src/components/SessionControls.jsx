import React, { useMemo, useState } from "react";
import SourcePreviewModal from "./SourcePreviewModal";

function norm(s) {
  return (s || "").trim().toLowerCase();
}

const TOPIC_HINT =
  "Topic is chosen automatically from your file (metadata, filename, or first solid heading).";
const DIFF_HINT = "Used for Path, Learn, and Quiz calls in this session.";

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
    <section
      className="session-workspace-hero session-workspace-hero--compact"
      aria-label="Current session"
    >
      <div className="session-workspace-hero__inner">
        <div className="session-compact-toolbar">
          <div className="session-compact-toolbar__meta" role="group" aria-label="Session topic and difficulty">
            <div className="session-compact-field">
              <span className="session-compact-field__label" title={TOPIC_HINT}>
                Topic
              </span>
              <p
                id="session-topic-display"
                className="session-compact-topic"
                title={topic.trim() || undefined}
                aria-describedby="session-topic-hint"
              >
                {topic.trim() ? topic : "—"}
              </p>
              <span id="session-topic-hint" className="sr-only">
                {TOPIC_HINT}
              </span>
            </div>
            <div className="session-compact-field session-compact-field--difficulty">
              <label
                htmlFor="session-difficulty"
                className="session-compact-field__label"
                title={DIFF_HINT}
              >
                Difficulty
              </label>
              <select
                id="session-difficulty"
                className="session-compact-select input-lab"
                value={difficulty}
                onChange={(e) => onDifficultyChange(e.target.value)}
                aria-describedby="session-difficulty-hint"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
              <span id="session-difficulty-hint" className="sr-only">
                {DIFF_HINT}
              </span>
            </div>
          </div>
          <div className="session-compact-toolbar__actions" role="group" aria-label="Session actions">
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

        {suggestedDiffers ? (
          <p className="rail-meta session-compact-suggested">
            <span className="rail-meta-label">Model suggestion</span>
            <span className="rail-meta-value">{suggestedTopic}</span>
          </p>
        ) : null}
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
