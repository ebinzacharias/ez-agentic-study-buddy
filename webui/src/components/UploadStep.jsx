import React, { useRef, useState } from "react";

// Modern SVG Icons
function CheckmarkIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

function DownArrowIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 5V19M12 19L19 12M12 19L5 12" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

function ArrowRightIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

function NeuralCore({ isActive }) {
  return (
    <div className={`neural-core ${isActive ? "neural-core--active" : ""}`} aria-hidden="true">
      <svg viewBox="0 0 100 100" className="neural-core__svg">
        <defs>
          <filter id="neural-glow">
            <feGaussianBlur stdDeviation="2"/>
          </filter>
        </defs>
        <circle cx="50" cy="50" r="45" fill="none" stroke="#4fd1c5" strokeWidth="1" opacity="0.3"/>
        <circle cx="50" cy="50" r="35" fill="none" stroke="#4fd1c5" strokeWidth="0.8" opacity="0.2"/>
        <circle cx="50" cy="20" r="2" fill="#4fd1c5" filter="url(#neural-glow)"/>
        <circle cx="75" cy="50" r="2" fill="#4fd1c5" filter="url(#neural-glow)"/>
        <circle cx="50" cy="80" r="2" fill="#4fd1c5" filter="url(#neural-glow)"/>
        <circle cx="25" cy="50" r="2" fill="#4fd1c5" filter="url(#neural-glow)"/>
        <circle cx="50" cy="50" r="3" fill="#4fd1c5" opacity="0.8"/>
      </svg>
    </div>
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
    <form onSubmit={onSubmit} className={`upload-portal ${dragOver ? "upload-portal--drag-active" : ""} ${file ? "upload-portal--has-file" : ""}`}>
      <div className="upload-portal__neural-wrapper">
        <NeuralCore isActive={!!file || dragOver} />
      </div>

      <div
        className="upload-drop-portal"
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
        aria-label="Drop your study material here or click to browse"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.md,.markdown,.pdf,.json"
          onChange={onFileChange}
          className="upload-drop-portal__input"
          aria-label="Study material file input"
        />

        <div className="upload-portal__content">
          {file ? (
            <div className="upload-portal__file-state">
              <div className="file-icon" aria-hidden="true"><CheckmarkIcon /></div>
              <h2 className="file-name">{file.name}</h2>
              <p className="file-meta">{(file.size / 1024).toFixed(1)} KB • Ready</p>
            </div>
          ) : (
            <div className="upload-portal__empty-state">
              <div className="drop-indicator" aria-hidden="true"><DownArrowIcon /></div>
              <h2 className="portal-title">Drop your material</h2>
              <p className="portal-subtitle">PDF, Markdown, or Text</p>
            </div>
          )}
        </div>
      </div>

      {file && (
        <button
          type="submit"
          disabled={loading}
          className="upload-submit-btn"
          aria-label={loading ? "Processing your file" : "Start learning session"}
        >
          <span className="submit-content">
            {loading ? (
              <>
                <span className="loader-spinner" aria-hidden="true"></span>
                <span>Initializing…</span>
              </>
            ) : (
              <>
                <span>Start learning</span>
                <span className="submit-arrow" aria-hidden="true"><ArrowRightIcon /></span>
              </>
            )}
          </span>
        </button>
      )}
    </form>
  );
}
