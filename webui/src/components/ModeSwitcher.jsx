import React from "react";
import { motion } from "framer-motion";

const MODES = [
  {
    id: "plan",
    label: "Plan",
    icon: (
      <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <path d="M2 4h12M2 8h8M2 12h5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    id: "teach",
    label: "Learn",
    icon: (
      <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <rect x="1.5" y="2.5" width="13" height="9" rx="1.5" stroke="currentColor" strokeWidth="1.7" />
        <path d="M8 11.5v2M5.5 13.5h5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    id: "quiz",
    label: "Quiz",
    icon: (
      <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.7" />
        <path d="M6.25 6.25C6.25 5.28 7.01 4.5 8 4.5s1.75.78 1.75 1.75c0 .9-.65 1.4-1.25 1.9-.27.23-.5.5-.5.85" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <circle cx="8" cy="11.5" r="0.85" fill="currentColor" />
      </svg>
    ),
  },
];

export default function ModeSwitcher({ activeMode, onChange }) {
  return (
    <div className="mode-bar" role="tablist" aria-label="Workspace mode">
      {MODES.map(({ id, label, icon }) => {
        const isActive = activeMode === id;
        return (
          <button
            key={id}
            type="button"
            role="tab"
            id={`mode-tab-${id}`}
            aria-selected={isActive}
            aria-controls={`panel-${id}`}
            className={`mode-tab${isActive ? " is-active" : ""}`}
            onClick={() => onChange(id)}
          >
            {isActive && (
              <motion.span
                className="mode-tab__track"
                layoutId="mode-pill"
                transition={{ type: "spring", stiffness: 400, damping: 34 }}
              />
            )}
            <span className="mode-tab__icon">{icon}</span>
            <span className="mode-tab__label">{label}</span>
          </button>
        );
      })}
    </div>
  );
}
