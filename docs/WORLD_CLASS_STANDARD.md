# World-Class Standard

Every task, review, and delivery in this project must meet the following non-negotiable standards. "Good enough" is not the bar. The bar is: would a discerning customer trust this with their data, time, and money?

## UI/UX Standard

- Every interactive element must be reachable, tappable, and visibly responsive.
- Every button must do exactly what its label promises or be disabled with a clear reason.
- Loading, empty, and error states must be designed, not just functional.
- Typography, spacing, and color must be consistent with the design system.
- Mobile, tablet, and desktop must all be usable — not just technically rendered.
- Animations must feel intentional, not decorative or distracting.

## Backend Standard

- Every API route must validate input, handle errors, and return meaningful status codes.
- Database writes must be atomic or clearly documented as non-atomic.
- Background jobs must be observable: status, progress, failure reason.
- No silent failures. Every catch block must log or surface the error.
- Timeouts must be explicit, not left to framework defaults.

## Data Standard

- Every piece of customer data must be mapped: what it is, where it is stored, why it is collected.
- Sensitive data (email, photos, body measurements) must be stored in private buckets or encrypted columns.
- Data must never appear in logs, prompts, screenshots, or error messages unless explicitly safe.
- Retention and deletion expectations must be documented even if not yet enforced.

## QA Standard

- Every page must be visited and every primary flow must be walked end-to-end before a task is marked complete.
- Console errors, network failures, and uncaught exceptions are blockers, not warnings.
- Regression in existing functionality is a blocker.
- Acceptance criteria must be verified individually, not assumed from build success.

## Design Standard

- No visual changes unless the task explicitly requires them.
- Design tokens, typography, spacing, and color must match the locked design system.
- New UI surfaces require a clear product reason and explicit approval.

## Research Standard

- Unknown providers, pricing models, rate limits, or legal implications require research before implementation.
- Research must be proposed with a time estimate and scope, not silently executed.
- Architectural decisions with long-term consequences require documented trade-off analysis.

## Security and Privacy Standard

- No secrets in code, logs, prompts, or version control.
- No public exposure of private storage buckets.
- No client-side storage of sensitive data beyond what the flow requires.
- Auth boundaries must be documented even when auth is not yet implemented.

## Performance Standard

- Pages must load in under 3 seconds on a reasonable connection.
- Bundle sizes must not grow without a clear reason.
- Database queries must be indexed for common access patterns.
- No N+1 queries in list views.

## Reliability Standard

- The app must not crash on any reachable route.
- Missing data must result in graceful fallbacks, not white screens.
- External service failures (Supabase, OpenAI, Seedance) must be handled with clear user-facing messages.
- Polling and retry logic must have bounded attempts and clear timeout behavior.
