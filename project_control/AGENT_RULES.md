# Agent Rules

## Hard Restrictions

Agents must not:

- Modify `.env` or `.env.local`.
- Print, copy, summarize, or expose secret values.
- Modify deployment files without explicit human approval.
- Modify git history.
- Run destructive commands.
- Delete files.
- Deploy the application.
- Change visual design during control-layer work.
- Build MIRA product features during control-layer work.
- Expand Supabase wiring during control-layer work.

## Human Approval Required

Human approval is required before:

- Any deployment action.
- Any change to authentication, billing, privacy, legal, or data retention behavior.
- Any change to `.env.example` that adds new required credentials.
- Any database migration or Supabase schema change.
- Any provider integration that spends money or calls external generation APIs.
- Any dependency installation or package upgrade.
- Any destructive command or file deletion.
- Any git history rewrite, force push, reset, or clean.
- Any switch from supervised mode to automatic execution mode.

## Builder Requirements

Builders must:

- Read `project_control/` before proposing work.
- Keep changes scoped to the current task.
- Preserve existing architecture and visual style.
- Provide evidence after changes.
- Stop when blocked and write blockers to `BLOCKERS.md`.
- Accumulate non-blocking questions in `HUMAN_QUESTIONS.md`.

## Project Autopilot v2 Rules

- Project Autopilot is the control plane.
- Codex is the primary builder for now.
- Claude Code is available only as a manual/future CLI provider depending on provider status.
- Claude Agent SDK requires `ANTHROPIC_API_KEY` and is not enabled automatically.
- Design Director review is required for UI/design changes.
- Research Director review is required for uncertain vendor, security, privacy, paid API, legal, architecture, or deployment decisions.
- Scheduler remains disabled.
- Automatic Claude execution remains disabled.
- Deploy automation remains disabled.
- Paid APIs are disabled by default.
- Worktrees are required for parallel writes.
- No live database, RLS, storage, or Supabase changes may happen without explicit human approval.
