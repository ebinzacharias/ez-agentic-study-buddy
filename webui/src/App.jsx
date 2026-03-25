import React, { useMemo, useState } from "react";

export default function App() {
  const apiBaseUrl = useMemo(
    () => import.meta.env.VITE_API_URL || "http://localhost:8000",
    []
  );

  const [sessionId, setSessionId] = useState("");
  const [topic, setTopic] = useState("");
  const [suggestedTopic, setSuggestedTopic] = useState("");
  const [difficulty, setDifficulty] = useState("beginner");

  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [uploadResult, setUploadResult] = useState(null);
  const [planResult, setPlanResult] = useState(null);
  const [maxConcepts, setMaxConcepts] = useState(10);

  const [selectedConcept, setSelectedConcept] = useState("");
  const [teachContext, setTeachContext] = useState("");
  const [teachResult, setTeachResult] = useState(null);

  const resetErrors = () => setError("");

  const resetSession = () => {
    setSessionId("");
    setTopic("");
    setSuggestedTopic("");
    setFile(null);
    setUploadResult(null);
    setPlanResult(null);
    setTeachResult(null);
    setSelectedConcept("");
    setTeachContext("");
    resetErrors();
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0] || null);
    setUploadResult(null);
    setPlanResult(null);
    setTeachResult(null);
    resetErrors();
  };

  const uploadAndCreateSession = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    resetErrors();
    setUploadResult(null);
    setPlanResult(null);
    setTeachResult(null);
    setSelectedConcept("");

    const formData = new FormData();
    formData.append("files", file);
    formData.append("difficulty_level", difficulty);
    if (topic.trim()) {
      formData.append("topic", topic.trim());
    }
    try {
      const resp = await fetch(`${apiBaseUrl}/session/from-upload`, {
        method: "POST",
        body: formData,
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "Upload failed");
      setSessionId(data.session_id);
      setUploadResult(data);
      if (data.topic) setTopic(data.topic);
      if (data.suggested_topic) setSuggestedTopic(data.suggested_topic);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const runPlan = async () => {
    if (!sessionId) {
      setError("Upload material first.");
      return;
    }
    setLoading(true);
    resetErrors();
    setPlanResult(null);
    setTeachResult(null);
    try {
      const resp = await fetch(`${apiBaseUrl}/session/${sessionId}/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic,
          difficulty_level: difficulty,
          max_concepts: maxConcepts,
        }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "Plan failed");
      setPlanResult(data);
      const first = data.concepts?.[0]?.concept_name;
      if (first) setSelectedConcept(first);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const runTeach = async () => {
    if (!sessionId) {
      setError("Upload material first.");
      return;
    }
    if (!selectedConcept.trim()) {
      setError("Pick a concept to teach.");
      return;
    }
    setLoading(true);
    resetErrors();
    setTeachResult(null);
    try {
      const resp = await fetch(`${apiBaseUrl}/session/${sessionId}/teach`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          concept_name: selectedConcept,
          difficulty_level: difficulty,
          context: teachContext,
        }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "Teach failed");
      setTeachResult(data);
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

      {/* Step 1: Upload-first flow */}
      {!sessionId && (
        <div className="card">
          <form onSubmit={uploadAndCreateSession} className="upload-form">
            <input
              type="file"
              accept=".txt,.md,.markdown,.pdf,.json"
              onChange={handleFileChange}
            />
            <button type="submit" disabled={!file || loading}>
              {loading ? "Working..." : "Upload & Start"}
            </button>
          </form>
          <div className="hint">
            For PDFs, install <code>pymupdf</code> on the API server.
          </div>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {/* Step 2: Show material and session controls after upload */}
      {uploadResult && (
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
      )}

      {/* Step 3: Topic/difficulty/session controls after upload */}
      {sessionId && (
        <>
          <div className="card">
            <div className="row">
              <div className="field">
                <label>Topic (suggested)</label>
                <input
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., Python Basics"
                />
              </div>

              <div className="field">
                <label>Difficulty</label>
                <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div className="field actions">
                <label>&nbsp;</label>
                <button type="button" onClick={resetSession} disabled={loading}>
                  New Upload
                </button>
              </div>
            </div>
            <div className="pill">
              Session: {sessionId}
              {suggestedTopic ? ` · Suggested: ${suggestedTopic}` : ""}
            </div>
          </div>

          <div className="card">
            <div className="row">
              <div className="field">
                <label>Max concepts</label>
                <input
                  type="number"
                  min="1"
                  max="25"
                  value={maxConcepts}
                  onChange={(e) => setMaxConcepts(Number(e.target.value) || 10)}
                />
              </div>
              <div className="field actions">
                <label>&nbsp;</label>
                <button type="button" onClick={runPlan} disabled={!sessionId || loading}>
                  Plan Learning Path
                </button>
              </div>
            </div>
            <div className="hint">
              Planning/teaching uses an LLM. Ensure your API environment has <code>GROQ_API_KEY</code> set.
            </div>
          </div>

          {planResult && (
            <div className="result">
              <h2>Learning Path</h2>
              <ul>
                {planResult.concepts?.map((c) => (
                  <li key={`${c.order}-${c.concept_name}`}>{c.order}. {c.concept_name}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="card">
            <div className="row">
              <div className="field">
                <label>Concept</label>
                <select
                  value={selectedConcept}
                  onChange={(e) => setSelectedConcept(e.target.value)}
                  disabled={!planResult}
                >
                  <option value="">Select a concept</option>
                  {(planResult?.concepts || []).map((c) => (
                    <option key={c.concept_name} value={c.concept_name}>
                      {c.concept_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="field actions">
                <label>&nbsp;</label>
                <button type="button" onClick={runTeach} disabled={!selectedConcept || loading}>
                  Teach
                </button>
              </div>
            </div>

            <div className="field">
              <label>Context (optional)</label>
              <textarea
                value={teachContext}
                onChange={(e) => setTeachContext(e.target.value)}
                placeholder="What do you already know? Where did you get stuck?"
              />
            </div>
          </div>

          {teachResult && (
            <div className="result">
              <h2>Teaching: {teachResult.concept_name}</h2>
              <pre className="preview">{teachResult.explanation}</pre>
            </div>
          )}
        </>
      )}

      <footer>
        <small>EZ-Agentic Study Buddy &copy; 2026</small>
      </footer>
    </div>
  );
}
