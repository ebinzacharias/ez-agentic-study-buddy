import React, { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

/**
 * Plain extracted text rarely has Markdown paragraph breaks. Turn typical extracts into
 * Markdown so line breaks and double newlines render as readable prose in the modal.
 * Skip when fenced code is present so ``` blocks stay intact.
 */
function prepareSourceMarkdown(raw) {
  const t = raw.trim();
  if (!t) return "";
  if (/```/.test(t)) return t;
  const blocks = t
    .split(/\n{2,}/)
    .map((b) => b.trim())
    .filter(Boolean);
  if (blocks.length === 0) return "";
  return blocks
    .map((block) =>
      block.split("\n").map((line) => line.trimEnd()).join("  \n")
    )
    .join("\n\n");
}

export default function SourcePreviewModal({
  open,
  onClose,
  apiBaseUrl,
  sessionId,
  fileLabel,
}) {
  const dialogRef = useRef(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState(null);

  useEffect(() => {
    const el = dialogRef.current;
    if (!el) return;
    if (open) {
      if (!el.open) el.showModal();
    } else if (el.open) {
      el.close();
    }
  }, [open]);

  useEffect(() => {
    const el = dialogRef.current;
    if (!el) return;
    const onDialogClose = () => onClose();
    el.addEventListener("close", onDialogClose);
    return () => el.removeEventListener("close", onDialogClose);
  }, [onClose]);

  useEffect(() => {
    if (!open || !sessionId) return;
    let cancelled = false;
    setLoading(true);
    setLoadError(null);
    setText("");

    (async () => {
      try {
        const resp = await fetch(
          `${apiBaseUrl}/session/${encodeURIComponent(sessionId)}/source`
        );
        const data = await resp.json();
        if (cancelled) return;
        if (!resp.ok) {
          setLoadError(typeof data.error === "string" ? data.error : "Could not load source");
          setLoading(false);
          return;
        }
        setText(typeof data.text === "string" ? data.text : "");
        setLoading(false);
      } catch {
        if (cancelled) return;
        setLoadError("Could not reach the server.");
        setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [open, sessionId, apiBaseUrl]);

  return (
    <dialog
      ref={dialogRef}
      className="source-preview-dialog"
      aria-labelledby="source-preview-title"
    >
      <div className="source-preview-dialog__shell">
        <header className="source-preview-dialog__header">
          <div className="source-preview-dialog__title-block">
            <h2 id="source-preview-title" className="source-preview-dialog__title">
              Your upload
            </h2>
            {fileLabel ? (
              <p className="source-preview-dialog__subtitle">{fileLabel}</p>
            ) : null}
          </div>
          <button
            type="button"
            className="source-preview-dialog__close"
            onClick={() => dialogRef.current?.close()}
            aria-label="Close preview"
          >
            ×
          </button>
        </header>
        <div className="source-preview-dialog__body">
          {loading ? (
            <p className="source-preview-dialog__status">Loading…</p>
          ) : null}
          {loadError ? (
            <p className="source-preview-dialog__error" role="alert">
              {loadError}
            </p>
          ) : null}
          {!loading && !loadError ? (
            <div className="source-preview-dialog__scroll">
              {text.trim() ? (
                <article
                  className="source-preview-dialog__prose teach-explanation"
                  aria-label="Extracted document text"
                >
                  <ReactMarkdown
                    components={{
                      a: ({ node, ...props }) => (
                        <a {...props} target="_blank" rel="noopener noreferrer" />
                      ),
                    }}
                  >
                    {prepareSourceMarkdown(text)}
                  </ReactMarkdown>
                </article>
              ) : (
                <p className="source-preview-dialog__empty">
                  No text was extracted from this file.
                </p>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </dialog>
  );
}
