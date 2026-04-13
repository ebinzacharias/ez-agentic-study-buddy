import React, { useMemo, useState } from "react";
import {
  createUserFacingApiError,
  errorDisplayFromCaughtMessage,
  isSessionExpired,
} from "./api";

function DocIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"
        stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
      />
      <polyline
        points="14 2 14 8 20 8"
        stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
      />
    </svg>
  );
}

function LoadingScreen({ file }) {
  return (
    <div className="lp-loading" role="status" aria-label="Starting session">
      <div className="lp-loading__inner">
        <div className="lp-loading__ring" aria-hidden="true" />

        {file ? (
          <div className="lp-loading__file-badge">
            <span className="lp-loading__file-icon"><DocIcon /></span>
            <span className="lp-loading__file-name">{file.name}</span>
          </div>
        ) : null}

        <h2 className="lp-loading__title">Building your session…</h2>
        <p className="lp-loading__sub">
          Reading your file and setting up the workspace.
          <br />Usually takes a few seconds.
        </p>

        <div className="lp-loading__track" aria-hidden="true">
          <span className="lp-loading__step lp-loading__step--active">
            <span className="lp-loading__dot" />
            <span className="lp-loading__step-lbl">Upload</span>
          </span>
          <span className="lp-loading__line" />
          <span className="lp-loading__step lp-loading__step--active lp-loading__step--delay">
            <span className="lp-loading__dot" />
            <span className="lp-loading__step-lbl">Process</span>
          </span>
          <span className="lp-loading__line" />
          <span className="lp-loading__step">
            <span className="lp-loading__dot" />
            <span className="lp-loading__step-lbl">Launch</span>
          </span>
        </div>
      </div>
    </div>
  );
}

import UploadStep from "./components/UploadStep";
import MaterialPreview from "./components/MaterialPreview";
import SessionControls from "./components/SessionControls";
import PlanStep from "./components/PlanStep";
import TeachStep from "./components/TeachStep";
import QuizStep from "./components/QuizStep";
import NextActionBanner from "./components/NextActionBanner";
import ModeSwitcher from "./components/ModeSwitcher";
import QuizProgressTracker from "./components/QuizProgressTracker";

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
  const [error, setError] = useState(null);

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

  const resetErrors = () => setError(null);

  const failResponse = (data) => {
    if (isSessionExpired(data)) {
      resetSession();
      const err = new Error("session expired");
      err.sessionExpired = true;
      throw err;
    }
    throw createUserFacingApiError(data);
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
      if (!resp.ok) failResponse(data);
      setSessionId(data.session_id);
      setUploadResult(data);
      if (data.topic) setTopic(data.topic);
      if (data.suggested_topic) setSuggestedTopic(data.suggested_topic);
    } catch (err) {
      if (err.sessionExpired) return;
      setError(err.userFacing ?? errorDisplayFromCaughtMessage(err.message));
    } finally {
      setLoading(false);
    }
  };

  const runPlan = async (maxConceptsOverride) => {
    if (!sessionId) {
      setError({ title: "Upload material first" });
      return;
    }
    const maxConceptsToUse =
      typeof maxConceptsOverride === "number" && !Number.isNaN(maxConceptsOverride)
        ? maxConceptsOverride
        : maxConcepts;
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
          max_concepts: maxConceptsToUse,
        }),
      });
      const data = await resp.json();
      if (!resp.ok) failResponse(data);
      setPlanResult(data);
      const first = data.concepts?.[0]?.concept_name;
      if (first) setSelectedConcept(first);
    } catch (err) {
      if (err.sessionExpired) return;
      setError(err.userFacing ?? errorDisplayFromCaughtMessage(err.message));
    } finally {
      setLoading(false);
    }
  };

  const runTeach = async () => {
    if (!sessionId) {
      setError({ title: "Upload material first" });
      return;
    }
    if (!selectedConcept.trim()) {
      setError({ title: "Pick a concept to learn" });
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
      if (!resp.ok) failResponse(data);
      setTeachResult(data);
      setNextAction(data.next_action || null);
    } catch (err) {
      if (err.sessionExpired) return;
      setError(err.userFacing ?? errorDisplayFromCaughtMessage(err.message));
    } finally {
      setLoading(false);
    }
  };

  const runQuiz = async () => {
    if (!sessionId) {
      setError({ title: "Upload material first" });
      return;
    }
    const conceptToQuiz = quizConcept.trim() || selectedConcept.trim();
    if (!conceptToQuiz) {
      setError({ title: "Enter a concept to quiz on" });
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
      if (!resp.ok) failResponse(data);
      setQuizResult(data);
    } catch (err) {
      if (err.sessionExpired) return;
      setError(err.userFacing ?? errorDisplayFromCaughtMessage(err.message));
    } finally {
      setLoading(false);
    }
  };

  const runEvaluate = async () => {
    if (!quizResult) {
      setError({ title: "Generate a quiz first" });
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
      if (!resp.ok) failResponse(data);
      setEvalResult(data);
      setNextAction(data.next_action || null);
    } catch (err) {
      if (err.sessionExpired) return;
      setError(err.userFacing ?? errorDisplayFromCaughtMessage(err.message));
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

  const clearQuizProgress = () => {
    setQuizResult(null);
    setQuizAnswers({});
    setEvalResult(null);
    resetErrors();
  };

  let mobilePrimary = null;
  if (sessionId && !loading) {
    if (activeLearnTab === "plan") {
      if (planResult?.concepts?.length) {
        mobilePrimary = {
          label: loading ? "Generating…" : "Go to Learn",
          onClick: () => setActiveLearnTab("teach"),
          disabled: loading,
        };
      } else {
        mobilePrimary = {
          label: loading ? "Generating…" : "Generate learning path",
          onClick: () => runPlan(),
          disabled: loading,
        };
      }
    } else if (activeLearnTab === "teach") {
      mobilePrimary = {
        label: "Learn concept",
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

      <div className="app-top-sticky">
        <header className="site-header">
          <div className="site-header__inner">
            <div className="site-header__balance" aria-hidden="true" />
            <div className="site-header__focus">
              <div className="brand brand--showpiece">
                <p className="brand__tagline">
                  Upload. Path. Learn. Grounded in your data.
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
          <SessionControls
            sessionId={sessionId}
            apiBaseUrl={apiBaseUrl}
            uploadResult={uploadResult}
            topic={topic}
            suggestedTopic={suggestedTopic}
            difficulty={difficulty}
            loading={loading}
            onDifficultyChange={setDifficulty}
            onReset={resetSession}
          />
        ) : null}

        {sessionId ? (
          <ModeSwitcher
            activeMode={activeLearnTab}
            onChange={setActiveLearnTab}
          />
        ) : null}
      </div>

      <main id="main-workspace" className="app-main">
        <div
          className={`app-grid ${sessionId ? `app-grid--with-session app-grid--mode-${activeLearnTab === "teach" ? "learn" : activeLearnTab}` : ""}`}
        >
          {!sessionId ? (
            <section className="workspace workspace--onboarding" aria-labelledby="onboarding-heading">
              {loading ? (
                <LoadingScreen file={file} />
              ) : null}

              {/* ── Above-fold split: hero copy | upload card ── */}
              <div className={`lp-fold${loading ? " lp-fold--hidden" : ""}`}>
                <div className="lp-fold__copy">
                  <h2 id="onboarding-heading" className="lp-fold__title">
                    Turn any file into{" "}
                    <span className="lp-fold__title-accent">
                      a study session.
                    </span>
                  </h2>
                  <p className="lp-fold__sub">
                    Drop a document. Pick what to focus on. Every explanation
                    and quiz question comes directly from your file — nothing
                    gets invented or pulled from somewhere else.
                  </p>
                  <ol className="lp-steps" aria-label="How it works">
                    {[
                      { label: "Path",  desc: "Ordered concept list built from your file",    color: "#4FD1C5" },
                      { label: "Learn", desc: "Explanations grounded in your own text",        color: "#818CF8" },
                      { label: "Quiz",  desc: "Questions drawn from the same source",          color: "#34D399" },
                    ].map((s, i) => (
                      <li
                        key={s.label}
                        className="lp-step"
                        style={{ "--step-color": s.color, "--step-i": i }}
                      >
                        <span className="lp-step__label">{s.label}</span>
                        <span className="lp-step__desc">{s.desc}</span>
                      </li>
                    ))}
                  </ol>
                </div>

                <div className="lp-fold__form">
                  <UploadStep
                    file={file}
                    loading={loading}
                    onFileChange={handleFileChange}
                    onSubmit={uploadAndCreateSession}
                  />
                  {error ? (
                    <div
                      className="workspace-error workspace-error--stage lp-fold__error"
                      role="alert"
                    >
                      <p className="workspace-error__title">{error.title}</p>
                      {error.detail ? (
                        <p className="workspace-error__detail">{error.detail}</p>
                      ) : null}
                    </div>
                  ) : null}
                </div>
              </div>

              <MaterialPreview uploadResult={uploadResult} />
            </section>
          ) : null}

          {sessionId ? (
            <>
              {activeLearnTab !== "teach" ? (
                <aside
                  className={`session-rail ${activeLearnTab === "quiz" ? "session-rail--quiz" : "session-rail--plan"}`}
                  aria-label={
                    activeLearnTab === "quiz"
                      ? "Quiz progress"
                      : "Learning path and materials"
                  }
                >
                  {activeLearnTab === "quiz" ? (
                    <>
                      {error ? (
                        <div className="workspace-error workspace-error--rail" role="alert">
                          <p className="workspace-error__title">{error.title}</p>
                          {error.detail ? (
                            <p className="workspace-error__detail">{error.detail}</p>
                          ) : null}
                        </div>
                      ) : null}
                      <QuizProgressTracker
                        quizResult={quizResult}
                        quizAnswers={quizAnswers}
                        evalResult={evalResult}
                        numQuestions={numQuestions}
                      />
                    </>
                  ) : (
                    <>
                      {error ? (
                        <div className="workspace-error workspace-error--rail" role="alert">
                          <p className="workspace-error__title">{error.title}</p>
                          {error.detail ? (
                            <p className="workspace-error__detail">{error.detail}</p>
                          ) : null}
                        </div>
                      ) : null}

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
                            Same order as <strong>Path</strong>. Jump here from any mode, or use{" "}
                            <strong>Learn</strong> / <strong>Quiz</strong> in the main panel.
                          </p>
                        </div>
                      ) : null}
                    </>
                  )}
                </aside>
              ) : null}

              <section
                className={`main-stage ${activeLearnTab === "quiz" ? "main-stage--quiz" : ""} ${activeLearnTab === "teach" ? "main-stage--learn" : ""}`}
                aria-labelledby="stage-heading"
              >
                <h2 id="stage-heading" className="sr-only">
                  Active study step
                </h2>

                {activeLearnTab === "teach" && error ? (
                  <div className="workspace-error workspace-error--stage" role="alert">
                    <p className="workspace-error__title">{error.title}</p>
                    {error.detail ? (
                      <p className="workspace-error__detail">{error.detail}</p>
                    ) : null}
                  </div>
                ) : null}

                <NextActionBanner
                  nextAction={nextAction}
                  loading={loading}
                  onFollow={followNextAction}
                />

                <div key={activeLearnTab} className="stage-panels mode-panel-transition">
                  <div
                    id="panel-plan"
                    role="tabpanel"
                    aria-labelledby="mode-tab-plan"
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
                        onPickConcept={selectConceptFromRail}
                      />
                    ) : null}
                  </div>

                  <div
                    id="panel-teach"
                    role="tabpanel"
                    aria-labelledby="mode-tab-teach"
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
                    aria-labelledby="mode-tab-quiz"
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
                        onStartNewQuiz={clearQuizProgress}
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
        <p className="site-footer__primary">
          EZ Study Lab • Adaptive Learning Studio • © {new Date().getFullYear()}
        </p>
        <p className="site-footer__meta">
          Open materials, local session, rule-based scoring.
        </p>
      </footer>
    </div>
  );
}
