# MIRA Master Plan

MIRA is a premium virtual try-on MVP for fashion discovery. The product goal is to let a shopper create a lightweight profile, upload body reference photos, choose apparel, generate a realistic try-on image, optionally generate a short video, and move to purchase with confidence.

The product experience should feel premium, privacy-aware, bilingual, and fast. The current MVP is intentionally scaffolded around mocked generation providers and a Supabase schema so the team can validate flow, quality, and orchestration before investing in full provider integrations.

## Current Strategic Priorities

1. Stabilize the engineering workflow before adding more product features.
2. Use Codex or Claude Code as builders within strict guardrails.
3. Use OpenAI as supervisor and QA reviewer before human handoff.
4. Preserve the visual direction and premium interaction model.
5. Accumulate blockers and non-blocking human questions in durable project state files.

## Product Boundaries

- No additional product features should be built until the Agent Control Layer is usable.
- Supabase wiring should not expand until live end-to-end validation is planned.
- Generation providers should remain isolated behind provider modules.
- Privacy and user trust remain first-order product requirements.
