import React, { useRef, useState } from "react";

function UploadIcon() {
  return (
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <polyline
        points="17 8 12 3 7 8"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <line
        x1="12"
        y1="3"
        x2="12"
        y2="15"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M20 6L9 17L4 12"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ArrowIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M5 12h14M13 6l6 6-6 6"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function UploadStep({ file, loading, onFileChange, onSubmit }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) {
      const dt = new DataTransfer();
      dt.items.add(dropped);
      inputRef.current.files = dt.files;
      onFileChange({ target: { files: [dropped] } });
    }
  };

  const open = () => inputRef.current?.click();

  return (
    <section id="lp-upload" className="lp-upload-section" aria-label="Upload your study material">
      <form
        onSubmit={onSubmit}
        className={`lp-upload${dragOver ? " lp-upload--drag" : ""}${file ? " lp-upload--ready" : ""}`}
      >
        <div className="lp-upload__inner">
          {/* Card header */}
          <div className="lp-upload__head">
            <span className="lp-upload__badge">Step 1 · Upload</span>
            <h2 className="lp-upload__title">Drop your material to begin</h2>
            <p className="lp-upload__hint">
              One file starts a private session locked to that document.
            </p>
          </div>

          {/* Drop zone */}
          <div
            className="lp-upload__zone"
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={open}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                open();
              }
            }}
            role="button"
            tabIndex={0}
            aria-label="Drop your study material here or press Enter to browse files"
          >
            <input
              ref={inputRef}
              type="file"
              accept=".txt,.md,.markdown,.pdf,.json"
              onChange={onFileChange}
              className="lp-upload__input"
            />

            {file ? (
              <div className="lp-upload__picked">
                <span className="lp-upload__check-icon">
                  <CheckIcon />
                </span>
                <div className="lp-upload__picked-info">
                  <p className="lp-upload__file-name">{file.name}</p>
                  <p className="lp-upload__file-size">
                    {(file.size / 1024).toFixed(1)} KB · Ready
                  </p>
                </div>
              </div>
            ) : (
              <div className="lp-upload__empty">
                <span className="lp-upload__cloud-icon">
                  <UploadIcon />
                </span>
                <p className="lp-upload__empty-title">Drop file here</p>
                <p className="lp-upload__empty-hint">or click to browse</p>
              </div>
            )}
          </div>

          {/* Format chips */}
          <div className="lp-upload__formats" aria-hidden="true">
            {["PDF", "MD", "TXT", "JSON"].map((f) => (
              <span key={f} className="lp-upload__fmt">{f}</span>
            ))}
          </div>

          {/* Browse button */}
          <button
            type="button"
            className="lp-upload__browse"
            onClick={(e) => { e.preventDefault(); open(); }}
          >
            {file ? "Change file" : "Browse files"}
          </button>

          {/* Start CTA — only visible when file is picked */}
          {file ? (
            <button
              type="submit"
              disabled={loading}
              className="lp-upload__start"
              aria-label={loading ? "Starting session" : "Start learning session"}
            >
              {loading ? (
                <>
                  <span className="lp-upload__spinner" aria-hidden="true" />
                  Starting session…
                </>
              ) : (
                <>
                  Start session
                  <ArrowIcon />
                </>
              )}
            </button>
          ) : null}
        </div>
      </form>
    </section>
  );
}
