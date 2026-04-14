# Define the complete content for components-reference.md
content = """# UI Component Reference Guide — EZ Study Lab (v2.0.0)

Use these patterns to ensure 100% compliance with the **EZ-PO Next-Gen Design System**. These examples serve as the visual "Gold Standard" for all generated code.

**Design Foundation:**
- **Primary:** Deep Slate `#0F172A` — foundation of focus
- **Agent AI:** Electric Indigo `#6366F1` — planning & agent states
- **Learning Path:** Emerald `#10B981` — progress & mastery
- **Surface:** Ultra-light Canvas `#F8FAFC` + Glass-morphic Cards `rgba(255, 255, 255, 0.8)`
- **Typography:** Sora (display) + Inter (body) — never use bold (700)

---

## 1. Feature & Information Cards
Cards are the primary container for the Agentic Dashboard. They must be clean, grouped, and responsive with glass-morphic treatment.

✅ **COMPLIANT PATTERN**
```jsx
<div className="bg-white/80 backdrop-blur p-6 rounded-[1rem] shadow-sm border border-[#E2E8F0] flex flex-col gap-4 hover:border-[#6366F1] hover:shadow-[0_0_20px_rgba(99,102,241,0.15)] transition-all group">
  <div className="flex justify-between items-start">
    <div className="flex flex-col gap-1">
      <h3 className="text-lg font-semibold text-[#0F172A]">Concept: Neural Networks</h3>
      <span className="text-sm text-[#64748B]">Progress: Learning Path 3/5</span>
    </div>
    <span className="px-2 py-1 bg-[#F8FAFC] text-[#6366F1] text-sm font-medium rounded-[0.5rem]">AI Agent</span>
  </div>
  <p className="text-base text-[#64748B] leading-relaxed">
    Master deep learning fundamentals with adaptive difficulty. Your AI tutor adjusts based on performance.
  </p>
  <div className="pt-4 border-t border-[#E2E8F0] flex flex-col gap-2">
    <div className="flex justify-between text-xs font-medium text-[#64748B]">
      <span>Mastery</span>
      <span>72%</span>
    </div>
    <div className="h-2 w-full bg-[#E2E8F0] rounded-full overflow-hidden">
      <div className="h-full bg-[#10B981] w-[72%] transition-all duration-500"></div>
    </div>
  </div>
</div>

✅ COMPLIANT WRAPPER (Full-Viewport Agentic UX)

```jsx
<main className="min-h-screen bg-[#F8FAFC] p-4 lg:p-8">
  <header className="mb-8 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
    <div className="flex flex-col gap-1">
      <h1 className="text-clamp[2rem,5vw,3rem] font-semibold text-[#0F172A]">EZ Study Lab</h1>
      <p className="text-sm text-[#64748B]">Your AI-Powered Learning Companion</p>
    </div>
    <div className="flex gap-3">
      {/* Search/Filter Bar */}
      <input 
        type="text" 
        className="rounded-[1rem] border border-[#E2E8F0] px-4 py-2 text-sm focus:ring-2 focus:ring-[#6366F1] outline-none bg-white/80 backdrop-blur transition-all w-full lg:w-64" 
        placeholder="Search concepts..." 
      />
      <button className="bg-[#6366F1] text-white px-4 py-2 rounded-[1rem] text-sm font-medium hover:bg-[#4F46E5] transition-all whitespace-nowrap shadow-sm">
        New Session
      </button>
    </div>
  </header>
  
  <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {/* Concept Cards, Learning Paths, Agent Status — go here */}
  </section>
</main>
```

## 2. Action Buttons & Interaction

Buttons must follow the 4px grid and standard font weights. Never use font-bold (700).

| Variant | Logic | Tailwind Classes |
|---------|-------|------------------|
| **Primary (Agent)** | Main Action / AI Planning | `bg-[#6366F1] text-white px-4 py-2 rounded-[1rem] font-medium hover:bg-[#4F46E5] transition-all shadow-sm` |
| **Secondary (Learning)** | Neutral / Progress | `bg-white text-[#0F172A] border border-[#E2E8F0] px-4 py-2 rounded-[1rem] font-medium hover:bg-[#F8FAFC]` |
| **Success (Mastery)** | Positive Outcome | `bg-[#10B981] text-white px-4 py-2 rounded-[1rem] font-medium hover:bg-[#059669] transition-all` |
| **Quiz Hint** | Warning / Help | `bg-[#F59E0B] text-[#0F172A] px-4 py-2 rounded-[1rem] font-medium hover:bg-[#FBBF24]` |
| **Ghost (Subtle)** | Secondary Action | `text-[#6366F1] hover:bg-[#F8FAFC] px-3 py-1.5 rounded-[0.5rem] transition-colors font-medium` |

## 3. Empty & Loading States (Agentic UX)

When data is missing or loading, use a structured placeholder to prevent layout shifts and maintain user trust.

```jsx
<div className="flex flex-col items-center justify-center p-12 border-2 border-dashed border-[#E2E8F0] rounded-[1rem] bg-white/50 backdrop-blur text-center">
  <div className="w-12 h-12 bg-[#6366F1]/10 rounded-full flex items-center justify-center mb-4 shadow-[0_0_20px_rgba(99,102,241,0.15)]">
    <span className="text-xl">🧠</span>
  </div>
  <p className="font-semibold text-lg text-[#0F172A]">No Concepts Yet</p>
  <p className="text-sm text-[#64748B] max-w-xs mt-2">Upload your study material to let the AI generate personalized learning paths.</p>
</div>
```

**Agent Status Indicator (Thinking/Active):**
```jsx
<div className="flex items-center gap-2 px-3 py-2 bg-[#6366F1]/10 border border-[#6366F1]/30 rounded-[1rem] shadow-[0_0_20px_rgba(99,102,241,0.15)]">
  <div className="w-2 h-2 bg-[#6366F1] rounded-full animate-pulse"></div>
  <span className="text-sm font-medium text-[#6366F1]">AI Agent is planning your session...</span>
</div>
```


## 4. Typography Scale (Sora + Inter)

Strictly enforce these Tailwind class combinations to maintain engineering-grade legibility. **Never use bold (700)—max is font-semibold (600).**

| Element | Classes | Usage |
|---------|---------|-------|
| **H1 (Page Title)** | `text-clamp[2rem,5vw,3rem] font-semibold text-[#0F172A] tracking-tight` | "EZ Study Lab", "Your Learning Path" |
| **H2 (Section Header)** | `text-lg font-semibold text-[#0F172A]` | "Active Sessions", "Recommended Concepts" |
| **H3 (Card Header)** | `text-base font-semibold text-[#0F172A]` | Card titles, concept names |
| **Body Text** | `text-base font-normal text-[#64748B] leading-relaxed` | Descriptions, explanations, quiz text |
| **Label / Small** | `text-sm font-medium text-[#64748B]` | Metadata, timestamps, progress |
| **Agent Accent** | `text-sm font-medium text-[#6366F1]` | Active status, AI-generated, highlighting |
| **Success/Progress** | `text-sm font-medium text-[#10B981]` | Completion, mastery, positive feedback |
| **Caption / Micro** | `text-xs font-normal text-[#94A3B8]` | Hints, secondary info, disabled states |

---

## 5. Spacing & Geometry (4px Grid)

Maintain the 4px grid for all spacing and use consistent radii.

- **Padding/Margin:** 4px, 8px, 12px, 16px, 24px, 32px, 40px, 56px (Tailwind: p-1, p-2, p-3, p-4, p-6, p-8, p-10, p-14)
- **Border Radius:**
  - Cards & large containers: `rounded-[1rem]` (16px)
  - Buttons & badges: `rounded-[1rem]` (16px)
  - Subtle elements: `rounded-[0.5rem]` (8px)
  - Pills: `rounded-[9999px]`
- **Shadows:**
  - Subtle: `shadow-sm`
  - Active/Hover: `shadow-[0_0_20px_rgba(99,102,241,0.15)]` (Indigo glow for Agent elements)
  - Elevated: `shadow-md`

---

## 6. Responsive Layout (Mobile-First)

Always start with `flex-col` and layer responsive prefixes.

```jsx
{/* Example: Desktop cards in 3-column grid, tablet 2-col, mobile stacked */}
<section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4 lg:p-8">
  {/* Cards */}
</section>
```

---

## 7. Color Usage Reference

| Token | Value | Use Case |
|-------|-------|----------|
| **Primary (Deep Slate)** | `#0F172A` | Headings, primary text, focus |
| **Agent (Indigo)** | `#6366F1` | AI buttons, active states, agent status |
| **Learning (Emerald)** | `#10B981` | Success, progress bars, mastery |
| **Canvas (Background)** | `#F8FAFC` | Main page background |
| **Card (Glass)** | `rgba(255,255,255,0.8)` + `backdrop-blur` | Container backgrounds |
| **Border** | `#E2E8F0` | Dividers, card edges |
| **Secondary Text** | `#64748B` | Body copy, captions |
| **Quiz Wrong** | `#EF4444` | Incorrect answer feedback |
| **Quiz Hint** | `#F59E0B` | Helpful guidance |