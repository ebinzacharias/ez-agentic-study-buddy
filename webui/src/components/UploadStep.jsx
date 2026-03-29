import React, { useRef, useState } from "react";
import { GetStartedButton } from "@/components/ui/get-started-button";

function UploadDecorIcon({ filePresent }) {
  return (
    <span className="upload-zone__icon" aria-hidden="true">
      {filePresent ? (
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
          <path d="M14 2v6h6" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
          <path d="M9 15h6M9 11h6" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
        </svg>
      ) : (
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 16V8m0 0l-3 3m3-3l3 3M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      )}
    </span>
  );
}

export default function UploadStep({
  file,
  loading,
  onFileChange,
  onSubmit,
}) {
  const fileInputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) {
      const dt = new DataTransfer();
      dt.items.add(dropped);
      fileInputRef.current.files = dt.files;
      onFileChange({ target: { files: [dropped] } });
    }
  };

  return (
    <form onSubmit={onSubmit} className="upload-form-card">
      <div
        className={`upload-zone ${dragOver ? "upload-zone--active" : ""} ${file ? "upload-zone--has-file" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
        role="button"
        tabIndex={0}
        aria-label="Choose file or drop study material here"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.md,.markdown,.pdf,.json"
          onChange={onFileChange}
          className="upload-zone__input"
          aria-label="Study material file"
        />
        <UploadDecorIcon filePresent={!!file} />
        <div className="upload-zone__text">
          {file ? (
            <>
              <strong>{file.name}</strong>
              <span className="upload-zone__size">{(file.size / 1024).toFixed(1)} KB</span>
            </>
          ) : (
            <>
              <strong>Drop your study material here</strong>
              <span className="upload-zone__hint">Or click to browse — TXT, MD, PDF, JSON</span>
            </>
          )}
        </div>
      </div>

      {file && (
        <GetStartedButton
          type="submit"
          disabled={loading}
          className="btn-block btn-touch"
        >
          {loading ? "Processing…" : "Upload and start session"}
        </GetStartedButton>
      )}
    </form>
  );
}
