# Autonomy Protocol

## Initial Mode

The first supported mode is `supervised`.

In supervised mode, the agent:

1. Reads project control files.
2. Collects evidence.
3. Requests OpenAI planning and QA where credentials are available.
4. Generates a builder prompt for Codex or Claude.
5. Stops before executing builder work.
6. Writes an iteration log.

## Future 3-Hour Loop

The intended future loop runs every `run_frequency_hours` from config, initially every 3 hours.

Each scheduled run should:

1. Load config and state.
2. Read `project_control/` files.
3. Collect evidence.
4. Ask OpenAI for next task planning.
5. Generate a builder prompt.
6. Wait for human approval or an approved automatic execution mode.
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
