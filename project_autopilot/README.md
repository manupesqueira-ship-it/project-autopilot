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

Doctor now reports one `PASS`, `WARN`, or `FAIL` line per check and ends with:

```text
DOCTOR_RESULT: PASS
DOCTOR_RESULT: WARN
DOCTOR_RESULT: FAIL
```

`PASS` and `WARN` exit with code `0`; `FAIL` exits with code `2`.

Doctor includes config schema validation from `config_validator.py`, including autonomy mode, intensity mode, budgets, model routing, command safety, browser QA config, and Claude handoff config.

### Dry Run (safe preview)

```bash
python -B project_autopilot/agent_loop.py --project mira --dry-run
```

Reads config and control pack, collects git evidence, skips OpenAI calls, skips validation commands, writes a builder prompt under `logs/`.

Dry run also creates a structured evidence bundle under:

```text
logs/evidence/<project_id>/<timestamp>/
```

### Local Plan (offline fallback)

```bash
python -B project_autopilot/agent_loop.py --project mira --local-plan
```

Generates a builder prompt from local state only. No OpenAI call. Runs build/typecheck/lint to collect real evidence. Always free. Use this when OpenAI is unavailable, over quota, or when you want zero API cost.

Local plans include deterministic risk classification from `risk_classifier.py`.

### Cycle (one bounded planning cycle)

```bash
python -B project_autopilot/agent_loop.py --project mira --cycle
```

Collects evidence, calls OpenAI for planning + QA + correction prompt. If OpenAI fails (429, quota, missing key, budget), automatically falls back to local plan, writes failure log, sends Telegram alert, and exits cleanly.

### Status

```bash
python -B project_autopilot/agent_loop.py --project mira --status
```

Prints project config, budget state, cycle count, task state, run history, latest evidence bundle, latest QA verdict, git status, blocker count, and research request count. No API calls.

Status also prints a concise recent-run table and a risk summary for the active task queue.

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

### Post-Builder Intake

After Claude Code or Codex finishes implementation, save its report to a markdown file. A report should follow `project_autopilot/templates/BUILDER_REPORT.template.md` and include:

- task title
- files created
- files modified
- commands run
- validation results
- what was verified
- what was not verified
- blockers
- risks
- git status

Run:

```bash
python -B project_autopilot/agent_loop.py --project mira --post-builder path/to/report.md
```

Equivalent alias:

```bash
python -B project_autopilot/agent_loop.py --project mira --intake-builder-report path/to/report.md
```

Post-builder intake:

1. Reads the builder report.
2. Collects fresh evidence.
3. Creates an evidence bundle.
4. Runs deterministic risk classification.
5. Produces a structured QA verdict.
6. Writes `logs/<project_id>_post_builder_<timestamp>.md`.
7. Updates task state.
8. Generates a correction prompt when fixes are required.

QA verdicts:

| Verdict | Meaning |
|---|---|
| `PASS` | Evidence looks ready for human review and commit. |
| `FAIL_FIX_REQUIRED` | A validation command or QA gate failed; use the correction prompt. |
| `RESEARCH_REQUIRED` | More research is needed before continuing. |
| `HUMAN_DECISION_REQUIRED` | A human needs to decide before more work proceeds. |
| `BLOCKED` | Stop until the blocker is resolved. |

If the verdict is `FAIL_FIX_REQUIRED`, Project Autopilot writes:

```text
logs/<project_id>_correction_prompt_latest.md
```

Paste that prompt into Claude Code or Codex for the fix pass.

Project Autopilot does **not** auto-commit. Commit remains a human-controlled step.

## How to Use with Claude Code

1. Run `--doctor` to validate your environment.
2. Run `--local-plan` or `--cycle` to generate a builder prompt.
3. Run `--handoff-claude` to get the prompt path and instructions.
4. Paste the prompt into Claude Code.
5. Claude Code executes the task, provides evidence.
6. Save Claude's report to a markdown file.
7. Run `--post-builder path/to/report.md`.
8. Review the QA verdict and correction prompt if one is generated.
9. Commit only after validation and human review.

## Reliability Core

Project Autopilot includes a small Reliability Core before scheduler or automatic execution:

- `config_validator.py`: validates project YAML and rejects dangerous configured commands.
- `evidence_bundle.py`: writes one structured evidence bundle per run.
- `task_state.py`: tracks simple task states in `logs/<project_id>_task_state.json`.
- `risk_classifier.py`: deterministic local risk classification with no OpenAI call.
- `run_history.py`: records run, command, evidence, QA, blocker, research, and error events in `logs/run_history.jsonl`.
- `research_log.py`: records requested research in `logs/research_index.jsonl` without performing the research automatically.

Task states:

```text
planned -> assigned -> implemented -> validating -> passed -> committed
```

Alternative states:

```text
needs_fix
blocked
parked
```

Risk categories:

- `safe_local_change`
- `product_behavior_change`
- `data_schema_change`
- `paid_api_risk`
- `deploy_risk`
- `secrets_risk`
- `destructive_risk`
- `research_required`
- `human_decision_required`

Recommended workflow:

```text
local-plan -> handoff to Claude/Codex -> validate -> evidence bundle -> commit
```

## Activity and Run History

Project Autopilot keeps local observability files under `logs/`:

| File | Purpose |
|---|---|
| `logs/run_history.jsonl` | Append-only event stream for runs and commands. |
| `logs/research_index.jsonl` | Append-only index of proposed research requests. |
| `logs/evidence/<project_id>/<timestamp>/metadata.json` | Per-run evidence metadata and metrics. |

Tracked run events include:

- `run_started`
- `run_finished`
- `command_started`
- `command_finished`
- `evidence_bundle_created`
- `builder_prompt_created`
- `qa_verdict_created`
- `correction_prompt_created`
- `blocker_recorded`
- `research_requested`
- `state_transition`
- `error`

Run summaries include duration, command count, failed command count, created/modified/deleted file counts, added/removed line counts, evidence bundle path, QA verdict, risk level, estimated model cost, and paid API call count.

Project Autopilot does **not** track secrets, `.env` contents, `.env.local` contents, raw credential values, browser cookies, or external billing truth. Model cost is a conservative local estimate for routing and budgeting only.

### Why Automatic Execution Is Disabled by Default

Project Autopilot generates builder prompts but does not execute them automatically. This keeps humans in control of what Claude Code does. Automatic execution can be enabled per-project by setting `allow_automatic_builder_execution: true` in the project YAML, but this is not recommended until the manual workflow is proven reliable and guardrails are mature.

## Why Scheduler Is Not Enabled Yet

The scheduler should wait until manual cycles are boringly reliable. Before scheduler work, Project Autopilot needs repeated clean runs of doctor, local-plan, evidence bundle creation, browser QA, and post-builder validation without human cleanup.

## Why Automatic Claude Execution Is Not Enabled Yet

Automatic Claude execution needs stronger execution isolation, retry rules, safe task eligibility, commit policy, and rollback/abort behavior. Until then, Claude handoff stays manual.

## How to Create a New Project

### Automated (recommended)

```bash
python -B project_autopilot/init_project.py \
  --project-id demo \
  --project-name "Demo Project" \
  --repo-path "C:\Users\manup\projects\demo"
```

This creates:

- `project_control/` in the target repo with all control files from templates.
- `project_autopilot/config/projects/<project-id>.yaml` with safe defaults.
- `logs/` and `screenshots/<project-id>/` directories.

Existing files are **never overwritten** unless `--force` is passed.

**Defaults:**

| Setting | Value |
|---|---|
| `intensity_mode` | `low_cost` |
| `paid_api_mode` | `disabled_by_default` |
| `max_parallel_agents` | `1` |
| `max_cycles_per_day` | `4` |

After init, edit the generated YAML to set `framework`, `package_manager`, and commands for your project.

### Manual

1. Create a YAML config at `project_autopilot/config/projects/<project_id>.yaml`.
   Use `mira.yaml` as a reference.
2. Create a `project_control/` directory in your repo root with the control files.
   Use the templates in `project_autopilot/templates/` as starting points.

### Validate

Run `--doctor` against the new project to validate setup:

```bash
python -B project_autopilot/agent_loop.py --project <project_id> --doctor
```

Then run `--dry-run` or `--local-plan` to verify prompt generation.

## What Not to Do

- Do not run `--cycle` without checking `--doctor` first.
- Do not enable `paid_api_mode: enabled_with_budget` without reviewing budgets.
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

## VPS Readiness and Scheduler Foundation

Project Autopilot is **local-first today**. VPS deployment is planned but not active.

### Run Lock

`run_lock.py` prevents two `--cycle` runs from executing at the same time. Lock files live under `logs/locks/<project_id>.lock`. Stale locks (default: 4 hours) are automatically cleared. Only `--cycle` acquires a lock. Other modes (`--doctor`, `--status`, `--local-plan`, `--dry-run`) do not lock.

### HALT_AUTOPILOT

If `project_control/HALT_AUTOPILOT.md` exists:

- `--cycle` refuses to run and exits with code 2.
- `--local-plan` warns but still runs (read-only planning is safe).
- `--doctor` reports HALT active.
- `--status` reports HALT active.

To halt: create the file with a reason. To resume: delete it.

### Scheduler Readiness

`--doctor` now reports `SCHEDULER_READINESS` with a checklist:

- run_lock available
- HALT_AUTOPILOT supported
- max_cycles_per_day configured
- run_frequency_hours configured
- automatic builder execution disabled
- paid APIs disabled by default
- deploy automation disabled
- Telegram configured
- evidence bundle available
- post-builder intake available

Result: `READY`, `NOT_READY`, or `WARN`. No actual scheduler is implemented yet.

### Why Scheduler Is Not Enabled Yet

The scheduler should wait until manual cycles are boringly reliable. Before scheduler work, Project Autopilot needs repeated clean runs without human cleanup.

### Systemd Templates

Template files for future VPS deployment:

- `project_autopilot/templates/systemd/pa-cycle.service.template`
- `project_autopilot/templates/systemd/pa-cycle.timer.template`

These are **not installed or enabled**. They contain placeholders (`{{PROJECT_ID}}`, `{{WORKDIR}}`, `{{PYTHON_BIN}}`, `{{COMMAND}}`, `{{USER}}`) to be filled before deployment.

### VPS Coexistence Rules

- Existing project at `/root/bot/` must not be touched.
- Existing services use `bot-*` prefixes.
- Project Autopilot uses `pa-*` prefixes for service names.
- Separate install path, separate venv, separate user (later).
- See `project_control/VPS_DEPLOYMENT_PLAN.md` for full details.

## Backward Compatibility

The old `agent/` entrypoints remain as wrappers that point to Project Autopilot.
