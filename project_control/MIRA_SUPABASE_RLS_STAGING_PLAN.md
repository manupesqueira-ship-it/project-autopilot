# MIRA Supabase RLS Staging Plan

> **WARNING: DO NOT EXECUTE ANY SQL IN THIS DOCUMENT.**
> This is a planning and simulation document only.
> No SQL may be executed, no Supabase project may be mutated, and no policies
> may be created until a human approves each step and staging tests pass.

Created: 2026-04-30
Project: mira-mvp (ref vtaqyammimmgxlkqwjat)
Status: PLANNING ONLY — NO EXECUTION

---

## 1. Current Unsafe State

### 1.1 Tables

| Table | RLS Enabled | force_rls | Policies | anon privileges | authenticated privileges |
|---|---|---|---|---|---|
| users_profile | NO | false | 0 | ALL 7 (SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER) | ALL 7 |
| user_assets | NO | false | 0 | ALL 7 | ALL 7 |
| generations | NO | false | 0 | ALL 7 | ALL 7 |

### 1.2 What This Means in Practice

Anyone who obtains the Supabase publishable anon key — which is embedded in the
frontend JavaScript bundle — can:

- SELECT all rows from every customer-facing table.
- INSERT arbitrary rows into any table.
- UPDATE any row without authentication.
- DELETE any row or all rows.
- TRUNCATE entire tables with a single statement.
- Read body measurements, personal profiles, and photo metadata of all users.

### 1.3 Supabase Auth Status

| Setting | Current value | Required value |
|---|---|---|
| Anonymous Sign-Ins | OFF | ON (before RLS can be enabled) |
| CAPTCHA / Attack Protection | OFF | ON (before public beta) |
| Site URL | http://localhost:3000 | Production domain |
| Redirect URLs | 0 configured | Production + staging URLs |

### 1.4 Identity Model Gap

The application currently has no Supabase Auth session. `auth.uid()` is NULL on
every request. All identity is stored in browser localStorage (`mira_profile_id`),
which is a Supabase-generated UUID with no cryptographic binding to any user.
Any JavaScript that runs in the browser can read or forge this value.

### 1.5 auth_user_id Population

`users_profile.auth_user_id` exists as a nullable column but is NULL on every
existing row. It cannot be used in RLS policies until anonymous auth is enabled
and new rows are inserted by an authenticated session.

---

## 2. Required Ownership Model

### 2.1 Identity Chain

The target ownership model requires a verified identity chain on every row:

```
auth.users (Supabase Auth)
  └── auth.uid()               -- stable per session, set by Supabase
        └── users_profile.auth_user_id  -- FK to auth.users(id)
              └── user_assets.user_profile_id  -- FK to users_profile(id)
              └── generations.user_profile_id  -- FK to users_profile(id)
```

### 2.2 Ownership by Table

| Table | Primary ownership column | Policy expression |
|---|---|---|
| users_profile | auth_user_id | `auth_user_id = auth.uid()` |
| user_assets | user_profile_id (via join) | `EXISTS (SELECT 1 FROM users_profile WHERE id = user_assets.user_profile_id AND auth_user_id = auth.uid())` |
| generations | user_profile_id (via join) | `EXISTS (SELECT 1 FROM users_profile WHERE id = generations.user_profile_id AND auth_user_id = auth.uid())` |

The join-based approach is preferred for MVP because it avoids adding new
columns to user_assets and generations. If performance becomes a concern, a
direct `auth_user_id` column can be added to those tables (see
MIRA_RLS_DECISION_MATRIX.md Option B).

### 2.3 Anonymous Auth Model

- Anonymous Sign-Ins create a real `auth.users` row and issue a JWT.
- The client SDK automatically attaches this JWT as a Bearer token on every
  Supabase request.
- `auth.uid()` returns the anonymous user's UUID for the session lifetime.
- The anonymous session persists in browser storage (localStorage / cookies)
  and survives page refreshes.
- Loss of browser storage means the user loses their session and cannot
  re-authenticate (no account recovery path in this model).
- Anonymous sessions can be upgraded to full accounts later via Supabase
  identity linking. This is out of scope for the current sprint.

### 2.4 Service Role Boundary

The Supabase service_role key bypasses RLS entirely. It must never appear in:

- Any `NEXT_PUBLIC_*` environment variable.
- Any client-side code file.
- Any commit, log, or screenshot.

It must only be used in:

- Next.js API routes (`app/api/**`).
- Server-side Supabase clients (`lib/supabase/server.ts`
  `createServiceRoleServer()`).
- The generation-store write path (`createGeneration`, `updateGeneration`).

---

## 3. Pre-RLS Checks

The following checks must be completed and verified by a human before any
RLS is enabled on any table. They are read-only diagnostics.

### 3.1 Verify Auth User ID Population

Confirm that new onboarding flows populate `auth_user_id`:

```sql
-- STAGING ONLY — DO NOT RUN IN PRODUCTION WITHOUT HUMAN APPROVAL
SELECT id, auth_user_id, created_at
FROM users_profile
ORDER BY created_at DESC
LIMIT 10;
-- Expected after auth foundation: auth_user_id is non-NULL for new rows.
-- Expected before auth foundation: auth_user_id is NULL on all rows.
```

### 3.2 Count NULL Ownership Columns

```sql
-- STAGING ONLY — READ ONLY
SELECT
  COUNT(*)                                          AS total_profiles,
  COUNT(*) FILTER (WHERE auth_user_id IS NULL)      AS null_auth_user_id,
  COUNT(*) FILTER (WHERE auth_user_id IS NOT NULL)  AS populated_auth_user_id
FROM users_profile;

SELECT
  COUNT(*)                                           AS total_assets,
  COUNT(*) FILTER (WHERE user_profile_id IS NULL)    AS null_profile_id
FROM user_assets;

SELECT
  COUNT(*)                                           AS total_generations,
  COUNT(*) FILTER (WHERE user_profile_id IS NULL)    AS null_profile_id
FROM generations;
```

**Acceptance criteria**: `null_auth_user_id` on `users_profile` must be 0
before RLS is enabled. If any NULL rows exist, they must be deleted or
backfilled (see MIRA_SUPABASE_BACKFILL_AND_OWNERSHIP_PLAN.md).

### 3.3 Verify auth.uid() Is Non-NULL in Session

Before enabling RLS, confirm that a live browser session with anonymous auth
enabled produces a valid `auth.uid()`. This can be tested in the Supabase
SQL Editor using the anon role:

```sql
-- Run as anon role in Supabase SQL editor (use "anon" role switch)
SELECT auth.uid();
-- Expected: a valid UUID
-- If NULL: anonymous auth is not enabled or session is not established
```

### 3.4 Orphan Row Audit

```sql
-- STAGING ONLY — READ ONLY
-- user_assets with no matching profile
SELECT ua.id, ua.user_profile_id
FROM user_assets ua
LEFT JOIN users_profile up ON ua.user_profile_id = up.id
WHERE up.id IS NULL;

-- generations with no matching profile
SELECT g.id, g.user_profile_id
FROM generations g
LEFT JOIN users_profile up ON g.user_profile_id = up.id
WHERE up.id IS NULL;
```

All orphan rows must be resolved before RLS is enabled, or they will become
permanently inaccessible once policies require ownership.

### 3.5 Verify Storage Path Convention

Confirm that the scan page is writing storage objects under paths that begin
with `auth.uid()` (not `profileId`) before enabling storage policies. Storage
policy `(storage.foldername(name))[1] = auth.uid()::text` only works if the
first path segment is the auth user's UUID.

---

## 4. Required Data Backfill

See MIRA_SUPABASE_BACKFILL_AND_OWNERSHIP_PLAN.md for full details.

### 4.1 Summary

| Column | Table | Problem | Resolution |
|---|---|---|---|
| auth_user_id | users_profile | Nullable; NULL on all existing rows | Delete test data OR backfill (complex); start fresh recommended |
| user_profile_id | user_assets | Nullable; orphan risk | Ensure NOT NULL in schema; delete orphans |
| user_profile_id | generations | Nullable; orphan risk | Ensure NOT NULL in schema; delete orphans |

### 4.2 Recommended Approach for MVP

Because all existing rows are test data with no real customer value, the
recommended approach is to delete all existing rows and start fresh after
anonymous auth is enabled. This eliminates all NULL backfill complexity.

---

## 5. Policy Design by Table

All SQL below is DRAFT — DO NOT EXECUTE.

### 5.1 users_profile

```sql
-- DRAFT — DO NOT RUN

-- Revoke dangerous grants (must precede RLS enable)
REVOKE TRUNCATE, TRIGGER, REFERENCES ON users_profile FROM anon, authenticated;

-- Enable RLS
ALTER TABLE users_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE users_profile FORCE ROW LEVEL SECURITY;

-- SELECT: owner only
CREATE POLICY "users_profile_select_own"
  ON users_profile FOR SELECT
  USING (auth_user_id = auth.uid());

-- INSERT: owner sets own auth_user_id
CREATE POLICY "users_profile_insert_own"
  ON users_profile FOR INSERT
  WITH CHECK (auth_user_id = auth.uid());

-- UPDATE: owner can update own row; cannot change auth_user_id
CREATE POLICY "users_profile_update_own"
  ON users_profile FOR UPDATE
  USING (auth_user_id = auth.uid())
  WITH CHECK (auth_user_id = auth.uid());

-- DELETE: owner only; no client-initiated delete for MVP (use service_role for admin deletion)
-- Uncomment only if user-initiated deletion is implemented:
-- CREATE POLICY "users_profile_delete_own"
--   ON users_profile FOR DELETE
--   USING (auth_user_id = auth.uid());
```

**Notes:**
- No anon INSERT without auth session. After enabling anonymous auth, the
  anon client will have an active JWT so `auth.uid()` is available.
- `FORCE ROW LEVEL SECURITY` ensures policies apply even when the table owner
  (superuser context) is the caller. For API routes using service_role, RLS is
  bypassed regardless of this setting; FORCE only affects the postgres role.

### 5.2 user_assets

```sql
-- DRAFT — DO NOT RUN

REVOKE TRUNCATE, TRIGGER, REFERENCES ON user_assets FROM anon, authenticated;

ALTER TABLE user_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_assets FORCE ROW LEVEL SECURITY;

-- SELECT: join to users_profile to confirm ownership
CREATE POLICY "user_assets_select_own"
  ON user_assets FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM users_profile
      WHERE users_profile.id = user_assets.user_profile_id
        AND users_profile.auth_user_id = auth.uid()
    )
  );

-- INSERT: client can insert only if profile belongs to them
CREATE POLICY "user_assets_insert_own"
  ON user_assets FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM users_profile
      WHERE users_profile.id = user_assets.user_profile_id
        AND users_profile.auth_user_id = auth.uid()
    )
  );

-- DELETE: owner can delete own assets
CREATE POLICY "user_assets_delete_own"
  ON user_assets FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM users_profile
      WHERE users_profile.id = user_assets.user_profile_id
        AND users_profile.auth_user_id = auth.uid()
    )
  );

-- No UPDATE policy: assets are write-once from client perspective
```

### 5.3 generations

```sql
-- DRAFT — DO NOT RUN

REVOKE TRUNCATE, TRIGGER, REFERENCES ON generations FROM anon, authenticated;

ALTER TABLE generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE generations FORCE ROW LEVEL SECURITY;

-- SELECT: owner can read own generations
CREATE POLICY "generations_select_own"
  ON generations FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM users_profile
      WHERE users_profile.id = generations.user_profile_id
        AND users_profile.auth_user_id = auth.uid()
    )
  );

-- INSERT and UPDATE on generations are server-side only via service_role.
-- No client-side INSERT or UPDATE policies should be created.
-- service_role bypasses RLS, so no policy is needed for server writes.
```

**Rationale for server-only writes on generations:**
The generation lifecycle (insert pending, update in-progress, update completed)
is orchestrated by the API route (`app/api/tryon/jobs/route.ts`) and
`lib/generation-store.ts`. This code already runs server-side. Giving the
client INSERT/UPDATE privileges on generations opens a spoofing surface where
a malicious client could inject fake generation rows or modify generation
status. Server-side service_role writes are the secure path.

---

## 6. Anonymous Auth Assumptions

RLS policies in this plan assume the following about the anonymous auth model:

1. `supabase.auth.signInAnonymously()` is called before any write to
   `users_profile`, `user_assets`, or storage.
2. The resulting session is stored in browser localStorage by the Supabase
   client SDK and automatically refreshed.
3. Every subsequent Supabase request from the browser includes the anonymous
   JWT, making `auth.uid()` non-NULL in RLS evaluation.
4. Anonymous sessions survive page refresh but not localStorage clearing.
5. The onboarding flow (`app/[locale]/(app)/onboarding/page.tsx`) calls
   `getOrCreateAnonymousUser()` from `lib/supabase/auth.ts` before the
   profile INSERT, and includes `auth_user_id: auth.uid()` in the INSERT body.
6. If `signInAnonymously()` fails (e.g., the Supabase setting is not yet ON),
   the app gracefully degrades: `auth_user_id` is null, onboarding still
   completes, but the row will not be RLS-compatible.
7. Only ONE anonymous session per device per localStorage scope. The
   `getOrCreateAnonymousUser()` helper checks for an existing session before
   creating a new one.

**What must NOT be assumed:**
- Anonymous auth does not provide email, phone, or account recovery.
- An anonymous user who clears localStorage loses access to their data
  permanently (no recovery path in MVP scope).
- Anonymous auth does not prevent a user from creating multiple accounts by
  clearing storage.
- Anonymous auth is not a substitute for proper authentication in a production
  system with high-value data.

---

## 7. Server-Side service_role Assumptions

The service_role key bypasses all RLS and row-level access control. The
following assumptions govern its use:

1. `SUPABASE_SERVICE_ROLE_KEY` is only set in `.env.local` (server-side only).
   It must never appear in a `NEXT_PUBLIC_*` variable.
2. `createServiceRoleServer()` in `lib/supabase/server.ts` is only called
   from server-only files (API routes, server actions, server components).
3. service_role is used for:
   - `createGeneration()` — INSERT into generations table
   - `updateGeneration()` — UPDATE generation status/output paths
   - Future: admin deletion of user data
4. service_role is NOT used for:
   - `getGeneration()` — uses anon client so RLS applies to reads
   - Scan page uploads — uses authenticated browser client
   - Onboarding profile creation — uses authenticated browser client
5. If `SUPABASE_SERVICE_ROLE_KEY` is not set, the server falls back to the
   anon client. This is the current state. Before enabling RLS, the service_role
   key must be configured or the generation write path will fail.
6. The service_role client must never be returned to the browser or serialized
   in a response body.

---

## 8. What Must Be Tested in Staging First

All of the following must pass in a Supabase staging project (separate from
mira-mvp) before any RLS changes are made to the production project.

### 8.1 Functional Tests

| Test | Expected result |
|---|---|
| Anonymous sign-in creates auth.users row | YES |
| Onboarding INSERT populates auth_user_id | YES |
| Scan upload to user-photos succeeds | YES |
| Scan INSERT to user_assets succeeds | YES |
| Try-on reads own users_profile | YES |
| Try-on reads own user_assets | YES |
| Generation INSERT succeeds via service_role | YES |
| Generation status poll returns own row | YES |
| Cross-user: cannot read another user's profile | NO rows returned |
| Cross-user: cannot read another user's assets | NO rows returned |
| Cross-user: cannot insert into another user's profile | Rejected |
| anon cannot TRUNCATE any table | Rejected |
| Result page loads for own generation | YES |
| Result page returns 404 for another user's generation | 404 or empty |

### 8.2 Storage Tests

| Test | Expected result |
|---|---|
| Upload to user-photos under own auth.uid() path | YES |
| Upload to user-photos under another user's path | Rejected |
| Read own photo from user-photos | YES |
| Read another user's photo from user-photos | Rejected |
| Upload file exceeding size limit | Rejected |
| Upload non-image MIME type to user-photos | Rejected |

### 8.3 Regression Tests

| Test | Expected result |
|---|---|
| Full E2E mock flow (`mira_full_e2e_mock_flow`) passes | YES |
| Onboarding completes without errors | YES |
| Scan page reaches completion state | YES |
| Try-on page loads profile and generates result | YES |
| Result page displays mock output | YES |

### 8.4 Rollback Test

| Test | Expected result |
|---|---|
| Disabling RLS after enabling restores full access | YES |
| Dropping policies and re-enabling grants restores pre-RLS state | YES |

---

## 9. What Must Never Be Done Directly in Production

The following actions are forbidden on the live `mira-mvp` Supabase project
except after a complete staging test cycle and explicit human approval:

1. `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` on any table.
2. `CREATE POLICY ...` on any table.
3. `REVOKE ... FROM anon, authenticated` on any table.
4. `ALTER TABLE ... ADD COLUMN auth_user_id ...` on user_assets or generations.
5. `DELETE FROM users_profile` or any bulk delete.
6. `UPDATE storage.buckets SET public = false` for any bucket.
7. Creating storage policies on `storage.objects`.
8. Enabling Anonymous Sign-Ins in Supabase Auth settings while app code has not
   been verified to call `signInAnonymously()`.
9. Setting `SUPABASE_SERVICE_ROLE_KEY` without first verifying the server client
   code is correct and no fallback to anon client can occur.

---

## 10. Human Approval Gates

The following gates require explicit human review and sign-off before proceeding:

| Gate | Prerequisite | What human verifies |
|---|---|---|
| Gate 1: Auth Foundation | Code in place for `getOrCreateAnonymousUser()` | Service_role key configured; Supabase setting ready to enable |
| Gate 2: Enable Anonymous Sign-Ins | Gate 1 complete | Supabase Dashboard setting checked; staging test profile created with populated auth_user_id |
| Gate 3: Data Cleanup Approved | Gate 2 complete | No real customer data exists; deletion of test rows confirmed acceptable |
| Gate 4: RLS Enable in Staging | Gate 3 complete | Staging project created; all functional tests pass; rollback tested |
| Gate 5: Policy Review | Gate 4 complete | Human reads every CREATE POLICY statement and confirms intent |
| Gate 6: Production Apply | Gate 5 complete | Full E2E regression passed in staging; rollback plan confirmed ready |
| Gate 7: Post-deploy Verification | Gate 6 complete | Live smoke test confirms onboarding, scan, try-on, result all work |

No gate may be skipped. If any test fails at any gate, the sprint stops and
the issue is diagnosed before continuing.

---

## Appendix: Key File References

| File | Role |
|---|---|
| `lib/supabase/auth.ts` | `getOrCreateAnonymousUser()` helper |
| `lib/supabase/server.ts` | `createServiceRoleServer()` |
| `lib/supabase/client.ts` | Browser anon client |
| `app/[locale]/(app)/onboarding/page.tsx` | Profile INSERT with auth_user_id |
| `app/[locale]/(app)/scan/page.tsx` | Photo upload and user_assets INSERT |
| `lib/generation-store.ts` | Generations INSERT/UPDATE/SELECT |
| `lib/tryon-flow.ts` | users_profile and user_assets SELECT |
| `app/api/tryon/jobs/route.ts` | Server-side generation creation |
| `app/api/tryon/status/[generationId]/route.ts` | Status polling |
| `project_control/MIRA_RLS_DECISION_MATRIX.md` | Ownership strategy decisions |
| `project_control/MIRA_RLS_STORAGE_MIGRATION_DRAFT.md` | Draft SQL reference |
| `project_control/MIRA_SUPABASE_SECURITY_ALIGNMENT_PLAN.md` | Full security audit |
