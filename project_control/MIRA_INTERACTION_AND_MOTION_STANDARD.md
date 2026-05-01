# MIRA Interaction and Motion Standard

> Motion in MIRA exists to communicate, not to decorate.
> Every animation must have a reason. If you can't articulate why it moves, it shouldn't.

---

## 1. Motion Principles

### Purpose-Driven
Motion serves exactly three functions in MIRA:
1. **Feedback** — Confirm an action was received (button press, upload started)
2. **Orientation** — Show where something came from or where it went (page transitions, panel slides)
3. **Focus** — Direct attention to a change (new result appeared, error surfaced)

If an animation doesn't serve one of these, remove it.

### Characteristics
- **Quick**: Interactions feel responsive. Most transitions complete in 150–300ms.
- **Smooth**: Easing curves, never linear. `ease-out` for entrances, `ease-in` for exits, `ease-in-out` for position changes.
- **Subtle**: The user should feel the motion, not watch it. If someone comments "cool animation," it's probably too much.
- **Consistent**: Same type of action = same type of motion. A panel slides in from the right on page one, it slides in from the right on every page.

---

## 2. Page Transitions

### Between Pages
- **Default**: Crossfade with 200ms duration. Content fades out (100ms) then new content fades in (100ms).
- **Drill-down** (catalog → detail): Content slides left, new page slides in from right. 250ms, ease-out.
- **Back**: Reverse of drill-down. Content slides right. 200ms, ease-out.
- **Modal open**: Overlay fades in (150ms), modal content scales from 0.95 to 1.0 with fade (200ms, ease-out).
- **Modal close**: Reverse, slightly faster (150ms total).

### Rules
- No full-page wipes, flips, or 3D transitions.
- Page content should begin rendering immediately — don't wait for exit animation to complete before starting the enter animation.
- Shared elements (header, navigation) should NOT transition — they remain stable to anchor the user.

---

## 3. Try-On Flow Feedback

The try-on flow is MIRA's core interaction. Motion here must build confidence.

### Upload Phase
| State | Motion |
|---|---|
| Photo selected | Thumbnail scales in from 0.9 to 1.0 (150ms, ease-out) with slight fade-in |
| Upload starting | Progress bar appears with slide-in from left (100ms) |
| Upload progress | Progress bar fills smoothly (CSS transition, no jumps) |
| Upload complete | Progress bar fills to 100%, then fades out (200ms) with checkmark fade-in |

### Processing Phase
| State | Motion |
|---|---|
| Processing starts | Stage text ("Analyzing photo…") fades in with upward slide (150ms) |
| Stage change | Current text fades out downward, new text fades in upward (200ms crossfade) |
| Processing complete | Stage text fades out, result area prepares (200ms) |

### Result Reveal
- **Primary reveal**: Result image fades in from slight blur to sharp (400ms, ease-out). This is MIRA's "wow moment" — it earns a slightly longer, more deliberate animation.
- **Supporting info** (garment name, actions): Stagger in 50ms after result image, simple fade-in (200ms).
- **No bounce, no zoom, no confetti.** The result image speaks for itself.

---

## 4. Skeleton / Loading States

### Skeleton Appearance
- Skeletons appear immediately (0ms delay) when content is loading.
- Shimmer animation: subtle gradient sweep from left to right, 1.5s duration, infinite loop.
- Shimmer gradient: from background color → slightly lighter → background color. Subtle, not glaring.

### Skeleton → Content Transition
- Content replaces skeleton with a simple fade (150ms). No elaborate reveals.
- All content in a group should appear together, not one card at a time (prevents "popcorn" loading).
- Exception: Image-heavy grids may stagger rows (not individual items) with 50ms delay per row.

### Processing Loaders
- For long operations (try-on processing, 5–30 seconds):
  - Use a designed progress state, not just a skeleton.
  - Show stages of processing as text updates.
  - Include a subtle progress indicator (determinate if possible, indeterminate if not).
  - Elapsed time display only if processing exceeds 10 seconds.

---

## 5. Microinteractions

Small interactions that make the product feel alive and responsive.

### Buttons
| Interaction | Motion |
|---|---|
| Hover | Background color shift (100ms, ease) |
| Press | Scale to 0.98 (50ms, ease-in) |
| Release | Scale back to 1.0 (100ms, ease-out) |
| Disabled | No motion. Reduced opacity (0.5) applied statically |

### Cards (Garment Cards)
| Interaction | Motion |
|---|---|
| Hover | Image scales to 1.03 within overflow-hidden container (200ms, ease-out). CTA fades in (150ms) |
| Hover exit | Reverse, same timing |
| Tap/Click | Brief scale to 0.98 (50ms) then navigate |

### Form Inputs
| Interaction | Motion |
|---|---|
| Focus | Border color transition (100ms). Floating label moves up (150ms, ease-out) if applicable |
| Error | Input border transitions to error color (100ms). Error message slides down + fades in (150ms) |
| Error clear | Error message fades out (100ms). Border returns to default (100ms) |

### Toggles & Checkboxes
| Interaction | Motion |
|---|---|
| Toggle | Knob slides (150ms, ease-in-out). Track color transitions (100ms) |
| Checkbox | Checkmark draws in with stroke animation (150ms) or scales in (100ms) |

### Toasts / Notifications
| Interaction | Motion |
|---|---|
| Enter | Slide in from top-right + fade (200ms, ease-out) |
| Auto-dismiss | Fade out + slide up (200ms, ease-in) after 4 seconds |
| Manual dismiss | Fade out (100ms) on close button click |

---

## 6. Accessibility-Safe Motion

### `prefers-reduced-motion` Support

When the user's OS is set to reduce motion:

- **Disable**: All translate/scale animations. Parallax effects. Auto-playing animations. Shimmer on skeletons.
- **Keep**: Opacity transitions (fade in/out at reduced duration, 100ms max). Color transitions. Essential state changes (progress bars).
- **Replace**: Slide transitions become instant crossfades. Skeleton shimmer becomes static skeleton.

### Implementation
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 100ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Focus Motion
- Focus ring appearance: instant (no fade-in). Users navigating by keyboard need immediate feedback.
- Focus-driven scroll: smooth scroll to focused element is acceptable even with reduced motion, as it aids orientation.

---

## 7. What Not to Animate

These motions are explicitly banned in MIRA:

| Banned Motion | Why |
|---|---|
| Bounce effects | Playful/childish, undermines premium feel |
| Spring/elastic physics | Same as above; over-engineered for UI |
| Rotate/flip transitions | Disorienting, gimmicky |
| Continuous background animations | Distracting, performance-draining |
| Scroll-jacking | Removes user control, causes nausea |
| Parallax backgrounds | Performance-heavy, adds no value |
| Auto-advancing carousels | Users can't read at forced pace |
| Text typing/typewriter effects | Slow, frustrating, artificially delays information |
| Number counting animations | Unnecessary for this product context |
| Confetti / particle effects | Not aligned with premium fashion context |
| Shake animations for errors | Aggressive, anxiety-inducing |
| Zoom-and-pan on page load | Disorienting, delays interaction |

---

## 8. Performance Constraints

Motion must never compromise performance.

### Technical Limits
- **Only animate these CSS properties**: `transform`, `opacity`. These are GPU-composited and cheap.
- **Never animate**: `width`, `height`, `top`, `left`, `margin`, `padding`, `border-width`, `font-size`, `box-shadow`. These trigger layout recalculation.
- **Exception**: `background-color` and `border-color` transitions are acceptable for state changes (they trigger paint, not layout).

### Budget
| Constraint | Limit |
|---|---|
| Concurrent animations on screen | ≤ 5 |
| Animation duration (UI feedback) | 100–300ms |
| Animation duration (content reveal) | 200–500ms |
| Total animation JS per page | 0 KB preferred (CSS only). Max 10 KB if JS animation library needed |
| Frame rate | 60fps minimum. If an animation drops below 60fps on a mid-range device, remove it |

### Testing
- All animations must be tested on a throttled CPU (Chrome DevTools, 4× slowdown).
- If an animation causes visible jank at 4× CPU slowdown, simplify or remove it.
- Layout shift caused by animations must be 0 (use `transform` for position changes, not layout properties).

---

*This standard is enforced in code review. Animations not meeting these criteria are flagged for removal.*
