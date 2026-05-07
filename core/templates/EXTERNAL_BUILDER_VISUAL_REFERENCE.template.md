# External Builder Visual Reference Request

> Use this template when requesting a visual prototype from Base44, Lovable, or similar tools.

---

## Project Context

- **Project:** MIRA — AI-powered virtual try-on for fashion
- **Tech Stack:** Next.js 14, React, TypeScript, Tailwind CSS
- **Design Direction:** Premium, minimal, fashion-tech aesthetic
- **Target:** Mobile-first, responsive up to 1440px

---

## Request Scope

### What We Want

- [ ] Visual prototype only — static or interactive UI components.
- [ ] React/Next.js-compatible component structure if possible.
- [ ] Tailwind CSS for styling (no custom CSS frameworks).
- [ ] Mobile layout (375px) as primary, desktop as secondary.

### Page/Component Target

**Page:** `[SPECIFY: landing / onboarding / scan / catalog / tryon / result]`

**Description:**
```
[Describe what this page/component should look like and do visually.
Include layout, sections, interactions, and visual tone.]
```

### Required States

For each component, provide designs for:

- [ ] Default / loaded state
- [ ] Loading state (spinner, skeleton, or progress indicator)
- [ ] Empty state (no data available)
- [ ] Error state (something went wrong)
- [ ] Disabled state (action not available)
- [ ] Mobile layout (375px)
- [ ] Desktop layout (1440px)

---

## Design Constraints

### Use These Tokens

```
Colors: ink (#1a1a1a), cream (#faf8f5), accent (as defined in tailwind.config.ts)
Font: System font stack or as defined in project
Spacing: 4px base unit, multiples of 4
Border radius: consistent with existing components
```

### Do NOT Include

- [ ] **No backend logic** — no API routes, no server functions.
- [ ] **No authentication** — no login, signup, session, or token logic.
- [ ] **No Supabase** — no database queries, no storage, no RLS.
- [ ] **No environment variables** — no `process.env` references.
- [ ] **No paid API calls** — no OpenAI, no cloud services.
- [ ] **No real data** — use placeholder/mock data only.
- [ ] **No real photos** — use placeholder images or solid color blocks.
- [ ] **No npm package additions** — use only packages already in the project.
- [ ] **No file uploads to external services**.
- [ ] **No analytics or tracking code**.

---

## Export Requirements

Please provide:

1. **File list** — all generated files with paths.
2. **Component tree** — parent/child structure of components.
3. **Design rationale** — why specific layout/color/spacing choices were made.
4. **Mobile screenshots** — visual preview at 375px width.
5. **Desktop screenshots** — visual preview at 1440px width.
6. **Interaction notes** — hover, focus, active, disabled behaviors.
7. **Accessibility notes** — aria labels, keyboard navigation, contrast.

---

## After Generation

The output will go through MIRA's External Builder Import Review process:

1. Committed to an isolated `external/` branch.
2. Reviewed for security and architecture compliance.
3. Adapted to match MIRA's existing design system and component structure.
4. QA validated before merge.

**The generated code is treated as untrusted and will be modified as needed.**

---

*Template version: 1.0 | See: project_control/EXTERNAL_BUILDER_POLICY.md*
