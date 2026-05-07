# Design Director Standard

Project Autopilot must not accept mediocre UI just because it compiles.

The Design Director is a strict review layer for visual hierarchy, usability, brand coherence, accessibility, copy clarity, premium feel, and originality. It is evidence-driven: screenshots, Browser QA, Flow QA, visual QA artifacts, and human visual review matter more than static source heuristics.

## Rules

- UI/design changes require Design Director review.
- Major visual changes require fresh screenshots or human visual review.
- The Design Director can warn or block even when lint, typecheck, and build pass.
- Static scoring is directional, not absolute truth.
- Generic SaaS patterns, cheap gradients, random color use, unclear CTAs, weak typography, mobile overflow, and overdecorated UI should be penalized.
- Clear hierarchy, elegant restraint, strong visual identity, polished states, accessibility, and emotionally compelling product presentation should be rewarded.

## Required Output

- Verdict: `DESIGN_PASS`, `DESIGN_WARN`, `DESIGN_FAIL`, or `DESIGN_REQUIRES_HUMAN_VISUAL_REVIEW`.
- Scores for design, innovation, premium feel, usability, accessibility, and copy.
- Missing evidence and required follow-up actions.
