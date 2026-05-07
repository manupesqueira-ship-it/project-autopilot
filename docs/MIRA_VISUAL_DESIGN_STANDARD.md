# MIRA Visual Design Standard

> Visual direction for every surface in MIRA.
> This is not a component library — it defines the principles and constraints that a component library must follow.

---

## 1. Typography Direction

MIRA typography is editorial, not utilitarian.

### Hierarchy
| Level | Usage | Weight | Relative Size |
|---|---|---|---|
| Display | Hero headlines, landing page | Light or Regular | 3× base |
| H1 | Page titles | Medium | 2× base |
| H2 | Section headers | Medium | 1.5× base |
| H3 | Card titles, subsections | Semibold | 1.25× base |
| Body | Primary content | Regular | 1× base (16px minimum) |
| Caption | Metadata, timestamps | Regular | 0.875× base |
| Overline | Labels, categories | Medium, uppercase, tracked | 0.75× base |

### Rules
- **Minimum body size**: 16px on all devices. No 12px body text.
- **Line height**: 1.5 for body text, 1.2 for headings, 1.7 for long-form reading.
- **Measure**: Body text lines should not exceed 65 characters. Use `max-width` to constrain.
- **Weight contrast**: Use at most 3 weights on a single screen. Weight changes signal hierarchy, not decoration.
- **Letter spacing**: Tighten headings slightly (-0.01–-0.02em). Open up overlines (+0.05–0.1em). Never adjust body text spacing.
- **Font pairing**: One sans-serif for UI. Optionally one serif for editorial/display use. No more than two typefaces total.

---

## 2. Spacing Rhythm

All spacing derives from a base unit. Consistency creates visual calm.

### Base Unit: 4px

| Token | Value | Usage |
|---|---|---|
| `space-1` | 4px | Inline element gaps, icon-to-label |
| `space-2` | 8px | Tight component padding, list item gaps |
| `space-3` | 12px | Input padding, compact card padding |
| `space-4` | 16px | Standard component padding |
| `space-6` | 24px | Section padding on mobile |
| `space-8` | 32px | Section gaps, card gaps |
| `space-12` | 48px | Major section separation |
| `space-16` | 64px | Page-level vertical rhythm |
| `space-24` | 96px | Hero/landing page vertical space |

### Rules
- **Never use arbitrary values**. If 20px "looks right," use 16px or 24px instead.
- **Vertical rhythm > horizontal**: Prioritize consistent vertical spacing between sections.
- **Mobile reduction**: On viewports < 640px, outer padding reduces by one step (e.g., `space-8` → `space-6`).
- **Component internal spacing**: Always smaller than the gap between components.

---

## 3. Color Principles

Color in MIRA is quiet, confident, and never the star.

### Philosophy
- The product imagery (garments, try-on results) should be the most colorful thing on screen.
- The UI itself uses a restrained neutral palette with one accent color for interactive elements.
- Color must not be the only way to convey information (accessibility requirement).

### Palette Structure
| Role | Description | Example Usage |
|---|---|---|
| **Surface** | Background tones, near-white to warm gray | Page background, card background |
| **On-surface** | Text and icons on surface colors | Body text, secondary text, icons |
| **Accent** | Single brand color, used sparingly | Primary buttons, active states, links |
| **On-accent** | Text/icons on accent backgrounds | Button labels |
| **Success** | Positive feedback | Upload complete, result ready |
| **Warning** | Caution states | File size near limit |
| **Error** | Destructive / failure states | Upload failed, invalid input |
| **Overlay** | Semi-transparent backgrounds | Modals, image overlays |

### Rules
- **Maximum 2 non-neutral colors** visible on any single screen (accent + one semantic color).
- **No gradients on backgrounds** unless specifically approved for a hero section and executed with subtlety (2-3% opacity shift, not rainbow).
- **Dark mode**: If implemented, it must be a fully designed experience, not an inverted light mode.
- **Surface colors**: Warm undertone preferred. Pure #FFFFFF is acceptable but pure #000000 for text is not — use a near-black (e.g., #1A1A1A).
- **Opacity**: Use opacity for hover states and overlays, not for creating new colors.

---

## 4. Image Presentation

Images are MIRA's core product. They must be treated with editorial care.

### Garment Images
- **Aspect ratio**: Consistent within any grid or list. 3:4 for portrait garments, 1:1 for thumbnails.
- **Background**: Clean, consistent. Remove-background or studio white preferred.
- **Quality**: Minimum 800px on the longest edge for card views. 2x for retina.
- **Loading**: Progressive — blur placeholder → full image. Never a blank space that pops in.
- **Cropping**: Smart cropping that preserves the garment's key features. Never clip necklines, hemlines, or key details.

### Try-On Results
- **Presentation**: Results are the hero. Full-width on mobile, generous sizing on desktop.
- **Comparison**: Before/after or side-by-side must use identical framing and consistent image sizing.
- **Quality indicator**: If a result has quality limitations, show a subtle badge rather than hiding it.
- **Zoom**: Pinch-to-zoom on mobile, click-to-zoom on desktop for result detail.

### General Image Rules
- No visible compression artifacts.
- No broken image icons — always a styled fallback.
- Lazy loading for below-fold images with `loading="lazy"` and proper `width`/`height` attributes to prevent CLS.
- All images must have alt text. Garment images: describe the garment. Results: describe the try-on combination.

---

## 5. Product Card Standard

The garment card is MIRA's most repeated element. It must be perfect.

### Anatomy
```
┌──────────────────────┐
│                      │
│    [Garment Image]   │  ← 3:4 aspect ratio, fills card width
│                      │
├──────────────────────┤
│  Brand Name          │  ← Overline style, uppercase
│  Garment Title       │  ← H3 weight, 2 lines max, ellipsis
│  $Price              │  ← Body weight
│  [Try On]            │  ← CTA, visible on hover/always on mobile
└──────────────────────┘
```

### Rules
- **No drop shadows** on cards. Use subtle border or background contrast to define edges.
- **Border radius**: Consistent across all cards. Small (4–8px) preferred. No pill-shaped cards.
- **Grid**: 2 columns on mobile, 3–4 on desktop. Gap matches spacing rhythm.
- **Hover state**: Subtle image zoom (scale 1.02–1.05) with overflow hidden and CTA reveal. No color inversion, no bounce.
- **Selection state**: Clear, accessible indicator (border accent, checkmark overlay).
- **Loading state**: Skeleton matching exact card dimensions — not a generic gray box.

---

## 6. Result Page Standard

The try-on result is MIRA's defining moment. This page must be exceptional.

### Layout
- **Mobile**: Result image fills viewport width with minimal padding. Controls below.
- **Desktop**: Result image centered, generous surrounding space. Controls alongside or below.

### Required Elements
1. **Result image** — highest quality available, zoomable
2. **Garment identification** — name, brand, price visible without scrolling
3. **Primary action** — "Save" or "Share" as single prominent CTA
4. **Secondary actions** — "Try another garment," "Try different photo" as text links or secondary buttons
5. **Quality/confidence** — if applicable, a tasteful indicator of result quality
6. **Privacy note** — micro-copy about result storage duration

### What to Avoid on Results
- Cluttered toolbars with too many icons
- Comparison sliders that are finicky on mobile
- Auto-playing videos or animations that distract from the result
- Watermarks that damage the user's perception of quality

---

## 7. Catalog Standard

The catalog is where users browse and decide. It must balance density with clarity.

### Layout Options
| Layout | When to Use |
|---|---|
| Grid (2-col mobile, 3-4 desktop) | Default browsing, maximum items visible |
| List | Detail-heavy browsing, when descriptions matter |
| Featured + Grid | Curated landing with hero items |

### Filtering & Sorting
- **Filters**: Slide-in panel on mobile (not inline, it wastes space). Sidebar on desktop.
- **Active filters**: Shown as removable chips above the grid. Count of results visible.
- **Sort**: Dropdown, not tabs. Keep it minimal (Recommended, Price, New).
- **No results**: Designed empty state with suggestions ("Try removing a filter" or "Browse all").

### Pagination / Infinite Scroll
- **Preferred**: "Load more" button over infinite scroll (gives user control, better for SEO).
- **If infinite scroll**: Include a footer that's reachable, and a "back to top" shortcut.
- **Never**: Pagination with numbered pages on mobile.

---

## 8. Loading, Empty, and Error States

Every state is a designed state. No screen is ever "not designed yet."

### Loading States
- **Skeleton screens**: Match the layout of the content they replace. Same heights, widths, and spacing.
- **Shimmer**: Subtle left-to-right shimmer animation on skeletons. Not pulsing opacity.
- **Processing (try-on)**: A dedicated, designed wait state. Progress indication (percentage or stage: "Analyzing photo… Fitting garment… Rendering result…"). Engaging, not anxiety-inducing.
- **Never**: Raw spinner only. Spinner + skeleton is acceptable if the spinner indicates a specific operation.

### Empty States
- **First-time empty**: Friendly, guiding. Illustration or icon + explanation + CTA to start. "Your try-on results will appear here. Start by browsing the catalog."
- **Filtered empty**: Actionable. "No garments match these filters. [Clear filters]"
- **Error empty**: See error states below.

### Error States
- **Inline**: Red border + message near the relevant input. No toasts for form errors.
- **Section-level**: Replace the failed content area with error message + retry. Don't blank the whole page.
- **Page-level**: Only for full page failures. Styled error page with illustration, message, and links to working sections.
- **Transient**: Auto-dismiss toasts for non-critical issues (network blip recovered). Top-right, 4 second duration, dismissible.

---

## 9. What to Avoid

These are visual anti-patterns that are explicitly forbidden in MIRA:

| Avoid | Why | Instead |
|---|---|---|
| Drop shadows on cards | Looks dated and SaaS-generic | Subtle borders or background contrast |
| Gradient backgrounds | Signals cheap/promotional design | Solid surfaces with intentional color |
| Rounded pill buttons for primary actions | Feels playful, not premium | Subtle border radius (4–8px) |
| Neon/electric accent colors | Fights with garment imagery | Muted, sophisticated accent tones |
| Floating action buttons (FAB) | Mobile UX anti-pattern for this context | Inline CTAs within content flow |
| Icon-only navigation | Ambiguous without labels | Icons + text labels |
| Parallax scrolling | Performance-heavy, often nauseating | Static, well-composed layouts |
| Carousel/slider for core content | Hides content, poor mobile UX | Grid or vertical scroll |
| Thin-weight body text | Hard to read, signals fragility | Regular weight, 16px minimum |
| Stock photography | Destroys trust and authenticity | Real product photos or designed illustrations |
| Modal overuse | Interrupts flow, traps users | Inline expansion or dedicated pages |
| Animated backgrounds | Distracts from product imagery | Static, quiet surfaces |

---

*This standard is the visual contract. Deviations require Design Director approval with documented rationale.*
