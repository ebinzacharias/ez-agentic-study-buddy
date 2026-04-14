import React from "react";
import { AnimatePresence, motion } from "framer-motion";

const MODES = [
  {
    id: "plan",
    label: "Path",
    desc: "Ordered concepts from your file",
    icon: (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
        <path d="M3 4.5h12M3 9h8M3 13.5h5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    id: "teach",
    label: "Learn",
    desc: "Explanations grounded in your upload",
    icon: (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
        <rect x="2" y="3" width="14" height="10" rx="1.5" stroke="currentColor" strokeWidth="1.6" />
        <path d="M9 13v2M6.5 15h5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    id: "quiz",
    label: "Quiz",
    desc: "Practice questions on each concept",
    icon: (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
        <circle cx="9" cy="9" r="7" stroke="currentColor" strokeWidth="1.6" />
        <path
          d="M7 7.25C7 6.01 7.9 5 9 5s2 1.01 2 2.25c0 1.1-.8 1.65-1.5 2.25-.3.27-.5.55-.5.9"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
        />
        <circle cx="9" cy="13" r="0.9" fill="currentColor" />
      </svg>
    ),
  },
];

export default function ModeSwitcher({ activeMode, onChange }) {
  return (
    <div className="mode-switcher-bar" aria-label="Workspace navigation">
      <div className="mode-bar" role="tablist" aria-label="Workspace mode">
        {MODES.map(({ id, label, desc, icon }) => {
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
              <AnimatePresence>
                {isActive && (
                  <motion.div
                    key="indicator"
                    className="mode-tab__indicator"
                    layoutId="mode-pill"
                    initial={false}
                    transition={{ type: "spring", stiffness: 400, damping: 32 }}
                  />
                )}
              </AnimatePresence>
              <span className="mode-tab__icon">{icon}</span>
              <span className="mode-tab__content">
                <span className="mode-tab__label">{label}</span>
                <span className="mode-tab__desc">{desc}</span>
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
