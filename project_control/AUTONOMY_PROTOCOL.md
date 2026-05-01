# Autonomy Protocol

## Initial Mode

MIRA uses Project Autopilot in `autonomous_guarded` mode with low-cost model routing by default.

In guarded mode, Project Autopilot:

1. Reads project control files.
2. Collects evidence.
3. Requests OpenAI planning and QA where credentials and budgets allow.
4. Generates a builder prompt for Codex or Claude.
5. Stops before executing builder work.
6. Writes an iteration log.

## Future 3-Hour Loop

The intended future loop runs every `run_frequency_hours` from config, initially every 3 hours.

Each scheduled run should:

1. Load config and state.
2. Read `project_control/` files.
3. Collect evidence.
4. Ask OpenAI for next task planning when credentials and budgets allow.
5. Generate a builder prompt for safe local builder work.
6. Escalate only when human approval is truly required.
7. Collect post-builder evidence.
8. Ask OpenAI for QA review.
9. Generate correction prompts if needed.
10. Mark state as pass, fail, blocked, or needs approval.
11. Send Telegram alerts when configured.

## Retry Policy

- `max_retries_per_task` defaults to 3.
- A failed task may receive a correction prompt and be retried.
- After 3 failed attempts, the task becomes blocked.
- Retry exhaustion is written to `BLOCKERS.md` and sent through Telegram when enabled.

## Pass / Fail States

- `planned`: next builder prompt generated.
- `waiting_for_human`: approval or decision is required.
- `running`: builder or QA work is in progress.
- `passed`: quality gates passed.
- `failed`: quality gates failed but retries remain.
- `blocked`: a blocking decision, missing credential, repeated failure, or unresolved broken build prevents progress.

## Telegram Escalation Logic

Send Telegram alerts when `telegram_enabled` is true and credentials are available for:

- Blocking decisions.
- Failed task after 3 retries.
- Missing credentials.
- Build broken and unresolved.
- Approval required.

If Telegram credentials are missing, record the issue in `BLOCKERS.md` only when the current task requires Telegram delivery; otherwise record a non-blocking question.

## Project Autopilot v2 Control Plane

Project Autopilot coordinates work; it does not replace Codex, Claude Code, Lovable, Replit, or future builder tools.

- Codex is the primary builder for now.
- Claude Code is manual/future CLI handoff unless automatic execution is explicitly enabled later.
- Claude Agent SDK is a future provider and requires `ANTHROPIC_API_KEY`; it is not called automatically.
- Design Director is required for UI/design changes.
- Research Director is required when decisions involve uncertain providers, security, paid APIs, legal/privacy, cloud/VPS/deployment architecture, AI model/vendor choice, or RLS/security design.
- Scheduler remains disabled until manual cycles are reliable and explicitly approved.
- Automatic Claude execution remains disabled.
- Deploy automation remains disabled.
- Paid APIs remain disabled by default.
- Worktrees are required for parallel writes.
- Live DB/RLS/storage changes require explicit human approval and must never run as hidden side effects.

## v2 Post-Builder Policy

After builder work, Project Autopilot must run `--post-builder` or `--policy-check` to produce a unified verdict.

- `SAFE_TO_COMMIT`: commit may proceed if generated logs/screenshots are not staged.
- `NEEDS_FIX`: create or use a correction prompt, then rerun validation.
- `BLOCKED`: stop and record blocker or human decision need.
- `HUMAN_REVIEW_REQUIRED`: pause for human review, design review, research approval, or risk acceptance.
- `SAFE_NO_CHANGES`: no commit required.

Automatic commit remains allowed only for scoped, local, non-secret, non-deployment, non-paid, non-live-database work where all required gates pass.
