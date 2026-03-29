import React, { useState } from "react";

export default function SessionControls({
  sessionId,
  topic,
  suggestedTopic,
  difficulty,
  loading,
  onTopicChange,
  onDifficultyChange,
  onReset,
}) {
  const [copied, setCopied] = useState(false);
  const shortId = sessionId.length > 12
    ? `${sessionId.slice(0, 8)}…${sessionId.slice(-4)}`
    : sessionId;

  const copyId = async () => {
    try {
      await navigator.clipboard.writeText(sessionId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  return (
    <>
      <div className="session-metadata-card">
        <div className="session-metadata-card__header">
          <div className="session-id-label">
            <span className="session-id-key">Session</span>
            <code className="session-id-value" title={sessionId}>
              {shortId}
            </code>
          </div>
          <button
            type="button"
            className="btn-session-copy btn-small"
            onClick={copyId}
            disabled={!sessionId}
            aria-label="Copy full session ID to clipboard"
          >
            {copied ? "Copied" : "Copy ID"}
          </button>
        </div>

        <div className="row row--stack-sm session-metadata-card__fields">
          <div className="field">
            <label htmlFor="session-topic">Topic</label>
            <input
              id="session-topic"
              className="input-lab"
              value={topic}
              onChange={(e) => onTopicChange(e.target.value)}
              placeholder="e.g., Python Basics"
              autoComplete="off"
            />
          </div>
          <div className="field">
            <label htmlFor="session-difficulty">Difficulty</label>
            <select
              id="session-difficulty"
              className="input-lab"
              value={difficulty}
              onChange={(e) => onDifficultyChange(e.target.value)}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>

        {suggestedTopic ? (
          <p className="rail-meta session-metadata-card__suggested">
            <span className="rail-meta-label">Suggested topic</span>
            <span className="rail-meta-value">{suggestedTopic}</span>
          </p>
        ) : null}
      </div>

      <button
        type="button"
        className="btn-session-ghost btn-block btn-touch"
        onClick={onReset}
        disabled={loading}
      >
        New upload &amp; reset session
      </button>
    </>
  );
}
