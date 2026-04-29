# MIRA Secure MVP Runbook

> Master human-facing guide for advancing MIRA toward private beta.
> Last updated: 2026-04-29

---

## A. Current State Summary

| Area | Status |
|---|---|
| Anonymous Auth code | Implemented (lib/supabase/auth.ts) |
| QA selectors | All 5 pages covered |
| Mock E2E path | Implemented, production-guarded |
| Flow QA framework | 5 flows defined, all have runners |
| RLS | Disabled (correct for now) |
| Storage policies | None (correct for now) |
| Real customer data | BLOCKED |
| Overall verdict | BLOCKED_FOR_REAL_CUSTOMER_DATA |

## B. What Is Safe Today

- Run mock E2E flow (no paid APIs, no live Supabase writes in mock path).
- Run route/selector/onboarding readiness flows.
- Run backend audit and Control Center.
- Run readiness report.
- Create test profiles via onboarding (writes to Supabase with anon key, acceptable for dev).
- Skip photos in scan (no Supabase writes).
- Browse catalog (read-only).

## C. What Is Unsafe Today

- Storing real customer photos, body measurements, or personal data.
- Running try-on generation without mock mode (calls paid APIs).
- Enabling RLS before decisions and staging test.
- Sharing the app URL publicly (no CAPTCHA, no rate limiting).
- Using the service_role key in client-side code.

## D. How to Run Mock E2E

### PowerShell
```powershell
$env:NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS="true"
npm run dev
```

### Bash / Git Bash
```bash
NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true npm run dev
```

### Then run the flow
```bash
python -B project_autopilot/flow_qa.py --project mira --run mira_full_e2e_mock_flow
```

Expected: PASS. If BLOCKED, check mock mode is active. If SKIPPED, check dev server is running.

## E. How to Enable Anonymous Sign-Ins

1. Open: https://supabase.com/dashboard/project/vtaqyammimmgxlkqwjat/auth/providers
2. Enable "Anonymous Sign-Ins" toggle.
3. Save.
4. Restart dev server.

Full details: `project_control/MIRA_SUPABASE_MANUAL_ACTIVATION_CHECKLIST.md`

## F. How to Add SUPABASE_SERVICE_ROLE_KEY Locally

1. Open: https://supabase.com/dashboard/project/vtaqyammimmgxlkqwjat/settings/api
2. Copy the `service_role` secret key.
3. Add to `.env.local`:
   ```
   SUPABASE_SERVICE_ROLE_KEY=<paste-key-here>
   ```
4. Restart dev server.
5. NEVER commit `.env.local`.

## G. How to Verify auth_user_id Populates

1. Enable Anonymous Sign-Ins (Step E).
2. Start dev server: `npm run dev`
3. Open http://localhost:3000/es/onboarding
4. Fill and submit a test profile.
5. In Supabase Dashboard > Table Editor > users_profile, check latest row.
6. `auth_user_id` should be a non-null UUID.

Full details: `project_control/MIRA_LOCAL_AUTH_VERIFICATION_PLAN.md`

## H. How to Run Backend Audit

```bash
python -B project_autopilot/agent_loop.py --project mira --backend-audit
```

Expected: PARTIAL_READY (until RLS is enabled).

## I. How to Run Control Center

```bash
python -B project_autopilot/agent_loop.py --project mira --control-center
```

Opens: `logs/control_center/mira_control_center.html`

## J. How to Inspect Latest Flow QA Report

```bash
cat logs/flow_qa/mira/latest/flow_report.md
```

Or view screenshots: `logs/flow_qa/mira/latest/screenshots/`

## K. How to Run Readiness Report

```bash
python -B project_autopilot/mira_readiness.py --project mira
```

JSON output: `logs/mira_readiness_latest.json`

## L. How to Decide RLS Strategy

Review: `project_control/MIRA_RLS_DECISION_MATRIX.md`

Key decisions needed:
1. user_assets ownership: direct auth_user_id column (recommended) vs JOIN.
2. generations ownership: direct auth_user_id column (recommended) vs JOIN.
3. Storage paths: {auth.uid()}/... (recommended) vs {profileId}/...
4. generations bucket: keep public for MVP vs make private.

## M. What NOT to Do Yet

- **Do NOT enable RLS** until decisions made and staging tested.
- **Do NOT run SQL** from migration draft on live project.
- **Do NOT store real customer data** until RLS + policies active.
- **Do NOT run paid generation** in QA (use mock mode).
- **Do NOT share the app URL** publicly until CAPTCHA enabled.
- **Do NOT deploy** to production.

## N. Next 3 Sprints

### Sprint 1: Activate Auth
- Enable Anonymous Sign-Ins.
- Add service_role key to .env.local.
- Verify auth_user_id populates.
- Run full mock E2E with live server.

### Sprint 2: RLS Staging
- Make ownership/storage decisions.
- Apply RLS + policies in Supabase staging branch or disposable project.
- Test with Flow QA.
- Test rollback.

### Sprint 3: Security Hardening
- Enable CAPTCHA.
- Set production Site URL.
- Add bucket restrictions.
- Make generations bucket private + signed URLs.
- Prepare for private beta deployment.

---

## Quick Reference Commands

```bash
# Readiness report
python -B project_autopilot/mira_readiness.py --project mira

# Backend audit
python -B project_autopilot/agent_loop.py --project mira --backend-audit

# Control Center
python -B project_autopilot/agent_loop.py --project mira --control-center

# Flow QA diagnose
python -B project_autopilot/flow_qa.py --project mira --diagnose

# All readiness flows (dev server must be running)
python -B project_autopilot/flow_qa.py --project mira --run mira_route_readiness
python -B project_autopilot/flow_qa.py --project mira --run mira_selector_readiness
python -B project_autopilot/flow_qa.py --project mira --run mira_onboarding_safe_dry_flow

# Full mock E2E (dev server with mock mode must be running)
python -B project_autopilot/flow_qa.py --project mira --run mira_full_e2e_mock_flow

# NO-HUMAN VALIDATION: auto-starts mock dev server, runs all flows, stops server
python -B project_autopilot/flow_qa.py --project mira --validate-mock-e2e

# Run single flow with managed mock dev server
python -B project_autopilot/flow_qa.py --project mira --run mira_full_e2e_mock_flow --start-dev-server
```

### No-Human Validation

The `--validate-mock-e2e` command:
1. Starts a dev server with `NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true` as a subprocess.
2. Runs route readiness, selector readiness, onboarding dry flow, and full mock E2E.
3. Stops the dev server.
4. Writes summary to `logs/flow_qa/mira/latest/validation_summary.md`.
5. Returns 0 if no code failures, 1 if any flow FAILs.

**What it proves:** The full user journey works end-to-end with mock generation, no paid APIs, no real customer data.

**What it does NOT prove:** Real Supabase auth, RLS policies, storage access, paid generation quality.

**Remaining external/manual blockers (not code issues):**
- Enable Anonymous Sign-Ins in Supabase Dashboard
- Add SUPABASE_SERVICE_ROLE_KEY to .env.local
- Make RLS ownership/storage decisions
- Enable CAPTCHA before public testing
- Set production Site URL
