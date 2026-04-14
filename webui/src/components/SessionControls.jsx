import React, { useMemo } from "react";

function norm(s) {
  return (s || "").trim().toLowerCase();
}

function FileIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M4 2h5.5L12 4.5V14H4V2z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
      <path d="M9 2v3h3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function SessionControls({
  uploadResult,
  topic,
  suggestedTopic,
}) {
  const suggestedDiffers = suggestedTopic && norm(suggestedTopic) !== norm(topic);

  const fileLabel = useMemo(() => {
    const names = uploadResult?.materials?.map((m) => m.filename).filter(Boolean);
    if (!names?.length) return null;
    return names.join(", ");
  }, [uploadResult]);

  return (
    <section className="session-bar" aria-label="Current session">
      <div className="session-bar__inner">
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
    </section>
  );
}
