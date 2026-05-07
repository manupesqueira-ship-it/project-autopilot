# MIRA UI Anti-Patterns

> Patterns that are explicitly rejected for MIRA.
> If you see any of these in a PR, it does not merge. If you see them in production, file a bug.

---

## 1. Generic SaaS Dashboard Look

**The problem**: MIRA looks like a Tailwind template, an admin panel, or a B2B analytics dashboard. Sidebars with icon lists, top bars with breadcrumbs, card grids with uniform shadows, blue accent everywhere.

**Why it kills MIRA**: MIRA is a consumer fashion product. It should feel like shopping at a boutique, not managing a Jira board. SaaS-generic design signals "utility" and "work" — the opposite of fashion.

**Red flags**:
- Left sidebar navigation with icon + label stacks
- Breadcrumb trails (home > catalog > dresses > item)
- Cards with identical drop shadows in uniform grids
- "Dashboard" as a page name or concept
- Tables for displaying product data to end users
- Blue-and-white default color scheme

**Instead**: Full-bleed imagery, editorial layouts, bottom navigation on mobile, visually-driven browsing. Think Zara app, not Salesforce.

---

## 2. Weak CTAs

**The problem**: The primary action on the page is unclear, visually timid, or competing with too many other actions.

**Why it kills MIRA**: If the user doesn't know what to do next, they leave. A fashion try-on product needs confident direction: "Try this on" should be unmissable.

**Red flags**:
- Multiple buttons of equal visual weight on the same screen
- Ghost/outline buttons used for primary actions
- CTAs that say "Submit," "Continue," "Go," or other generic verbs
- CTA buried below the fold on mobile
- CTA color that blends with the background
- Link-styled text for the primary action

**Instead**: One dominant CTA per screen. Filled, high-contrast, action-specific label ("Try On," "See Your Look," "Save Result"). Secondary actions are visually subdued (text link or outline).

---

## 3. Too Many Cards

**The problem**: Everything is a card. Settings are cards. Results are cards. Instructions are cards. The page is a wall of rectangles.

**Why it kills MIRA**: Cards create visual monotony. When everything is equally boxed, nothing has hierarchy. The user's eye has nowhere to land. It also feels like a back-office tool.

**Red flags**:
- More than 8 cards visible simultaneously on mobile
- Cards used for single-line information (status, a toggle, a label)
- Cards nested inside cards
- Cards with only text (no image or interactive element)
- Every section of a page wrapped in its own card

**Instead**: Use cards only for discrete, browsable items (garments, results). Use open layouts with typography and spacing to create hierarchy for other content. Section dividers, generous whitespace, and typographic contrast replace card borders.

---

## 4. Random Gradients

**The problem**: Gradients used decoratively without purpose — gradient headers, gradient buttons, gradient text, gradient backgrounds.

**Why it kills MIRA**: Cheap gradients are the hallmark of 2018 startup landing pages. They signal "we used a CSS gradient generator" rather than "we designed this intentionally." They fight with product imagery for attention.

**Red flags**:
- Linear gradients on header backgrounds (especially blue → purple)
- Gradient text (hard to read, browser-inconsistent)
- Rainbow or multi-stop gradients anywhere
- Gradients on buttons
- Animated gradients
- Gradients that serve no informational purpose

**Instead**: Solid, intentional background colors. If a gradient is truly warranted (rare), it should be barely perceptible — a 2-3% tone shift, not a color ramp. The only acceptable gradient is a subtle overlay on images to ensure text readability.

---

## 5. Bad Mobile Spacing

**The problem**: Desktop layout compressed onto a phone screen. Content edge-to-edge with no padding. Touch targets too small. Text too small. Elements overlapping.

**Why it kills MIRA**: Mobile is MIRA's primary platform. Poor mobile spacing makes the product feel broken, cheap, and frustrating to use.

**Red flags**:
- Content touching screen edges (no horizontal padding)
- Touch targets under 44×44px
- Less than 8px between tappable elements
- Text smaller than 14px on mobile
- Horizontal scrolling on any page
- Buttons that require precise tapping (small hit area)
- Form fields too narrow to see input clearly
- Modals that don't account for mobile keyboards

**Instead**: 16–24px horizontal page padding on mobile. 44px minimum touch targets. 8px minimum gap between interactive elements. Test every screen on a 375px viewport with actual fingers, not a cursor.

---

## 6. Fake Premium Imagery

**The problem**: Using stock photos, AI-generated fashion images with artifacts, low-resolution placeholder images, or inconsistent image styles to create a false sense of quality.

**Why it kills MIRA**: MIRA's core promise is visual. If the product images look fake, the try-on results won't be trusted either. One bad image undermines the entire catalog.

**Red flags**:
- Stock photos with visible watermarks or studio-generic poses
- AI-generated images with telltale artifacts (wrong finger counts, blurred text on clothing, impossible fabric draping)
- Mixed image styles (some studio, some lifestyle, some flat-lay, different backgrounds)
- Images with different aspect ratios in the same grid
- Placeholder images that have been "temporary" for more than one sprint
- Low-resolution images upscaled with visible blur

**Instead**: Consistent, high-quality product photography. If real product images aren't available yet, use a designed placeholder system (garment silhouettes, category illustrations) rather than faking quality. Admit what's placeholder rather than pretending.

---

## 7. Confusing Upload States

**The problem**: The user uploads a photo and has no idea what's happening. No progress, no confirmation, no error if it fails. Or worse: the upload state is ambiguous — did it work? Is it still going?

**Why it kills MIRA**: The upload is MIRA's critical trust moment. The user just shared a personal photo. If the product goes silent or acts confused, trust evaporates instantly.

**Red flags**:
- Upload button with no visual feedback on click
- Spinner with no text explanation ("loading…" tells nothing)
- No progress indicator for uploads over 1 second
- Upload "completes" but no confirmation is shown
- Error after 30 seconds with no prior indication of trouble
- Re-upload required but previous selection is lost
- Multiple upload buttons on the same screen with different behaviors
- Drag-and-drop area that doesn't indicate it accepts drops

**Instead**: Immediate feedback on file selection (thumbnail preview). Progress bar for upload. Clear stage communication ("Uploading… Processing… Almost ready…"). Success confirmation with the uploaded image visible. Error with specific cause and one-tap retry. Drag zone with clear affordance (dashed border, icon, instruction text).

---

## 8. Hidden Privacy Risk

**The problem**: The user uploads personal photos but the product doesn't communicate what happens to them, how long they're stored, or who can see them. Privacy information is buried in a legal page nobody reads.

**Why it kills MIRA**: Fashion try-on requires body photos. This is intimate data. If users don't feel safe, they won't use the product. Privacy failure isn't just a UX issue — it's an existential product risk.

**Red flags**:
- No privacy messaging anywhere near the upload flow
- Privacy policy only accessible via footer link
- Privacy language that is purely legal ("pursuant to Section 4.2…") with no plain-language summary
- Photos shared or displayed in any context the user didn't explicitly consent to
- No visible option to delete uploaded photos or results
- Social sharing enabled by default
- Photo metadata (location, device info) collected without disclosure
- User photos used in promotional material or examples without explicit consent

**Instead**: One-line privacy summary on the upload screen ("Your photo is processed securely and auto-deleted in 24 hours"). Delete button accessible from any result view. Privacy settings within one tap of account menu. Plain-language data summary alongside legal policy. Never share, display, or use user photos beyond the stated purpose.

---

## 9. Unclear Result States

**The problem**: The user completed a try-on but can't tell if the result is good, partial, failed, or still processing. Results are shown without context about quality, limitations, or next steps.

**Why it kills MIRA**: The result is the payoff for the entire flow. Ambiguity here destroys satisfaction and trust. "Is this how it's supposed to look?" is a question the user should never have to ask.

**Red flags**:
- Result displayed without any quality/confidence indicator
- Result that's clearly low-quality shown at full size without acknowledgment
- No distinction between "processing" and "done" states
- Multiple results shown with no indication of which is best or most recent
- Result page with no next action (dead end)
- Failed result shown as if it succeeded (garment in wrong position, obvious artifacts)
- Result thumbnail too small to evaluate quality
- No way to compare result with original photo

**Instead**: Result presented at full quality with clear "Result ready" confirmation. Quality issues acknowledged with specific messaging ("Lighting in your photo made shadows difficult — try a brighter photo for better results"). Clear primary action (save, share, try another). Failed results explicitly flagged with guidance for improvement. History of results accessible and organized.

---

## 10. Overbuilt Control Panels

**The problem**: Settings, preferences, and controls that offer more configuration than the user needs or wants. Dropdown menus with 15 options. Settings pages with 30 toggles. Advanced modes that nobody activates.

**Why it kills MIRA**: Complexity signals enterprise software. MIRA is not Photoshop. Users came to try on clothes, not configure a system. Every unnecessary control is cognitive load that delays the user from their goal.

**Red flags**:
- Settings page with more than 10 options
- Nested settings (settings within settings)
- "Advanced" mode or section
- Dropdown menus with more than 7 options
- Filter panels with more than 5 filter categories
- Configuration required before using a core feature
- Toggle or switch whose purpose isn't immediately obvious
- Controls labeled with jargon ("Enable WebGL rendering," "Inference mode")
- Admin/debug controls visible in production UI

**Instead**: Intelligent defaults that work for 90% of users. Settings page with ≤ 5 meaningful options. Filtering that uses common fashion categories (size, color, category, price range) — nothing more unless data proves demand. Progressive disclosure: show simple controls first, reveal complexity only when the user seeks it. Never expose technical implementation details to end users.

---

## Pattern Recognition Guide

When reviewing a PR or design, scan for these meta-patterns:

| Signal | Likely Anti-Pattern |
|---|---|
| Screen looks like it could be in any SaaS product | #1 Generic SaaS |
| User would have to think about what to click | #2 Weak CTAs |
| Page feels like a wall of rectangles | #3 Too Many Cards |
| Colors compete with product imagery | #4 Random Gradients |
| You'd struggle to tap accurately on a phone | #5 Bad Mobile Spacing |
| Images feel inconsistent or untrustworthy | #6 Fake Premium |
| You can't tell what the product is doing | #7 Confusing Upload |
| You'd hesitate to upload a personal photo | #8 Hidden Privacy |
| You're unsure if the result is done/good/failed | #9 Unclear Results |
| You see controls you'd never use | #10 Overbuilt Controls |

---

*Every anti-pattern in this document has been seen in real MIRA work or comparable products. They are not theoretical — they are traps. Review against this list before every merge.*
