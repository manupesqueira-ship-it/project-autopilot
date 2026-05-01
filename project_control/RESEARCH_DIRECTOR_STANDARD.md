# Research Director Standard

Project Autopilot must know when a decision requires research before implementation.

The Research Director does not perform research automatically. It classifies research needs, creates structured requests, and blocks or warns when implementation would be premature.

## Research Modes

- `quick_check`: 5-15 minutes for a narrow factual check.
- `standard`: 30-60 minutes for vendor/API/architecture comparison.
- `deep_research`: 90+ minutes and requires explicit human approval.

## Triggers

- New API/provider choice.
- Security-sensitive decision.
- Paid API choice.
- Legal/privacy issue.
- UX benchmark needed.
- Competitive analysis needed.
- Unknown technical architecture.
- Pricing/cost risk.
- Compliance risk.
- Cloud, GitHub, VPS, or deployment architecture.
- AI model/vendor comparison.
- Image/video generation provider selection.
- User data retention decision.
- RLS/security design.
- Design inspiration or innovation benchmark.

## Rule

Do not fake research. Do not invent sources. If current evidence is insufficient, mark the decision as research-required.
