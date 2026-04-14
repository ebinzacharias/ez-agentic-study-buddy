# Audit Checklist & Debt Patterns

Use this checklist to categorize files and code patterns during the `analyze` phase.

## 1. File Deletion Criteria (The "Ghost" List)
A file should be flagged for deletion if it meets any of the following:
- **Orphaned:** 0 incoming imports from the entry-point dependency tree.
- **Redundant Assets:** Images, SVGs, or JSON files in `/public` or `/assets` that are not referenced in the code.
- **Temporary:** Files with names containing `copy`, `temp`, `test-old`, or `backup`.
- **Shadow Files:** `.css` or `.scss` files that have been 100% replaced by Tailwind classes in their corresponding component.

## 2. Legacy Pattern Detection (The "Debt" List)
Flag these patterns for refactoring to maintain a modern frontend stack:
- **Class-Based Components:** `class X extends React.Component` (Convert to Functional + Hooks).
- **Manual DOM Manipulation:** Use of `document.getElementById` or `querySelector` (Convert to `useRef` or state-driven rendering).
- **Var/Let Overuse:** Global `var` declarations (Convert to `const` where applicable).
- **Hardcoded Styling:** Style props like `style={{ color: '#0078D4' }}` (Convert to Tailwind classes using `design-tokens.json`).

## 3. Library & Dependency Health
- **Unused Packages:** Listed in `package.json` but never imported.
- **Duplicate Logic:** Multiple libraries doing the same thing (e.g., having both `axios` and `fetch` used interchangeably).
- **Outdated Data Fetching:** Old `useEffect` fetching patterns (Suggest `React Query` or `SWR` if the project uses them elsewhere).

## 4. Ideal Folder Structure (Restructure Target)
If a project is disorganized, suggest moving files to match this "Clean Room" layout:
- `src/api/` — API clients and services.
- `src/components/ui/` — Atomic design elements (Buttons, Inputs, Cards).
- `src/components/features/` — Business-logic-specific components.
- `src/hooks/` — Global custom hooks.
- `src/store/` — State management (Context).