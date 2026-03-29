/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        border: "var(--color-border)",
        input: "var(--color-border)",
        ring: "var(--color-focus-ring)",
        background: "var(--color-bg-page)",
        foreground: "var(--color-text-primary)",
        primary: {
          DEFAULT: "var(--color-primary)",
          foreground: "var(--color-on-primary)",
        },
        "primary-foreground": "var(--color-on-primary)",
        secondary: {
          DEFAULT: "var(--color-bg-elevated)",
          foreground: "var(--color-text-primary)",
        },
        destructive: {
          DEFAULT: "var(--color-error)",
          foreground: "#ffffff",
        },
        accent: {
          DEFAULT: "var(--color-accent-dim)",
          foreground: "var(--color-text-primary)",
        },
        muted: {
          DEFAULT: "var(--color-bg-elevated)",
          foreground: "var(--color-text-muted)",
        },
      },
    },
  },
  plugins: [],
};
