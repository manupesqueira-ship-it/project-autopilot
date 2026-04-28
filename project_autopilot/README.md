# Project Autopilot

Reusable autonomous builder orchestrator. Not specific to MIRA. Loads project-specific context, commands, budgets, models, and guardrails from configuration and `project_control/`.

MIRA is the first configured project.

## Operating Model

- **Claude Code** is the heavy implementation agent (builder).
- **Codex / ChatGPT** are supervisor, QA, prompt generation, review, and cost control.
- **Project Autopilot** orchestrates: reads state, collects evidence, calls OpenAI for planning/QA, generates builder prompts, handles failures gracefully.

The generated builder prompt is optimized for pasting directly into Claude Code.

## Quick Reference

### Doctor (validate environment)

```bash
python -B project_autopilot/agent_loop.py --project mira --doctor
```

Checks .env files, credentials, project config, control files, package.json scripts, git status. Does not call OpenAI. Does not send Telegram.

### Dry Run (safe preview)

```bash
python -B project_autopilot/agent_loop.py --project mira --dry-run
```

Reads config and control pack, collects git evidence, skips OpenAI calls, skips validation commands, writes a builder prompt under `logs/`.

### Local Plan (offline fallback)

```bash
python -B project_autopilot/agent_loop.py --project mira --local-plan
```

Generates a builder prompt from local state only. No OpenAI call. Runs build/typecheck/lint to collect real evidence. Always free. Use this when OpenAI is unavailable, over quota, or when you want zero API cost.

### Cycle (one bounded planning cycle)

```bash
python -B project_autopilot/agent_loop.py --project mira --cycle
```

Collects evidence, calls OpenAI for planning + QA + correction prompt. If OpenAI fails (429, quota, missing key, budget), automatically falls back to local plan, writes failure log, sends Telegram alert, and exits cleanly.

### Status

```bash
python -B project_autopilot/agent_loop.py --project mira --status
```

Prints project config, budget state, cycle count, last log, git status. No API calls.

### Telegram Test

```bash
python -B project_autopilot/telegram_alerts.py --project mira --test
```

Sends a test alert. Credentials are read from the environment:

- `MIRA_TELEGRAM_BOT_TOKEN` or `TELEGRAM_BOT_TOKEN`
- `MIRA_TELEGRAM_CHAT_ID` or `TELEGRAM_CHAT_ID`

### Handoff to Claude Code

```bash
python -B project_autopilot/agent_loop.py --project mira --handoff-claude
```

Generates a builder prompt (or reuses the latest one), then prints the path and instructions for pasting into Claude Code. This is the recommended workflow.

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-manual
```

Prints the latest prompt path only. Does not generate a new prompt.

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-execute
```

Attempts to invoke the Claude CLI automatically. **Blocked by default.** Requires `allow_automatic_builder_execution: true` in the project YAML. This exists as a future path, not a current recommendation.

## How to Use with Claude Code

1. Run `--doctor` to validate your environment.
2. Run `--local-plan` or `--cycle` to generate a builder prompt.
3. Run `--handoff-claude` to get the prompt path and instructions.
4. Paste the prompt into Claude Code.
5. Claude Code executes the task, provides evidence.
6. Review the output. Run the next cycle when ready.

### Why Automatic Execution Is Disabled by Default

Project Autopilot generates builder prompts but does not execute them automatically. This keeps humans in control of what Claude Code does. Automatic execution can be enabled per-project by setting `allow_automatic_builder_execution: true` in the project YAML, but this is not recommended until the manual workflow is proven reliable and guardrails are mature.

## How to Create a New Project

1. Create a YAML config at `project_autopilot/config/projects/<project_id>.yaml`.
   Use `mira.yaml` as a reference.
2. Create a `project_control/` directory in your repo root with the control files.
   Use the templates in `project_autopilot/templates/` as starting points.
3. Run `--doctor` against the new project to validate setup:
   ```bash
   python -B project_autopilot/agent_loop.py --project <project_id> --doctor
   ```
4. Run `--dry-run` or `--local-plan` to verify prompt generation.

## What Not to Do

- Do not run `--cycle` without checking `--doctor` first.
- Do not enable `paid_api_mode: enabled` without reviewing budgets.
- Do not commit `.env` or `.env.local`.
- Do not set `intensity_mode: high_intensity` unless you have budget headroom.
- Do not skip reading `project_control/` files before resuming product work.
- Do not let builders execute without reviewing the generated prompt first.
- Do not deploy from Project Autopilot. Deployment requires explicit human action.

## Cost Control

`cost_controller.py` tracks estimated model usage, paid API calls, and budget limits. Local planning (`--local-plan`, `--dry-run`) is always free and never blocked by budget.

## Project Control Packs

Each project supplies its own context pack (e.g., `project_control/`). Reusable templates live under `project_autopilot/templates/`.

## Environment Variables

Project Autopilot loads `.env` and `.env.local` from the repo root. Required variables depend on the mode:

| Variable | Required for |
|---|---|
| `OPENAI_API_KEY` | `--cycle` (optional — falls back to local plan) |
| `TELEGRAM_BOT_TOKEN` | Telegram alerts (optional) |
| `TELEGRAM_CHAT_ID` | Telegram alerts (optional) |

## Backward Compatibility

The old `agent/` entrypoints remain as wrappers that point to Project Autopilot.
