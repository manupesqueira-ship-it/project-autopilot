<!-- ============================================================ -->
<!-- ██████████████████████████████████████████████████████████ -->
<!-- ██                                                        ██ -->
<!-- ██   REVIEW ONLY — DO NOT EXECUTE THIS SQL               ██ -->
<!-- ██                                                        ██ -->
<!-- ██   This file contains DRAFT SQL for human review.      ██ -->
<!-- ██   NO part of this file should be run against any      ██ -->
<!-- ██   Supabase project without:                           ██ -->
<!-- ██     1. Full human review and sign-off                 ██ -->
<!-- ██     2. Successful staging/branch test                 ██ -->
<!-- ██     3. Explicit production approval                   ██ -->
<!-- ██     4. Verified rollback plan in place                ██ -->
<!-- ██                                                        ██ -->
<!-- ██████████████████████████████████████████████████████████ -->
<!-- ============================================================ -->

# MIRA Supabase RLS SQL Draft

**Status**: DRAFT — NOT APPROVED FOR EXECUTION
**Created**: 2026-04-30
**Author**: MIRA Project Autopilot (review-only agent)
**Target project**: mira-mvp (ref vtaqyammimmgxlkqwjat, AWS us-west-2)

---

## WARNING

> **DO NOT EXECUTE ANY SQL IN THIS DOCUMENT.**
>
> Every code block below is a draft for offline human review only.
> All SQL is commented out or marked DRAFT.
> This document must be reviewed, corrected, and explicitly approved
> before any statement is executed in staging or production.

---

## Assumptions

Before any SQL in this document can safely execute, ALL of the following
must be true. If any assumption is unmet, execution will break the app.

| # | Assumption | Evidence Required |
|---|---|---|
| A1 | Anonymous Sign-Ins are ENABLED in Supabase Auth Settings | Dashboard screenshot or `auth.config` check |
| A2 | `users_profile.auth_user_id` is populated for NEW rows (onboarding calls `signInAnonymously` first) | Live INSERT test row with non-null `auth_user_id` |
| A3 | Existing test data has been handled (deleted or backfilled) — see Backfill Prerequisites | Count query returns 0 rows with NULL `auth_user_id` |
| A4 | `SUPABASE_SERVICE_ROLE_KEY` is set in `.env.local` server-side only (not `NEXT_PUBLIC_`) | Env var present in server process; not in client bundle |
| A5 | Code changes for storage path convention decided and implemented (`{auth.uid()}/...` vs `{profileId}/...`) | Decision documented in MIRA_RLS_DECISION_MATRIX.md |
| A6 | Staging test of all policies has passed | Staging QA report attached |
| A7 | Rollback procedure has been tested in staging | Rollback run confirmed in staging |

---

## Backfill Prerequisites

Current state: every `users_profile` row has `auth_user_id = NULL`.
This means RLS policies using `auth.uid() = auth_user_id` will match ZERO rows
if enabled today. Enabling RLS now with 0 backfill = complete app lockout.

### Option A: Delete All Test Data (RECOMMENDED for MVP)

If there are no real customers, delete all test rows before applying RLS.
This is the safest and simplest approach.

```sql
-- DRAFT — DO NOT RUN LIVE
-- Delete in dependency order (FK constraints require this order)
-- Run each statement only after confirming data is disposable

-- DELETE FROM generations;
-- DELETE FROM user_assets;
-- DELETE FROM users_profile;

-- Also purge storage objects via Supabase Dashboard > Storage
-- or via Supabase CLI: supabase storage rm --recursive user-photos/
```

### Option B: Backfill Existing Rows (Complex — Not Recommended for MVP)

Only use this option if existing data must be preserved.
Requires creating anonymous auth.users rows and linking them.

```sql
-- DRAFT — DO NOT RUN LIVE
-- This approach is complex and fragile.
-- For MVP with test-only data, prefer Option A (delete).

-- Step B1: Create one anonymous auth user per orphaned profile row
-- (Must be done via Supabase Admin API or auth.signInAnonymously in a loop)
-- No SQL-only method exists for this step.

-- Step B2: After creating auth users externally, link them:
-- UPDATE users_profile
--   SET auth_user_id = '<new-auth-uid>'
--   WHERE id = '<profile-id>';
-- Repeat for each row.

-- Step B3: Verify all rows now have non-null auth_user_id
-- SELECT id, auth_user_id FROM users_profile WHERE auth_user_id IS NULL;
-- Expected: 0 rows
```

---

## Phase 1: Revoke Dangerous Grants

The `anon` and `authenticated` roles currently hold all 7 Postgres privileges
(SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER) on all three tables.
TRUNCATE, REFERENCES, and TRIGGER are never needed by client-side application code.

```sql
-- DRAFT — DO NOT RUN LIVE
-- Revoke dangerous privileges from application roles on all target tables.
-- service_role retains all privileges (it is not affected by these REVOKEs).

-- REVOKE TRUNCATE, TRIGGER, REFERENCES ON users_profile FROM anon, authenticated;
-- REVOKE TRUNCATE, TRIGGER, REFERENCES ON user_assets FROM anon, authenticated;
-- REVOKE TRUNCATE, TRIGGER, REFERENCES ON generations FROM anon, authenticated;
```

Rationale:
- `TRUNCATE` allows bulk deletion of the entire table via anon key. Never needed by client.
- `TRIGGER` allows creating triggers — no client should do this.
- `REFERENCES` allows creating FKs — no client should do this.
- Revoking these does NOT break any current app operation.

---

## Phase 2: Enable Row Level Security

Enable RLS on all three target tables.
`FORCE ROW LEVEL SECURITY` also applies RLS to the table owner role.

```sql
-- DRAFT — DO NOT RUN LIVE
-- Only execute AFTER:
--   (a) Assumption A1-A7 above are all verified
--   (b) Policies in Phase 3 are ready to be applied immediately after

-- users_profile
-- ALTER TABLE users_profile ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE users_profile FORCE ROW LEVEL SECURITY;

-- user_assets
-- ALTER TABLE user_assets ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_assets FORCE ROW LEVEL SECURITY;

-- generations
-- ALTER TABLE generations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE generations FORCE ROW LEVEL SECURITY;
```

**CRITICAL**: Do NOT enable RLS without immediately applying the policies in Phase 3.
Enabling RLS with 0 policies = default-deny = complete app lockout.

---

## Phase 3: RLS Policies — users_profile

Table: `users_profile`
Ownership column: `auth_user_id UUID` (FK to `auth.users(id)`)
Policy pattern: `auth_user_id = auth.uid()`

```sql
-- DRAFT — DO NOT RUN LIVE
-- All statements below are draft only.

-- SELECT: Users can read their own profile row only.
-- CREATE POLICY "users_profile_select_own"
--   ON users_profile
--   FOR SELECT
--   USING (auth_user_id = auth.uid());

-- INSERT: Users can insert a profile row only if auth_user_id matches their session.
-- This prevents one user from creating a profile attributed to another user.
-- CREATE POLICY "users_profile_insert_own"
--   ON users_profile
--   FOR INSERT
--   WITH CHECK (auth_user_id = auth.uid());

-- UPDATE: Users can update their own profile row only.
-- Both USING (which row) and WITH CHECK (what values) are set to prevent
-- a user from changing auth_user_id to point at another user.
-- CREATE POLICY "users_profile_update_own"
--   ON users_profile
--   FOR UPDATE
--   USING (auth_user_id = auth.uid())
--   WITH CHECK (auth_user_id = auth.uid());

-- DELETE: Users can delete their own profile row.
-- Consider whether self-deletion is desired (data retention implications).
-- If deletion should require a server-side action, omit this policy
-- and handle via service_role API route instead.
-- CREATE POLICY "users_profile_delete_own"
--   ON users_profile
--   FOR DELETE
--   USING (auth_user_id = auth.uid());
```

Notes on users_profile:
- No anon SELECT policy: anon users without a session cannot see any profile.
- No "public" SELECT policy: profiles are private by default.
- If a user clears browser storage and gets a new anonymous session, their old
  profile becomes inaccessible (they have a new auth.uid()). This is a UX
  trade-off acceptable for MVP anonymous auth.

---

## Phase 4: RLS Policies — user_assets

Table: `user_assets`
Ownership path: `user_profile_id -> users_profile.id -> auth_user_id -> auth.uid()`
Policy pattern: EXISTS subquery JOIN (no direct auth_user_id column on user_assets)

Two options are drafted below. Choose one.

### Option A: JOIN-based policies (no schema change required)

```sql
-- DRAFT — DO NOT RUN LIVE
-- Uses a subquery to join user_assets -> users_profile -> auth.uid()
-- Slightly slower than direct column but avoids ALTER TABLE.

-- SELECT: Users can read assets linked to their own profile.
-- CREATE POLICY "user_assets_select_own"
--   ON user_assets
--   FOR SELECT
--   USING (
--     EXISTS (
--       SELECT 1 FROM users_profile
--       WHERE users_profile.id = user_assets.user_profile_id
--         AND users_profile.auth_user_id = auth.uid()
--     )
--   );

-- INSERT: Users can insert assets linked to their own profile.
-- CREATE POLICY "user_assets_insert_own"
--   ON user_assets
--   FOR INSERT
--   WITH CHECK (
--     EXISTS (
--       SELECT 1 FROM users_profile
--       WHERE users_profile.id = user_assets.user_profile_id
--         AND users_profile.auth_user_id = auth.uid()
--     )
--   );

-- DELETE: Users can delete their own assets.
-- CREATE POLICY "user_assets_delete_own"
--   ON user_assets
--   FOR DELETE
--   USING (
--     EXISTS (
--       SELECT 1 FROM users_profile
--       WHERE users_profile.id = user_assets.user_profile_id
--         AND users_profile.auth_user_id = auth.uid()
--     )
--   );
```

### Option B: Direct auth_user_id column (requires schema change — RECOMMENDED)

```sql
-- DRAFT — DO NOT RUN LIVE
-- Step B1: Add auth_user_id column to user_assets
-- ALTER TABLE user_assets
--   ADD COLUMN IF NOT EXISTS auth_user_id UUID REFERENCES auth.users(id);

-- Step B2: Backfill from users_profile (only if rows exist and are not being deleted)
-- UPDATE user_assets ua
--   SET auth_user_id = up.auth_user_id
--   FROM users_profile up
--   WHERE ua.user_profile_id = up.id
--     AND up.auth_user_id IS NOT NULL;

-- Step B3: Policies using direct column (faster, simpler)
-- CREATE POLICY "user_assets_select_own"
--   ON user_assets
--   FOR SELECT
--   USING (auth_user_id = auth.uid());

-- CREATE POLICY "user_assets_insert_own"
--   ON user_assets
--   FOR INSERT
--   WITH CHECK (auth_user_id = auth.uid());

-- CREATE POLICY "user_assets_delete_own"
--   ON user_assets
--   FOR DELETE
--   USING (auth_user_id = auth.uid());

-- Step B4: After enabling and verifying, optionally add NOT NULL constraint
-- Requires all rows to have auth_user_id populated first.
-- ALTER TABLE user_assets ALTER COLUMN auth_user_id SET NOT NULL;
```

Notes on user_assets:
- No UPDATE policy: assets (uploaded photos) should be immutable from client perspective.
- Server-side cleanup (via service_role) can still modify/delete rows regardless of policies.
- `user_profile_id` must be NOT NULL for join-based policies to work correctly.

---

## Phase 5: RLS Policies — generations

Table: `generations`
Ownership path: `user_profile_id -> users_profile.id -> auth_user_id -> auth.uid()`
Write model: INSERT/UPDATE done server-side via `service_role` (bypasses RLS).
Read model: Client reads own generation via SELECT policy.

```sql
-- DRAFT — DO NOT RUN LIVE

-- SELECT: Users can read generation rows linked to their own profile.
-- Server-side reads via service_role bypass this policy (intended).
-- CREATE POLICY "generations_select_own"
--   ON generations
--   FOR SELECT
--   USING (
--     EXISTS (
--       SELECT 1 FROM users_profile
--       WHERE users_profile.id = generations.user_profile_id
--         AND users_profile.auth_user_id = auth.uid()
--     )
--   );

-- INSERT: Intentionally omitted for client role.
-- generation-store.ts uses createServiceRoleServer() for all generation INSERTs.
-- service_role bypasses RLS — no INSERT policy needed.
-- If a fallback INSERT policy for client is ever needed, draft it here:
--
-- CREATE POLICY "generations_insert_own"
--   ON generations
--   FOR INSERT
--   WITH CHECK (
--     EXISTS (
--       SELECT 1 FROM users_profile
--       WHERE users_profile.id = generations.user_profile_id
--         AND users_profile.auth_user_id = auth.uid()
--     )
--   );
--
-- WARNING: Only add the above if generation-store.ts is changed to use the anon client
-- for inserts. Currently it uses service_role, so no client INSERT policy is needed.

-- UPDATE: Intentionally omitted for client role.
-- Status updates are done server-side via service_role.

-- DELETE: Intentionally omitted.
-- Implement a server-side deletion endpoint if needed.
```

Notes on generations:
- With only a SELECT policy, clients can READ their results but cannot INSERT or UPDATE.
- This is intentional: generation creation and status updates are server-owned operations.
- If `service_role` is not configured (missing `SUPABASE_SERVICE_ROLE_KEY`), generation
  writes will fall back to anon client — which will fail once RLS is enabled.
  The service_role key MUST be set before RLS is enabled on this table.

---

## Phase 6: Rollback Plan

If RLS causes any breakage after activation, execute the following to restore
the previous (insecure but functional) state:

```sql
-- EMERGENCY ROLLBACK — DO NOT RUN UNLESS BREAKAGE CONFIRMED
-- Disabling RLS restores the pre-migration open-access state.
-- Run only if the app is broken and a hotfix is not possible in time.

-- ALTER TABLE users_profile DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_assets DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE generations DISABLE ROW LEVEL SECURITY;

-- Drop all policies created above (users_profile)
-- DROP POLICY IF EXISTS "users_profile_select_own" ON users_profile;
-- DROP POLICY IF EXISTS "users_profile_insert_own" ON users_profile;
-- DROP POLICY IF EXISTS "users_profile_update_own" ON users_profile;
-- DROP POLICY IF EXISTS "users_profile_delete_own" ON users_profile;

-- Drop all policies created above (user_assets - Option A)
-- DROP POLICY IF EXISTS "user_assets_select_own" ON user_assets;
-- DROP POLICY IF EXISTS "user_assets_insert_own" ON user_assets;
-- DROP POLICY IF EXISTS "user_assets_delete_own" ON user_assets;

-- Drop all policies created above (generations)
-- DROP POLICY IF EXISTS "generations_select_own" ON generations;

-- Restore grants if they were revoked (optional, only if needed)
-- GRANT TRUNCATE, TRIGGER, REFERENCES ON users_profile TO anon, authenticated;
-- GRANT TRUNCATE, TRIGGER, REFERENCES ON user_assets TO anon, authenticated;
-- GRANT TRUNCATE, TRIGGER, REFERENCES ON generations TO anon, authenticated;
```

**After rollback**: the system returns to the insecure open-access state.
This is safe only for internal test data. Do NOT allow real user data while rolled back.

---

## Execution Order Summary

If all assumptions are met and staging test passes, the recommended execution order is:

1. Verify assumptions A1-A7 (do not skip any)
2. Handle existing data (Option A: delete, or Option B: backfill)
3. Execute Phase 1: REVOKE dangerous grants
4. Execute Phase 2: ENABLE RLS on all tables
5. Execute Phase 3: CREATE policies for users_profile
6. Execute Phase 4: CREATE policies for user_assets (choose Option A or B)
7. Execute Phase 5: CREATE policies for generations
8. Run validation queries from MIRA_SUPABASE_SECURITY_VALIDATION_QUERIES_DRAFT.md
9. Run full app QA checklist from MIRA_SUPABASE_MIGRATION_REVIEW_CHECKLIST.md
10. If any failure: execute rollback from Phase 6

---

## Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | RLS enabled before any auth_user_id rows exist = complete lockout | P0 | Verify A2+A3 before Phase 2 |
| R2 | service_role key missing = generation writes fail after RLS | P0 | Verify A4 before Phase 2 |
| R3 | Storage path mismatch = upload policy rejects files | P1 | Verify A5; test in staging |
| R4 | Orphan rows in user_assets (null user_profile_id) locked out | P1 | Run orphan check query first |
| R5 | NULL user_profile_id in generations = not matched by any policy | P1 | Ensure user_profile_id is set before RLS |
| R6 | Rollback restores insecure state (real data exposed again) | P1 | Never run real user data until all staging tests pass |
| R7 | FORCE ROW LEVEL SECURITY blocks service_role table owner access | P2 | Remove FORCE if service_role writes are needed without explicit bypass |
| R8 | Old anonymous sessions expire — users lose access to their profile | P3 | Document UX; add session refresh logic |

---

*End of MIRA_SUPABASE_RLS_SQL_DRAFT_NOT_FOR_EXECUTION.sql.md*
*This file is a review artifact. Do not execute any SQL contained herein.*
