# Project Autopilot v1 — Go / No-Go Decision

**Created:** 2026-04-30
**Status:** ACTIVE — to be reviewed by human owner before declaring v1 complete
**Owner:** Human must complete this document. No agent may fill it in.

---

## Purpose

This is a one-page decision gate. The human owner reads it, runs the final command bundle, checks each criterion, and declares GO or NO-GO in writing at the bottom.

No sprint, commit, or scope expansion is authorized after a GO decision without explicit re-authorization.

---

## GO Criteria

All of the following must be true before declaring GO:

- [ ] `python -B -m compileall project_autopilot agent` exits with zero errors
- [ ] `npm run lint` exits with zero errors
- [ ] `npm run typecheck` exits with zero errors
- [ ] `python -B project_autopilot/agent_loop.py --project mira --doctor` exits cleanly
- [ ] `python -B project_autopilot/agent_loop.py --project mira --autopilot-health` exits cleanly
- [ ] `python -B project_autopilot/policy_test_fixtures.py --project mira --run all` reports 59/59 pass
- [ ] `python -B project_autopilot/agent_loop.py --project mira --claude-sdk-dry-run` confirms no Anthropic call, scheduler disabled, automatic execution disabled
- [ ] `python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-preflight --task "v1 go-nogo smoke"` exits with no hard failures and no real worktree created
- [ ] `python -B project_autopilot/agent_loop.py --project mira --claude-worktree-smoke-test` exits cleanly
- [ ] `python -B project_autopilot/claude_manual_handoff.py --project mira --task "v1 go-nogo smoke" --dry-run` exits cleanly
- [ ] `python -B project_autopilot/flow_qa.py --project mira --validate-mock-e2e` passes
- [ ] `python -B project_autopilot/agent_loop.py --project mira --local-plan` generates a plan without errors
- [ ] `python -B project_autopilot/agent_loop.py --project mira --control-center` generates without errors
- [ ] `git status --short` returns empty (clean working tree)
- [ ] `git diff --check` returns no errors
- [ ] AUTOPILOT_FINISH_LINE_CUTOVER_PLAN.md is committed
- [ ] AUTOPILOT_V1_COMPLETION_CHECKLIST.md is committed
- [ ] AUTOPILOT_DEFERRED_SCOPE.md is committed
- [ ] AUTOPILOT_GO_NO_GO_DECISION.md is committed
- [ ] No item in Section 11 (Safety Readiness) of the checklist is failing

---

## NO-GO Criteria

Any single one of the following forces a NO-GO:

- `python -B -m compileall project_autopilot agent` has errors
- Policy fixture suite has any failure (fewer than 59/59 pass)
- `--claude-sdk-dry-run` reports scheduler enabled or automatic execution enabled
- `--autopilot-health` reports a hard failure (not just a warning)
- `git status --short` shows uncommitted changes in allowed files that are not yet committed
- Any `.env*` file is staged or committed
- Any secret or API key appears in any committed file
- Any `logs/` or `screenshots/` content is staged
- BLOCKERS.md has an open blocker with severity `blocking` that is not parked or resolved
- The scheduler is enabled (even if "just for testing")
- Automatic Claude execution is enabled
- Any auto-merge mechanism is reachable
- Any live Supabase mutation is reachable from a normal Autopilot command

---

## Warning Criteria

These do not force a NO-GO but must be noted in the human's decision record:

- `npm run build` fails (MIRA product issue, not Autopilot — note and continue)
- `--cycle` returns 429 or credential error (API billing issue — note, use `--local-plan`)
- Telegram alerts have not been tested recently (advisory, not blocking for v1)
- `--autopilot-health` reports warnings (not hard failures) about missing optional providers
- BLOCKERS.md has open non-critical items that are parked with a reason
- HUMAN_QUESTIONS.md has open items that are explicitly marked non-blocking

---

## Exact Final Command Bundle

Run these commands in this exact order. Copy-paste the output. Review each result. Check each GO criterion.

```bash
# 1. Python syntax check
python -B -m compileall project_autopilot agent 2>&1

# 2. JS/TS checks
npm run lint 2>&1
npm run typecheck 2>&1

# 3. Core health
python -B project_autopilot/agent_loop.py --project mira --doctor
python -B project_autopilot/agent_loop.py --project mira --autopilot-health

# 4. Policy
python -B project_autopilot/policy_test_fixtures.py --project mira --run all
python -B project_autopilot/agent_loop.py --project mira --policy-check

# 5. Claude boundary
python -B project_autopilot/agent_loop.py --project mira --claude-sdk-dry-run
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-preflight --task "v1 go-nogo smoke"
python -B project_autopilot/agent_loop.py --project mira --claude-sandbox-simulate --task "v1 go-nogo smoke"
python -B project_autopilot/agent_loop.py --project mira --claude-worktree-smoke-test

# 6. Manual handoff
python -B project_autopilot/claude_manual_handoff.py --project mira --task "v1 go-nogo smoke" --dry-run
python -B project_autopilot/agent_loop.py --project mira --claude-manual-handoff-dry-run --task "v1 go-nogo smoke"

# 7. Flow QA
python -B project_autopilot/flow_qa.py --project mira --dry-run
python -B project_autopilot/flow_qa.py --project mira --validate-mock-e2e

# 8. Evidence and planning
python -B project_autopilot/agent_loop.py --project mira --local-plan
python -B project_autopilot/agent_loop.py --project mira --control-center

# 9. Repo hygiene
git diff --check
git status --short
git diff --stat
git log --oneline -3
```

---

## Definition of "Done Enough"

Project Autopilot v1 is "done enough" when:

1. Every command in the final command bundle runs without a hard failure.
2. The policy fixture suite passes at 59/59.
3. No scheduler, no automatic Claude execution, no auto-merge, no deployment is enabled.
4. The four finish-line documents are committed to `project_control/`.
5. The human owner has read this document, checked the GO criteria, and recorded a GO decision below.

"Done enough" does not mean:
- Every planned feature is built.
- Every optional improvement is complete.
- Every deferred item is addressed.
- The VPS is set up.
- GitHub Actions is connected.
- Live Claude builder execution has happened.

The control plane is reliable, safe, and proven at the local scope. That is sufficient for v1.

---

## Recommended Next Product Task After Completion

After declaring Project Autopilot v1 complete, the immediate next task is MIRA product development, specifically:

**Enable MIRA Anonymous Sign-Ins and apply RLS policies**

Steps:
1. Enable CAPTCHA (hCaptcha or Turnstile) in Supabase Dashboard.
2. Set `SUPABASE_SERVICE_ROLE_KEY` in `.env.local`.
3. Apply RLS and storage policies from `supabase/drafts/` — staging test first, confirm with manual verification checklist in `MIRA_SUPABASE_MANUAL_ACTIVATION_CHECKLIST.md`.
4. Run `python -B project_autopilot/supabase_auth_verify.py --project mira` after each step.
5. Confirm `NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=false npm run dev` runs the real flow without Supabase errors.
6. Run the full manual E2E test from `MIRA_E2E_VALIDATION_PLAN.md`.

This is a human-operated task. Project Autopilot may be used to generate a plan, run post-builder policy on any code changes, and collect evidence — but the Supabase Dashboard actions require direct human access.

---

## Human Decision Record

**Instructions for the human owner:** Run the final command bundle above. Check each GO criterion. Then fill in this section.

```
Date:
Run by:

GO criteria — all checked? [ ] YES  [ ] NO

NO-GO criteria — any triggered? [ ] YES (describe below)  [ ] NO

Warnings noted:


Decision: [ ] GO  [ ] NO-GO

Reason (if NO-GO or if warnings exist):


Next action:
```

Do not leave this section blank. An undecided document is not a GO.
