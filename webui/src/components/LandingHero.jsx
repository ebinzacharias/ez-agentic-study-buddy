import React from "react";

const BENTO = [
  {
    step: "01",
    tag: "Path",
    title: "Build a concept roadmap",
    body: "AI extracts ordered topics from your document so you always know what to study next.",
    bar: "#4FD1C5",
  },
  {
    step: "02",
    tag: "Learn",
    title: "Grounded explanations",
    body: "Every lesson cites the text you uploaded — no hallucinations, no generic summaries.",
    bar: "#818CF8",
  },
  {
    step: "03",
    tag: "Quiz",
    title: "Test on your content",
    body: "Auto-generated questions reference the same source file. Adjust difficulty on the fly.",
    bar: "#34D399",
  },
];

export default function LandingHero() {
  return (
    <section className="lp-features" aria-labelledby="lp-features-heading">
      <div className="lp-features__inner">
        <p className="lp-features__eyebrow">Three steps. One session.</p>
        <h2 id="lp-features-heading" className="lp-features__heading">
          Path → Learn → Quiz
        </h2>

        <ul className="lp-bento" role="list">
          {BENTO.map((b) => (
            <li key={b.step} className="lp-bento__card">
              <div className="lp-bento__top">
                <span className="lp-bento__step">{b.step}</span>
                <span className="lp-bento__tag">{b.tag}</span>
              </div>
              <h3 className="lp-bento__title">{b.title}</h3>
              <p className="lp-bento__body">{b.body}</p>
              <span
                className="lp-bento__bar"
                style={{ background: b.bar }}
                aria-hidden="true"
              />
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
