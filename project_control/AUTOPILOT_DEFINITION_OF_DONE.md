# Project Autopilot Definition of Done

Universal completion gates for any Project Autopilot sprint:

1. Repo was clean at start.
2. Scope was respected.
3. Changes stayed inside allowed files.
4. No secrets or env files were touched.
5. No live database mutation occurred unless explicitly approved.
6. No paid APIs were called unless explicitly approved.
7. `python -B -m compileall project_autopilot agent` passed.
8. `npm run lint` passed when applicable.
9. `npm run typecheck` passed when applicable.
10. `npm run build` passed when applicable.
11. Flow QA ran if product flow was affected.
12. Mock E2E ran if the user journey or demo path was affected.
13. Backend audit ran if backend/security/data behavior was affected.
14. Design Director ran if UI/design was affected.
15. Research Director was used if uncertain/vendor/security/paid decisions were affected.
16. Readiness report was updated or re-run.
17. Control Center was generated.
18. Evidence was generated.
19. Blockers were updated when blocking issues appeared.
20. Human questions were updated for non-blocking unresolved decisions.
21. Auto-commit happened only when safe.
22. Generated logs/screenshots were not staged.
23. Final repo was clean after commit, or dirty state was explicitly reported.

## Auto-Commit Rule

Auto-commit is allowed only when all required gates pass and changes are scoped, non-secret, non-destructive, non-deployment, non-paid, and non-live-database work.

## Unified Post-Builder Verdicts

Project Autopilot v2 post-builder policy produces one of:

- `SAFE_TO_COMMIT`: all applicable hard gates passed and commit may proceed if generated logs/screenshots are not staged.
- `NEEDS_FIX`: validation, QA, design, Flow QA, or other fixable gates failed. Generate/use the correction prompt and rerun `--post-builder`.
- `BLOCKED`: a hard safety gate fired, such as secrets/env files, SQL/RLS/live DB mutation, paid APIs, scheduler activation, automatic Claude execution, deployment, or generated logs staged.
- `HUMAN_REVIEW_REQUIRED`: no hard failure, but human decision, design review, research approval, or risk acceptance is required.
- `SAFE_NO_CHANGES`: no working-tree changes were detected; no commit is needed.

## Post-Builder Enforcement

`--post-builder` must evaluate provider, risk, scope, forbidden files, secrets/env, validation, design, research, backend, Flow QA, evidence, Definition of Done, and human approval gates before declaring work safe to commit.

Use:

```bash
python -B project_autopilot/agent_loop.py --project mira --post-builder logs/<builder_report>.md
python -B project_autopilot/agent_loop.py --project mira --policy-check
```

## Policy Fixture Regression Gate

Project Autopilot v2 policy behavior must stay covered by deterministic fixtures:

```bash
python -B project_autopilot/policy_test_fixtures.py --project mira --run all
```

The fixture suite must pass before Claude Agent SDK execution, scheduler activation, automatic builder execution, or broader autonomy is enabled. Fixtures simulate safe docs, UI/design changes, backend changes, Supabase/security review, forbidden env paths, secret-like text, paid APIs, scheduler activation, automatic Claude execution, generated logs, research-required decisions, design failure, and validation failure. Results are generated under ignored `logs/policy_tests/`.

## Operational Health Gate

Operators should use the consolidated health command before expanding autonomy:

```bash
python -B project_autopilot/agent_loop.py --project mira --autopilot-health
```

The health report summarizes provider readiness, policy fixtures, v2 readiness, post-builder policy availability, Flow QA/mock E2E, backend audit, MIRA readiness, HALT/run lock, scheduler status, automatic Claude execution status, Control Center availability, blockers, next actions, and Claude SDK readiness. `--doctor` must also surface latest policy fixture status.

Recommended operator flow:

```text
--doctor -> --autopilot-health -> --policy-fixtures -> --local-plan or --post-builder -> --control-center
```

Pre-Claude readiness requires local `ANTHROPIC_API_KEY`, provider dry-run mode, worktree/sandbox policy, allowlist/denylist, cost/budget gates, passing policy fixtures, and explicit human approval for the first live Claude SDK call. Scheduler and automatic Claude execution remain disabled.

## Claude Agent SDK Dry-Run Gate

Before any Claude Agent SDK live-call sprint, this command must pass or produce only accepted warnings:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-sdk-dry-run
```

The dry-run gate must confirm:

1. `ANTHROPIC_API_KEY` status is reported without exposing the value.
2. No Anthropic, Claude Code, OpenAI, Supabase, or paid API call occurred.
3. Automatic Claude execution is disabled.
4. Scheduler is disabled.
5. Post-builder policy and policy fixtures are active.
6. Builder Orchestrator routes Claude-suitable work to `dry_run_only`.
7. Future live Claude calls require explicit human approval.

The first live Claude SDK call is a future controlled analysis call, not a builder execution. Sandboxed builder execution and automatic execution require separate approvals.

## Controlled Claude Analysis Gate

Controlled Claude analysis is permitted only when explicitly invoked:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-analysis-approved --task "<analysis task>"
```

Completion requires:

1. Prompt redaction ran.
2. `secrets_sent` is false.
3. `no_tools`, `no_commands`, and `no_file_edits` are true.
4. Anthropic call count is zero for dry-run or exactly one for approved live analysis.
5. Evidence exists under ignored `logs/claude/<project_id>/latest/`.
6. Scheduler and automatic Claude execution remain disabled.

## Claude Analysis Review Gate

After controlled Claude analysis, the saved response must be reviewed locally:

```bash
python -B project_autopilot/claude_analysis_review.py --project mira --latest
```

The review must:

1. Read saved evidence only.
2. Make no external API calls.
3. Map Claude risks to Project Autopilot gates.
4. Identify policy fixture, research, blocker, documentation, sandbox, worktree, rollback, and commit-safety implications.
5. Produce a formal decision before sandbox design.

`PROCEED_TO_SANDBOX_DESIGN` allows only the next design sprint. It does not permit Claude builder execution, scheduler activation, auto-merge, deployment, live database work, or paid APIs.

## OpenAI Auditor / Multi-Step Loop Gate

OpenAI Auditor and the multi-step loop are dry-run only until a future controlled live-call or sandbox-execution sprint is explicitly approved.

Required checks:

1. Provider registry includes `openai_auditor`.
2. `openai_auditor.py --status` runs without calling OpenAI.
3. `openai_auditor.py --plan` writes ignored planning evidence only.
4. `multistep_loop.py --dry-run-objective` previews lifecycle states without execution.
5. Policy fixtures cover OpenAI Auditor live-call, self-approval, and policy-bypass risks.
6. Autopilot health and Control Center show live OpenAI calls disabled.
7. Project Autopilot remains final judge; OpenAI Auditor cannot skip policy, QA, Design Director, Research Director, backend audit, or Definition of Done.

## Stop Conditions

Stop and ask for human approval before secrets, env files, git history, destructive commands, deployment, live Supabase changes, SQL/RLS/storage policies, paid APIs, scheduler enablement, automatic Claude execution, or parallel writes without worktrees.
