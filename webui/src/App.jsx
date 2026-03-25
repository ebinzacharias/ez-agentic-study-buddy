import React, { useMemo, useState } from "react";
import { fmtError, isSessionExpired } from "./api";
import UploadStep from "./components/UploadStep";
import MaterialPreview from "./components/MaterialPreview";
import SessionControls from "./components/SessionControls";
import PlanStep from "./components/PlanStep";
import TeachStep from "./components/TeachStep";
import QuizStep from "./components/QuizStep";
import NextActionBanner from "./components/NextActionBanner";

export default function App() {
  const apiBaseUrl = useMemo(
    () => import.meta.env.VITE_API_URL || "http://localhost:8000",
    []
  );

  // ── Session state ──────────────────────────────────────────────
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

  const [quizConcept, setQuizConcept] = useState("");
  const [numQuestions, setNumQuestions] = useState(3);
  const [quizResult, setQuizResult] = useState(null);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [evalResult, setEvalResult] = useState(null);

  const [nextAction, setNextAction] = useState(null);

  // ── Helpers ────────────────────────────────────────────────────
  const resetErrors = () => setError("");

  const handleApiError = (data) => {
    if (isSessionExpired(data)) resetSession();
    throw new Error(fmtError(data));
  };

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
    setQuizConcept("");
    setQuizResult(null);
    setQuizAnswers({});
    setEvalResult(null);
    setNextAction(null);
    resetErrors();
  };

  const clearDownstream = (...keep) => {
    if (!keep.includes("plan")) setPlanResult(null);
    if (!keep.includes("teach")) setTeachResult(null);
    if (!keep.includes("quiz")) { setQuizResult(null); setQuizAnswers({}); }
    if (!keep.includes("eval")) setEvalResult(null);
  };

  // ── API actions ────────────────────────────────────────────────
  const handleFileChange = (e) => {
    setFile(e.target.files[0] || null);
    clearDownstream();
    resetErrors();
  };

  const uploadAndCreateSession = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    resetErrors();
    clearDownstream();
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
      if (!resp.ok) throw new Error(fmtError(data));
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
    clearDownstream();
    try {
      const resp = await fetch(`${apiBaseUrl}/session/${sessionId}/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, difficulty_level: difficulty, max_concepts: maxConcepts }),
      });
      const data = await resp.json();
      if (!resp.ok) handleApiError(data);
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
    clearDownstream("plan");
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
      if (!resp.ok) handleApiError(data);
      setTeachResult(data);
      setNextAction(data.next_action || null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const runQuiz = async () => {
    if (!sessionId) { setError("Upload material first."); return; }
    const conceptToQuiz = quizConcept.trim() || selectedConcept.trim();
    if (!conceptToQuiz) { setError("Enter a concept to quiz on."); return; }
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
          concept_name: conceptToQuiz,
          difficulty_level: difficulty,
          num_questions: numQuestions,
          question_types: "multiple_choice",
        }),
      });
      const data = await resp.json();
      if (!resp.ok) handleApiError(data);
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
      if (!resp.ok) handleApiError(data);
      setEvalResult(data);
      setNextAction(data.next_action || null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const followNextAction = () => {
    if (!nextAction) return;
    const { action, concept } = nextAction;
    if (action === "teach_concept" || action === "set_current_concept" || action === "add_concept") {
      if (concept) setSelectedConcept(concept);
      setTeachResult(null);
      setQuizResult(null);
      setQuizAnswers({});
      setEvalResult(null);
      setNextAction(null);
    } else if (action === "generate_quiz") {
      if (concept) setQuizConcept(concept);
      setQuizResult(null);
      setQuizAnswers({});
      setEvalResult(null);
      setNextAction(null);
    } else if (action === "plan_learning_path") {
      setNextAction(null);
      runPlan();
    }
  };

  // ── Render ─────────────────────────────────────────────────────
  return (
    <div className="container">
      <h1>EZ Study Buddy</h1>
      <div className="muted">Upload your materials. Learn adaptively.</div>

      {!sessionId && (
        <UploadStep
          file={file}
          difficulty={difficulty}
          topic={topic}
          loading={loading}
          onFileChange={handleFileChange}
          onDifficultyChange={setDifficulty}
          onTopicChange={setTopic}
          onSubmit={uploadAndCreateSession}
        />
      )}

      {error && <div className="error">{error}</div>}

      <MaterialPreview uploadResult={uploadResult} />

      {sessionId && (
        <>
          <SessionControls
            sessionId={sessionId}
            topic={topic}
            suggestedTopic={suggestedTopic}
            difficulty={difficulty}
            loading={loading}
            onTopicChange={setTopic}
            onDifficultyChange={setDifficulty}
            onReset={resetSession}
          />

          <PlanStep
            maxConcepts={maxConcepts}
            planResult={planResult}
            loading={loading}
            disabled={!sessionId}
            onMaxConceptsChange={setMaxConcepts}
            onPlan={runPlan}
          />

          <TeachStep
            selectedConcept={selectedConcept}
            teachContext={teachContext}
            teachResult={teachResult}
            planResult={planResult}
            loading={loading}
            onConceptChange={setSelectedConcept}
            onContextChange={setTeachContext}
            onTeach={runTeach}
          />

          <QuizStep
            topic={topic}
            quizConcept={quizConcept}
            selectedConcept={selectedConcept}
            numQuestions={numQuestions}
            quizResult={quizResult}
            quizAnswers={quizAnswers}
            evalResult={evalResult}
            planResult={planResult}
            loading={loading}
            onQuizConceptChange={setQuizConcept}
            onNumQuestionsChange={setNumQuestions}
            onAnswerChange={(qNum, opt) =>
              setQuizAnswers((a) => ({ ...a, [qNum]: opt }))
            }
            onGenerateQuiz={runQuiz}
            onEvaluate={runEvaluate}
            onSetQuizConcept={setQuizConcept}
          />

          <NextActionBanner
            nextAction={nextAction}
            loading={loading}
            onFollow={followNextAction}
          />
        </>
      )}

      <footer>
        <small>EZ Study Buddy &mdash; AI-powered adaptive learning &copy; 2026</small>
      </footer>
    </div>
  );
}

