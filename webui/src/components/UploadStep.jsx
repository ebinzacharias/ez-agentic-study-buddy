import React, { useRef, useState } from "react";

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
  const fileInputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) {
      // Simulate a file input change
      const dt = new DataTransfer();
      dt.items.add(dropped);
      fileInputRef.current.files = dt.files;
      onFileChange({ target: { files: [dropped] } });
    }
  };

  return (
    <form onSubmit={onSubmit}>
      <div
        className={`upload-zone ${dragOver ? "upload-zone--active" : ""} ${file ? "upload-zone--has-file" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.md,.markdown,.pdf,.json"
          onChange={onFileChange}
          style={{ display: "none" }}
        />
        <div className="upload-zone__icon">{file ? "📄" : "📂"}</div>
        <div className="upload-zone__text">
          {file ? (
            <><strong>{file.name}</strong><span className="upload-zone__size">{(file.size / 1024).toFixed(1)} KB</span></>
          ) : (
            <><strong>Drop your study material here</strong><span className="upload-zone__hint">or click to browse — TXT, MD, PDF, JSON</span></>
          )}
        </div>
      </div>

      {file && (
        <button type="submit" disabled={loading} style={{ width: "100%", marginTop: "12px" }}>
          {loading ? "Processing…" : "Upload & Start Studying →"}
        </button>
      )}
    </form>
  );
}
