# AUTOPILOT DESIGN BENCHMARKS

**Version:** 1.0  
**Date:** 2026-04-30  
**Owner:** Project Autopilot — Design Director  
**Status:** ACTIVE

---

## 1. Design Ambition

MIRA is not a generic productivity tool. Its design must reflect the level of craft and intentionality that users associate with the best-designed software in the world.

The design ambition for every screen, component, and interaction is:

> **"Would a designer at Linear, Stripe, or Apple feel proud of this?"**

If the honest answer is no — it is not ready to ship.

This document is the reference standard for the Design Director agent and any human reviewer evaluating MIRA's visual and interaction quality.

---

## 2. Reference-Quality Categories

Each category defines a design pole to reach for. Multiple categories may apply to a single screen.

### 2.1 Premium Fashion — Editorial Restraint
**Reference:** Bottega Veneta campaigns, The Row, A-POC-Able Issey Miyake digital  
**What it means:**
- Silence is a design element. White space earns its place.
- Typography does most of the work. No decoration compensates for weak type.
- Color is either a considered statement or absent.
- Asymmetry used deliberately, not accidentally.

**Apply when:** Brand moments, landing pages, editorial or hero sections.

### 2.2 Apple-Level Clarity
**Reference:** Apple.com, iOS system UI, macOS settings  
**What it means:**
- One primary action per screen. Everything else is secondary.
- Labels use plain language. No jargon. No ambiguity.
- Icons are literal until they've been learned. Then they can be abstract.
- Animation communicates state change, not decoration.
- Every pixel is intentional.

**Apply when:** Core utility flows, forms, settings, data entry.

### 2.3 Linear-Level Product Polish
**Reference:** Linear.app, Vercel dashboard, Raycast  
**What it means:**
- Keyboard shortcuts are first-class citizens.
- Loading states are thoughtful, not spinners.
- Empty states have context, not just illustrations.
- Density is a design choice with user control.
- Typography in data views is monospaced or tabular where appropriate.
- Color is semantic: status, priority, type — not decoration.

**Apply when:** Dashboards, task lists, admin views, data tables.

### 2.4 Editorial Minimalism
**Reference:** Are.na, Fonts In Use, Swiss graphic design tradition  
**What it means:**
- Grid is sacred. Alignments are exact.
- Typefaces are chosen for character, not familiarity.
- No drop shadows unless they have spatial meaning.
- Color palette is constrained to 2–3 intentional hues.
- Nothing on the page is accidental.

**Apply when:** Content views, reading experiences, documentation surfaces.

### 2.5 High-Trust Fintech/Security Style
**Reference:** Stripe Dashboard, 1Password, Notion security pages  
**What it means:**
- Visual weight signals importance. Destructive actions are visually heavy and require confirmation.
- Color usage is conservative: errors are red, warnings are amber, success is muted green.
- No playfulness in contexts involving money, access, or risk.
- Status badges, timestamps, and audit trails are always visible when relevant.
- Monospace fonts for keys, hashes, IDs, and technical values.

**Apply when:** Authentication, billing, permissions, API keys, security settings, data exports.

---

## 3. Things to Avoid

The following are explicitly prohibited. Finding any of these in a design submission warrants a WARN or BLOCK.

### 3.1 Generic SaaS Cards
**What it looks like:** Rounded card with icon in top-left, title, body text, and a blue "Learn more" button. Repeated in a 3-column grid.  
**Why it fails:** No design decision was made. This is the output of no thought.  
**Verdict:** BLOCK if this is the primary UI pattern without justification.

### 3.2 Cheap Gradients
**What it looks like:** Linear gradient background from purple to blue, or hero section with gradient-to-transparent overlay on an image.  
**Why it fails:** Overused to the point of meaninglessness. Communicates no brand or functional intent.  
**Exception:** Gradients with precise semantic or brand purpose (e.g., chart fill under a line) may be acceptable.  
**Verdict:** WARN by default; BLOCK if it's a primary design element.

### 3.3 Random Colors
**What it looks like:** Tag badges in 6 unrelated colors, no semantic meaning, no system.  
**Why it fails:** Color is one of the most powerful tools in visual communication. Using it randomly destroys trust and clarity.  
**Verdict:** BLOCK. All color use must map to a semantic system.

### 3.4 Overused Templates
**What it looks like:** Landing page that looks identical to any Tailwind UI or shadcn/ui starter kit without customization.  
**Why it fails:** Zero differentiation. Users recognize the template.  
**Verdict:** WARN if used as a base. BLOCK if shipped without meaningful customization.

### 3.5 Weak Hierarchy
**What it looks like:** All text is the same weight. Headings and body text are interchangeable. CTAs are not visually dominant.  
**Why it fails:** Users cannot scan the page. Cognitive load increases. Conversion and comprehension both suffer.  
**Verdict:** WARN.

### 3.6 Unclear CTA
**What it looks like:** Three buttons of equal visual weight. No clear primary action.  
**Why it fails:** Users don't know what to do next.  
**Verdict:** WARN if two or more primary-weight CTAs exist on the same screen.

### 3.7 Gimmicks Without Utility
**What it looks like:** Animated counter, particle background, lottie animation that plays on every page load, hover effects that obscure content.  
**Why it fails:** Adds cognitive noise. Signals insecurity, not confidence.  
**Verdict:** WARN for animations that serve no UX purpose. BLOCK for animations that obscure information.

---

## 4. How the Design Director Should Evaluate Novelty

The Design Director must ask three questions when evaluating novelty:

1. **"Have I seen this exact pattern used in our competitive set in the last 12 months?"**
   - If yes: What is the differentiated reason to use it anyway? Document it.
   - If no: Is the novelty earned by the use case, or is it novelty for its own sake?

2. **"Does this design make the right choice for this specific context?"**
   - A pattern can be novel and wrong. An established pattern can be correct and excellent.
   - Novelty is not inherently valuable. Fit is.

3. **"Would this design degrade gracefully if stripped of its distinctive element?"**
   - If the core layout and hierarchy only work because of the distinctive element, the foundation is weak.
   - Great design remains functional without its most distinctive feature.

---

## 5. How Visual QA Should Support Design Review

Visual QA is not design review. It is a checklist of objective criteria.

Visual QA must confirm:

- [ ] No horizontal scroll on standard viewport sizes (1280px, 1440px, 375px mobile)
- [ ] No text overflow or truncation in primary content areas
- [ ] Minimum 4.5:1 color contrast ratio on all body text (WCAG AA)
- [ ] Minimum 3:1 on large text and UI components
- [ ] Interactive elements have visible focus states
- [ ] No layout shift on data load (skeleton states present)
- [ ] No unstyled flash (FOUC) on route transitions
- [ ] Icon sizes consistent within component families (16/20/24px)
- [ ] Button heights consistent within tier (sm/md/lg)
- [ ] Spacing uses design tokens, not arbitrary px values

Visual QA issues are WARN by default. Combined with a Design Director WARN they escalate to BLOCK.

---

## 6. Human Visual Review Criteria

Human visual review is mandatory when:

1. A new primary screen or major component is introduced
2. The Design Director issued a WARN on any visual element
3. The component involves user trust (auth, billing, permissions)
4. A before/after comparison shows significant regression
5. A new typeface, color, or spacing system is introduced

Human reviewers must evaluate:

- Does this feel premium and intentional?
- Does this feel consistent with other MIRA screens?
- Is there a clear visual hierarchy?
- Would I show this as a reference example?

Human verdict is binary: **APPROVE** or **REWORK**. No partial approvals.

---

## 7. Screenshot Evidence Requirements

Every design cycle must produce:

1. **Full-page screenshot at 1440px** — desktop primary layout
2. **Full-page screenshot at 375px** — mobile viewport
3. **Focused screenshot of the primary CTA area**
4. **Screenshot of each distinct state:** loading, empty, error, success
5. **Screenshot with dark mode** (if dark mode is implemented)

Screenshots must be committed alongside code changes. A design submission without screenshots is treated as incomplete and cannot receive a PASS verdict.

---

## 8. Before/After Comparison Standard

When a design change modifies an existing screen:

- Before screenshot must be sourced from the most recent approved version (not a local draft)
- After screenshot must match the committed implementation
- Comparison must note: what changed, why, and which design reference category it targets
- If the before state was already rated PASS, the after state must clearly exceed it or justify the change

---

## 9. Design Score Thresholds

| Score | Verdict | Meaning |
|---|---|---|
| 90–100 | **PASS — REFERENCE QUALITY** | Eligible to be used as a design benchmark for future work |
| 75–89 | **PASS — ACCEPTABLE** | Meets standard; ships as-is |
| 60–74 | **WARN — REWORK** | Below standard; specific issues must be resolved before ship |
| 40–59 | **BLOCK — REJECT** | Does not meet MIRA design standard; full design revision required |
| 0–39 | **BLOCK — CRITICAL** | Fundamental failure; escalate to human design lead immediately |

**Hard rules:**
- Any prohibited pattern (Section 3) auto-triggers BLOCK regardless of score
- Missing screenshots auto-triggers WARN on evidence category
- Missing competitive benchmark auto-triggers WARN on research category

---

*This document is the operating standard for the Design Director. All design verdicts must be traceable to criteria in this document.*
