# Project Autopilot v1 — Finish-Line Cutover Plan

**Created:** 2026-04-30
**Status:** ACTIVE — hard stop document
**Purpose:** Define exactly what Project Autopilot v1 is, what it must prove, when it is done, and when work returns to MIRA product development.

---

## 1. Current State Summary

### What is built and working

- Provider Registry: Codex, OpenAI Auditor, Claude Code, Claude Agent SDK — all registered, metadata-only, no live execution.
- OpenAI Auditor Provider: `--status` and `--plan` run without calling OpenAI.
- Multi-Step Loop: `--dry-run-objective` previews lifecycle states without execution.
- Claude controlled analysis: invocable via `--claude-analysis-approved`, prompt redaction active, secrets never sent.
- Claude analysis review: `claude_analysis_review.py --latest` reads saved evidence only, no external calls.
- Claude sandbox boundary / preflight: `--claude-sandbox-preflight` and `--claude-sandbox-simulate` both run; no real worktrees created.
- Claude sandbox runner approval interface: status, approval preflight, dry-run, and rollback-plan commands all operational.
- Human-approved worktree creation-only flow: create/verify/cleanup smoke test passes.
- Policy Engine: post-builder verdicts (SAFE_TO_COMMIT / NEEDS_FIX / BLOCKED / HUMAN_REVIEW_REQUIRED / SAFE_NO_CHANGES) are active.
- Policy fixtures: 59/59 pass on latest main.
- Control Center: `--control-center` generates human-readable state snapshot.
- Design Director: integrated, advisory, evaluates UI changes against DESIGN_RUBRIC.md.
- Research Director: integrated, invoked before new dependencies or significant decisions.
- Builder Orchestrator: routes tasks, selects providers, determines required approvals — does not execute.
- Flow QA: CLI operational (`--list`, `--dry-run`, `--diagnose`, `--run`); mock E2E validates full flow without Supabase or paid APIs.
- Mock E2E: `mira_full_e2e_mock_flow` passes when dev server is up with QA mock mode enabled.
- Autopilot health: `--autopilot-health` reports overall readiness.
- Scheduler: DISABLED.
- Automatic Claude execution: DISABLED.
- Manual Claude handoff: dry-run and smoke test operational.

### What is not yet done

- No live Claude builder execution in a sandbox.
- No scheduler cycle ever triggered automatically.
- No auto-merge has ever fired.
- No VPS runner deployed.
- No GitHub Actions automation connected.
- No live Supabase mutations from Project Autopilot.
- MIRA product Supabase security (RLS, storage policies, CAPTCHA) not yet enabled — this is a MIRA product blocker, not an Autopilot blocker.

---

## 2. What Project Autopilot v1 Is Supposed to Do

Project Autopilot v1 is a **human-supervised control plane** that:

1. Reads the task queue and project control state.
2. Plans the next task using OpenAI Auditor or local fallback — no automatic execution.
3. Generates a structured builder prompt (for Codex or Claude) without executing it automatically.
4. Accepts a completed builder report after a human or manually-invoked builder finishes work.
5. Runs post-builder policy: validation, QA, design, evidence gates.
6. Produces a deterministic verdict: SAFE_TO_COMMIT / NEEDS_FIX / BLOCKED / HUMAN_REVIEW_REQUIRED.
7. Creates a sandbox worktree on explicit human approval (worktree creation only, not execution).
8. Produces a manual Claude handoff packet so a human can invoke Claude Code in the worktree.
9. Sends Telegram alerts for blockers and escalations.
10. Maintains evidence bundles, run history, and Control Center state.
11. Enforces all policy gates: no secrets, no env files, no live DB, no scheduler, no auto-merge, no deployment, no paid APIs without explicit approval.

---

## 3. What Project Autopilot v1 Is NOT Supposed to Do

- **NOT** execute Claude automatically in any context.
- **NOT** schedule or trigger itself on a cron.
- **NOT** merge pull requests.
- **NOT** push to main or protected branches directly.
- **NOT** execute Supabase migrations or mutations.
- **NOT** call paid image or video generation APIs.
- **NOT** deploy anything to production or staging.
- **NOT** create GitHub Actions workflows that trigger autonomously.
- **NOT** run parallel agent writers without isolated worktrees and human approval.
- **NOT** operate on a VPS.
- **NOT** bypass any policy gate for speed or convenience.
- **NOT** replace the human decision-maker for irreversible actions.

---

## 4. Minimum Required Capabilities for v1 Completion

The following capabilities must all be confirmed with passing evidence before declaring v1 complete. Each must produce a clean result with no hard failures.

| # | Capability | Confirming command |
|---|-----------|-------------------|
| 1 | Doctor passes | `python -B project_autopilot/agent_loop.py --project mira --doctor` |
| 2 | Autopilot health passes | `python -B project_autopilot/agent_loop.py --project mira --autopilot-health` |
| 3 | Policy fixtures 59/59 | `python -B project_autopilot/policy_test_fixtures.py --project mira --run all` |
| 4 | Claude SDK dry-run passes | `python -B project_autopilot/agent_loop.py --project mira --claude-sdk-dry-run` |
| 5 | Local plan generates | `python -B project_autopilot/agent_loop.py --project mira --local-plan` |
| 6 | Post-builder policy runs | `python -B project_autopilot/agent_loop.py --project mira --policy-check` |
| 7 | Control Center generates | `python -B project_autopilot/agent_loop.py --project mira --control-center` |
| 8 | Sandbox preflight runs | `python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-preflight --task "smoke test"` |
| 9 | Sandbox simulation runs | `python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-simulate --task "smoke test"` |
| 10 | Worktree smoke test passes | `python -B project_autopilot/agent_loop.py --project mira --claude-worktree-smoke-test` |
| 11 | Manual handoff dry-run passes | `python -B project_autopilot/claude_manual_handoff.py --project mira --task "smoke test" --dry-run` |
| 12 | Flow QA dry-run passes | `python -B project_autopilot/flow_qa.py --project mira --dry-run` |
| 13 | Mock E2E validates | `python -B project_autopilot/flow_qa.py --project mira --validate-mock-e2e` |
| 14 | Python compileall passes | `python -B -m compileall project_autopilot agent` |
| 15 | npm lint passes | `npm run lint` |
| 16 | npm typecheck passes | `npm run typecheck` |

---

## 5. Required Validation Commands

Run in this exact sequence before declaring v1 complete:

```bash
# Step 1: Python syntax
python -B -m compileall project_autopilot agent 2>&1

# Step 2: JavaScript/TypeScript
npm run lint 2>&1
npm run typecheck 2>&1

# Step 3: Autopilot core
python -B project_autopilot/agent_loop.py --project mira --doctor
python -B project_autopilot/agent_loop.py --project mira --autopilot-health

# Step 4: Policy
python -B project_autopilot/policy_test_fixtures.py --project mira --run all
python -B project_autopilot/agent_loop.py --project mira --policy-check

# Step 5: Sandbox boundary
python -B project_autopilot/agent_loop.py --project mira --claude-sdk-dry-run
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-preflight --task "v1 validation smoke test"
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-simulate --task "v1 validation smoke test"
python -B project_autopilot/agent_loop.py --project mira --claude-worktree-smoke-test

# Step 6: Manual handoff
python -B project_autopilot/claude_manual_handoff.py --project mira --task "v1 validation smoke test" --dry-run
python -B project_autopilot/agent_loop.py --project mira --claude-manual-handoff-dry-run --task "v1 validation smoke test"

# Step 7: Flow QA
python -B project_autopilot/flow_qa.py --project mira --dry-run
python -B project_autopilot/flow_qa.py --project mira --validate-mock-e2e

# Step 8: Evidence and Control Center
python -B project_autopilot/agent_loop.py --project mira --local-plan
python -B project_autopilot/agent_loop.py --project mira --control-center

# Step 9: Git hygiene
git diff --check
git status --short
git diff --stat
```

---

## 6. Required Evidence

Before declaring v1 complete, the following evidence must exist under `logs/` (gitignored):

- `logs/policy_tests/` — policy fixture run results.
- `logs/claude/<project_id>/latest/` — dry-run evidence from Claude SDK dry-run gate.
- `logs/claude_sandbox/<project_id>/latest/worktree_creation.*` — worktree creation evidence.
- `logs/claude_sandbox/<project_id>/latest/worktree_cleanup.*` — worktree cleanup evidence.
- At least one Control Center report generated after the final validation sequence.
- At least one local plan generated without errors.

---

## 7. Human Approval Requirements

These actions require explicit human approval before they occur — they are never autonomous:

| Action | Gate |
|--------|------|
| First live Claude SDK call (analysis, not build) | Human must type `--claude-analysis-approved` |
| First real sandbox worktree creation | Human must confirm in the approval flow |
| Any worktree creation outside dry-run | Human run-lock review |
| Declaring v1 complete and returning to MIRA | Human must read this document and confirm |
| Scheduler enablement | Forbidden until explicitly authorized in a future sprint |
| Automatic Claude execution | Forbidden until explicitly authorized in a future sprint |
| Auto-merge | Permanently forbidden |
| Deployment | Permanently forbidden without explicit human decision |
| Live Supabase mutations from Autopilot | Permanently forbidden without explicit human decision |

---

## 8. What Must Remain Disabled for the Entire v1 Window

These items must NOT be enabled during the Project Autopilot v1 completion sprint or at the moment of declaring v1 complete:

- **Scheduler** — no cron trigger, no background loop, no automated cycle.
- **Automatic Claude execution** — Claude only runs when a human explicitly invokes it.
- **Auto-merge** — no PR is merged without a human approving the merge action.
- **Deployment** — nothing deploys to production, staging, or VPS.
- **Live Supabase** — Project Autopilot does not write to any Supabase table or run migrations.
- **Paid APIs** — no image generation, video generation, or external paid API calls from Autopilot.
- **GitHub Actions automation** — no workflow is connected to run Autopilot autonomously.
- **VPS runner** — not deployed, not configured, not accessed.

---

## 9. Recommended Final Sprint Sequence

These are the only remaining sprints allowed before declaring v1 complete. Each sprint is one focused commit.

### Sprint F-1: Final validation run

Run all 16 required capability commands. Capture output. Confirm all pass. Fix any syntax or import errors. Do not add new features.

### Sprint F-2: Finish-line documentation commit (this document)

Commit `AUTOPILOT_FINISH_LINE_CUTOVER_PLAN.md`, `AUTOPILOT_V1_COMPLETION_CHECKLIST.md`, `AUTOPILOT_DEFERRED_SCOPE.md`, and `AUTOPILOT_GO_NO_GO_DECISION.md` to `project_control/`.

### Sprint F-3: Go/No-Go human decision

Human reads the Go/No-Go decision document. Human confirms all GO criteria are met. Human declares v1 complete in writing (a comment, a commit message, or a Telegram note).

### Sprint F-4: Return to MIRA product development

Close the `agent/autopilot-finish-line` branch. Resume from MIRA's open blockers: RLS, storage policies, CAPTCHA, privacy/retention, production URL configuration.

No additional Autopilot sprints are authorized after Sprint F-3 unless a specific MIRA product need requires a bounded Autopilot fix.

---

## 10. Hard Stop Point

**Project Autopilot v1 is complete when all 16 required capabilities pass clean and the human declares done.**

After that point:

- No new Autopilot features until MIRA product is at a natural pause point.
- No scope creep into VPS, GitHub Actions, scheduler, parallel agents, or cloud execution.
- MIRA product work resumes as the primary priority.
- Any Autopilot improvements during MIRA work must be strictly bounded to fixing a broken gate, not expanding scope.

The product (MIRA) is the mission. Project Autopilot is infrastructure supporting the mission. Infrastructure is complete when it is reliable and safe, not when it has every planned feature.
