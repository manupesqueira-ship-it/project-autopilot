# Project Autopilot v1 — Final Status Summary

**Created:** 2026-05-01
**Status:** DRAFT — reflects state at time of creation, to be confirmed after final validation

---

## 1. What Project Autopilot v1 Can Do Today

### Control Plane
- **Doctor** (`--doctor`): Validates environment, credentials, config, control files, git state.
- **Status** (`--status`): Prints project config, budget, cycles, git status, recent logs.
- **Autopilot Health** (`--autopilot-health`): Reports overall system readiness.
- **Local Plan** (`--local-plan`): Generates deterministic builder prompt from local state without any API call.
- **Dry Run** (`--dry-run`): Reads config, collects git evidence, writes builder prompt, skips OpenAI.
- **Control Center** (`--control-center`): Generates human-readable state snapshot including scheduler status, safety gates, blockers, and policy fixture results.

### Provider Registry
- **Codex**: Registered, metadata-only.
- **OpenAI Auditor**: `--status` and `--plan` run without calling OpenAI.
- **Claude Code**: Registered, sandbox-only mode.
- **Claude Agent SDK**: Registered, dry-run-only mode.

### Multi-Step Loop
- `--dry-run-objective` previews lifecycle states without execution.

### Claude Sandbox & Analysis
- **Controlled analysis**: Invocable via `--claude-analysis-approved` with prompt redaction and secret exclusion.
- **Analysis review**: `claude_analysis_review.py --latest` reads saved evidence, no external calls.
- **Sandbox preflight**: `--claude-sandbox-preflight` runs boundary checks without creating worktrees.
- **Sandbox simulation**: `--claude-sandbox-simulate` simulates execution without creating worktrees.
- **Runner approval interface**: Status, approval preflight, dry-run, and rollback-plan commands operational.
- **Worktree creation-only flow**: Create/verify/cleanup smoke test passes on human approval.
- **Manual Claude handoff**: Generates complete handoff packet (sandbox path, allowlists, denylists, rules, stop conditions) for human to invoke Claude Code in a worktree.

### Policy Engine
- **Post-builder policy**: Evaluates provider, risk, scope, forbidden files, secrets/env, validation, design, research, backend, Flow QA, evidence, Definition of Done, and human approval gates.
- **Five verdicts**: SAFE_TO_COMMIT, NEEDS_FIX, BLOCKED, HUMAN_REVIEW_REQUIRED, SAFE_NO_CHANGES — all reachable.
- **Policy fixtures**: At least 69/69 after manual handoff additions (59 original + handoff fixtures).
- **No bypass**: No `--skip-policy` flag exists or is reachable.

### Flow QA
- CLI operational: `--list`, `--dry-run`, `--diagnose`, `--run`.
- Mock E2E validates full flow without Supabase or paid APIs.
- `--validate-mock-e2e` runs with auto-managed dev server.

### Evidence & Logging
- Evidence bundles generated cleanly.
- Records include agent, task, cycle, timestamps, cost, verdict.
- Sensitive logging audit passes (no PII or secrets in logs).
- Generated logs gitignored.

### Safety
- HALT file mechanism stops execution.
- Run lock prevents concurrent cycles.
- Telegram alerts for blockers and escalations.

---

## 2. What It Cannot Do Yet

- **No live Claude builder execution** in a sandbox worktree (dry-run and simulation only).
- **No automated scheduling** — no cycle has ever triggered automatically.
- **No auto-merge** — no PR has ever been merged without human action.
- **No VPS runner** — not deployed, not configured.
- **No GitHub Actions** — no workflow connected.
- **No live Supabase mutations** from Autopilot commands.
- **No live multi-step loop execution** — preview only.
- **No agent-to-agent communication** — providers do not pass results to each other automatically.
- **No parallel agent writers** — only single-agent worktree flow tested.

---

## 3. What Remains Disabled

| Item | Status | Required to Stay Disabled |
|------|--------|--------------------------|
| Scheduler | DISABLED | YES — until explicitly authorized in future sprint |
| Automatic Claude execution | DISABLED | YES — Claude only runs on explicit human invocation |
| Auto-merge | DISABLED | YES — permanently prohibited |
| Deployment triggers | DISABLED | YES — permanently prohibited without human decision |
| Live Supabase from Autopilot | DISABLED | YES — permanently prohibited without human decision |
| Paid APIs from Autopilot | DISABLED | YES — permanently prohibited without explicit approval |
| GitHub Actions | NOT CONNECTED | YES — requires separate human-approved sprint |
| VPS runner | NOT DEPLOYED | YES — requires dedicated sprint and security review |

---

## 4. What Requires Human Approval

| Action | Gate |
|--------|------|
| First live Claude analysis on real task | Human types `--claude-analysis-approved` with real task |
| Real sandbox worktree creation | Human confirms in approval flow |
| Declaring v1 complete | Human reads Go/No-Go doc and confirms |
| Scheduler enablement | Forbidden until future sprint authorization |
| Auto-merge | Permanently forbidden |
| Deployment | Human-only action |
| Live Supabase mutations | Human-only action via Dashboard |
| Paid API calls | Explicit human approval per call |

---

## 5. What Is Safe to Use for MIRA Product Development

- `--local-plan` to generate builder prompts for MIRA tasks.
- `--dry-run` to preview what a cycle would do without calling APIs.
- `--doctor` and `--status` to check environment health.
- `--autopilot-health` to check overall readiness.
- `--control-center` to view system state.
- `--policy-check` and post-builder policy on MIRA code changes.
- `--claude-sandbox-preflight` and `--claude-sandbox-simulate` to preview sandbox execution.
- `claude_manual_handoff.py --dry-run` to generate handoff packets for Claude Code.
- `flow_qa.py --validate-mock-e2e` to validate MIRA flows in mock mode.
- Policy fixture suite to verify policy engine integrity after changes.

---

## 6. What Must Not Be Used Yet

- `--cycle` with live OpenAI calls (requires verified API credentials and budget).
- Live Claude builder execution in any worktree (requires separate human-approved sprint).
- Scheduler cron in any form.
- Any command that would write to Supabase from Autopilot.
- Any command that would deploy, merge, or push to protected branches.
- Any command that would call paid image/video generation APIs.

---

## 7. Known Blockers

### MIRA Product Blockers (not Autopilot blockers)
- **Supabase security model**: RLS disabled on all customer tables, storage policies missing, CAPTCHA off. MIRA must not store real customer data until resolved.
- **Production URL configuration**: Site URL still localhost:3000.
- **Privacy/retention policy**: Not yet defined.

### Autopilot Advisory (non-blocking for v1)
- OpenAI `--cycle` previously hit 429 — resolved with fallback, but live cycle not required for v1.
- Telegram alerts not recently tested — advisory, not blocking.
- `npm run build` may show MIRA product warnings — not an Autopilot issue.

---

## 8. Known Acceptable Warnings

- `--autopilot-health` may report warnings about missing optional providers (e.g., VPS runner not configured). These are expected and non-blocking.
- `npm run build` may fail due to MIRA product issues (missing Supabase env vars in CI). This is a MIRA product issue, not an Autopilot gate.
- BLOCKERS.md has parked items with documented reasons. These are acknowledged, not forgotten.

---

## 9. Recommended Default Operating Mode

After v1 GO decision:

1. **Use `--local-plan`** as the default planning mode (free, no API, deterministic).
2. **Use manual Claude handoff** for builder work — generate the packet, invoke Claude Code yourself.
3. **Run post-builder policy** on every code change before committing.
4. **Run `--doctor`** before each work session to confirm environment health.
5. **Run policy fixtures** after any change to the policy engine.
6. **Keep scheduler DISABLED** until explicitly re-authorized.
7. **Keep automatic Claude execution DISABLED** until explicitly re-authorized.
8. **Focus on MIRA product development** — Autopilot is infrastructure, not the mission.
