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
  const [payload, setPayload] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState(null);

  const pdfSrc =
    sessionId && apiBaseUrl
      ? `${apiBaseUrl}/session/${encodeURIComponent(sessionId)}/source-file`
      : "";

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
    setPayload(null);

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
        setPayload({
          text: typeof data.text === "string" ? data.text : "",
          pdfAvailable: Boolean(data.pdf_available),
          pdfFilename: typeof data.pdf_filename === "string" ? data.pdf_filename : "",
          filenames: Array.isArray(data.filenames) ? data.filenames : [],
        });
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

  const showPdf = Boolean(payload?.pdfAvailable && pdfSrc);
  const text = payload?.text ?? "";

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
            {showPdf ? (
              <p className="source-preview-dialog__subtitle source-preview-dialog__subtitle--note">
                Showing the original PDF in your browser. Text extract is still what Plan / Learn /
                Quiz use.
              </p>
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
          {!loading && !loadError && showPdf ? (
            <div className="source-preview-dialog__scroll source-preview-dialog__scroll--pdf">
              <iframe
                title={payload?.pdfFilename || "PDF preview"}
                className="source-preview-dialog__pdf"
                src={pdfSrc}
              />
            </div>
          ) : null}
          {!loading && !loadError && !showPdf && text.trim() ? (
            <div className="source-preview-dialog__scroll">
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
            </div>
          ) : null}
          {!loading && !loadError && !showPdf && !text.trim() ? (
            <p className="source-preview-dialog__empty">
              No text was extracted from this file.
            </p>
          ) : null}
        </div>
      </div>
    </dialog>
  );
}
