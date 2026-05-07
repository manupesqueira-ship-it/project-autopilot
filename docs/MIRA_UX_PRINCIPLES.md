# MIRA UX Principles

> Ten principles that govern every design and implementation decision in MIRA.
> When principles conflict, the one listed earlier takes priority.

---

## 1. Clarity

The user should never wonder "what does this do?" or "what happens next?"

- Every screen has one obvious purpose.
- Labels describe actions, not abstractions. "Upload your photo" not "Submit media."
- Navigation is self-evident. If you need a tutorial to explain it, redesign it.
- Status is always visible: what's happening, what just happened, what to do next.
- Icons are paired with text labels. Icon-only buttons are permitted only for universally understood symbols (close, back, menu).

**Test**: Show the screen to someone for 3 seconds. If they can't tell you what it does, it fails.

---

## 2. Confidence

MIRA must feel like it knows what it's doing.

- No hedging language: "We'll try to process your image" → "Processing your image."
- Results are presented decisively, not tentatively.
- Errors are specific and solution-oriented: "This photo needs better lighting — try near a window" not "Upload failed."
- The UI never apologizes excessively. One acknowledgment, one fix path, move forward.
- Empty states are designed, not afterthoughts. They guide, not just inform.

**Test**: Does the copy sound like it was written by someone who believes in the product?

---

## 3. Speed

Speed is a feature. Perceived performance matters as much as actual performance.

- Optimistic UI where safe: show the expected result immediately, reconcile in background.
- Skeleton screens, not spinners, for content loading.
- Progressive image loading: blur-up or low-res preview → full quality.
- Prefetch likely next screens (e.g., when user hovers on a garment, prefetch detail view).
- Never block the UI for non-critical operations (analytics, logging, non-essential fetches).

### Performance Budgets
| Metric | Target |
|---|---|
| First Contentful Paint | < 1.5s |
| Largest Contentful Paint | < 2.5s |
| Cumulative Layout Shift | < 0.1 |
| First Input Delay | < 100ms |
| Total Blocking Time | < 200ms |
| Time to Interactive | < 3.5s |

**Test**: Does the app feel instant on a mid-range phone with 4G?

---

## 4. Delight Without Gimmicks

Delight comes from things working beautifully, not from confetti animations.

- Delight is: a try-on result loading with a smooth reveal. A garment card that responds to hover with subtle depth. A result that looks better than expected.
- Delight is NOT: particle effects, emoji rain, achievement badges for uploading a photo, gamification of basic tasks.
- Surprise should be positive and rare: an unexpectedly good result, a thoughtful detail in an edge case.
- Animations serve function (communicate state change, direct attention) before decoration.
- Sound and haptics: not used unless there is a clear, tested reason.

**Test**: Would this delight moment feel at home on a luxury fashion site?

---

## 5. Privacy Reassurance

Users are uploading personal photos. Every interaction must reinforce safety.

- **Proactive, not reactive**: Tell users what happens to their data before they ask.
- **Contextual**: Privacy messaging appears at the moment of relevance (upload screen, result screen) — not buried in a settings page.
- **Specific**: "Your photo is processed on our servers and deleted within 24 hours" not "We take your privacy seriously."
- **Visual**: Use lock icons, shield indicators, or subtle visual cues near upload areas.
- **Control**: Users can delete their photos and results at any time, with immediate confirmation.

### Privacy Messaging Placement
- Upload screen: One-line statement about photo handling
- Result screen: Note about storage duration
- Account settings: Full privacy controls with delete options
- Footer: Link to privacy policy (human-readable, not legal-only)

**Test**: Would a privacy-conscious user feel comfortable uploading a full-body photo?

---

## 6. Error Recovery

Errors are inevitable. Recovery must be effortless.

- **Prevent first**: Validate inputs before submission. Check file types, sizes, and dimensions client-side before upload.
- **Explain clearly**: What went wrong, in human language. Not error codes, not stack traces.
- **Offer a path forward**: Every error message includes a specific action the user can take.
- **Preserve work**: Never lose user input on error. If a form fails, the data remains. If an upload fails, offer retry without re-selection.
- **Degrade gracefully**: If the try-on service is slow or down, show the garment details, offer to notify when ready, or suggest alternatives — do not show a blank page.

### Error Hierarchy
1. **Inline validation**: Catch issues before submission (file too large, wrong format)
2. **Contextual error**: Show near the relevant element, not as a generic toast
3. **Full-screen error**: Only for unrecoverable states (service completely unavailable)
4. **Retry**: Automatic retry for transient failures (network blips) — max 2 attempts, then surface to user

**Test**: Can a user recover from any error state in one action?

---

## 7. User Control

The user is in charge. The product assists, never overrides.

- **Undo**: Any destructive action (delete photo, remove result) has a confirmation or undo window.
- **Back**: The back button always works. It always goes where the user expects.
- **Cancel**: Long-running operations (try-on processing) can be cancelled.
- **Preferences**: If the product makes assumptions (default garment size, preferred style), users can change them easily.
- **No traps**: Users can leave any flow at any point without losing data or being punished.
- **No forced actions**: Never require sharing, rating, or feedback to continue using core features.

**Test**: Can the user exit any screen and return without losing progress?

---

## 8. Premium Perception

MIRA must feel premium without being pretentious.

- **Quality over quantity**: Show 6 beautifully presented garments, not 60 in a cramped grid.
- **Details matter**: Consistent border radii, aligned elements, proper kerning, matching icon weights.
- **Restraint**: Premium means knowing what to leave out. If a component doesn't serve the user's goal, remove it.
- **Imagery**: Only high-resolution, well-lit, properly color-corrected images. One bad image cheapens the entire experience.
- **Typography**: Type should feel editorial. Hierarchy, weight contrast, and generous line height.
- **Negative space**: White space is not wasted space. It is a design element that communicates quality.

**Test**: Place a screenshot of MIRA next to Net-a-Porter, Ssense, or Farfetch. Does it belong?

---

## 9. Accessibility

Accessibility is not an add-on. It is a requirement.

- **Color contrast**: All text meets WCAG AA minimum (4.5:1 normal text, 3:1 large text).
- **Keyboard navigation**: Every interactive element is reachable and operable via keyboard.
- **Screen readers**: Semantic HTML, ARIA labels where needed, logical focus order.
- **Motion sensitivity**: Respect `prefers-reduced-motion`. Provide static alternatives to all animations.
- **Touch targets**: Minimum 44×44px on mobile.
- **Text scaling**: UI must remain functional at 200% browser zoom.
- **Alt text**: Every image has descriptive alt text. Decorative images use `alt=""`.
- **Focus indicators**: Visible, styled focus rings on all interactive elements. Never `outline: none` without a replacement.

### Accessibility Audit Checklist
- [ ] axe-core scan passes with 0 critical/serious issues
- [ ] Tab order follows visual layout
- [ ] All form inputs have associated labels
- [ ] Color is not the sole means of conveying information
- [ ] Dynamic content changes are announced to assistive technology

**Test**: Can a keyboard-only user complete the core try-on flow?

---

## 10. Internationalization

MIRA is designed for a global audience from day one.

- **Text expansion**: Layouts accommodate 40% text expansion for translations without breaking.
- **Directionality**: Components use logical properties (`margin-inline-start` not `margin-left`) to support RTL.
- **Date/number formats**: Use locale-aware formatting. No hardcoded "MM/DD/YYYY."
- **Cultural sensitivity**: Fashion imagery and copy should feel globally inclusive, not US/Euro-centric.
- **No embedded text in images**: All text is rendered as text, never baked into images.
- **String externalization**: All user-facing strings in message files, not hardcoded in components.
- **Pluralization**: Use proper plural rules, not string concatenation with "s."

**Test**: Would this screen work in Japanese, Arabic, and Portuguese without layout breakage?

---

*These principles are referenced in design reviews, PR reviews, and automated quality checks. Cite the relevant principle number when flagging issues.*
