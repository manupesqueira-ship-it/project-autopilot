# MIRA Secure MVP Runbook

> Master human-facing guide for advancing MIRA toward private beta.
> Last updated: 2026-04-30

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
| Product flow hardening | Implemented (MIME/size validation, API guards) |
| Security staging pack | Complete (RLS/storage matrices, test plan, rollback) |
| Visual QA | Standard + tooling + external builder policy |
| Internal demo | Ready at /[locale]/demo |
| Overall verdict | INTERNAL_DEMO_READY_REALDATA_BLOCKED |

## B. What Is Safe Today

- **Open the internal demo** at `http://localhost:3000/es/demo` (start with `NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true npm run dev`).
- Click "Start full demo" for a one-click catalog → tryon → result flow with mock data.
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
cd C:\Users\manup\projects\mira
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Remove-Item -Recurse -Force .next -ErrorAction SilentlyContinue
$env:NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS="true"
npm run dev
```

Then open `http://localhost:3000/es/demo`.

Do not use old tabs. Do not use old port 3099 unless a Project Autopilot tool explicitly reports that port. Demo mock mode does not require real photos, real customer data, Supabase writes, or paid APIs. Real onboarding and scan still require Supabase public config.

### Bash / Git Bash
```bash
NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true npm run dev
```

### Then run the flow
```bash
python -B project_autopilot/flow_qa.py --project mira --run mira_full_e2e_mock_flow
```

Expected: PASS. If BLOCKED, check mock mode is active. If SKIPPED, check dev server is running.

## D2. Supabase Local Env Setup

Your `.env.local` must have these three variables (never commit this file):

```
NEXT_PUBLIC_SUPABASE_URL=https://vtaqyammimmgxlkqwjat.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_publishable_key_here
SUPABASE_SERVICE_ROLE_KEY=your_secret_service_role_key_here
```

Get the values from: Supabase Dashboard > Settings > API

**Verify without printing secrets:**
```bash
python -B project_autopilot/env_preflight.py --project mira
```

Expected: all three show `PRESENT`. If any show `MISSING`, the app will show a friendly error instead of crashing.

**Common mistake:** Adding `SUPABASE_SERVICE_ROLE_KEY` but forgetting the `NEXT_PUBLIC_` prefixed vars. All three are required.

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

## N. Security Staging Pack

The security staging pack provides all draft policies, test plans, and rollback procedures needed
before enabling RLS or storage policies. All files are in `project_control/security/` and `supabase/drafts/`.

### Security Staging Docs
- `project_control/security/MIRA_RLS_STORAGE_STAGING_PLAN.md` — Master staging plan
- `project_control/security/MIRA_RLS_POLICY_MATRIX.md` — Per-table RLS policies
- `project_control/security/MIRA_STORAGE_POLICY_MATRIX.md` — Per-bucket storage policies
- `project_control/security/MIRA_SECURITY_TEST_PLAN.md` — A/B user test matrix (30 cases)
- `project_control/security/MIRA_SECURITY_ROLLBACK_PLAN.md` — Phased rollback procedures
- `project_control/security/MIRA_SECURITY_OWNERSHIP_FINDINGS.md` — API ownership risk review

### SQL Drafts (DO NOT RUN ON PRODUCTION)
- `supabase/drafts/rls_candidate_policies.sql` — RLS policies for all tables
- `supabase/drafts/storage_candidate_policies.sql` — Storage policies for all buckets

### Security Staging Validator
```bash
python -B project_autopilot/security_staging_plan.py --project mira
```

### Key Ownership Findings
- Status endpoint (`/api/tryon/status/[id]`) has NO ownership check — any UUID returns data.
- Jobs endpoint trusts client-provided profileId without server auth verification.
- Both must be fixed before real customer data.

## O. Internal Local Demo Flow

To walk through the complete user experience with mock data (no paid APIs, no real photos):

1. Start the dev server:
   ```powershell
   cd C:\Users\manup\projects\mira
   Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
   Remove-Item -Recurse -Force .next -ErrorAction SilentlyContinue
   $env:NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS="true"
   npm run dev
   ```
2. Open http://localhost:3000/es/demo (or `/en/demo`)
3. Click "Start full demo"
4. Browse catalog, select any product
5. On try-on page, select a size and click "Try On"
6. View result page - mock generation will show placeholder image/video

**Safety:** Mock mode uses no paid APIs, no real Supabase writes in the demo generation path, and no real customer data.

## P. Next 3 Sprints

### Sprint 1: Activate Auth (partially done)
- ~~Enable Anonymous Sign-Ins.~~ DONE
- ~~Add service_role key to .env.local.~~ DONE
- Verify auth_user_id populates.
- Run full mock E2E with live server.

### Sprint 2: RLS Staging
- Make ownership/storage decisions (use decision matrix).
- Add auth_user_id column to user_assets and generations.
- Apply RLS + policies in disposable Supabase project.
- Run A/B security test matrix (30 test cases).
- Test rollback procedures.
- Add auth verification to status and jobs endpoints.

### Sprint 3: Security Hardening
- Enable CAPTCHA.
- Set production Site URL.
- Add bucket MIME/size restrictions.
- Switch generations bucket to private + signed URLs.
- Update client storage upload paths to `{auth.uid()}/...`.
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
- ~~Enable Anonymous Sign-Ins in Supabase Dashboard~~ DONE
- ~~Add SUPABASE_SERVICE_ROLE_KEY to .env.local~~ DONE
- Make RLS ownership/storage decisions
- Enable CAPTCHA before public testing

### Supabase Auth Verification

```bash
python -B project_autopilot/supabase_auth_verify.py --project mira
```

Verifies env vars, code wiring, auth helper, onboarding/scan integration, and mock mode safety. Must be PASS before testing with live Supabase.

```bash
python -B project_autopilot/supabase_auth_verify.py --project mira --live-dev-check
```

Performs anonymous auth + fake profile insert against live Supabase using dev-only data. Confirms auth_user_id is non-null. **Status: PASS (2026-04-30).**

- Set production Site URL

### Sensitive Logging Audit

```bash
python -B project_autopilot/sensitive_logging_audit.py --project mira
```

Checks for unsafe logging of tokens, sessions, PII, storage paths, and raw errors.
Must be PASS before real customer data. See `project_control/MIRA_PRIVACY_LOGGING_GUARDRAILS.md`.
