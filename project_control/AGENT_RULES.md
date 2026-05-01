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
- `--post-builder` must produce a unified v2 policy verdict before work is considered committable.
- `SAFE_TO_COMMIT` is the only v2 post-builder verdict that permits commit without additional fixes or review.
- `NEEDS_FIX` requires a correction prompt and a new validation pass.
- `BLOCKED` must not be bypassed by a builder; request human decision or choose a safer alternative.
- `HUMAN_REVIEW_REQUIRED` requires an explicit human decision before commit.
- `python -B project_autopilot/policy_test_fixtures.py --project mira --run all` must pass before changing policy gates, enabling Claude SDK execution, enabling scheduler, or enabling automatic builder execution.
- Policy fixture results are generated logs and must not be staged.
- Operators should run `--doctor`, `--autopilot-health`, `--policy-fixtures`, then `--local-plan` or `--post-builder`, then `--control-center`.
- Claude Agent SDK readiness checks may report whether `ANTHROPIC_API_KEY` is present, but must never print the value or call Anthropic.
- Claude SDK integration requires dry-run mode, worktree/sandbox policy, allowlist/denylist, cost/budget gates, passing policy fixtures, and explicit human approval for the first live call.
- Claude SDK dry-run is allowed only through `python -B project_autopilot/agent_loop.py --project mira --claude-sdk-dry-run` or `project_autopilot/claude_sdk_dry_run.py`.
- Claude SDK dry-run may report `PRESENT_VALUE_HIDDEN`, `MISSING`, or `EMPTY`; it must never expose the key, install dependencies, import live SDK behavior that makes network calls, or execute a builder.
- A controlled live Claude analysis call is a future phase and requires explicit approval for that exact call. It must be analysis-only until sandboxed builder execution is separately approved.
- Controlled Claude analysis is allowed only with `--claude-analysis-approved`; dry-run uses `--claude-analysis-dry-run`.
- Controlled Claude analysis must sanitize prompts, send no secrets, use no tools, edit no files, execute no commands, and write evidence under ignored `logs/claude/`.
- Saved Claude analysis must be reviewed locally with `python -B project_autopilot/claude_analysis_review.py --project mira --latest` before sandboxed Claude builder design starts.
- Claude analysis review may recommend sandbox design, fixtures, research, blockers, or human review, but it must not call external APIs or grant builder execution permission.
- Claude builder execution remains blocked until a separate sandboxed worktree sprint explicitly enables it.
- OpenAI Auditor is a planner/reviewer provider, not a default builder.
- OpenAI Auditor dry-run may plan work, refine prompts, diagnose blockers, and review evidence, but it must not call OpenAI, edit files, execute builders, or approve its own output.
- Multi-step loop dry-runs may model planner -> builder -> reviewer -> policy flow, but must not execute providers.
- Project Autopilot policy remains the final judge for commits.
