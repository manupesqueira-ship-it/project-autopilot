# Project Autopilot v1 — Completion Checklist

**Created:** 2026-04-30
**Status:** ACTIVE
**How to use:** Work through each section. Mark each item PASS or FAIL. All REQUIRED items must be PASS before declaring v1 complete. OPTIONAL items may be left incomplete. DEFERRED items must not be started. FORBIDDEN items must not be started.

Label legend:
- `REQUIRED` — must pass before v1 is declared complete
- `OPTIONAL` — desirable but not blocking
- `DEFERRED` — must not be done until explicitly authorized
- `FORBIDDEN` — permanently prohibited in v1 context

---

## Section 1 — Control Plane Readiness

- [ ] `REQUIRED` `--doctor` exits cleanly with no hard failures
- [ ] `REQUIRED` `--status` prints project config, budget, cycles, git state
- [ ] `REQUIRED` `--local-plan` generates a builder prompt without any API call
- [ ] `REQUIRED` `--autopilot-health` reports overall readiness without errors
- [ ] `REQUIRED` `--dry-run` reads config and writes builder prompt, skips OpenAI
- [ ] `REQUIRED` Run lock (`run_lock.py`) blocks concurrent cycles correctly
- [ ] `REQUIRED` HALT file mechanism stops execution when present
- [ ] `OPTIONAL` `--cycle` calls OpenAI when credentials are valid (non-blocking if API unavailable)
- [ ] `OPTIONAL` Telegram alerts confirmed working in test mode
- [ ] `DEFERRED` Scheduler cron activation
- [ ] `DEFERRED` Automatic cycle triggering without human initiation
- [ ] `FORBIDDEN` Scheduler enabled during v1 completion window

---

## Section 2 — OpenAI Auditor Readiness

- [ ] `REQUIRED` Provider registry includes `openai_auditor` entry
- [ ] `REQUIRED` `openai_auditor.py --status` runs without calling OpenAI
- [ ] `REQUIRED` `openai_auditor.py --plan` writes planning evidence under ignored `logs/`
- [ ] `REQUIRED` `multistep_loop.py --dry-run-objective` previews lifecycle states without execution
- [ ] `REQUIRED` Policy fixtures cover OpenAI Auditor live-call and self-approval risks
- [ ] `REQUIRED` Autopilot health confirms live OpenAI calls are disabled
- [ ] `OPTIONAL` Live OpenAI `--cycle` tested with valid credentials
- [ ] `DEFERRED` OpenAI Auditor live call as part of automated cycle
- [ ] `FORBIDDEN` OpenAI Auditor approving its own output
- [ ] `FORBIDDEN` OpenAI Auditor skipping policy gate, QA, or Definition of Done

---

## Section 3 — Claude Sandbox Readiness

- [ ] `REQUIRED` `--claude-sdk-dry-run` passes: no Anthropic call, scheduler disabled, automatic execution disabled
- [ ] `REQUIRED` `--claude-sandbox-preflight --task "<task>"` runs; no real worktree created
- [ ] `REQUIRED` `--claude-sandbox-simulate --task "<task>"` runs; no real worktree created
- [ ] `REQUIRED` `claude_sandbox_runner.py --status` runs cleanly
- [ ] `REQUIRED` `claude_sandbox_runner.py --approval-preflight --task "<task>"` runs cleanly
- [ ] `REQUIRED` `claude_sandbox_runner.py --dry-run --task "<task>"` runs cleanly
- [ ] `REQUIRED` `claude_sandbox_runner.py --rollback-plan --task "<task>"` runs cleanly
- [ ] `REQUIRED` No Anthropic or OpenAI API calls occur during any preflight or simulation command
- [ ] `REQUIRED` Policy fixtures cover direct master write, env access, SQL/RLS, deploy, auto-merge, missing rollback, missing post-builder policy
- [ ] `DEFERRED` Live Claude builder execution in a sandbox worktree
- [ ] `DEFERRED` Approval state `APPROVED_FOR_BUILDER_EXECUTION_FUTURE` becoming executable
- [ ] `FORBIDDEN` Any Claude builder execution without separate human-approved sprint
- [ ] `FORBIDDEN` Automatic Claude execution triggered by scheduler or policy pass

---

## Section 4 — Manual Claude Handoff Readiness

- [ ] `REQUIRED` `claude_manual_handoff.py --project mira --task "<task>" --dry-run` passes
- [ ] `REQUIRED` `--claude-manual-handoff-dry-run --task "<task>"` agent loop wrapper passes
- [ ] `REQUIRED` Handoff packet includes: sandbox path, branch, allowlists, denylists, no-secret/no-env/no-SQL/no-deploy/no-paid-API rules, stop conditions, builder report format, post-builder command, cleanup command
- [ ] `REQUIRED` Project Autopilot does not execute Claude, call Anthropic/OpenAI, edit sandbox files, commit in the sandbox, merge, or touch product code during handoff generation
- [ ] `REQUIRED` Policy fixtures cover manual handoff dry-run, approved worktree requirement, secret exclusion, env denial, SQL/deploy/paid API denial
- [ ] `OPTIONAL` One full create-approved handoff smoke test with a real (temporary) worktree — confirmed clean and documented
- [ ] `DEFERRED` Automated handoff packet delivery to Claude Code in CI
- [ ] `FORBIDDEN` Handoff that includes secrets, env values, or live DB credentials

---

## Section 5 — Policy Engine Readiness

- [ ] `REQUIRED` Policy fixture suite passes: 59/59 (run `python -B project_autopilot/policy_test_fixtures.py --project mira --run all`)
- [ ] `REQUIRED` `--policy-check` produces a valid verdict
- [ ] `REQUIRED` `--post-builder <report>` evaluates provider, risk, scope, forbidden files, secrets/env, validation, design, research, backend, Flow QA, evidence, Definition of Done, and human approval gates
- [ ] `REQUIRED` All five verdicts are reachable: SAFE_TO_COMMIT, NEEDS_FIX, BLOCKED, HUMAN_REVIEW_REQUIRED, SAFE_NO_CHANGES
- [ ] `REQUIRED` BLOCKED verdict fires on: secrets/env, SQL/RLS/live DB mutation, paid APIs, scheduler activation, automatic Claude execution, deployment, generated logs staged
- [ ] `REQUIRED` No `--skip-policy` flag exists or is reachable
- [ ] `OPTIONAL` Policy fixtures extended to cover new v1 scenarios discovered during final sprint
- [ ] `DEFERRED` Policy fixture suite coverage expanded for VPS runner scenarios
- [ ] `DEFERRED` Policy coverage for GitHub Actions automation scenarios
- [ ] `FORBIDDEN` Any code path that bypasses the policy gate

---

## Section 6 — QA Readiness

- [ ] `REQUIRED` `flow_qa.py --dry-run` passes without errors
- [ ] `REQUIRED` `flow_qa.py --validate-mock-e2e` passes (QA mock mode, no Supabase, no paid APIs)
- [ ] `REQUIRED` All 4+ flows defined in `mira_flows.yaml` are listable via `--list`
- [ ] `REQUIRED` `--diagnose` runs without errors
- [ ] `REQUIRED` `browser_qa.py` runs without import errors
- [ ] `REQUIRED` `qa_reviewer.py` runs without import errors
- [ ] `OPTIONAL` Full Playwright flow with managed dev server confirmed working locally
- [ ] `OPTIONAL` Visual QA screenshots generated and reviewed
- [ ] `DEFERRED` Full E2E with live Supabase and real credentials
- [ ] `DEFERRED` Real generation provider in QA flow
- [ ] `FORBIDDEN` QA flow calling paid APIs without explicit approval
- [ ] `FORBIDDEN` QA flow writing to live Supabase tables

---

## Section 7 — Control Center Readiness

- [ ] `REQUIRED` `--control-center` generates without errors
- [ ] `REQUIRED` Control Center reflects current scheduler status (DISABLED)
- [ ] `REQUIRED` Control Center reflects current automatic Claude execution status (DISABLED)
- [ ] `REQUIRED` Control Center reflects active blockers from BLOCKERS.md
- [ ] `REQUIRED` Control Center reflects policy fixture status
- [ ] `REQUIRED` Control Center reflects readiness report data
- [ ] `OPTIONAL` Control Center includes Flow QA integration summary
- [ ] `OPTIONAL` Control Center includes runtime env readiness
- [ ] `DEFERRED` Control Center served as a web dashboard
- [ ] `DEFERRED` Control Center connected to live VPS metrics

---

## Section 8 — Evidence and Logging Readiness

- [ ] `REQUIRED` Evidence bundle generates cleanly (`evidence_bundle.py` or equivalent via agent loop)
- [ ] `REQUIRED` Evidence records include: agent, task, cycle, timestamps, cost, verdict
- [ ] `REQUIRED` Evidence records do not include secrets or user PII
- [ ] `REQUIRED` Generated logs are gitignored (`logs/`, `screenshots/` not staged)
- [ ] `REQUIRED` `run_history.py` and `run_metrics.py` run without errors
- [ ] `REQUIRED` `sensitive_logging_audit.py --project mira` returns PASS
- [ ] `OPTIONAL` Evidence bundle includes validation command outputs
- [ ] `DEFERRED` Evidence uploaded to GitHub artifacts via CI
- [ ] `DEFERRED` Evidence visualized in a dashboard
- [ ] `FORBIDDEN` Evidence records that include raw secrets, API keys, or user PII

---

## Section 9 — Human Decision Queue Readiness

- [ ] `REQUIRED` `project_control/HUMAN_QUESTIONS.md` is current and accurately reflects open decisions
- [ ] `REQUIRED` `project_control/BLOCKERS.md` is current: all resolved blockers marked resolved, open blockers clearly stated
- [ ] `REQUIRED` No open Autopilot-specific blocker exists that would prevent v1 validation commands from running
- [ ] `REQUIRED` Autopilot correctly writes new blockers to BLOCKERS.md when policy hard gates fire
- [ ] `OPTIONAL` Human decision queue has been reviewed and non-blocking items are deferred cleanly
- [ ] `DEFERRED` Automated HUMAN_QUESTIONS.md updates from CI
- [ ] `FORBIDDEN` Autopilot resolving a human decision without human input

---

## Section 10 — Repo Hygiene Readiness

- [ ] `REQUIRED` `git status --short` returns clean working tree before and after final validation
- [ ] `REQUIRED` `git diff --check` returns no whitespace errors
- [ ] `REQUIRED` `python -B -m compileall project_autopilot agent` passes with zero errors
- [ ] `REQUIRED` `npm run lint` passes
- [ ] `REQUIRED` `npm run typecheck` passes
- [ ] `REQUIRED` No `.env*` files staged or committed
- [ ] `REQUIRED` No secrets, API keys, or credentials in any committed file
- [ ] `REQUIRED` `logs/` and `screenshots/` are gitignored and not staged
- [ ] `OPTIONAL` `npm run build` passes (not required for Autopilot v1 specifically)
- [ ] `DEFERRED` Automated pre-commit hooks for all the above
- [ ] `FORBIDDEN` Committing generated logs, screenshots, or evidence bundles

---

## Section 11 — Safety Readiness

- [ ] `REQUIRED` Scheduler is DISABLED — confirmed in health report and Control Center
- [ ] `REQUIRED` Automatic Claude execution is DISABLED — confirmed in health report and Control Center
- [ ] `REQUIRED` No auto-merge mechanism exists or is reachable
- [ ] `REQUIRED` No deployment trigger exists or is reachable
- [ ] `REQUIRED` No live Supabase mutation is possible from any Autopilot command without explicit human-approved flow
- [ ] `REQUIRED` No paid API call is possible from any Autopilot command without explicit human-approved flow
- [ ] `REQUIRED` HALT file mechanism halts execution when present
- [ ] `REQUIRED` Policy engine cannot be bypassed via any CLI flag or config
- [ ] `REQUIRED` Run lock prevents concurrent cycles
- [ ] `REQUIRED` Forbidden action list from AGENT_RULES.md is enforced in post-builder policy
- [ ] `OPTIONAL` Telegram alert sends when HALT file is written
- [ ] `DEFERRED` Safety monitoring from VPS or CI environment
- [ ] `FORBIDDEN` Any mechanism that enables automatic execution without human approval
- [ ] `FORBIDDEN` Any mechanism that removes the HALT file automatically

---

## Section 12 — MIRA Handoff Readiness

- [ ] `REQUIRED` All Project Autopilot v1 required capabilities confirmed passing
- [ ] `REQUIRED` AUTOPILOT_FINISH_LINE_CUTOVER_PLAN.md committed to `project_control/`
- [ ] `REQUIRED` AUTOPILOT_V1_COMPLETION_CHECKLIST.md committed to `project_control/`
- [ ] `REQUIRED` AUTOPILOT_DEFERRED_SCOPE.md committed to `project_control/`
- [ ] `REQUIRED` AUTOPILOT_GO_NO_GO_DECISION.md committed to `project_control/`
- [ ] `REQUIRED` Human has read the Go/No-Go document and confirmed GO
- [ ] `REQUIRED` MIRA product open blockers (RLS, storage policies, CAPTCHA) are documented in BLOCKERS.md
- [ ] `REQUIRED` TASK_QUEUE.md reflects the next MIRA product task, not an Autopilot task
- [ ] `OPTIONAL` Branch `agent/autopilot-finish-line` merged to main after human review
- [ ] `DEFERRED` Any further Autopilot feature work until MIRA product need arises
- [ ] `FORBIDDEN` Continuing Autopilot expansion after v1 is declared complete without explicit re-authorization

---

## Final Completion Gate

All items labeled `REQUIRED` across all 12 sections must be checked PASS.
Human must confirm the Go/No-Go document.
Only then is Project Autopilot v1 declared complete.
