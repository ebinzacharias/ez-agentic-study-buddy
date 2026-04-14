import React, { useMemo, useState } from "react";
import SourcePreviewModal from "./SourcePreviewModal";

function norm(s) {
  return (s || "").trim().toLowerCase();
}

function FileIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path
        d="M4 2h5.5L12 4.5V14H4V2z"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinejoin="round"
      />
      <path d="M9 2v3h3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function SourceIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.4" />
      <path d="M8 5v4M8 11v.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

function ResetIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path
        d="M3 8a5 5 0 1 0 1.5-3.5L3 3v3h3"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function SessionControls({
  sessionId,
  apiBaseUrl,
  uploadResult,
  topic,
  suggestedTopic,
  loading,
  onReset,
}) {
  const [sourceOpen, setSourceOpen] = useState(false);

  const suggestedDiffers = suggestedTopic && norm(suggestedTopic) !== norm(topic);

  const fileLabel = useMemo(() => {
    const names = uploadResult?.materials?.map((m) => m.filename).filter(Boolean);
    if (!names?.length) return null;
    return names.join(", ");
  }, [uploadResult]);

  return (
    <section className="session-bar" aria-label="Current session">
      <div className="session-bar__inner">
        {/* Left: file badge + topic */}
        <div className="session-bar__identity">
          {fileLabel && (
            <span className="session-bar__file">
              <FileIcon />
              <span className="session-bar__filename">{fileLabel}</span>
            </span>
          )}
          {fileLabel && <span className="session-bar__divider" aria-hidden="true" />}
          <div className="session-bar__topic-group">
            <span className="session-bar__label">Topic</span>
            <span className="session-bar__topic" title={topic.trim() || undefined}>
              {topic.trim() ? topic : "Auto-detected"}
            </span>
          </div>
          {suggestedDiffers && (
            <>
              <span className="session-bar__divider" aria-hidden="true" />
              <span className="session-bar__suggestion" title="Model-suggested topic">
                {suggestedTopic}
              </span>
            </>
          )}
        </div>

        {/* Right: actions */}
        <div className="session-bar__actions">
          <button
            type="button"
            className="session-btn session-btn--ghost"
            onClick={() => setSourceOpen(true)}
            disabled={loading || !sessionId}
          >
            <SourceIcon />
            Source
          </button>

          <button
            type="button"
            className="session-btn session-btn--reset"
            onClick={onReset}
            disabled={loading}
          >
            <ResetIcon />
            New session
          </button>
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
