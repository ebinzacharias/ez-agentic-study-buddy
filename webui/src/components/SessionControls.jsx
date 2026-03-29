import React from "react";

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
  return (
    <div className="card">
      <div className="row">
        <div className="field">
          <label>Topic (suggested)</label>
          <input
            value={topic}
            onChange={(e) => onTopicChange(e.target.value)}
            placeholder="e.g., Python Basics"
          />
        </div>
        <div className="field">
          <label>Difficulty</label>
          <select value={difficulty} onChange={(e) => onDifficultyChange(e.target.value)}>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
        <div className="field actions">
          <label>&nbsp;</label>
          <button type="button" onClick={onReset} disabled={loading}>
            New Upload
          </button>
        </div>
      </div>
      <div className="pill">
        Session: {sessionId}
        {suggestedTopic ? <> &middot; Suggested: {suggestedTopic}</> : ""}
      </div>
    </div>
  );
}
