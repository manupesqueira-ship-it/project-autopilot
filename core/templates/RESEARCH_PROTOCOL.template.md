# Research Protocol

When Project Autopilot encounters uncertainty that cannot be resolved by reading the codebase or project control files, it must propose research before proceeding. Research is never silently executed. It is proposed with scope, time estimate, and expected output.

## When Research Is Required

- **Unknown technical provider**: API not previously used, undocumented behavior, unclear rate limits.
- **Pricing and rate limits**: Before integrating any paid API, research current pricing, free tiers, and rate limits.
- **Legal, privacy, or security uncertainty**: Data handling requirements, GDPR/CCPA implications, biometric data regulations.
- **Architecture decisions with long-term consequences**: Database schema changes, auth strategy, storage architecture, provider lock-in.
- **Library or framework selection**: Before adding a dependency, research alternatives, maintenance status, bundle size impact.
- **AI/image/video/payment/storage provider evaluation**: Compare providers on quality, cost, latency, reliability, and API design.
- **Competitive or product benchmark**: When a product decision needs market context.
- **UX or design benchmark**: When a design decision needs precedent or best-practice context.

## Research Modes

### quick_check (10-15 minutes)
- Verify a single fact: API endpoint, pricing tier, library version, or config option.
- Output: One paragraph with source link.
- Example: "Does Supabase storage support signed URLs with expiry?"

### standard_research (30-45 minutes)
- Compare 2-3 options on defined criteria.
- Output: Comparison table + recommendation + risks.
- Example: "Compare Seedance 2.0 vs RunwayML vs Kling for try-on video generation."

### deep_research (90+ minutes)
- Full evaluation of a complex domain: legal requirements, architecture trade-offs, provider ecosystem.
- Output: Structured report with sections, sources, recommendations, and open questions.
- Example: "Evaluate biometric data handling requirements for a virtual try-on app operating in Mexico, US, and EU."

## Research Proposal Format

```
Research needed: [title]
Mode: quick_check | standard_research | deep_research
Estimated time: [X minutes]
Why: [one sentence explaining the uncertainty]
Expected output: [what the research should produce]
Blocking: [yes/no — does work stop until research is complete?]
```

## Rules

- Research is proposed, not silently executed, unless the task explicitly asks for research.
- The human or supervisor approves the research scope before execution begins.
- Research output is stored in `project_control/DECISIONS.md` or a dedicated research log.
- Research must cite sources when possible.
- Research must distinguish between verified facts and informed assumptions.
- Deep research should be scheduled as its own task, not embedded in an implementation task.
