import React from "react";

const MODES = [
  { id: "plan", label: "Plan" },
  { id: "teach", label: "Learn" },
  { id: "quiz", label: "Quiz" },
];

export default function ModeSwitcher({ activeMode, onChange }) {
  return (
    <div className="mode-switcher-bar">
      <div
        className="mode-switcher"
        role="tablist"
        aria-label="Workspace mode"
      >
        {MODES.map(({ id, label }) => {
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
