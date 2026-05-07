# MIRA Visual QA Review

> Use this template for systematic visual quality review of MIRA pages.

---

## Review Metadata

- **Date:** `[YYYY-MM-DD]`
- **Reviewer:** `[Name or agent ID]`
- **Pages reviewed:** `[list]`
- **Viewport tested:** `[375px / 768px / 1440px]`
- **Browser:** `[Chrome / Safari / Firefox]`

---

## Page-by-Page Review

### Landing Page (`/`)

| Criteria | Status | Notes |
|----------|--------|-------|
| Typography hierarchy correct | [ ] | |
| Spacing rhythm (4px base) | [ ] | |
| Mobile layout (375px) | [ ] | |
| Desktop layout (1440px) | [ ] | |
| No horizontal scroll | [ ] | |
| CTA buttons visible and styled | [ ] | |
| Focus indicators on all links | [ ] | |
| Logo accessible (aria-label) | [ ] | |
| Language toggle functional | [ ] | |
| Brand marquee renders correctly | [ ] | |

### Onboarding Page (`/onboarding`)

| Criteria | Status | Notes |
|----------|--------|-------|
| All inputs have labels | [ ] | |
| All inputs have `data-testid` | [ ] | |
| Chip buttons show `aria-pressed` | [ ] | |
| Focus rings visible on all inputs | [ ] | |
| Error state uses `role="alert"` | [ ] | |
| Loading state shows "…" on button | [ ] | |
| Disabled state visually distinct | [ ] | |
| StepIndicator shows progress | [ ] | |
| Mobile layout single-column | [ ] | |
| Form validation prevents empty submit | [ ] | |

### Scan Page (`/scan`)

| Criteria | Status | Notes |
|----------|--------|-------|
| Photo slots labeled (front/side/back) | [ ] | |
| Empty slot has camera icon + dashed border | [ ] | |
| Filled slot shows image + checkmark | [ ] | |
| Upload `data-testid` present per slot | [ ] | |
| File input accepts images only | [ ] | |
| Skip button is secondary style | [ ] | |
| Loading state on upload | [ ] | |
| Error alert if upload fails | [ ] | |
| Mobile camera capture works | [ ] | |
| Privacy messaging present | [ ] | |

### Catalog Page (`/catalog`)

| Criteria | Status | Notes |
|----------|--------|-------|
| Product grid responsive | [ ] | |
| Product cards have `data-testid` | [ ] | |
| Filter chips have `aria-pressed` | [ ] | |
| Empty state designed ("No products") | [ ] | |
| Product images have alt text | [ ] | |
| Card hover/focus effects present | [ ] | |
| Entire card is clickable | [ ] | |
| Brand/category filters functional | [ ] | |
| Grid spacing consistent | [ ] | |
| Mobile: single or two-column grid | [ ] | |

### Try-On Page (`/tryon/[productId]`)

| Criteria | Status | Notes |
|----------|--------|-------|
| Product image visible | [ ] | |
| Size selector has `aria-pressed` | [ ] | |
| "Try On" button prominent | [ ] | |
| Loading state shows spinner/text | [ ] | |
| Error state shows recovery action | [ ] | |
| Missing profile alert visible | [ ] | |
| `data-testid` on all interactive elements | [ ] | |
| Mobile layout stacks vertically | [ ] | |
| Focus management on size buttons | [ ] | |
| Back navigation available | [ ] | |

### Result Page (`/result/[generationId]`)

| Criteria | Status | Notes |
|----------|--------|-------|
| Status polling with `aria-live` | [ ] | |
| Loading spinner with label | [ ] | |
| Generated image full-width mobile | [ ] | |
| Video autoplays muted | [ ] | |
| Rating stars accessible | [ ] | |
| Buy CTA high-contrast | [ ] | |
| "Try Another" button present | [ ] | |
| Failed state shows error + recovery | [ ] | |
| Smooth state transitions | [ ] | |
| `data-testid` on result elements | [ ] | |

---

## Cross-Cutting Checks

| Category | Status | Notes |
|----------|--------|-------|
| Consistent button styles across pages | [ ] | |
| Consistent spacing rhythm | [ ] | |
| Consistent typography hierarchy | [ ] | |
| No console errors on any page | [ ] | |
| No broken images | [ ] | |
| No placeholder text in production | [ ] | |
| prefers-reduced-motion respected | [ ] | |
| WCAG AA contrast on all text | [ ] | |
| All forms keyboard-navigable | [ ] | |
| Tab order logical on all pages | [ ] | |

---

## Screenshots / Evidence

| Page | Viewport | Path |
|------|----------|------|
| Landing | 375px | `screenshots/[path]` |
| Landing | 1440px | `screenshots/[path]` |
| ... | ... | ... |

---

## Issues Found

| # | Page | Severity | Description | Fix |
|---|------|----------|-------------|-----|
| 1 | | P0/P1/P2 | | |
| ... | | | | |

### Severity Key

- **P0** — Broken functionality, inaccessible content, or security issue. Blocks ship.
- **P1** — Visible quality issue affecting user trust. Fix before launch.
- **P2** — Minor polish. Fix when convenient.

---

## Overall Verdict

- [ ] **PASS** — All pages meet MIRA Visual Quality Standard.
- [ ] **PASS WITH ISSUES** — Minor issues documented, none blocking.
- [ ] **FAIL** — P0 or multiple P1 issues found. Fix required.

---

*Template version: 1.0 | See: project_control/visual/MIRA_VISUAL_QUALITY_STANDARD.md*
