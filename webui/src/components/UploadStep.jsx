import React from "react";

export default function UploadStep({
  file,
  difficulty,
  topic,
  loading,
  onFileChange,
  onDifficultyChange,
  onTopicChange,
  onSubmit,
}) {
  return (
    <div className="card">
      <form onSubmit={onSubmit} className="upload-form">
        <input
          type="file"
          accept=".txt,.md,.markdown,.pdf,.json"
          onChange={onFileChange}
        />
        <button type="submit" disabled={!file || loading}>
          {loading ? "Working..." : "Upload & Start"}
        </button>
      </form>
      <div className="hint">
        Supported: TXT, MD, PDF, JSON. For PDFs, install <code>pymupdf</code> on the API server.
      </div>
    </div>
  );
}
