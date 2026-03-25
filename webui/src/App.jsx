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

  // Quiz state
  const [numQuestions, setNumQuestions] = useState(3);
  const [quizResult, setQuizResult] = useState(null);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [evalResult, setEvalResult] = useState(null);

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
    setQuizResult(null);
    setQuizAnswers({});
    setEvalResult(null);
    resetErrors();
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0] || null);
    setUploadResult(null);
    setPlanResult(null);
    setTeachResult(null);
    setQuizResult(null);
    setQuizAnswers({});
    setEvalResult(null);
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
    setQuizResult(null);
    setQuizAnswers({});
    setEvalResult(null);
    setSelectedConcept("");
    const formData = new FormData();
    formData.append("files", file);
    formData.append("difficulty_level", difficulty);
    if (topic.trim()) formData.append("topic", topic.trim());
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
    if (!sessionId) { setError("Upload material first."); return; }
    setLoading(true);
    resetErrors();
    setPlanResult(null);
    setTeachResult(null);
    setQuizResult(null);
    setQuizAnswers({});
    setEvalResult(null);
    try {
      const resp = await fetch(`${apiBaseUrl}/session/${sessionId}/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, difficulty_level: difficulty, max_concepts: maxConcepts }),
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
    if (!sessionId) { setError("Upload material first."); return; }
    if (!selectedConcept.trim()) { setError("Pick a concept to teach."); return; }
    setLoading(true);
    resetErrors();
    setTeachResult(null);
    setQuizResult(null);
    setQuizAnswers({});
    setEvalResult(null);
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

  const runQuiz = async () => {
    if (!sessionId) { setError("Upload material first."); return; }
    if (!selectedConcept.trim()) { setError("Pick a concept to quiz on."); return; }
    setLoading(true);
    resetErrors();
    setQuizResult(null);
    setQuizAnswers({});
    setEvalResult(null);
    try {
      const resp = await fetch(`${apiBaseUrl}/session/${sessionId}/quiz`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          concept_name: selectedConcept,
          difficulty_level: difficulty,
          num_questions: numQuestions,
          question_types: "multiple_choice,short_answer",
        }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "Quiz generation failed");
      setQuizResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const runEvaluate = async () => {
    if (!quizResult) { setError("Generate a quiz first."); return; }
    setLoading(true);
    resetErrors();
    setEvalResult(null);
    const answers = quizResult.questions.map((q) => ({
      question_number: q.question_number,
      answer: quizAnswers[q.question_number] || "",
    }));
    try {
      const resp = await fetch(`${apiBaseUrl}/session/${sessionId}/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          quiz_data: JSON.stringify(quizResult),
          learner_answers: JSON.stringify({ answers }),
        }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "Evaluation failed");
      setEvalResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>EZ-Agentic Study Buddy</h1>
      <div className="muted">API: {apiBaseUrl}</div>

      {/* Step 1: Upload */}
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
            Supported: TXT, MD, PDF, JSON. For PDFs, install <code>pymupdf</code> on the API server.
          </div>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {/* Step 2: Material preview */}
      {uploadResult && (
        <div className="result">
          <h2>Material</h2>
          {uploadResult.materials && (
            <div className="hint">{uploadResult.materials.map((m) => m.filename).join(", ")}</div>
          )}
          <h3>Section Titles</h3>
          <ul>
            {uploadResult.section_titles.length === 0 && <li>(none found)</li>}
            {uploadResult.section_titles.map((t, i) => <li key={i}>{t}</li>)}
          </ul>
          <h3>Content Preview</h3>
          <pre className="preview">{uploadResult.preview}</pre>
        </div>
      )}

      {/* Steps 3+: Session controls */}
      {sessionId && (
        <>
          {/* Topic / Difficulty / Reset */}
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
                <button type="button" onClick={resetSession} disabled={loading}>New Upload</button>
              </div>
            </div>
            <div className="pill">
              Session: {sessionId}
              {suggestedTopic ? ` Â· Suggested: ${suggestedTopic}` : ""}
            </div>
          </div>

          {/* Plan */}
          <div className="card">
            <div className="row">
              <div className="field">
                <label>Max concepts</label>
                <input
                  type="number" min="1" max="25" value={maxConcepts}
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
              Uses an LLM â€” ensure <code>GROQ_API_KEY</code> is set.
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

          {/* Teach */}
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
                    <option key={c.concept_name} value={c.concept_name}>{c.concept_name}</option>
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

          {/* Quiz */}
          <div className="card">
            <div className="row">
              <div className="field">
                <label>Questions</label>
                <input
                  type="number" min="1" max="10" value={numQuestions}
                  onChange={(e) => setNumQuestions(Number(e.target.value) || 3)}
                />
              </div>
              <div className="field actions">
                <label>&nbsp;</label>
                <button type="button" onClick={runQuiz} disabled={!selectedConcept || loading}>
                  Generate Quiz
                </button>
              </div>
            </div>
            <div className="hint">Generates a quiz on the selected concept.</div>
          </div>

          {quizResult && (
            <div className="result">
              <h2>Quiz: {quizResult.concept_name}</h2>
              {quizResult.questions?.map((q) => (
                <div key={q.question_number} className="quiz-question">
                  <p><strong>Q{q.question_number}.</strong> {q.question}</p>
                  {q.options ? (
                    <div className="quiz-options">
                      {q.options.map((opt, i) => (
                        <label key={i} className="quiz-option">
                          <input
                            type="radio"
                            name={`q${q.question_number}`}
                            value={opt}
                            checked={quizAnswers[q.question_number] === opt}
                            onChange={() => setQuizAnswers((a) => ({ ...a, [q.question_number]: opt }))}
                          />
                          {opt}
                        </label>
                      ))}
                    </div>
                  ) : (
                    <textarea
                      className="quiz-input"
                      placeholder="Your answer..."
                      value={quizAnswers[q.question_number] || ""}
                      onChange={(e) => setQuizAnswers((a) => ({ ...a, [q.question_number]: e.target.value }))}
                    />
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={runEvaluate}
                disabled={loading}
                style={{ marginTop: "1rem" }}
              >
                {loading ? "Evaluating..." : "Submit & Evaluate"}
              </button>
            </div>
          )}

          {/* Evaluation Results */}
          {evalResult && (
            <div className="result">
              <h2>Results &mdash; {evalResult.overall_percentage}%</h2>
              <div className="score-bar">
                <div
                  className="score-fill"
                  style={{ width: `${evalResult.overall_percentage}%` }}
                />
              </div>
              <p className="muted">
                {evalResult.questions_evaluated} / {evalResult.total_questions} answered &middot;{" "}
                Score: {evalResult.total_score} / {evalResult.total_questions}
              </p>
              {evalResult.scores?.map((s) => {
                const q = quizResult?.questions?.find((qq) => qq.question_number === s.question_number);
                return (
                  <div key={s.question_number} className={`eval-item ${s.is_correct ? "correct" : "incorrect"}`}>
                    <strong>Q{s.question_number}</strong> &mdash; {s.feedback} ({Math.round(s.score * 100)}%)
                    {!s.is_correct && q?.correct_answer && (
                      <div className="correct-answer">Correct answer: <em>{q.correct_answer}</em></div>
                    )}
                  </div>
                );
              })}
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

