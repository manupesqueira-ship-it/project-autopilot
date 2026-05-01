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

Before any expansion into Claude Agent SDK execution, scheduler runs, or automatic builder execution, the policy fixture suite must pass:

```bash
python -B project_autopilot/policy_test_fixtures.py --project mira --run all
```

The fixture suite is local and deterministic. It simulates changed files and builder reports for safe docs, UI, backend, Supabase/security, env/secrets, paid API, scheduler, automatic Claude, generated logs, research, design failure, and validation failure cases. It must not call external APIs, execute SQL, mutate Supabase, or stage generated logs.

## Operational Health Workflow

Use the consolidated operator workflow before starting or accepting builder work:

```text
--doctor -> --autopilot-health -> --policy-fixtures -> --local-plan or --post-builder -> --control-center
```

`--autopilot-health` reports the overall control-plane verdict, provider readiness, policy fixture health, Flow QA/mock E2E status, backend audit status, MIRA readiness status, Control Center availability, HALT/run lock state, scheduler status, automatic Claude execution status, Claude Agent SDK readiness, blockers, next actions, and evidence paths.

Pre-Claude readiness requires local `ANTHROPIC_API_KEY`, dry-run provider mode, worktree/sandbox policy, allowlist/denylist, cost/budget gates, passing policy fixtures, and explicit human approval before the first live Claude SDK call. Scheduler and automatic Claude execution remain disabled.
- `SAFE_NO_CHANGES`: no commit required.

## Claude Agent SDK Dry-Run Gate

Claude Agent SDK may be checked only in dry-run mode until a human explicitly approves a controlled live analysis call.

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-sdk-dry-run
```

Dry-run mode may report `ANTHROPIC_API_KEY` as `PRESENT_VALUE_HIDDEN`, `MISSING`, or `EMPTY`. It must not print the key, call Anthropic, execute Claude Code, install SDK packages, edit files, or enable automatic execution.

Before any live Claude SDK call:

1. Policy fixtures must pass.
2. Post-builder policy must be active.
3. Worktree/sandbox policy must be followed.
4. Allowlist/denylist must be in place.
5. Cost/budget gates must be reviewed.
6. The human must approve the specific call.

The first live call, when approved later, must be analysis-only and unable to edit files.

## Controlled Claude Analysis Call

The first live Claude path is now a controlled analysis call, not builder execution.

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-analysis-dry-run
python -B project_autopilot/agent_loop.py --project mira --claude-analysis-approved --task "Review Project Autopilot v2 architecture and identify top 5 risks"
```

Rules:

- `--claude-analysis-dry-run` must not call Anthropic.
- `--claude-analysis-approved` may make exactly one analysis-only Anthropic call.
- Claude must not receive secrets, use tools, edit files, execute commands, deploy, mutate live systems, or enable scheduler/automatic execution.
- Prompt redaction must run before any live call.
- Evidence must be saved under `logs/claude/<project_id>/latest/`.
- Sandboxed builder execution remains a future phase requiring separate approval.
- Claude analysis model is configured with `claude_analysis_model` in project YAML. Default: `claude-haiku-4-5-20251001`.
- Do not use deprecated 3.5/3.7 Claude model aliases. Use `claude-sonnet-4-6` only when stronger analysis is explicitly needed and available.

Automatic commit remains allowed only for scoped, local, non-secret, non-deployment, non-paid, non-live-database work where all required gates pass.

## Claude Analysis Review Gate

After a controlled Claude analysis call, Project Autopilot must convert the saved analysis into a local policy decision before starting sandboxed builder design:

```bash
python -B project_autopilot/claude_analysis_review.py --project mira --latest
```

The review reads ignored evidence only and must not call Anthropic, OpenAI, Supabase, or paid APIs. It maps Claude recommendations to provider, post-builder policy, evidence, blocker, sandbox/tool, command, commit, rollback, worktree, research, and fixture gates.

Allowed review verdicts:

- `PROCEED_TO_SANDBOX_DESIGN`: design the sandbox only; do not execute builders.
- `NEEDS_POLICY_FIXTURE`: add deterministic policy fixture coverage first.
- `NEEDS_RESEARCH`: create/approve a research request before implementation.
- `BLOCKED`: stop and resolve the missing safety gate.
- `HUMAN_REVIEW_REQUIRED`: record the human decision before proceeding.

Sandboxed Claude builder execution remains a separate future approval even when the review says sandbox design may proceed.

## OpenAI Auditor and Multi-Step Loop Gate

OpenAI Auditor is a dry-run planner/reviewer provider. It may organize objectives, improve builder prompts, diagnose blocked builder reports, draft correction instructions, review evidence, and recommend next steps. It must not build, self-approve, or bypass Project Autopilot policy.

Dry-run commands:

```bash
python -B project_autopilot/agent_loop.py --project mira --openai-auditor-status
python -B project_autopilot/agent_loop.py --project mira --openai-auditor-plan --task "Build a sandboxed Claude builder loop"
python -B project_autopilot/agent_loop.py --project mira --multistep-dry-run --objective "Improve MIRA result page design"
```

The intended future loop is:

```text
human objective -> OpenAI planning -> builder selected -> Claude/Codex handoff -> builder blocked or done -> OpenAI review -> validation -> policy review -> final verdict
```

Project Autopilot remains the final judge. OpenAI Auditor cannot skip Design Director, Research Director, backend audit, Flow QA, post-builder policy, or Definition of Done.

Live OpenAI calls require explicit future approval and are disabled in the current mode.

## Claude Sandbox Boundary Gate

Sandboxed Claude builder execution remains disabled. Before a future execution sprint can be proposed, Project Autopilot must pass:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-preflight --task "<task>"
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-simulate --task "<task>"
```

The preflight and simulation are planning tools only. They must not call Anthropic or OpenAI, execute Claude, create a real worktree, edit product code, deploy, run SQL/RLS, access env files, or enable scheduler/automatic Claude execution.

Required boundary:

1. Worktree required; one agent per worktree.
2. Direct master/main writes prohibited.
3. Auto-merge and force-push prohibited.
4. File allowlist/denylist applied before handoff.
5. Command allowlist/denylist applied before handoff.
6. Prompt pack contains no secrets and no env content.
7. Rollback/rejection plan exists.
8. Evidence bundle and post-builder policy are required.
9. Blocked/retry cases return to OpenAI Auditor for correction planning.

`SANDBOX_PREFLIGHT_PASS` or `SANDBOX_SIMULATION_PASS` allows only a later human-approved execution design. It does not permit Project Autopilot to execute Claude.

## Claude Sandbox Runner Approval Gate

The runner interface adds a deterministic approval contract before any future worktree creation or builder execution:

```bash
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-approval-preflight --task "<task>"
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-runner-dry-run --task "<task>"
```

Current runner approvals are dry-run/future-only except `APPROVED_FOR_WORKTREE_CREATION_ONLY`, which may create one sandbox worktree through an explicit create-approved command. That approval still must not execute Claude, edit files, commit, merge, call external APIs, or enable scheduler/automatic execution.

Runner work is blocked if approval is missing, rollback is missing, post-builder policy is missing, env/secret scope appears, direct master writes are allowed, auto-merge is allowed, unapproved worktree creation happens, or builder execution happens. Cleanup must be scoped to the recorded `mira-sandbox-*` path only.
