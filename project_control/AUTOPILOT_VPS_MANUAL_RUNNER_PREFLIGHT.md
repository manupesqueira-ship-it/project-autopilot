# Project Autopilot — VPS Manual Runner Preflight Plan

**Status:** PREFLIGHT DOCS ONLY — No deployment has occurred.
**VPS IP:** 178.62.200.189 (Amsterdam 3, DigitalOcean)
**OS:** Ubuntu 24 LTS
**Date authored:** 2026-04-30

---

## 1. Goal of the Manual Runner

The manual runner is Stage 1 of Project Autopilot's VPS deployment. Its sole purpose is to let a human operator run a single, isolated Autopilot cycle by hand — with explicit console observation — before any automation is introduced.

- Confirm that the VPS environment runs the code without errors.
- Confirm that output artifacts (logs, evidence, cycle summaries) land in the correct paths.
- Confirm that Telegram reporting fires correctly.
- Confirm that the cycle completes and halts cleanly.
- Gather baseline timing data for a cold-start cycle.

The manual runner is NOT a shortcut to production. It is a controlled experiment.

---

## 2. What Is Explicitly Not Enabled in This Stage

The following capabilities are prohibited during the manual runner phase. Each item requires a separate, explicit human decision to enable:

| Capability | Status |
|---|---|
| systemd scheduler / cron | DISABLED — must remain off |
| Auto-Claude (LLM self-invocation loops) | DISABLED |
| Paid API calls (OpenAI, Anthropic, etc.) | DISABLED — use mocks only |
| Live Supabase writes | DISABLED — use local/mock DB |
| Auto-deploy pipelines | DISABLED |
| Auto-restart on failure | DISABLED |
| Telegram bot acting autonomously | DISABLED — reporting only |
| Email/SMS alerting | DISABLED |
| Any background daemon | DISABLED |

These items remain disabled until local cycles have been run and validated at least 5 consecutive times without human intervention being required for errors.

---

## 3. Required Local Readiness Before VPS

Before any attempt to run on the VPS, the following must be true locally:

### 3.1 Code Readiness
- [ ] `python -B -m compileall project_autopilot agent` passes with zero errors.
- [ ] `npm run lint` passes with zero errors (warnings acceptable).
- [ ] `npm run typecheck` passes with zero errors.
- [ ] `git diff --check` shows no whitespace errors.
- [ ] All unit tests pass locally (`pytest` or equivalent).
- [ ] At least one full dry-run cycle has completed locally without errors.

### 3.2 Environment Readiness
- [ ] `.env` file documented in internal runbook (not committed).
- [ ] All required environment variables listed in `project_control/`.
- [ ] Secrets are stored in a password manager — not in plaintext files.
- [ ] Python version pinned and confirmed matching VPS Python version.
- [ ] `requirements.txt` or `pyproject.toml` locked and tested.

### 3.3 Human Readiness
- [ ] Operator knows how to SSH into the VPS.
- [ ] Operator has a recovery plan if the cycle hangs.
- [ ] Operator has confirmed the NO-TOUCH ZONES (see `AUTOPILOT_VPS_NO_TOUCH_ZONES.md`).
- [ ] Operator has reviewed the security checklist.
- [ ] Operator has a kill command memorised or pinned.

---

## 4. First Manual VPS Command Philosophy

The first command run on the VPS for Project Autopilot must obey these principles:

### 4.1 One Cycle, One Human, One Terminal
Run exactly one cycle. Do not background it. Do not pipe it to a log file only — keep stdout visible in the terminal. Observe it in real time.

### 4.2 Explicit Python Invocation
Always invoke Python explicitly with the full path to the venv interpreter:

```bash
/root/autopilot/venv/bin/python -B -m project_autopilot.runner --dry-run --cycles 1
```

Never rely on PATH or shell aliases during the manual phase.

### 4.3 Dry-Run First
The very first invocation must include `--dry-run` (or equivalent flag). No live state mutations, no live API calls, no live DB writes on the first run.

### 4.4 Tee to Log
After dry-run succeeds, subsequent runs should tee to log:

```bash
/root/autopilot/venv/bin/python -B -m project_autopilot.runner --cycles 1 \
  2>&1 | tee /root/autopilot/logs/manual_run_$(date +%Y%m%dT%H%M%S).log
```

### 4.5 No Unattended Execution
Do not start a run and walk away. The operator must observe the full cycle, from start to clean exit.

---

## 5. No Scheduler

The scheduler (systemd timer, cron, APScheduler, celery-beat, or any equivalent) must not be configured, enabled, or started during the manual runner phase.

This means:
- No `systemctl enable` for any Autopilot unit.
- No `crontab -e` entries for Autopilot.
- No `@reboot` cron entries.
- No Python scheduler code running in the background.

The scheduler will be introduced only after:
1. Manual runs are boringly reliable (5+ clean cycles with no errors).
2. A separate document (`AUTOPILOT_VPS_SCHEDULER_PLAN.md`) is authored and reviewed.
3. Human explicitly approves the transition.

---

## 6. No Auto-Claude

Project Autopilot must not self-invoke the Claude API or any LLM API during the manual runner phase unless mocked.

This means:
- No `anthropic.Anthropic().messages.create(...)` calls hitting real endpoints.
- No `openai.ChatCompletion.create(...)` calls.
- All agent steps that require LLM output must use pre-recorded fixtures or stub responses.
- The `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` environment variables should not be present in the VPS environment during this phase.

Rationale: LLM costs are unbounded in a loop. A bug in cycle logic could trigger thousands of API calls before a human notices.

---

## 7. No Deploy

The manual runner phase must not trigger any deployment pipeline:

- No `git push` to production branches from the VPS.
- No Docker image builds targeting production registries.
- No Vercel/Netlify/Railway deploy hooks.
- No GitHub Actions workflows triggered from VPS.
- The VPS is an isolated execution environment only.

---

## 8. No Paid APIs

During the manual runner phase, all external API calls must be mocked or absent:

- OpenAI: use fixtures.
- Anthropic: use fixtures.
- Any data vendor APIs (exchange feeds, market data): use recorded snapshots.
- Telegram: allowed for status reporting only (no cost).
- Supabase: see Section 9.

If an API call would incur cost, it must be behind a `--live` flag that is OFF by default, and that flag must not be passed during manual runner phase.

---

## 9. No Live Supabase

During the manual runner phase, Supabase must not be used for live writes:

- Use a local SQLite or PostgreSQL instance for cycle state.
- Use fixture JSON files for read-only data that would normally come from Supabase.
- The `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` environment variables must not be present in the VPS environment during this phase.
- Evidence artifacts should be written to local disk only.

Rationale: A bug in cycle logic could corrupt live data before a human can intervene.

---

## 10. Human Approval Gates

The following checkpoints require explicit human sign-off before proceeding:

| Gate | Trigger | Required Action |
|---|---|---|
| G1: Enter VPS | First SSH session for Autopilot | Human reads NO-TOUCH ZONES, confirms in writing |
| G2: Install venv | Before `pip install` | Human confirms requirements.txt reviewed |
| G3: First dry-run | Before first `--dry-run` execution | Human confirms no live keys present |
| G4: First live-mock run | Before first run without `--dry-run` | Human reviews dry-run output and approves |
| G5: Telegram live | Before enabling Telegram reporting | Human confirms bot token is correct bot, correct chat |
| G6: Scheduler enable | After 5+ clean cycles | Human creates scheduler plan, reviews, approves |
| G7: Live API enable | After scheduler is stable | Human creates live API plan, reviews, approves |

No gate may be skipped. If a gate condition is unclear, stop and document the blocker in `project_control/BLOCKERS.md`.

---

## Appendix: Manual Runner Phase Exit Criteria

The manual runner phase is complete when all of the following are true:

- [ ] 5 consecutive clean cycles completed without errors.
- [ ] Logs land in correct paths every time.
- [ ] Telegram reporting fires correctly every time.
- [ ] Cycle timing is within expected bounds.
- [ ] No unexpected file writes outside designated paths.
- [ ] No API calls incurred unexpected costs.
- [ ] Human has reviewed 3 of the 5 cycle logs personally.
- [ ] Human has documented any edge cases observed.

Only then may the scheduler plan be authored.
