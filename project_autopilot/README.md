# Project Autopilot

Reusable autonomous builder orchestrator. Not specific to MIRA. Loads project-specific context, commands, budgets, models, and guardrails from configuration and `project_control/`.

MIRA is the first configured project.

## Operating Model

- **ChatGPT / OpenAI** acts as the quality director, product lead, architecture reviewer, backend reviewer, data policy reviewer, and QA lead. It enforces world-class standards.
- **Claude Code** is the heavy implementation agent (builder). It writes code, runs commands, and provides evidence.
- **Project Autopilot** orchestrates: reads state, collects evidence, calls OpenAI for planning/QA, generates builder prompts, handles failures gracefully.

The generated builder prompt includes quality expectations from `WORLD_CLASS_STANDARD.md`, `QA_PROTOCOL.md`, `CUSTOMER_DATA_POLICY.md`, and `RESEARCH_PROTOCOL.md`.

## Quality Standard

Project Autopilot enforces a world-class quality bar:
- Every button must work. Every flow must complete.
- Backend must be reliable and auditable. No silent failures.
- Customer data must be mapped, stored correctly, and protected per `CUSTOMER_DATA_POLICY.md`.
- QA checks from `QA_PROTOCOL.md` must be performed before marking any task complete.
- Build success alone is not sufficient — actual testing of buttons, forms, routes, and states is required.
- When research is needed (unknown provider, legal question, architecture decision), it must be proposed per `RESEARCH_PROTOCOL.md`, not silently skipped.

## Research Escalation

If a task involves an unknown provider, pricing uncertainty, legal/privacy question, or architecture decision with long-term consequences, Project Autopilot flags it as `RESEARCH_REQUIRED` with a proposed scope and time estimate. Research modes: `quick_check` (10-15 min), `standard_research` (30-45 min), `deep_research` (90+ min). Research is proposed, not silently executed.

## Customer Data Policy

Every project must map what customer data it collects, where it is stored, how sensitive it is, and what must never be exposed. See `project_control/CUSTOMER_DATA_POLICY.md`. Builder prompts include data policy reminders when the task involves user data.

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

### Browser QA (visual and functional evidence)

```bash
python -B project_autopilot/agent_loop.py --project mira --browser-qa
```

Walks all configured `route_walk_urls`, checks HTTP status, detects console errors and page errors, and takes screenshots (when Playwright is available). Requires the dev server to be running.

**Screenshots** are saved to `screenshots/<project_id>/` (e.g., `screenshots/mira/`).

**Report** is written to `logs/<project_id>_browser_qa_latest.md`.

**Pass/fail criteria:**
- Every route must return HTTP 200-399.
- Zero console errors.
- Zero page errors.
- Screenshots are captured for visual review.

**Playwright is optional.** Without it, browser QA falls back to HTTP-only checks (no screenshots, no console error detection). To install Playwright:

```bash
pip install playwright
python -m playwright install chromium
```

**Dev server must be running.** If the server is not reachable, browser QA prints a clear message and exits.

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
- Do not mark tasks complete without performing QA checks from `QA_PROTOCOL.md`.
- Do not skip customer data policy review when a task touches user data.
- Do not silently execute research. Propose it with scope and time estimate first.

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
