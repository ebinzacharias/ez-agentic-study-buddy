import React from "react";
import { CpuArchitecture } from "@/components/ui/cpu-architecture";

/**
 * Onboarding hero: visual metaphor (data paths → “processor”) + numbered flow.
 */
export default function LandingHero() {
  return (
    <section
      className="onboarding-hero card card--stage"
      aria-labelledby="landing-how-heading"
    >
      <div className="onboarding-hero__grid">
        <div className="onboarding-hero__copy">
          <h2 id="landing-how-heading" className="onboarding-hero__title">
            How it works
          </h2>
          <p className="onboarding-hero__lede">
            Your file is the source of truth. Each step feeds the next—nothing is
            invented outside what you uploaded.
          </p>
          <ol className="onboarding-hero__steps">
            <li className="onboarding-hero__step">
              <span className="onboarding-hero__step-num" aria-hidden="true">
                1
              </span>
              <div>
                <strong>Upload material</strong>
                <p>Create a session locked to your notes or document.</p>
              </div>
            </li>
            <li className="onboarding-hero__step">
              <span className="onboarding-hero__step-num" aria-hidden="true">
                2
              </span>
              <div>
                <strong>Plan → Teach → Quiz</strong>
                <p>
                  Extract a concept path, get explanations grounded in the text, then
                  check understanding with quizzes tied to the same content.
                </p>
              </div>
            </li>
          </ol>
        </div>
        <div className="onboarding-hero__viz onboarding-hero__viz--radar">
          <div className="onboarding-hero__diagram" aria-hidden="true">
            <CpuArchitecture
              text="AI"
              width="100%"
              height="100%"
              className="block h-full w-full"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
