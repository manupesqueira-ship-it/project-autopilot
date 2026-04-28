# Project Autopilot

Project Autopilot is a reusable autonomous builder orchestrator. It is not specific to MIRA. It loads project-specific context, commands, budgets, models, and guardrails from configuration and `project_control/`.

MIRA is the first configured project.

## Run MIRA In Dry-Run Mode

```bash
python -B project_autopilot/agent_loop.py --project mira --dry-run
```

Dry-run mode reads the project config and project control pack, collects safe git evidence, skips OpenAI calls, skips validation commands, and writes a builder prompt under `logs/`.

## Run One Guarded Cycle

```bash
python -B project_autopilot/agent_loop.py --project mira --cycle
```

This is still bounded: it runs one cycle only. It does not execute builder work. It calls OpenAI for planning, QA review, and correction prompt generation when credentials and budgets allow.

## Telegram Test

```bash
python -B project_autopilot/telegram_alerts.py --project mira --test
```

Telegram is only for blockers, repeated failures, high-risk actions, secrets, deploys, destructive database changes, paid API usage, or strategic decisions. Project Autopilot should avoid noisy alerts for safe local work.

Credentials are read from the environment:

- `MIRA_TELEGRAM_BOT_TOKEN` or `TELEGRAM_BOT_TOKEN`
- `MIRA_TELEGRAM_CHAT_ID` or `TELEGRAM_CHAT_ID`

Do not commit credentials.

## Project Configuration

Project configs live in:

```text
project_autopilot/config/projects/
```

MIRA is configured at:

```text
project_autopilot/config/projects/mira.yaml
```

Config controls:

- Project name and repo path
- Framework and package manager
- Build/typecheck/lint/test/dev commands
- Route walk URLs
- Autonomy and retry limits
- Parallelism limits
- Daily, cycle, and monthly budget limits
- Paid API mode
- Telegram behavior
- Builder routing
- Model routing

## Model Routing

Routing is configurable per project:

- Cheap model: summaries, log parsing, simple classification.
- Standard model: planning and builder prompt generation.
- Premium model: architecture, QA-critical decisions, visual review, or repeated failures.
- QA model: quality review.

Default intensity should be `low_cost` or `normal`, not `high_intensity`.

## Cost Control

`cost_controller.py` tracks estimated model usage, paid API calls, cycle budget, daily budget, monthly budget, and whether paid API mode is enabled.

Paid image/video generation is disabled unless explicitly enabled in project config and approved in the project control pack.

## Project Control Packs

Each project supplies its own context pack. For MIRA, it is:

```text
project_control/
```

Reusable templates live under:

```text
project_autopilot/templates/
```

## Backward Compatibility

The old `agent/` entrypoints remain as wrappers that point to Project Autopilot.

