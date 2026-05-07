# Quality Bar

Every builder task must satisfy these gates before it can be considered ready for human review.

## Technical Gates

- `npm run build` passes.
- `npm run typecheck` passes when available.
- `npm test` passes when a test script exists.
- No destructive commands are used.
- No changes are made to `.env`, `.env.local`, secrets, deployment files, or git history.
- Changes are narrowly scoped to the approved task.
- Errors are handled explicitly and surfaced clearly.
- New automation code defaults to supervised behavior.

## Visual Gates

- No visual design changes unless explicitly approved.
- Existing typography, spacing, motion, color, and page composition are preserved.
- No new UI surface is added without a clear product reason.
- Generated screenshots must be collected later when screenshot URLs are configured.

## Product Gates

- No new MIRA product features during control-layer work.
- Privacy-sensitive flows must avoid exposing user photos, env values, tokens, or secrets in logs.
- Provider integrations must remain isolated.
- Supabase expansion requires explicit human approval.

## Agent Evidence Gates

Each iteration should include:

- Task intent.
- Builder prompt.
- Git status.
- Changed files.
- Git diff summary or full diff when safe.
- Build/typecheck/test outputs as configured.
- QA review result.
- Open questions and blockers.
