# MIRA Supabase Migration Review Checklist

**Status**: DRAFT — FOR HUMAN REVIEW AND USE
**Created**: 2026-04-30
**Author**: MIRA Project Autopilot (review-only agent)
**Target**: RLS + Storage Policy migration for mira-mvp Supabase project

---

## Overview

This checklist must be completed in order by a human operator before, during, and after
applying the SQL from:

- `MIRA_SUPABASE_RLS_SQL_DRAFT_NOT_FOR_EXECUTION.sql.md`
- `MIRA_SUPABASE_STORAGE_SQL_DRAFT_NOT_FOR_EXECUTION.sql.md`

No step should be skipped. Each checkpoint must produce evidence that is retained.

---

## PREFLIGHT CHECKLIST

Complete ALL items before touching any SQL or Supabase settings.

### P1: Human Decisions Required

- [ ] **P1.1** — Ownership strategy for `user_assets` decided:
  - [ ] Option A: JOIN-based policy (no schema change)
  - [ ] Option B: Direct `auth_user_id` column (ALTER TABLE required)
  - Decision documented: ___________________________

- [ ] **P1.2** — Ownership strategy for `generations` decided:
  - [ ] Option A: JOIN-based policy (no schema change)
  - [ ] Option B: Direct `auth_user_id` column (ALTER TABLE required)
  - Decision documented: ___________________________

- [ ] **P1.3** — Storage path convention decided:
  - [ ] Option A: Keep `{profileId}/...` paths (JOIN-based storage policy)
  - [ ] Option B: Switch to `{auth.uid()}/...` paths (code change + file migration)
  - Decision documented: ___________________________

- [ ] **P1.4** — `generations` bucket visibility decided:
  - [ ] Keep public (MVP acceptable, no real customer photos yet)
  - [ ] Make private with signed URLs (required before real user data)
  - Decision documented: ___________________________

- [ ] **P1.5** — Existing data disposition decided:
  - [ ] Delete all test data (recommended — no real customers)
  - [ ] Backfill existing rows with auth users (complex — not recommended for MVP)
  - Decision documented: ___________________________

### P2: Code Prerequisites

- [ ] **P2.1** — `lib/supabase/auth.ts` exists with `getOrCreateAnonymousUser()`.
- [ ] **P2.2** — `app/[locale]/(app)/onboarding/page.tsx` calls `getOrCreateAnonymousUser()` before INSERT and passes `auth_user_id` in the row.
- [ ] **P2.3** — `lib/generation-store.ts` uses `createServiceRoleServer()` for INSERT and UPDATE operations on `generations`.
- [ ] **P2.4** — If storage Option B chosen: `app/[locale]/(app)/scan/page.tsx` uses `auth.uid()` as storage path prefix.
- [ ] **P2.5** — Code changes above have been tested locally with the dev Supabase project.

### P3: Environment Prerequisites

- [ ] **P3.1** — `SUPABASE_SERVICE_ROLE_KEY` is set in `.env.local` on the server.
- [ ] **P3.2** — `SUPABASE_SERVICE_ROLE_KEY` is NOT in any `NEXT_PUBLIC_` variable.
- [ ] **P3.3** — `SUPABASE_SERVICE_ROLE_KEY` is NOT committed to git.
- [ ] **P3.4** — Local app starts and runs against dev/staging project with service role key set.

### P4: Supabase Auth Prerequisites

- [ ] **P4.1** — Supabase Dashboard > Authentication > Settings > **Anonymous Sign-Ins: ENABLED**.
- [ ] **P4.2** — Supabase Dashboard > Authentication > Settings > **Site URL**: set to the correct URL (not localhost for production).
- [ ] **P4.3** — Supabase Dashboard > Authentication > Settings > **Redirect URLs**: configured.
- [ ] **P4.4** — (Optional but recommended) CAPTCHA (hCaptcha or Turnstile) enabled for abuse protection.

Evidence required for P4.1: Screenshot of Supabase Auth settings showing Anonymous Sign-Ins enabled.

### P5: Baseline Snapshot

- [ ] **P5.1** — Run Section 9 "Pre-Migration Baseline Snapshot" query from `MIRA_SUPABASE_SECURITY_VALIDATION_QUERIES_DRAFT.md`.
- [ ] **P5.2** — Save the query output (paste into a dated document or screenshot).
- [ ] **P5.3** — Confirm baseline shows: RLS disabled, 0 policies on all tables, 0 storage policies.
- [ ] **P5.4** — Run Section 1 null-ownership queries and record counts.

### P6: Staging Environment Confirmed

- [ ] **P6.1** — A dedicated staging Supabase project (or branch) exists and is separate from production.
- [ ] **P6.2** — Staging project URL and keys are configured in a `.env.staging` or equivalent.
- [ ] **P6.3** — App can be started against staging project.
- [ ] **P6.4** — Staging project has same schema as production (users_profile, user_assets, generations, all three buckets).

---

## STAGING CHECKLIST

Complete ALL items against the staging project BEFORE touching production.

### S1: Staging Data Setup

- [ ] **S1.1** — Staging database confirmed empty (no real customer data).
- [ ] **S1.2** — If Option A (delete): All existing test rows deleted in correct dependency order.
  - Evidence: Section 1 summary query returns total=0 for all tables.

### S2: Apply SQL in Staging (Staging Only)

Run each phase from `MIRA_SUPABASE_RLS_SQL_DRAFT_NOT_FOR_EXECUTION.sql.md` in order.
Record the result of each.

- [ ] **S2.1** — Phase 1: REVOKE dangerous grants executed in staging.
  - Evidence: Section 3A query shows no TRUNCATE/TRIGGER/REFERENCES for anon/authenticated.

- [ ] **S2.2** — Phase 2: ENABLE RLS on all three tables in staging.
  - Evidence: Section 4A query shows rowsecurity=true for all three tables.

- [ ] **S2.3** — Phase 3: Create users_profile policies in staging.
  - Evidence: Section 5B query shows 3-4 policies on users_profile.

- [ ] **S2.4** — Phase 4: Create user_assets policies in staging (chosen option).
  - Evidence: Section 5B query shows 2-3 policies on user_assets.

- [ ] **S2.5** — Phase 5: Create generations SELECT policy in staging.
  - Evidence: Section 5B query shows 1+ policies on generations.

### S3: Apply Storage Policies in Staging

Run each phase from `MIRA_SUPABASE_STORAGE_SQL_DRAFT_NOT_FOR_EXECUTION.sql.md` in order.

- [ ] **S3.1** — Bucket file_size_limit set for user-photos (10MB).
  - Evidence: Section 6A query shows file_size_limit=10485760 for user-photos.

- [ ] **S3.2** — Bucket allowed_mime_types set for user-photos.
  - Evidence: Section 6A query shows allowed_mime_types=['image/jpeg','image/png','image/webp'].

- [ ] **S3.3** — Bucket file_size_limit set for generations (50MB).
- [ ] **S3.4** — Bucket allowed_mime_types set for generations.
- [ ] **S3.5** — (Optional) Bucket limits set for product-images.

- [ ] **S3.6** — user-photos INSERT policy created (chosen option).
- [ ] **S3.7** — user-photos SELECT policy created.
- [ ] **S3.8** — user-photos DELETE policy created.

- [ ] **S3.9** — If generations is being made private: generations SELECT policy created.
  - Evidence: Section 5C query shows policy for generations bucket.

### S4: Functional Testing in Staging

Each test must be run with a real anonymous browser session against the staging project.

**Onboarding tests:**
- [ ] **S4.1** — Open app in fresh private/incognito window against staging.
- [ ] **S4.2** — Complete onboarding form and submit.
- [ ] **S4.3** — Verify a new `auth.users` row was created (Section 8A count increased by 1).
- [ ] **S4.4** — Verify `users_profile` row was created with `auth_user_id` set (Section 1A shows 0 nulls for this session).

**Scan / photo upload tests:**
- [ ] **S4.5** — Upload a front photo in scan page.
- [ ] **S4.6** — Verify upload succeeds (no error in browser console).
- [ ] **S4.7** — Verify `user_assets` row created with correct `user_profile_id`.
- [ ] **S4.8** — Verify storage object exists under correct path (Section 7B query).

**Try-on tests:**
- [ ] **S4.9** — Initiate a try-on (mock mode acceptable).
- [ ] **S4.10** — Verify generation row created in `generations` with `user_profile_id` set.
- [ ] **S4.11** — Verify generation status polling works (result page shows result).

**Cross-user isolation tests (REQUIRED before production):**
- [ ] **S4.12** — Open a SECOND private/incognito window against staging.
- [ ] **S4.13** — Complete onboarding as a second user.
- [ ] **S4.14** — Attempt to read the first user's profile by UUID: verify 0 rows returned.
  Evidence: Direct SQL query `SELECT * FROM users_profile WHERE id = '<first-user-profile-id>'` returns 0 rows when run as second user's session.
- [ ] **S4.15** — Attempt to read first user's assets: verify 0 rows returned.
- [ ] **S4.16** — Attempt to read first user's storage folder: verify access denied.
- [ ] **S4.17** — Attempt to read first user's generation: verify 0 rows returned.

**Rollback test:**
- [ ] **S4.18** — Apply rollback SQL from Phase 6 of RLS draft in staging.
- [ ] **S4.19** — Verify app still works after rollback (data accessible again).
- [ ] **S4.20** — Re-apply all policies (confirm they can be re-applied cleanly).

### S5: Staging QA Framework

- [ ] **S5.1** — Run `mira_full_e2e_mock_flow` Flow QA against staging.
  Command: `python -B project_autopilot/flow_qa.py --flow mira_full_e2e_mock_flow`
- [ ] **S5.2** — All Flow QA steps pass.
- [ ] **S5.3** — No new errors in server logs related to RLS or permissions.

---

## PRODUCTION APPROVAL CHECKLIST

ALL staging items above must be complete before this section is started.

### PA1: Sign-Offs Required

Each item requires a named human to review and confirm before production is touched.

- [ ] **PA1.1** — Technical reviewer has read both SQL draft files in full.
  Reviewer name: _______________________  Date: _______________

- [ ] **PA1.2** — Technical reviewer has verified staging functional test results (S4).
  Reviewer name: _______________________  Date: _______________

- [ ] **PA1.3** — Product/business owner has confirmed it is acceptable to proceed with production migration.
  Approver name: _______________________  Date: _______________

- [ ] **PA1.4** — Confirm production has NO real customer data yet (only test data).
  If real customers exist: separate, more conservative plan required. Stop here.
  Confirmer name: _______________________  Date: _______________

### PA2: Production Backup / Safety

- [ ] **PA2.1** — Production database backup taken before migration (Supabase Dashboard > Database > Backups).
  Backup timestamp: _______________________

- [ ] **PA2.2** — Backup download confirmed (or backup is accessible in Supabase dashboard).

- [ ] **PA2.3** — Rollback SQL is prepared and ready to paste if needed (Phase 6 of RLS draft + storage rollback).

- [ ] **PA2.4** — Maintenance window agreed (time when low user traffic expected).
  Maintenance window: _______________________

### PA3: Production-Specific Verification

- [ ] **PA3.1** — Production Supabase project confirmed (project ref verified, not staging).
- [ ] **PA3.2** — Production `SUPABASE_SERVICE_ROLE_KEY` is set in production server environment.
- [ ] **PA3.3** — Production Anonymous Sign-Ins are enabled.
- [ ] **PA3.4** — Production Site URL is set to production domain.
- [ ] **PA3.5** — Production Redirect URLs include production domain.

---

## PRODUCTION EXECUTION CHECKLIST

Run each step in order. Do NOT batch steps. Verify each before proceeding.

- [ ] **E1** — Apply existing data decision (delete test data or confirm data is clean).
- [ ] **E2** — Execute Phase 1: REVOKE dangerous grants. Verify Section 3A.
- [ ] **E3** — Execute Phase 2: ENABLE RLS. Verify Section 4A.
- [ ] **E4** — Execute Phase 3: users_profile policies. Verify Section 5B shows 3+ policies.
- [ ] **E5** — Execute Phase 4: user_assets policies (chosen option). Verify Section 5B.
- [ ] **E6** — Execute Phase 5: generations SELECT policy. Verify Section 5B.
- [ ] **E7** — Execute storage bucket limits SQL. Verify Section 6A.
- [ ] **E8** — Execute storage policies (chosen option). Verify Section 5C.
- [ ] **E9** — Run complete onboarding flow end-to-end in production browser window.
- [ ] **E10** — Run Section 10 post-migration verification queries. Record results.
- [ ] **E11** — Monitor Supabase logs for 15 minutes for any permission errors.

---

## ROLLBACK CHECKLIST

Execute if ANY production step above fails or the app is broken after migration.

- [ ] **R1** — Stop ongoing changes immediately.
- [ ] **R2** — Execute Phase 6 rollback SQL from `MIRA_SUPABASE_RLS_SQL_DRAFT_NOT_FOR_EXECUTION.sql.md`.
- [ ] **R3** — Execute storage rollback SQL from `MIRA_SUPABASE_STORAGE_SQL_DRAFT_NOT_FOR_EXECUTION.sql.md`.
- [ ] **R4** — Verify Section 4A shows rowsecurity=false for all tables.
- [ ] **R5** — Verify app is functional again (onboarding, scan, try-on).
- [ ] **R6** — Document what failed and why before attempting migration again.
- [ ] **R7** — Notify all team members of rollback.

**Post-rollback state**: System returns to insecure but functional state.
Do NOT allow real customer data while in rollback state.

---

## EVIDENCE REQUIRED

The following evidence must be collected and retained for audit purposes:

| # | Evidence | Format | When |
|---|---|---|---|
| E1 | Supabase Auth settings screenshot showing Anonymous Sign-Ins enabled | Screenshot | Before migration |
| E2 | Pre-migration baseline snapshot query output | Text/screenshot | Before migration |
| E3 | Null ownership count = 0 (or confirmed delete) | Text/screenshot | Before enabling RLS |
| E4 | Staging functional test results (S4.1-S4.17) | Notes document | After staging tests |
| E5 | Cross-user isolation test: 0 rows returned for other user's data | Text/screenshot | After staging tests |
| E6 | Rollback test: policies re-applied cleanly | Notes | After staging rollback test |
| E7 | Flow QA results (S5) | QA report | After staging tests |
| E8 | Technical reviewer sign-off (PA1.1, PA1.2) | Named sign-off | Before production |
| E9 | Production backup timestamp (PA2.1) | Text | Before production execution |
| E10 | Post-migration Section 10 verification query output | Text/screenshot | After production execution |
| E11 | 15-minute log monitoring result: no permission errors | Notes | After production execution |

---

## HUMAN APPROVALS REQUIRED

This migration MUST NOT proceed to production without these approvals:

1. **Technical Approval**: A technically qualified person has reviewed both SQL draft files,
   understands the changes, and confirms they are correct and safe for the MIRA data model.

2. **Staging Verification**: The same or a qualified second person has personally witnessed
   or reviewed the results of all staging functional tests, especially cross-user isolation.

3. **Business Approval**: A business/product owner has confirmed it is acceptable to apply
   the migration to the production project at this time.

4. **Data Confirmation**: Someone with knowledge of the production database has confirmed
   whether real customer data exists and what disposition decision applies.

These approvals are not optional. If any is missing, stop the migration until obtained.

---

## CONTACTS AND ESCALATION

Fill in before migration:

| Role | Name | Contact |
|---|---|---|
| Migration executor | | |
| Technical reviewer | | |
| Business approver | | |
| On-call for rollback | | |

---

*End of MIRA_SUPABASE_MIGRATION_REVIEW_CHECKLIST.md*
