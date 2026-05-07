# Cost Policy

MIRA uses Project Autopilot in a low-cost guarded mode by default.

## Budgets

- Per-cycle budget: configured in `project_autopilot/config/projects/mira.yaml`.
- Daily budget: configured in project config.
- Monthly budget: configured in project config.
- Max cycles per day: configured in project config.

## Model Usage

- Use cheap models for summaries, log parsing, simple classification, and status checks.
- Use standard models for planning and builder prompt generation.
- Use premium models only for architecture, QA-critical decisions, visual/design review, or repeated failures.
- Default intensity must be `low_cost` or `normal`, not `high_intensity`.

## Paid APIs

- Paid image generation is disabled unless explicitly approved.
- Paid video generation is disabled unless explicitly approved.
- Provider calls that spend money require human approval and Telegram escalation when enabled.
- Missing paid API credentials should not block safe local work unless the active task explicitly requires them.

## Escalation

Escalate through `BLOCKERS.md` and Telegram when enabled for:

- Budget exhaustion.
- Paid API usage request.
- Repeated task failure after configured retries.
- Strategic cost decisions.
- Any action that could create recurring spend.

