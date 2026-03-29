import React from "react";

export default function MaterialPreview({ uploadResult, className = "", variant = "default" }) {
  if (!uploadResult) return null;

  const isSourcePanel = variant === "sourcePanel";
  const title = isSourcePanel ? "Source material" : "Material";

  return (
    <div
      className={`result result--material ${isSourcePanel ? "result--material-source" : ""} ${className}`.trim()}
    >
      <h2 className="result__title">{title}</h2>
      {uploadResult.materials && (
        <div className="hint">
          {uploadResult.materials.map((m) => m.filename).join(", ")}
        </div>
      )}
      {!isSourcePanel ? (
        <>
          <h3>Section titles</h3>
          <ul>
            {uploadResult.section_titles.length === 0 && <li>(none found)</li>}
            {uploadResult.section_titles.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
        </>
      ) : null}
      <h3>{isSourcePanel ? "Extract preview" : "Content preview"}</h3>
      <pre className="preview" tabIndex={0}>
        {uploadResult.preview}
      </pre>
    </div>
  );
}
