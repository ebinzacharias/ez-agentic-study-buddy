import React, { useState } from "react";

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const apiBaseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError("");
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setResult(null);
    setError("");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const resp = await fetch(`${apiBaseUrl}/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "Upload failed");
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>EZ-Agentic Content Loader</h1>
      <div className="muted">API: {apiBaseUrl}</div>
      <form onSubmit={handleUpload} className="upload-form">
        <input
          type="file"
          accept=".txt,.md,.markdown,.pdf,.json"
          onChange={handleFileChange}
        />
        <button type="submit" disabled={!file || loading}>
          {loading ? "Uploading..." : "Upload & Parse"}
        </button>
      </form>
      {error && <div className="error">{error}</div>}
      {result && (
        <div className="result">
          <h2>Title: {result.title || "(untitled)"}</h2>
          <h3>Section Titles</h3>
          <ul>
            {result.section_titles.length === 0 && <li>(none found)</li>}
            {result.section_titles.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
          <h3>Content Preview</h3>
          <pre className="preview">{result.preview}</pre>
        </div>
      )}
      <footer>
        <small>EZ-Agentic Study Buddy &copy; 2026</small>
      </footer>
    </div>
  );
}
