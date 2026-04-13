import React from "react";

/**
 * Minimalist Landing Hero - Integrated into the dashboard background.
 * Displays as subtle guidance and mission statement, not as a separate card.
 * Uses "zero-UI" philosophy: content revealed only when needed.
 */
export default function LandingHero() {
  return (
    <div className="landing-hero-integrated">
      {/* Floating Mission Statement - Top Center */}
      <div className="mission-statement">
        <h1 className="mission-title">Your data. Your learning.</h1>
        <p className="mission-subtitle">
          Upload your materials and let AI create your personalized learning path.
        </p>
      </div>

      {/* Three Steps - Subtle Sidebar Guide (appears on desktop) */}
      <aside className="workflow-guide">
        <div className="workflow-step">
          <div className="step-indicator">1</div>
          <h3>Drop & Initialize</h3>
          <p>Upload your study material</p>
        </div>
        <div className="workflow-step">
          <div className="step-indicator">2</div>
          <h3>Learn</h3>
          <p>Follow AI-generated paths</p>
        </div>
        <div className="workflow-step">
          <div className="step-indicator">3</div>
          <h3>Master</h3>
          <p>Quiz & adapt difficulty</p>
        </div>
      </aside>

      {/* Ambient Background Element - Animated Neural Network */}
      <div className="ambient-neural-bg" aria-hidden="true">
        <svg className="neural-nodes" viewBox="0 0 1000 1000">
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          {/* Random nodes positioned across viewport */}
          <circle cx="100" cy="150" r="3" fill="#4fd1c5" opacity="0.3" filter="url(#glow)"/>
          <circle cx="850" cy="200" r="2.5" fill="#4fd1c5" opacity="0.2"/>
          <circle cx="200" cy="850" r="3" fill="#4fd1c5" opacity="0.25"/>
          <circle cx="900" cy="900" r="2" fill="#4fd1c5" opacity="0.2"/>
          <circle cx="450" cy="950" r="2.5" fill="#4fd1c5" opacity="0.15"/>
          
          {/* Subtle connecting lines */}
          <line x1="100" y1="150" x2="200" y2="250" stroke="#4fd1c5" strokeWidth="0.5" opacity="0.08"/>
          <line x1="850" y1="200" x2="900" y2="300" stroke="#4fd1c5" strokeWidth="0.5" opacity="0.08"/>
          <line x1="200" y1="850" x2="450" y2="950" stroke="#4fd1c5" strokeWidth="0.5" opacity="0.08"/>
        </svg>
      </div>
    </div>
  );
}
