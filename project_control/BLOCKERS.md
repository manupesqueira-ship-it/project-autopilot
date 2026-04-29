# Blockers

Blocking questions and decisions go here. These items should stop autonomous progress until a human resolves them.

## Open Blockers

### 2026-04-28 05:10 UTC - OpenAI API rate limit on --cycle

Status: resolved
Severity: non-critical
Source: Project Autopilot
Resolved: 2026-04-29
Resolution: Historical blocker. Root cause was identified as OpenAI API billing/quota balance, not a Project Autopilot code failure. Project Autopilot now handles 429 cleanly and local-plan/dry-run remain available.

Question or blocker:
OpenAI API `--cycle` returned HTTP 429 (Too Many Requests) during earlier testing. The supervisor planning cycle cannot complete until API billing, quota, or rate limits are verified.

This does NOT block:
- `--dry-run` mode (no API call).
- `--local-plan` mode (no API call).
- Claude Code builder workflow (uses local fallback plan).
- `--doctor` and `--status` modes.

Recommended action:
Verify OpenAI API billing and quota at platform.openai.com. Confirm the API key has access to the configured models (gpt-5.4-mini, gpt-5.4, gpt-5.5). Retry `--cycle` once resolved.

## Format

```md
### YYYY-MM-DD HH:MM - Short title

Status: open
Severity: blocking
Source: agent | builder | qa | human

Question or blocker:
...

Recommended action:
...
```

### 2026-04-28 05:36 UTC - Autopilot blocked: MissingOpenAICredentials

Status: resolved
Severity: blocking
Source: Project Autopilot
Resolved: 2026-04-29
Resolution: Historical blocker. Root cause was an empty local environment override causing OPENAI_API_KEY to be unavailable. Project Autopilot now reports missing credentials without printing secret values and falls back to local planning.

Question or blocker:
MissingOpenAICredentials
OPENAI_API_KEY is missing

Failure log:
logs\mira_autopilot_failure_20260428_053643.md

Recommended action:
OpenAI supervisor unavailable. A local fallback plan has been generated. Resolve the underlying issue (billing, quota, credentials) when convenient.

### 2026-04-28 05:39 UTC - Autopilot blocked: MissingOpenAICredentials

Status: resolved
Severity: blocking
Source: Project Autopilot
Resolved: 2026-04-29
Resolution: Historical duplicate of the local environment OPENAI_API_KEY issue. Kept for audit history, but no longer blocks local planning or product validation tooling.

Question or blocker:
MissingOpenAICredentials
OPENAI_API_KEY is missing

Failure log:
logs\mira_autopilot_failure_20260428_053911.md

Recommended action:
OpenAI supervisor unavailable. A local fallback plan has been generated. Resolve the underlying issue (billing, quota, credentials) when convenient.

### 2026-04-29 02:04 UTC - Post-builder QA: HUMAN_DECISION_REQUIRED

Status: parked
Severity: blocking
Source: Project Autopilot post-builder QA
Parked: 2026-04-29
Reason: Superseded by the 2026-04-29 02:31 UTC backend validation post-builder blocker, which captures the current manual Supabase verification requirement.

Question or blocker:
HUMAN_DECISION_REQUIRED

Post-builder log:
logs\mira_post_builder_20260429_020431.md

Recommended action:
Get human decision before more builder work.

### 2026-04-29 02:31 UTC - Post-builder QA: HUMAN_DECISION_REQUIRED

Status: parked
Severity: blocking
Source: Project Autopilot post-builder QA
Parked: 2026-04-29
Reason: Superseded by the later post-builder run after dependency installation and final validation gates.

Question or blocker:
HUMAN_DECISION_REQUIRED

Post-builder log:
logs\mira_post_builder_20260429_023122.md

Recommended action:
Get human decision before more builder work.

### 2026-04-29 02:39 UTC - Post-builder QA: HUMAN_DECISION_REQUIRED

Status: open
Severity: blocking
Source: Project Autopilot post-builder QA
Updated: 2026-04-29
Note: The `mira_profile` / `mira_photos` flow mismatch has been addressed in the flow-alignment sprint. This blocker remains open for live manual Supabase E2E verification of rows, storage, policies, and result polling.

Question or blocker:
HUMAN_DECISION_REQUIRED

Post-builder log:
logs\mira_post_builder_20260429_023939.md

Recommended action:
Get human decision before more builder work.

### 2026-04-29 - Supabase security model not ready for real customer data

Status: open
Severity: critical
Source: Manual Supabase audit + code inspection

Question or blocker:
P0 security gap. All 3 customer-facing tables (users_profile, user_assets, generations) have RLS disabled, 0 policies, and anon has all 7 Postgres privileges (SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER). Anyone with the public anon key — which is embedded in the frontend JS bundle — can read, modify, delete, or truncate all customer data including personal profiles, body measurements, and photo metadata.

Evidence:
- RLS disabled on users_profile, user_assets, generations (confirmed via SELECT-only audit)
- anon role has SELECT/INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER on all 3 tables
- 0 policies on any table
- 0 policies on storage.objects
- user-photos bucket is private but has no access policies (uploads/reads likely fail)
- generations and product-images buckets are public with no file size or MIME restrictions
- auth_user_id is nullable and unpopulated — no Supabase Auth in use
- user_profile_id is nullable on user_assets and generations
- Identity is localStorage-only (mira_profile_id) — tamperable
- Full analysis: project_control/MIRA_SUPABASE_SECURITY_ALIGNMENT_PLAN.md

Progress:
- 2026-04-29: Code-side anonymous auth foundation implemented (Section N of plan).
  Onboarding now sets auth_user_id. Server writes use service_role path.
  Auth helper created. App degrades gracefully if anonymous sign-ins not yet enabled.
- 2026-04-29: Supabase Auth Dashboard audit (Section N-pre of plan). Findings:
  - Anonymous Sign-Ins: OFF — auth_user_id stays null, RLS cannot be enabled
  - CAPTCHA / Attack Protection: OFF — signups open to abuse
  - Site URL: http://localhost:3000 — not production-ready
  - Redirect URLs: empty — OAuth/email-confirm redirects will fail outside localhost
  - New signups: open without leaked-password protection
  - Dashboard warning confirms: publishable key + RLS-off = unsafe to ship
  - 0 Edge Functions — all server logic must stay in Next.js API routes
- Remaining: Enable Anonymous Sign-Ins, enable CAPTCHA, set production Site URL,
  set SUPABASE_SERVICE_ROLE_KEY, apply RLS/policies, delete/backfill existing rows,
  run manual verification.

Impact:
MIRA must not store real customer photos, personal data, or body measurements until RLS, policies, and an identity model are in place.

Recommended action:
1. Enable Anonymous Sign-Ins in Supabase Dashboard > Authentication > Settings
2. Enable CAPTCHA (hCaptcha or Turnstile) for abuse protection
3. Set SUPABASE_SERVICE_ROLE_KEY in .env.local
4. Answer human questions in HUMAN_QUESTIONS.md
5. Apply RLS + policies from Section J of the plan in staging
6. Run manual verification checklist (Section L of the plan)

### 2026-04-29 - Flow QA selectors and framework added

Status: open
Severity: non-critical
Source: Overnight sprint

Progress:
- 2026-04-29: Stable QA selectors (data-testid) added across all 5 pages (onboarding, scan, catalog, tryon, result).
- 2026-04-29: Button component updated to accept testId prop.
- 2026-04-29: Flow QA framework created (flow_qa.py + mira_flows.yaml).
- 2026-04-29: 4 flows defined: route_readiness, selector_readiness, onboarding_safe_dry, full_flow_blocked.
- 2026-04-29: Flow QA CLI operational (--list, --dry-run, --diagnose, --run).
- 2026-04-29: Playwright-based execution works; gracefully skips when dev server is down.
- 2026-04-29: Backend audit enhanced with auth, selector, and Flow QA checks.
- 2026-04-29: Control Center updated with Flow QA integration.
- 2026-04-29: Mock generation plan documented (providers already mock when API keys absent).

Remaining to unblock full E2E Flow QA:
- Enable Anonymous Sign-Ins in Supabase Dashboard.
- Set SUPABASE_SERVICE_ROLE_KEY server-side.
- Decide test data strategy.
- ~~Implement Playwright route interception for mock generation.~~ DONE: QA mock mode implemented via NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS flag.
- Decide RLS/storage path plan.
- Draft and review storage policies.
- Decide real customer data safety approach.

Update 2026-04-29 (mock E2E sprint):
- QA mock mode implemented: lib/qa-mock.ts + API route guards.
- Full E2E mock flow added to Flow QA (mira_full_e2e_mock_flow).
- Mock mode is safe: defaults OFF, production-guarded, no paid APIs, no Supabase writes.
- To run: `NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true npm run dev` then `--run mira_full_e2e_mock_flow`.
- Remaining for REAL E2E: all Supabase security blockers still apply.

Update 2026-04-29 (secure MVP convergence sprint):
- Secure MVP readiness report created (mira_readiness.py).
- Master runbook created (MIRA_SECURE_MVP_RUNBOOK.md).
- Control Center updated with readiness data and 2 new evidence paths.
- Overall verdict: BLOCKED_FOR_REAL_CUSTOMER_DATA.
- Auth code: READY. Mock generation: READY. RLS docs: READY.
- Remaining: enable Anonymous Sign-Ins, add service_role key, make RLS decisions, run staging test.

Update 2026-04-29 (acceleration sprint):
- No-human mock E2E validation: `python -B project_autopilot/flow_qa.py --project mira --validate-mock-e2e`
- Auto-managed dev server (starts/stops as subprocess, no .env modification).
- All remaining blockers are now external/manual (Supabase Dashboard actions), not codebase ambiguity.

Update 2026-04-29 (privacy logging sprint):
- Sensitive logging audit tool created (sensitive_logging_audit.py). Verdict: PASS.
- Fixed 6 unsafe logging patterns: raw error objects in console, raw Supabase error messages shown to users.
- Privacy logging guardrails documented (MIRA_PRIVACY_LOGGING_GUARDRAILS.md).
- Backend audit, readiness report, and Control Center updated with privacy checks.
- Remaining privacy blockers: retention/deletion policy, privacy policy/terms, RLS ownership.

Update 2026-04-29 (env preflight sprint):
- Root cause: app crashed with "@supabase/ssr: Your project's URL and API key are required" because NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY were missing from .env.local.
- Fix: lib/supabase/env.ts validates env presence before client creation.
- Onboarding/scan show friendly error instead of raw crash.
- Env preflight tool: `python -B project_autopilot/env_preflight.py --project mira`
- Backend audit, readiness report, and Control Center updated with env checks.
- User must add all 3 Supabase env vars to .env.local (see runbook section D2).
