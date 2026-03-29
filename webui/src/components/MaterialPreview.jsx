import React from "react";

export default function MaterialPreview({ uploadResult, className = "" }) {
  if (!uploadResult) return null;

  return (
    <div className={`result result--material ${className}`.trim()}>
      <h2 className="result__title">Material</h2>
      {uploadResult.materials && (
        <div className="hint">
          {uploadResult.materials.map((m) => m.filename).join(", ")}
        </div>
      )}
      <h3>Section titles</h3>
      <ul>
        {uploadResult.section_titles.length === 0 && <li>(none found)</li>}
        {uploadResult.section_titles.map((t, i) => (
          <li key={i}>{t}</li>
        ))}
      </ul>
      <h3>Content preview</h3>
      <pre className="preview" tabIndex={0}>{uploadResult.preview}</pre>
    </div>
  );
}
