# MIRA Product Excellence Standard

> The bar for every screen, flow, and interaction in MIRA.
> If work does not meet this standard, it does not ship.

---

## 1. What "Excellent" Means for MIRA

Excellence is the intersection of **trust, beauty, and speed**.

- **Trust**: The user believes their photos are safe, the results are real, and the product respects them.
- **Beauty**: Every screen could be a screenshot in a fashion magazine editorial — intentional, restrained, and confident.
- **Speed**: The product feels instant. Where it cannot be instant, it communicates progress with elegance.

A feature is excellent when a fashion-forward user would screenshot it and share it unprompted.

---

## 2. What Is Unacceptable

| Category | Unacceptable Example |
|---|---|
| Visual | Generic card grids with drop shadows and rounded corners that look like every SaaS dashboard |
| Typography | System fonts, inconsistent sizes, no typographic hierarchy |
| Motion | Jittery transitions, no loading feedback, layout shifts on content load |
| Trust | No indication of what happens to uploaded photos; unclear data handling |
| Mobile | Desktop-first layouts squeezed onto phone screens; touch targets under 44px |
| Copy | "Welcome to our platform!" — generic, corporate, personality-free language |
| Results | A try-on result page that looks like a file manager or thumbnail grid |
| Errors | Raw error codes, blank screens, or "Something went wrong" with no recovery path |

If any of these appear in a PR, it is rejected.

---

## 3. Product Personality

MIRA is:

- **Confident, not arrogant.** It knows it delivers. It does not need to oversell.
- **Fashion-forward, not trendy.** Timeless aesthetics over this-season gimmicks.
- **Warm, not corporate.** Human voice, direct language, no jargon.
- **Precise, not cold.** Every pixel is intentional, but the experience feels effortless.
- **Private, not paranoid.** It protects user data without making privacy feel scary.

MIRA is NOT: cutesy, gamified, startup-bro, enterprise, clinical, or cheap.

---

## 4. Trust Requirements

Trust is non-negotiable. Every screen must answer these questions without the user having to ask:

1. **What happens to my photo?** — Clear, visible privacy statement near every upload interaction.
2. **Is this a real result?** — Results must look credible. No uncanny-valley composites. If quality is limited, say so honestly.
3. **Who sees my data?** — Privacy controls must be discoverable within one tap.
4. **Can I delete everything?** — Account/data deletion must be accessible, not buried.
5. **Is this a real company?** — Footer, about, contact — all must exist and feel legitimate.

### Trust Signals Checklist
- [ ] Upload flow includes a privacy micro-copy line
- [ ] Results page does not display user photos in a way that implies sharing
- [ ] No dark patterns (pre-checked sharing, confusing opt-outs)
- [ ] HTTPS, secure headers, no mixed content
- [ ] Session handling is invisible but secure

---

## 5. Fashion / Visual Requirements

MIRA is a fashion product. Visual quality is product quality.

- **Photography**: All placeholder/demo images must be editorial quality. No stock photos with watermarks, no low-resolution thumbnails, no awkward crops.
- **Color**: Palette must feel curated, not generated. Neutral base with one intentional accent. No rainbow gradients.
- **Garments**: Product images must be presented at high resolution with accurate color representation. Garment cards should feel like a luxury e-commerce product page.
- **White space**: Generous. Let content breathe. Cramped layouts signal cheapness.
- **Consistency**: If a garment card has a shadow on one page, it has the same shadow everywhere.

---

## 6. Conversion Requirements

Every flow must be designed to move users forward without pressure:

- **Primary CTA**: One clear, dominant action per screen. Not three competing buttons.
- **Try-on entry**: Must be reachable in ≤ 2 taps from any catalog page.
- **Upload friction**: Minimal. Drag-and-drop on desktop, camera/gallery on mobile. No multi-step wizards for a single photo.
- **Result to action**: After seeing a try-on result, the next step (save, share, try another) must be immediately obvious.
- **Onboarding**: Progressive disclosure. Do not front-load a 5-screen tutorial. Let users explore and learn.

### Conversion Quality Gates
- First meaningful interaction within 10 seconds of landing
- Try-on flow completable in under 60 seconds (excluding processing time)
- No dead-end screens — every state has a forward path

---

## 7. Mobile-First Expectations

Mobile is the primary platform. Desktop is the adaptation, not the other way around.

- **Touch targets**: Minimum 44×44px. No exceptions.
- **Thumb zone**: Primary actions within natural thumb reach on standard phone sizes.
- **Viewport**: No horizontal scroll. Ever.
- **Images**: Responsive, lazy-loaded, with proper aspect ratios. No layout shift on load.
- **Input**: Minimize typing. Use camera, gallery picker, and selection UI instead of text fields where possible.
- **Orientation**: Portrait-first. Landscape should not break, but is not the design target.
- **Performance**: First contentful paint under 2 seconds on 4G. Total blocking time under 200ms.

---

## 8. Demo Readiness Expectations

MIRA must be demo-ready at all times on the main branch.

- **No broken flows**: Every primary flow (browse catalog → select garment → upload photo → see result) must work end-to-end.
- **Graceful degradation**: If a backend service is down, the UI shows a dignified fallback — not a crash, not a blank page.
- **Sample data**: Demo accounts must have pre-loaded, high-quality sample results that showcase the product at its best.
- **Performance**: Demo must be fast. No "let me refresh, it's slow today" moments.
- **Visual polish**: No placeholder text ("Lorem ipsum"), no broken images, no unstyled components on any reachable page.

### Demo Readiness Checklist
- [ ] All primary flows complete without errors
- [ ] Sample try-on results loaded and visually impressive
- [ ] Mobile experience tested on real device (not just browser emulator)
- [ ] No console errors or warnings visible
- [ ] Loading states are polished, not raw spinners

---

## 9. Human Review Checklist

Before any PR merging UI work, a human reviewer must verify:

### Visual
- [ ] Does this look like a premium fashion product, not a SaaS dashboard?
- [ ] Is typography consistent with the design system?
- [ ] Are images high quality and properly sized?
- [ ] Is there sufficient white space?

### Interaction
- [ ] Are all interactive elements responsive to touch/click with feedback?
- [ ] Do transitions feel smooth and intentional?
- [ ] Are loading states handled gracefully?
- [ ] Do error states provide clear recovery paths?

### Trust
- [ ] Is privacy communication present where user data is involved?
- [ ] Are there any dark patterns?
- [ ] Would a first-time user feel safe uploading a photo?

### Mobile
- [ ] Tested on mobile viewport (375px minimum)?
- [ ] Touch targets ≥ 44px?
- [ ] No horizontal overflow?
- [ ] Images load performantly?

### Copy
- [ ] Is the language warm, confident, and specific to MIRA?
- [ ] No placeholder text remaining?
- [ ] No generic/corporate tone?

### Accessibility
- [ ] Color contrast meets WCAG AA (4.5:1 for text)?
- [ ] Interactive elements are keyboard-navigable?
- [ ] Images have meaningful alt text?
- [ ] Screen reader flow is logical?

---

*This standard is enforced by human review, automated auditor checks, and design director review. No exceptions without explicit sign-off.*
