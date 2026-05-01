# Project Autopilot

Reusable autonomous builder orchestrator. Not specific to MIRA. Loads project-specific context, commands, budgets, models, and guardrails from configuration and `project_control/`.

MIRA is the first configured project.

## Operating Model

- **ChatGPT / OpenAI** acts as the quality director, product lead, architecture reviewer, backend reviewer, data policy reviewer, and QA lead. It enforces world-class standards.
- **Claude Code** is the heavy implementation agent (builder). It writes code, runs commands, and provides evidence.
- **Project Autopilot** orchestrates: reads state, collects evidence, calls OpenAI for planning/QA, generates builder prompts, handles failures gracefully.

The generated builder prompt includes quality expectations from `WORLD_CLASS_STANDARD.md`, `QA_PROTOCOL.md`, `CUSTOMER_DATA_POLICY.md`, and `RESEARCH_PROTOCOL.md`.

## v2 Control Plane Foundation

Project Autopilot v2 formalizes Autopilot as a control plane:

- Codex is the current primary builder.
- Claude Code is a future/manual/CLI provider.
- Claude Agent SDK is a future formal provider requiring `ANTHROPIC_API_KEY`.
- Design Director is required for UI/design changes.
- Research Director is required for uncertain provider, security, privacy, paid API, legal, architecture, deployment, or RLS decisions.
- Builder Orchestrator recommends provider routing, QA gates, stop conditions, allowed files, and auto-commit policy.
- Scheduler, automatic Claude execution, deploy automation, and paid APIs remain disabled by default.
- Worktrees are required for parallel writes.

### v2 Commands

```bash
python -B project_autopilot/provider_registry.py --project mira
python -B project_autopilot/design_director.py --project mira
python -B project_autopilot/research_director.py --project mira --status
python -B project_autopilot/builder_orchestrator.py --project mira --status
python -B project_autopilot/builder_orchestrator.py --project mira --plan "Improve MIRA result page design"
python -B project_autopilot/autopilot_v2_check.py --project mira
python -B project_autopilot/agent_loop.py --project mira --policy-check
python -B project_autopilot/policy_test_fixtures.py --project mira --run all
python -B project_autopilot/agent_loop.py --project mira --policy-fixtures
python -B project_autopilot/agent_loop.py --project mira --autopilot-health
python -B project_autopilot/agent_loop.py --project mira --claude-sdk-dry-run
```

These commands do not execute builders, call Anthropic/OpenAI, call paid APIs, deploy, or mutate live databases.

### v2 Post-Builder Policy

```bash
python -B project_autopilot/agent_loop.py --project mira --post-builder logs/<builder_report>.md
```

`--post-builder` now produces one unified policy verdict:

| Verdict | Meaning |
|---|---|
| `SAFE_TO_COMMIT` | All applicable hard gates passed. Commit may proceed if generated logs/screenshots are not staged. |
| `NEEDS_FIX` | Fixable gate failure. Use the correction prompt and rerun validation. |
| `BLOCKED` | Hard safety gate. Do not bypass; record blocker or request human decision. |
| `HUMAN_REVIEW_REQUIRED` | Human visual/research/security/strategic review is required. |
| `SAFE_NO_CHANGES` | No working-tree changes were detected. |

Policy gates include provider status, risk, scope, forbidden files, secrets/env, validation, design, research, backend, Flow QA/mock E2E, evidence, Definition of Done, and human approval gates.

### v2 Policy Fixture Tests

Policy fixtures are deterministic regression tests for the post-builder gate matrix. They use simulated changed files and in-memory builder reports, so they do not create real `.env` files, touch product code, call external APIs, execute SQL, mutate Supabase, enable scheduler, or execute builders.

```bash
python -B project_autopilot/policy_test_fixtures.py --project mira --list
python -B project_autopilot/policy_test_fixtures.py --project mira --run docs_only_safe
python -B project_autopilot/policy_test_fixtures.py --project mira --run all
```

The suite covers safe docs, UI/design gates, backend/Flow QA gates, Supabase/security human review, forbidden env files, secret-like report text, paid APIs, scheduler activation, automatic Claude execution, generated logs, research-required decisions, forced design failure, and validation failure. Results are written to ignored files under `logs/policy_tests/<project_id>/latest/`.

This suite must pass before enabling Claude Agent SDK execution, scheduler runs, or automatic builder execution. Add new fixtures by extending `fixtures()` in `project_autopilot/policy_test_fixtures.py`; keep assertions focused on policy outcomes instead of duplicating policy logic.

### Operational Health

Use one consolidated operator command before new autonomy work:

```bash
python -B project_autopilot/agent_loop.py --project mira --autopilot-health
```

It summarizes provider registry, Design Director, Research Director, Builder Orchestrator, Autopilot v2 check, post-builder policy availability, policy fixture health, Flow QA/mock E2E, backend audit, MIRA readiness, Control Center, HALT/run lock, scheduler status, automatic Claude execution status, Claude Agent SDK readiness, blockers, next actions, and evidence paths. It writes ignored reports to:

```text
logs/mira_autopilot_health_latest.md
logs/mira_autopilot_health_latest.json
```

Recommended operator flow:

```text
--doctor -> --autopilot-health -> --policy-fixtures -> --local-plan or --post-builder -> --control-center
```

`--doctor` also surfaces latest policy fixture health. A missing fixture report is a warning; a failing fixture report is a failure.

Pre-Claude readiness requires local `ANTHROPIC_API_KEY` presence, provider dry-run mode, sandbox/worktree policy, allowlist/denylist, cost/budget gates, passing policy fixtures, and explicit human approval for the first live Claude SDK call. Scheduler and automatic Claude execution remain disabled.

### Claude Agent SDK Dry-Run

Claude Agent SDK integration is currently dry-run only:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-sdk-dry-run
python -B project_autopilot/claude_sdk_dry_run.py --project mira --status
python -B project_autopilot/claude_sdk_dry_run.py --project mira --plan "Review MIRA result page design"
```

The dry-run validator:

- Detects `ANTHROPIC_API_KEY` as `PRESENT_VALUE_HIDDEN`, `MISSING`, or `EMPTY`.
- Never prints the value.
- Does not call Anthropic, Claude Code, OpenAI, Supabase, or paid APIs.
- Confirms automatic Claude execution and scheduler remain disabled.
- Confirms future live calls require explicit human approval.
- Confirms provider routing can choose Claude Agent SDK in `dry_run_only` mode.

Reports are written to ignored files:

```text
logs/<project_id>_claude_sdk_dry_run_latest.md
logs/<project_id>_claude_sdk_dry_run_latest.json
```

The next phase is a single controlled analysis call, only after explicit human approval. Sandboxed builder execution and limited automatic execution are later phases.

### Controlled Claude Analysis Call

The first live Claude SDK path is analysis-only and requires an explicit approval flag:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-analysis-dry-run
python -B project_autopilot/agent_loop.py --project mira --claude-analysis-approved --task "Review Project Autopilot v2 architecture and identify top 5 risks"
```

`--claude-analysis-dry-run` never calls Anthropic. It builds the same sanitized prompt, applies redaction, checks budget guardrails, and writes evidence.

`--claude-analysis-approved` may make exactly one Anthropic call. It is forbidden to use tools, edit files, execute commands, deploy, mutate databases, request secrets, or enable automatic execution. The prompt is sanitized by `claude_prompt_safety.py`; secret-like strings are redacted before sending.

Evidence is written to ignored files:

```text
logs/claude/<project_id>/latest/claude_analysis_request_redacted.md
logs/claude/<project_id>/latest/claude_analysis_response.md
logs/claude/<project_id>/latest/claude_analysis_metadata.json
```

This is not builder execution. The next phase remains sandboxed builder execution in a dedicated worktree, only after separate human approval.

Claude analysis model configuration lives in the project YAML:

```yaml
claude_analysis_model: claude-haiku-4-5-20251001
```

Use `claude-haiku-4-5-20251001` for low-cost analysis. Use `claude-sonnet-4-6` only when stronger analysis is explicitly needed and available to the account. Do not use deprecated or retired 3.5/3.7 model aliases such as `claude-3-5-haiku-latest`.

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

### History

```bash
python -B project_autopilot/agent_loop.py --project mira --history
```

Prints the latest run id, duration, command count, QA verdict, latest blocker, and the last 10 recorded events. This is the quickest answer to "what happened?"

### Metrics

```bash
python -B project_autopilot/agent_loop.py --project mira --metrics
```

Prints latest-run activity metrics: active command duration, total run duration, commands executed, command failures, files created/modified/deleted, line delta, risk level, QA verdict, evidence bundle path, task state, open blocker count, research request count, and estimated model cost when available.

### Research Status

```bash
python -B project_autopilot/agent_loop.py --project mira --research-status
```

Prints the research index summary. It is safe when no research exists yet.

```bash
python -B project_autopilot/agent_loop.py --project mira --request-research "Evaluate browser QA flow scripts" --research-mode quick_check
```

Records a research request without performing research. Modes are `quick_check` (10-15 min), `standard_research` (30-45 min), and `deep_research` (90+ min). Deep research always requires explicit human approval and may send a Telegram alert when enabled.

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

### Browser QA (route, network, and visual evidence)

```bash
python -B project_autopilot/agent_loop.py --project mira --browser-qa
```

Walks all configured `route_walk_urls`, checks HTTP status, captures network events, and records route evidence across multiple viewports. Requires the dev server to be running.

**Why Playwright is optional but recommended:** Browser QA works without Playwright using HTTP-only fallback, but Playwright mode provides significantly richer evidence: screenshots, console error capture, page error capture, network request/response interception, and responsive viewport testing. HTTP-only mode can only check whether routes return valid HTTP status codes.

Browser QA has two modes:

| Mode | Behavior |
|---|---|
| `playwright` | Captures evidence at each configured viewport; records console errors, page errors, failed 4xx/5xx responses, failed resource loads (with URL, method, status, resource type), route duration, and screenshots. |
| `http_only` | Checks configured route URLs with HTTP GET only. No screenshots, console/page errors, or subresource network interception. Verdict is WARN, not PASS. |

Install Playwright with:

```bash
pip install playwright
python -m playwright install chromium
```

#### Viewports

Viewports are configurable in the project YAML:

```yaml
browser_qa_viewports:
  mobile: 375x812
  tablet: 768x1024
  desktop: 1280x800
```

If `browser_qa_viewports` is not configured, the defaults are used (mobile 375x812, tablet 768x1024, desktop 1280x800). Each route is visited once per viewport in Playwright mode. In HTTP-only mode, viewports are not used.

#### Network interception

In Playwright mode, Browser QA intercepts all network activity per route/viewport:

- **Failed responses:** Any HTTP 4xx/5xx response from the page or its subresources (API calls, fetch/XHR, scripts, stylesheets, images).
- **Failed requests:** Any request that fails entirely (DNS failure, connection refused, timeout).
- **Captured fields:** URL, HTTP method, status code, resource type, route being tested, viewport name.
- **Not captured:** Auth headers, cookies, bearer tokens, JWTs, request bodies. Only safe metadata is logged.

#### Verdicts

| Verdict | Meaning |
|---|---|
| `PASS` | All routes returned 2xx/3xx, zero console errors, zero page errors, zero failed network requests, in Playwright mode. |
| `WARN` | All routes returned 2xx/3xx in HTTP-only mode. HTTP-only fallback cannot validate client-side behavior. |
| `FAIL` | One or more routes failed: non-2xx/3xx status, console errors, page errors, or failed network requests. |
| `SKIPPED_DEV_SERVER_DOWN` | Dev server not reachable. Prints the exact start command. |

**Screenshots** are saved to:

```text
screenshots/<project_id>/<run_id>/<viewport>/<safe_route_name>.png
```

**Reports** are written to:

```text
logs/<project_id>_browser_qa_latest.md
logs/<project_id>_browser_qa_<timestamp>.md
```

**Dev server must be running.** If the server is not reachable, Browser QA exits cleanly with `SKIPPED_DEV_SERVER_DOWN` and prints the exact start command (e.g. `npm run dev`).

#### What Browser QA still cannot prove

Browser QA is evidence, not a complete test suite. It does **not**:

- Fill forms, click buttons, or test multi-step flows.
- Validate database writes or business logic correctness.
- Perform visual regression testing (screenshot comparison).
- Run accessibility audits.
- Prove that interactive features work end-to-end.

Use Browser QA alongside manual QA, post-builder intake, and project-specific E2E checks.

### Browser QA Diagnostics

```bash
python -B project_autopilot/agent_loop.py --project mira --browser-qa-diagnose
```

Diagnoses dev-server reachability without Playwright, screenshots, form submits, or product data changes. It tries the configured route URLs, localhost/127.0.0.1 equivalents, and common Next.js dev ports `3000-3003`. The report is written to:

```text
logs/<project_id>_browser_qa_diagnostics_latest.md
```

Browser QA uses the detected runtime base URL for the current run only. It does not rewrite project config.

### Manual E2E Plan

```bash
python -B project_autopilot/agent_loop.py --project mira --e2e-plan
```

Prints the path to the project-specific E2E validation plan and summarizes the exact next manual steps. For MIRA, the plan lives at:

```text
project_control/MIRA_E2E_VALIDATION_PLAN.md
```

`--e2e-plan` is intentionally read-only:

- Does not run browser automation.
- Does not call Supabase.
- Does not modify data.
- Does not require Playwright.
- Does not fail if the app is not running.

Use it before validating the real product flow:

```text
onboarding -> scan -> catalog/product -> tryon -> result polling
```

The E2E plan covers Supabase observations for `users_profile`, `user_assets`, `generations`, and the `user-photos` storage bucket.

### Product Validation Report

```bash
python -B project_autopilot/agent_loop.py --project mira --new-validation-report
```

Creates a blank validation report draft under `logs/`:

```text
logs/<project_id>_validation_report_<timestamp>.md
logs/<project_id>_validation_report_latest.md
```

The report template lives at:

```text
project_autopilot/templates/PRODUCT_VALIDATION_REPORT.template.md
```

Validation reports are ignored by git because they may reference local evidence paths. They must not include secrets, JWTs, cookies, API keys, or real customer photos.

### Backend Audit

```bash
python -B project_autopilot/agent_loop.py --project mira --backend-audit
```

Runs a static backend/data-flow audit without calling Supabase, OpenAI, paid APIs, or the dev server. It does not read `.env` or `.env.local` contents.

The audit detects:

- Supabase tables referenced in code.
- Storage buckets referenced in code.
- localStorage keys.
- API routes used by the frontend.
- Whether onboarding, scan upload, try-on generation, and result polling appear wired to persistence.
- Whether schema references, storage bucket documentation, and RLS comments appear aligned.
- Whether anything still looks mock, in-memory, or manual-verification-only.

Reports are written to:

```text
logs/<project_id>_backend_audit_latest.md
logs/<project_id>_backend_audit_<timestamp>.md
logs/<project_id>_backend_audit_latest.json
```

Readiness values:

| Verdict | Meaning |
|---|---|
| `READY_FOR_MANUAL_E2E` | Static code/schema signals are aligned enough to proceed with manual Supabase E2E. |
| `PARTIAL_READY` | The app has real persistence signals, but mock/in-memory behavior or manual checks remain. |
| `BLOCKED` | Static audit found an obvious schema/code mismatch. |
| `UNKNOWN` | Insufficient files were available for a confident audit. |

For MIRA, the backend audit should be read alongside:

```text
project_control/MIRA_DATA_MAP.md
project_control/MIRA_E2E_VALIDATION_PLAN.md
project_control/CUSTOMER_DATA_POLICY.md
```

`MIRA_DATA_MAP.md` is product-specific. It maps fields, localStorage keys, Supabase tables, storage buckets, sensitivity, logging restrictions, and open data questions. Backend audit is evidence for readiness; it is not proof that the live Supabase project contains the expected rows, bucket privacy, or policies.

### Control Center (v0.3 — Operational Graph + Node Details)

```bash
python -B project_autopilot/agent_loop.py --project mira --control-center
```

Generates a self-contained HTML dashboard at:

```text
logs/control_center/<project_id>_control_center.html
```

Open in any browser. The dashboard is a lightweight command center designed to answer five questions at a glance: what is happening now, what happens next, what is blocked, where to inspect evidence, and where human input is needed.

Key sections:

1. **Hero summary** — project name, status badge, 7 metric tiles (stage, task state, QA verdict, browser QA, blockers, questions, autonomy).
2. **"What happens next?" panel** — inferred next action, recommended CLI command (copyable), evidence file to inspect, whether human input is required.
3. **Autopilot Flow Map (operational graph)** — branching decision map replacing the old linear pipeline. Shows 7 lanes (Intake, Research, Planning, Builder, Implementation, Validation, QA Verdict, Scheduler) with branch nodes for each outcome path. QA Verdict lane shows all 5 branches: PASS, FAIL_FIX_REQUIRED, HUMAN_DECISION, RESEARCH_REQUIRED, BLOCKED. Nodes are colored by status (completed/active/amber/failed/disabled/pending). Clickable nodes expand detail panels showing inputs, outputs, next paths, evidence links, and commands. Includes a color legend.
4. **Human Action Panel** — open blocker count, open question count, latest titles, file paths to edit, suggested answer format. Shows green "no input required" when clear.
5. **Current task** — title, state, risk, acceptance criteria, prompt paths.
6. **Evidence Navigator** — table of 10 evidence artifacts (evidence bundle, browser QA report, backend audit, builder prompt, correction prompt, post-builder report, run history, research index, task state, autopilot state) with exists/missing dot, file path, and related stage.
7. **Capability map** — 9 capability areas as status cards.
8. **Latest run** — run ID, outcome, duration, commands, file changes, QA verdict.
9. **Quality gates** — lint, typecheck, build, QA, browser QA, backend audit badges.
10. **Browser QA** — verdict, routes, issues, screenshots.
11. **Backend / customer data** — tables, buckets, manual verification items.
12. **Blockers & human questions** — tables with status badges.
13. **Research** — request count, latest request.
14. **Activity timeline** — recent events table.
15. **Budget / cost** — limits, current spend, controls.
16. **Safety gates** — HALT, auto-exec, run lock, Telegram, deploy, scheduler status.

**What it does:** Reads existing local logs, evidence bundles, config, project control files, run history, and state. Generates static HTML with inline CSS and minimal self-contained JS (node detail toggle only). No external dependencies.

**What it does not do:** No server. No authentication. No live updates. No external dependencies. No secrets included. No action buttons. No command execution from the dashboard. Recommended commands are shown as copyable text only.

**How it complements Telegram:** Telegram alerts are push-based (immediate errors/successes). The Control Center is pull-based (on-demand full status snapshot). Use Telegram for real-time awareness; use Control Center for comprehensive review.

The generated HTML is ignored by git (`logs/control_center/`).

### Product Validation Readiness

`--doctor` prints `PRODUCT_VALIDATION_READINESS` after the normal environment and scheduler checks. It verifies:

- The project-specific E2E validation plan exists.
- Browser QA is available, including HTTP-only mode when Playwright is missing.
- `NEXT_PUBLIC_SUPABASE_URL` is present, without printing the value.
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` is present, without printing the value.
- `route_walk_urls` are configured.
- Customer data policy, QA protocol, and world-class standard docs exist.

Result values:

| Result | Meaning |
|---|---|
| `READY` | Required validation docs, routes, and Supabase public env vars are present. |
| `WARN` | Validation tooling exists, but something important needs attention, commonly local Supabase env vars. |
| `NOT_READY` | A required validation document or route/control file is missing. |

Passing `lint`, `typecheck`, and `build` is necessary but not sufficient. Product approval requires Browser QA evidence, manual E2E validation evidence, and post-builder QA review where relevant.

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

### Validation Layers

Project Autopilot separates validation into layers:

| Layer | Purpose |
|---|---|
| `lint/typecheck/build` | Confirms the codebase compiles and basic static checks pass. |
| Browser QA | Captures route, network, console, page-error, and screenshot evidence. |
| Backend audit | Statically checks code/schema/data-flow alignment before live Supabase validation. |
| Manual E2E validation | Proves real product behavior, backend persistence, and customer data handling. |
| Post-builder intake | Reviews builder reports, fresh evidence, risk, blockers, and correction prompts. |
| QA verdict | Decides whether the work is passable, needs fixes, requires research, requires a human decision, or is blocked. |

Build success alone must never be treated as product approval.

Recommended product validation sequence:

```text
doctor -> backend-audit -> browser-qa -> e2e-plan -> manual Supabase validation -> validation report -> post-builder -> commit only after PASS or accepted human decision
```

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
- `run_history.py`: records run, command, evidence, QA, blocker, research, and error events in `logs/run_history/<project_id>.jsonl`.
- `run_metrics.py`: summarizes recent run activity from run history, evidence bundles, command events, git metrics, blockers, research, and task state.
- `research_log.py`: records requested research in `logs/research/<project_id>_research_index.jsonl` without performing the research automatically.

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
| `logs/run_history/<project_id>.jsonl` | Append-only event stream for runs and commands. |
| `logs/research/<project_id>_research_index.jsonl` | Append-only index of proposed research requests. |
| `logs/evidence/<project_id>/<timestamp>/metadata.json` | Per-run evidence metadata and metrics. |

Tracked run events include:

- `run_started`
- `run_finished`
- `browser_qa_started`
- `browser_qa_finished`
- `browser_qa_failed`
- `command_started`
- `command_finished`
- `evidence_bundle_created`
- `builder_prompt_created`
- `qa_verdict_created`
- `correction_prompt_created`
- `blocker_recorded`
- `research_requested`
- `research_completed`
- `task_state_changed`
- `error`

Run summaries include total duration, active command duration, command count, failed command count, created/modified/deleted file counts, added/removed line counts, evidence bundle path, QA verdict, risk level, blockers opened, research requests, estimated model cost, and paid API call count.

Use:

```bash
python -B project_autopilot/agent_loop.py --project mira --history
python -B project_autopilot/agent_loop.py --project mira --metrics
python -B project_autopilot/agent_loop.py --project mira --research-status
```

These commands are intentionally boring and local. They help evaluate whether the agent is actually working by showing movement: commands ran, files changed, evidence was produced, QA gave a verdict, research was requested, or progress blocked somewhere specific.

Project Autopilot does **not** track secrets, `.env` contents, `.env.local` contents, raw credential values, browser cookies, or external billing truth. Model cost is a conservative local estimate for routing and budgeting only.

### What Is Not Enabled Yet

The following features exist in config or code but are **not active**:

- **Scheduler** — `retry_policy` is validated, `run_lock` works, systemd templates exist, but no scheduler runs autonomously. See "Scheduler Readiness" below.
- **Automatic Claude execution** — `allow_automatic_builder_execution` defaults to `false`. Needs execution isolation, retry rules, safe task eligibility, commit policy, and rollback behavior.
- **Auto-deploy** — No deploy commands are allowed in project config. Deployment is always manual.
- **Paid image/video generation** — `allow_paid_image_generation` and `allow_paid_video_generation` default to `false`.
- **Multi-agent parallel writes** — `max_parallel_agents` is validated but not consumed by a scheduler.
- **Dashboard** — No dashboard exists. Use `--status`, `--history`, `--metrics` for observability.

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
| `ANTHROPIC_API_KEY` | Claude Agent SDK future provider dry-run/live-readiness detection only |

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

- git clean
- config valid
- logs ignored
- run_lock available
- HALT_AUTOPILOT absent
- evidence bundle available
- risk classifier available
- Telegram configured
- budget limits valid
- max_cycles_per_day configured
- run_frequency_hours configured
- automatic builder execution disabled
- paid APIs disabled or budgeted
- deploy automation disabled
- retry policy configured
- no open critical blockers
- post-builder intake available

Result: `READY`, `NOT_READY`, or `WARN`. No actual scheduler is implemented yet.

Hard requirements (cause `NOT_READY`): run_lock available, HALT_AUTOPILOT absent, config valid, max_cycles_per_day configured, run_frequency_hours configured, budget limits valid.

### Retry / Backoff Policy

The project config supports a `retry_policy` block for future scheduler use:

```yaml
retry_policy:
  max_attempts: 3
  backoff_seconds: 60
  backoff_multiplier: 2
  stop_on_same_error_count: 3
```

- `max_attempts`: maximum retries per failed cycle (>= 1).
- `backoff_seconds`: initial delay between retries (>= 1).
- `backoff_multiplier`: exponential multiplier per retry (>= 1).
- `stop_on_same_error_count`: stop retrying if the same error recurs this many times (>= 1).

No scheduler consumes this config yet. It is validated by `--doctor` and included in the scheduler readiness check.

### Why Scheduler Is Not Enabled Yet

The scheduler should wait until manual cycles are boringly reliable. Before scheduler work, Project Autopilot needs:

- Repeated clean `--cycle` runs without human cleanup.
- All scheduler readiness checks passing (`READY`).
- HALT_AUTOPILOT tested and trusted.
- Run lock proven under real concurrent-attempt scenarios.
- Retry/backoff policy reviewed for production use.
- Telegram alerts confirmed working for error and success paths.

## Claude Analysis Review

After a controlled Claude analysis call, convert the saved response into a local policy decision:

```bash
python -B project_autopilot/claude_analysis_review.py --project mira --latest
python -B project_autopilot/agent_loop.py --project mira --claude-analysis-review
```

This review does not call Anthropic or any other external API. It reads `logs/claude/<project_id>/latest/`, extracts risks/recommendations, maps them to Project Autopilot gates, and writes:

```text
logs/claude/<project_id>/latest/claude_analysis_review.md
logs/claude/<project_id>/latest/claude_analysis_review.json
```

Review decisions:

- `PROCEED_TO_SANDBOX_DESIGN`: begin the sandbox design sprint only.
- `NEEDS_POLICY_FIXTURE`: add deterministic fixture coverage first.
- `NEEDS_RESEARCH`: create/approve research before implementation.
- `BLOCKED`: stop and resolve missing safety coverage.
- `HUMAN_REVIEW_REQUIRED`: record the decision before proceeding.

The review is still not builder execution. Claude cannot edit files, run commands, use tools, auto-merge, deploy, touch live databases, or enable scheduler/automatic execution.

## OpenAI Auditor and Multi-Step Loop

OpenAI Auditor is a dry-run planner/reviewer provider. It formalizes the role ChatGPT/Codex has been playing manually:

- plan the task
- improve the builder prompt
- diagnose blocked builder output
- generate correction strategy
- review evidence
- recommend the next step

OpenAI Auditor is not a default builder and cannot approve its own output. Project Autopilot policy remains the final judge.

Commands:

```bash
python -B project_autopilot/openai_auditor.py --project mira --status
python -B project_autopilot/openai_auditor.py --project mira --plan "Build a sandboxed Claude builder loop"
python -B project_autopilot/agent_loop.py --project mira --openai-auditor-status
python -B project_autopilot/agent_loop.py --project mira --openai-auditor-plan --task "Build a sandboxed Claude builder loop"
python -B project_autopilot/multistep_loop.py --project mira --dry-run-objective "Improve MIRA result page design"
python -B project_autopilot/agent_loop.py --project mira --multistep-dry-run --objective "Improve MIRA result page design"
```

All of these are dry-run/local only. They must not call OpenAI or Anthropic, execute Claude, enable scheduler, enable automatic Claude execution, deploy, mutate Supabase, or stage generated logs.

The future loop is:

```text
Human objective -> OpenAI Auditor plan -> builder selected -> Claude/Codex handoff -> builder blocked/done -> OpenAI Auditor review -> validation -> policy review -> SAFE_TO_COMMIT / NEEDS_FIX / BLOCKED
```

Generated reports:

```text
logs/openai_auditor/<project_id>/latest/openai_auditor_dry_run.md
logs/openai_auditor/<project_id>/latest/openai_auditor_dry_run.json
logs/multistep_loop/<project_id>/latest/multistep_loop_dry_run.md
logs/multistep_loop/<project_id>/latest/multistep_loop_dry_run.json
```

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
