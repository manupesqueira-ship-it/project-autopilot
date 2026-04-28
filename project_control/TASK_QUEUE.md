# Task Queue

## Current Priority

### Adopt Project Autopilot

Use Project Autopilot as the reusable control system that lets Codex or Claude Code act as builders while OpenAI acts as supervisor and QA reviewer.

Acceptance criteria:

- Project control state files exist and are read before planning work.
- Project Autopilot supports guarded autonomy, one-cycle runs, and dry-run mode.
- Builder prompts are generated instead of executed automatically.
- Evidence collection supports git status, git diff, changed files, build output, typecheck output, test output when available, and screenshots later when configured.
- OpenAI supervisor hooks exist for next task planning, QA review, and correction prompt generation.
- Telegram alert hooks exist for blockers, missing credentials, retry exhaustion, unresolved broken builds, and approval-required events.
- Cost policy and model routing are loaded from Project Autopilot config.
- Blocking questions go to `BLOCKERS.md`.
- Non-blocking questions go to `HUMAN_QUESTIONS.md`.
- Iteration logs are written under `logs/`.

## Paused Product Work

- Additional Supabase feature wiring.
- Provider implementation work.
- Visual design changes.
- New product flows.
- Deployment.
