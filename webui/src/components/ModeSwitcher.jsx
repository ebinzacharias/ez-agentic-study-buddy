import React from "react";

const MODES = [
  {
    id: "plan",
    label: "Path",
    title: "View your learning path and generate ordered concepts",
  },
  { id: "teach", label: "Learn", title: "Explanations grounded in your upload" },
  { id: "quiz", label: "Quiz", title: "Practice questions on a concept" },
];

export default function ModeSwitcher({ activeMode, onChange }) {
  return (
    <div className="mode-switcher-bar">
      <div
        className="mode-switcher"
        role="tablist"
        aria-label="Workspace mode"
      >
        {MODES.map(({ id, label, title }) => {
          const selected = activeMode === id;
          return (
            <button
              key={id}
              type="button"
              role="tab"
              id={`mode-tab-${id}`}
              aria-selected={selected}
              aria-controls={`panel-${id}`}
              tabIndex={0}
              title={title}
              className={`mode-switcher__segment ${selected ? "is-active" : ""}`}
              onClick={() => onChange(id)}
            >
              {label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
