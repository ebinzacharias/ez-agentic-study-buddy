import React, { useEffect, useMemo, useState } from "react";
import { fmtError, isSessionExpired } from "./api";
import LandingHero from "./components/LandingHero";
import UploadStep from "./components/UploadStep";
import MaterialPreview from "./components/MaterialPreview";
import SessionControls from "./components/SessionControls";
import PlanStep from "./components/PlanStep";
import TeachStep from "./components/TeachStep";
import QuizStep from "./components/QuizStep";
import NextActionBanner from "./components/NextActionBanner";

const LEARN_TABS = ["plan", "teach", "quiz"];

export default function App() {
  const apiBaseUrl = useMemo(
    () => import.meta.env.VITE_API_URL || "http://localhost:8000",
    []
  );

  const showRuntimeBadge = import.meta.env.VITE_SHOW_RUNTIME_BADGE === "true";

  const [activeLearnTab, setActiveLearnTab] = useState("plan");

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
    setActiveLearnTab("plan");
    resetErrors();
  };

  const clearDownstream = (...keep) => {
    if (!keep.includes("plan")) setPlanResult(null);
    if (!keep.includes("teach")) setTeachResult(null);
    if (!keep.includes("quiz")) {
      setQuizResult(null);
      setQuizAnswers({});
    }
    if (!keep.includes("eval")) setEvalResult(null);
  };

  useEffect(() => {
    if (planResult) {
      setActiveLearnTab((t) => (t === "plan" ? "teach" : t));
    }
  }, [planResult]);

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
    if (!sessionId) {
      setError("Upload material first.");
      return;
    }
    setLoading(true);
    resetErrors();
    clearDownstream();
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
    if (!sessionId) {
      setError("Upload material first.");
      return;
    }
    const conceptToQuiz = quizConcept.trim() || selectedConcept.trim();
    if (!conceptToQuiz) {
      setError("Enter a concept to quiz on.");
      return;
    }
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
    if (!quizResult) {
      setError("Generate a quiz first.");
      return;
    }
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
      setActiveLearnTab("teach");
    } else if (action === "generate_quiz") {
      if (concept) setQuizConcept(concept);
      setQuizResult(null);
      setQuizAnswers({});
      setEvalResult(null);
      setNextAction(null);
      setActiveLearnTab("quiz");
    } else if (action === "plan_learning_path") {
      setNextAction(null);
      setActiveLearnTab("plan");
      runPlan();
    }
  };

  const selectConceptFromRail = (name) => {
    setSelectedConcept(name);
    setActiveLearnTab("teach");
    setTeachResult(null);
    setQuizResult(null);
    setQuizAnswers({});
    setEvalResult(null);
    setQuizConcept("");
  };

  const stepperState = (id) => {
    const current = LEARN_TABS.indexOf(activeLearnTab);
    const idx = LEARN_TABS.indexOf(id);
    if (idx === current) return "current";
    if (id === "plan" && planResult) return "complete";
    if (id === "teach" && teachResult && activeLearnTab === "quiz") return "complete";
    return "upcoming";
  };

  let mobilePrimary = null;
  if (sessionId && !loading) {
    if (activeLearnTab === "plan") {
      mobilePrimary = { label: "Plan learning path", onClick: runPlan, disabled: false };
    } else if (activeLearnTab === "teach") {
      mobilePrimary = {
        label: "Teach concept",
        onClick: runTeach,
        disabled: !selectedConcept.trim(),
      };
    } else if (!quizResult) {
      mobilePrimary = {
        label: "Generate quiz",
        onClick: runQuiz,
        disabled: !(quizConcept.trim() || selectedConcept.trim()),
      };
    } else {
      mobilePrimary = {
        label: "Submit and evaluate",
        onClick: runEvaluate,
        disabled: false,
      };
    }
  }

  return (
    <div className="app-shell">
      <a href="#main-workspace" className="skip-link">
        Skip to main content
      </a>

      <header className="site-header">
        <div className="site-header__inner">
          <div className="site-header__balance" aria-hidden="true" />
          <div className="site-header__focus">
            <div className="brand brand--showpiece">
              <p className="brand__tagline">
                Upload. Plan. Learn. Grounded in your data.
              </p>
              <h1 className="brand__title">
                <span className="brand__title-ez" aria-label="Easy">
                  EZ
                </span>
                <span className="brand__title-rest">Study Lab</span>
              </h1>
            </div>
          </div>
          <aside className="site-header__aside" aria-label="System status">
            <span className="header-version-badge">v1.0 · Active</span>
            {showRuntimeBadge ? (
              <span className="env-badge" title="Runtime hint from build env">
                Local · Groq
              </span>
            ) : null}
          </aside>
        </div>
      </header>

      {sessionId ? (
        <div className="stepper-container">
          <nav className="stepper" aria-label="Learning workflow">
            {LEARN_TABS.map((id) => {
              const labels = {
                plan: "Plan",
                teach: "Teach",
                quiz: "Quiz",
              };
              const state = stepperState(id);
              const num = LEARN_TABS.indexOf(id) + 1;
              return (
                <button
                  key={id}
                  type="button"
                  className={`stepper__step stepper__step--${state}`}
                  aria-current={state === "current" ? "step" : undefined}
                  aria-label={`${labels[id]} step${state === "complete" ? ", completed" : ""}${state === "current" ? ", current" : ""}`}
                  onClick={() => setActiveLearnTab(id)}
                >
                  <span className="stepper__index" aria-hidden="true">
                    {state === "complete" ? "✓" : num}
                  </span>
                  <span className="stepper__label">{labels[id]}</span>
                </button>
              );
            })}
          </nav>
        </div>
      ) : null}

      <main id="main-workspace" className="app-main">
        <div className={`app-grid ${sessionId ? "app-grid--with-rail" : ""}`}>
          {!sessionId ? (
            <section className="workspace workspace--onboarding" aria-labelledby="onboarding-heading">
              <h2 id="onboarding-heading" className="sr-only">
                Start by uploading material
              </h2>
              <LandingHero />
              <UploadStep
                file={file}
                loading={loading}
                onFileChange={handleFileChange}
                onSubmit={uploadAndCreateSession}
              />
              {error ? (
                <div className="error error--stage" role="alert">
                  {error}
                </div>
              ) : null}
              <MaterialPreview uploadResult={uploadResult} />
            </section>
          ) : null}

          {sessionId ? (
            <>
              <aside className="session-rail" aria-label="Session and material">
                {error ? (
                  <div className="error error--rail" role="alert">
                    {error}
                  </div>
                ) : null}
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

                {planResult?.concepts?.length ? (
                  <div className="concept-rail card card--rail">
                    <h2 className="concept-rail__title">Learning path</h2>
                    <ol className="concept-rail__list">
                      {planResult.concepts.map((c) => (
                        <li key={`${c.order}-${c.concept_name}`}>
                          <button
                            type="button"
                            className={`concept-rail__btn ${selectedConcept === c.concept_name ? "is-active" : ""}`}
                            onClick={() => selectConceptFromRail(c.concept_name)}
                          >
                            <span className="concept-rail__order">{c.order}</span>
                            <span className="concept-rail__name">{c.concept_name}</span>
                          </button>
                        </li>
                      ))}
                    </ol>
                    <p className="concept-rail__hint">
                      Select a concept to focus teach mode. Switch to Quiz when ready.
                    </p>
                  </div>
                ) : null}

                {uploadResult ? (
                  <details className="rail-details">
                    <summary className="rail-details__summary">Material preview</summary>
                    <MaterialPreview
                      uploadResult={uploadResult}
                      className="result--compact"
                    />
                  </details>
                ) : null}
              </aside>

              <section
                className="main-stage"
                aria-labelledby="stage-heading"
              >
                <h2 id="stage-heading" className="sr-only">
                  Active study step
                </h2>

                <NextActionBanner
                  nextAction={nextAction}
                  loading={loading}
                  onFollow={followNextAction}
                />

                <div className="stage-panels">
                  <div
                    id="panel-plan"
                    role="tabpanel"
                    hidden={activeLearnTab !== "plan"}
                    className="stage-panel"
                  >
                    {activeLearnTab === "plan" ? (
                      <PlanStep
                        maxConcepts={maxConcepts}
                        planResult={planResult}
                        loading={loading}
                        disabled={!sessionId}
                        onMaxConceptsChange={setMaxConcepts}
                        onPlan={runPlan}
                      />
                    ) : null}
                  </div>

                  <div
                    id="panel-teach"
                    role="tabpanel"
                    hidden={activeLearnTab !== "teach"}
                    className="stage-panel"
                  >
                    {activeLearnTab === "teach" ? (
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
                    ) : null}
                  </div>

                  <div
                    id="panel-quiz"
                    role="tabpanel"
                    hidden={activeLearnTab !== "quiz"}
                    className="stage-panel"
                  >
                    {activeLearnTab === "quiz" ? (
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
                    ) : null}
                  </div>
                </div>
              </section>
            </>
          ) : null}
        </div>
      </main>

      {sessionId && mobilePrimary ? (
        <div className="mobile-sticky-actions" role="region" aria-label="Primary action">
          <button
            type="button"
            className="mobile-sticky-actions__btn"
            onClick={() => mobilePrimary.onClick()}
            disabled={mobilePrimary.disabled}
          >
            {loading ? "Working…" : mobilePrimary.label}
          </button>
        </div>
      ) : null}

      <footer className="site-footer">
        <p>
          EZ Study Lab — adaptive learning studio. © {new Date().getFullYear()}
        </p>
        <p className="site-footer__meta">Open materials, local session, rule-based scoring.</p>
      </footer>
    </div>
  );
}
