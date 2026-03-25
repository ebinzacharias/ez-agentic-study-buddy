import React from "react";

export default function MaterialPreview({ uploadResult }) {
  if (!uploadResult) return null;

  return (
    <div className="result">
      <h2>Material</h2>
      {uploadResult.materials && (
        <div className="hint">
          {uploadResult.materials.map((m) => m.filename).join(", ")}
        </div>
      )}
      <h3>Section Titles</h3>
      <ul>
        {uploadResult.section_titles.length === 0 && <li>(none found)</li>}
        {uploadResult.section_titles.map((t, i) => (
          <li key={i}>{t}</li>
        ))}
      </ul>
      <h3>Content Preview</h3>
      <pre className="preview">{uploadResult.preview}</pre>
    </div>
  );
}
