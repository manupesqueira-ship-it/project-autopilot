# MIRA Visual Quality Standard

> Defines what "world-class" means operationally for every screen, interaction, and pixel in MIRA.

---

## 1. Product Aesthetic Target

MIRA is a premium fashion-tech product. Every surface must communicate **trust, precision, and modern luxury** — the visual equivalent of a well-lit fitting room at a high-end boutique.

- Clean, high-contrast layouts with generous whitespace.
- Restrained color palette — ink, cream, and intentional accent tones only.
- No decorative clutter, no gratuitous gradients, no stock-photo energy.
- Typography carries authority: sharp hierarchy, consistent weights, no orphan lines.

### What "World-Class" Means Operationally

A screen is world-class when:
1. A first-time user understands the next action within 2 seconds.
2. Every interactive element responds visibly to hover, focus, active, and disabled states.
3. Loading, empty, and error states are designed — not afterthoughts.
4. The screen looks intentional on both a 375px phone and a 1440px desktop.
5. Nothing feels broken, placeholder, or developer-facing.

---

## 2. Spacing Rhythm

- Base unit: **4px** (`0.25rem`). All spacing must be a multiple of 4.
- Component internal padding: minimum `12px` (`0.75rem`).
- Section gaps: `24–48px` on mobile, `32–64px` on desktop.
- Touch targets: minimum `44×44px` (WCAG 2.5.8).
- Card padding: `16px` minimum.
- No adjacent elements closer than `8px` unless they are a deliberate group.

---

## 3. Typography Hierarchy

| Level | Usage | Weight | Size (mobile / desktop) |
|-------|-------|--------|-------------------------|
| H1 | Page titles | Bold | 24px / 32px |
| H2 | Section headers | Semibold | 20px / 24px |
| H3 | Card titles | Medium | 16px / 18px |
| Body | Paragraphs, descriptions | Regular | 14px / 16px |
| Caption | Labels, metadata | Regular | 12px / 14px |
| Button | CTA text | Semibold | 14px / 16px |

- Line height: 1.4–1.6 for body, 1.2–1.3 for headings.
- Max line length: 65 characters for body text.
- No font below 12px except legal footnotes.

---

## 4. Buttons & Taps

- Primary CTA: solid fill, high contrast, full-width on mobile.
- Secondary CTA: outline or muted fill, never competing with primary.
- All buttons must show:
  - **hover**: subtle background shift or shadow.
  - **focus-visible**: ring (`ring-2 ring-ink/40 ring-offset-2`).
  - **active/pressed**: scale or darken.
  - **disabled**: `opacity-50`, `cursor-not-allowed`, no hover effect.
  - **loading**: text replaced with `"…"` or spinner, button disabled.
- Chip/toggle buttons: `aria-pressed` required, visual pressed state distinct.
- Minimum touch target: 44×44px.

---

## 5. Loading States

Every async action must show a loading indicator:
- **Page-level**: centered spinner with label (e.g., "Generating…").
- **Button-level**: text replaced with `"…"`, button disabled.
- **Skeleton loaders**: preferred for content areas where layout is predictable.
- **Progress indicators**: required for multi-step processes (e.g., try-on generation).
- `aria-busy="true"` on the loading container.
- `aria-live="polite"` on status text that updates.

### What Must Be Rejected

- Blank screens during loading.
- Buttons that accept clicks while processing.
- Spinners without context text.
- Loading states longer than 30s without progress feedback.

---

## 6. Error States

- All error messages displayed in `role="alert"` containers.
- Error text must be human-readable — no error codes, no stack traces.
- Destructive errors: red/high-contrast background, clear recovery action.
- Network errors: suggest retry with a button.
- Validation errors: inline, adjacent to the offending field.
- Never blame the user. Frame as "something went wrong" not "you did it wrong."

---

## 7. Empty States

- Every list/grid that can be empty must have a designed empty state.
- Empty state includes: icon or illustration, short message, suggested action.
- Catalog empty filter: "No products found" with `role="status"`.
- Never show a blank white area where content should be.

---

## 8. Mobile-First Expectations

- Design for 375px width first, then scale up.
- All layouts must be single-column on mobile unless content demands otherwise.
- No horizontal scroll on any screen at any breakpoint.
- Sticky headers/footers only when they aid navigation — never for decoration.
- Bottom-anchored CTAs on mobile for thumb-reachable actions.
- Test at: 375px, 390px, 414px, 768px, 1024px, 1440px.

---

## 9. Accessibility Expectations

| Requirement | Standard |
|-------------|----------|
| Color contrast | WCAG AA (4.5:1 text, 3:1 UI) |
| Focus indicators | Visible ring on all interactive elements |
| Keyboard navigation | All flows completable without mouse |
| Screen reader | Semantic HTML, aria-labels, alt text |
| Touch targets | 44×44px minimum |
| Motion | `prefers-reduced-motion` respected |
| Form inputs | Associated labels via `htmlFor` or `aria-label` |
| Toggle state | `aria-pressed` on all chip/toggle buttons |
| Live regions | `aria-live` on status updates |
| Error alerts | `role="alert"` on error messages |

---

## 10. Step Navigation Clarity

- StepIndicator must show: current step, total steps, completed steps.
- `aria-current="step"` on active step.
- `aria-label="Step N of M"` on the nav container.
- Steps must be visually distinct: completed (filled), current (accent), upcoming (muted).
- Back navigation must be available unless destructive.

---

## 11. Product Cards

- Image: aspect ratio consistent (3:4 preferred), lazy-loaded, alt text required.
- Brand name: caption weight, secondary color.
- Product name: card title weight.
- Price: body weight, aligned consistently.
- Hover: subtle shadow or scale, cursor pointer.
- Focus: ring visible, card outlined.
- Tap area: entire card is clickable, not just text.

---

## 12. Result Page Quality

- Generated image: full-width on mobile, centered on desktop, alt text.
- Video: autoplay muted loop, controls accessible.
- Rating: star icons with `aria-label="N/5"`.
- Status polling: `aria-live="polite"` on status updates.
- State transitions: `AnimatePresence` for smooth entry/exit.
- Failed state: clear error message with recovery action.
- Buy/CTA buttons: high-contrast, full-width on mobile.

---

## 13. Scan/Upload Quality

- Photo slots: clear labels (front, side, back), requirement text.
- Empty slot: dashed border, camera icon, descriptive `aria-label`.
- Filled slot: image preview with checkmark overlay.
- File input: `accept="image/*"`, `capture="user"` for mobile.
- Upload feedback: immediate visual response on selection.
- Skip option: clearly secondary, not competing with primary action.

---

## 14. Perceived Trust & Privacy

- No dark patterns — every action is transparent.
- Photo upload area must communicate: "Your photos are private."
- No unexpected data collection — form fields explain why data is needed.
- Progress is never lost silently — unsaved changes get a warning.
- Error recovery never requires re-entering data.
- HTTPS indicators where relevant.
- Privacy policy link accessible from onboarding.

---

## 15. Motion Rules

- Duration: 150–300ms for micro-interactions, 300–500ms for page transitions.
- Easing: `ease-out` for entries, `ease-in` for exits, `ease-in-out` for transforms.
- No motion for motion's sake — every animation must communicate state change.
- `prefers-reduced-motion`: disable all non-essential animations.
- No layout shift during animation — content must not jump.

---

## 16. Layout Rules

- Max content width: 1200px, centered.
- Gutter: 16px on mobile, 24px on tablet, 32px on desktop.
- Grid: 1 column mobile, 2 columns tablet, 3–4 columns desktop for product grids.
- Vertical rhythm: consistent section spacing, no irregular gaps.
- No content touching screen edges — minimum 16px padding.

---

## 17. What Must Be Rejected

Any screen that exhibits:
- [ ] Unstyled browser defaults (checkboxes, selects, scrollbars on Windows).
- [ ] Console errors visible to users.
- [ ] Broken images or missing alt text.
- [ ] Placeholder text in production ("Lorem ipsum", "TODO", "test").
- [ ] Inconsistent button styles on the same page.
- [ ] Invisible focus states.
- [ ] Touch targets below 44×44px.
- [ ] Text contrast below WCAG AA.
- [ ] Loading states that show nothing.
- [ ] Error states that show raw error objects.
- [ ] Horizontal scroll on mobile.
- [ ] Orphan words in headings.
- [ ] Misaligned elements in the same row.
- [ ] Flickering or janky animations.
- [ ] Dead-end screens with no navigation.

---

## 18. Premium Fashion-Tech References (Abstract)

The visual language should evoke:
- The confidence of a well-designed luxury e-commerce experience.
- The precision of a professional measurement tool.
- The warmth of a personal styling session.
- The modernity of a cutting-edge AR/AI product.
- The trust of a privacy-first platform.

Avoid:
- The coldness of enterprise SaaS.
- The noise of fast-fashion marketplaces.
- The gimmickry of social media filters.
- The complexity of developer tools.

---

*This standard is the source of truth for all visual QA reviews. Every page, component, and interaction must pass against these criteria before shipping.*
