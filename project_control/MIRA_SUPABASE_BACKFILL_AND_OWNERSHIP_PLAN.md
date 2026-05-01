# MIRA Supabase Backfill and Ownership Plan

> **WARNING: DO NOT EXECUTE ANY SQL IN THIS DOCUMENT.**
> All SQL blocks are staging-only diagnostic drafts.
> No mutations may be run against the live mira-mvp project
> without human approval and prior staging verification.

Created: 2026-04-30
Project: mira-mvp (ref vtaqyammimmgxlkqwjat)
Status: PLANNING ONLY — NO EXECUTION

---

## 1. users_profile.auth_user_id Backfill Considerations

### 1.1 Current State

`users_profile.auth_user_id` is a nullable UUID column. Based on the security
audit (2026-04-29), every existing row has `auth_user_id = NULL`. This is
because the onboarding flow previously inserted profile rows without any
Supabase Auth session — there was no `auth.uid()` to set.

### 1.2 Why This Blocks RLS

RLS policies on `users_profile` are designed to use:

```sql
USING (auth_user_id = auth.uid())
```

If `auth_user_id` is NULL, this expression evaluates to NULL (not TRUE) for
every row, meaning:

- SELECT policies: no rows are returned.
- INSERT policies: all inserts are rejected (WITH CHECK evaluates to NULL/FALSE).
- UPDATE policies: no rows match.

**Result**: Enabling RLS while any rows have `auth_user_id = NULL` makes those
rows permanently invisible and unmodifiable by the owning user. They become
zombie rows accessible only via service_role.

### 1.3 Why Automatic Backfill Is Not Feasible

Backfilling `auth_user_id` on existing rows requires linking each row to a
Supabase Auth user. This is not possible for rows created without an auth
session:

- No auth.users row exists for these profile rows.
- The only identity available is the profile UUID stored in localStorage,
  which is not cryptographically bound to any auth session.
- Creating anonymous auth.users rows for each existing profile requires the
  Supabase Admin API and would produce auth sessions that no live browser
  holds (the original browser session is gone).
- Even if new auth.users rows were created, there is no way to deliver the
  new JWT to the user's browser to restore their session.

### 1.4 Options

| Option | Complexity | Data preserved | Recommended |
|---|---|---|---|
| A: Delete all rows, start fresh | Low | No | YES for MVP (test data only) |
| B: Backfill with new anonymous auth users | High | Yes | No — fragile and complex |
| C: Keep NULL rows, exclude from RLS | Medium | Partially | No — creates two-tier access model |

**Recommended: Option A.**

All existing rows are test data created during development and internal QA.
No real customer data exists. Deleting all rows and starting fresh after
anonymous auth is enabled is the cleanest and safest approach. New onboarding
flows will automatically populate `auth_user_id` via the code already in place
in `lib/supabase/auth.ts` and `app/[locale]/(app)/onboarding/page.tsx`.

### 1.5 Code Already in Place

The onboarding page was updated (sprint 2026-04-29) to call
`getOrCreateAnonymousUser()` before inserting a profile, and to include
`auth_user_id: user.id` in the INSERT. Once Anonymous Sign-Ins are enabled in
Supabase Auth settings, new rows will automatically have `auth_user_id` set.

### 1.6 Acceptance Criteria

Before enabling RLS on `users_profile`, verify:

- [ ] Anonymous Sign-Ins are enabled in Supabase Auth settings (Dashboard).
- [ ] A new onboarding flow in staging creates a profile with non-NULL `auth_user_id`.
- [ ] `SELECT count(*) FROM users_profile WHERE auth_user_id IS NULL` returns 0.

---

## 2. user_assets.user_profile_id Nullable Risks

### 2.1 Current State

`user_assets.user_profile_id` is a foreign key to `users_profile.id` and is
nullable. The scan page inserts asset rows with the `profileId` from localStorage,
so this field should be populated in most cases. However, if the profile was
not yet created or the localStorage key was missing, a row could be inserted
with `user_profile_id = NULL`.

### 2.2 RLS Impact

The RLS policy for `user_assets` uses a JOIN:

```sql
EXISTS (
  SELECT 1 FROM users_profile
  WHERE users_profile.id = user_assets.user_profile_id
    AND users_profile.auth_user_id = auth.uid()
)
```

If `user_profile_id` is NULL, the JOIN matches nothing and the EXISTS returns
FALSE. The asset row becomes invisible and unmodifiable by any client.

### 2.3 Risk Level

**Risk: MEDIUM.** In normal operation, `user_profile_id` is always set. NULL
values would only arise from bugs or edge cases (e.g., scan attempted before
onboarding completed, or localStorage cleared mid-flow). With test data,
these rows are safe to delete.

### 2.4 Long-Term Mitigation

After enabling RLS and once the flow is stable:

```sql
-- DRAFT — DO NOT RUN LIVE
-- Add NOT NULL constraint after confirming no NULL rows exist
ALTER TABLE user_assets ALTER COLUMN user_profile_id SET NOT NULL;
```

This constraint prevents future NULL rows at the database level. It should be
applied in a staging migration after verifying zero NULL rows.

---

## 3. generations.user_profile_id Nullable Risks

### 3.1 Current State

`generations.user_profile_id` is nullable. The generation-store inserts rows
with the `profileId` from the API request body. If the client sends no
`profileId` or sends `null`, the row is inserted with `user_profile_id = NULL`.

### 3.2 RLS Impact

Same as `user_assets`: a NULL `user_profile_id` means the JOIN-based RLS
policy returns FALSE for all users. The generation row becomes inaccessible
to any client. Only service_role can read or update it.

### 3.3 Specific Risk: Status Polling

The status polling endpoint (`app/api/tryon/status/[generationId]/route.ts`)
reads generations via service_role or anon client depending on configuration.
If using service_role (recommended), this is not affected by RLS and NULL
`user_profile_id` rows are readable server-side. If using the anon client,
NULL `user_profile_id` rows cannot be accessed after RLS is enabled.

**Recommendation**: The status API must use service_role to read generations.
This is already the target state per the security alignment plan.

### 3.4 Risk Level

**Risk: MEDIUM-HIGH.** If `user_profile_id` is NULL in a generation row and
the status API uses anon client with RLS enabled, result polling silently fails
returning no data. Users see a stuck or errored result page.

### 3.5 Long-Term Mitigation

```sql
-- DRAFT — DO NOT RUN LIVE
-- Add NOT NULL constraint on generations.user_profile_id
ALTER TABLE generations ALTER COLUMN user_profile_id SET NOT NULL;
```

Apply only after:
1. Verifying all existing rows have non-NULL `user_profile_id` (or deleting test data).
2. Updating the generation-store INSERT to always include `user_profile_id`.
3. Confirming API routes reject try-on requests without a valid profile ID.

---

## 4. Orphan Row Strategy

### 4.1 Definition of Orphan Rows

| Orphan type | Description | Risk |
|---|---|---|
| users_profile with auth_user_id = NULL | Profile exists but cannot be owned by any auth user | HIGH — invisible after RLS; blocks onboarding recovery |
| user_assets with user_profile_id = NULL | Asset row with no profile link | MEDIUM — invisible after RLS; wasted storage metadata |
| user_assets with broken profile FK | user_profile_id points to a deleted profile | MEDIUM — JOIN returns no match; asset inaccessible |
| generations with user_profile_id = NULL | Generation row with no profile link | HIGH — status polling breaks if using anon client |
| generations with broken profile FK | user_profile_id points to a deleted profile | HIGH — generation inaccessible to owner |

### 4.2 Orphan Resolution Strategy

**For MVP (test data only): delete all rows.**

```
Deletion order (respects FK constraints):
1. DELETE FROM generations;        -- no FK dependents
2. DELETE FROM user_assets;        -- no FK dependents beyond profile
3. DELETE FROM users_profile;      -- now safe (no child rows remain)
```

**For production (if real customers exist):**

1. Run orphan detection queries (see Section 5) to identify affected rows.
2. Decide per-row whether to delete or attempt recovery.
3. Contact affected users if feasible (no contact mechanism exists in MVP).
4. Delete unrecoverable orphan rows after a waiting period.

### 4.3 Cascade Deletion Design

Long-term, foreign key constraints should include `ON DELETE CASCADE` or
`ON DELETE SET NULL` as appropriate, so deletion of a `users_profile` row
automatically cleans up dependent rows. This is a schema improvement for a
future migration sprint.

---

## 5. Staging-Only Queries to Inspect Nulls

The following queries are read-only diagnostics. They may be run in a staging
Supabase project or reviewed via the Supabase SQL Editor in read-only mode.
They MUST NOT be run as part of a destructive migration without human approval.

### 5.1 Null Ownership Summary

```sql
-- STAGING ONLY — READ ONLY
-- Run this before enabling RLS to understand the data state

SELECT
  'users_profile' AS table_name,
  COUNT(*)                                        AS total_rows,
  COUNT(*) FILTER (WHERE auth_user_id IS NULL)    AS null_auth_user_id,
  COUNT(*) FILTER (WHERE auth_user_id IS NOT NULL) AS populated_auth_user_id
FROM users_profile

UNION ALL

SELECT
  'user_assets',
  COUNT(*),
  COUNT(*) FILTER (WHERE user_profile_id IS NULL),
  COUNT(*) FILTER (WHERE user_profile_id IS NOT NULL)
FROM user_assets

UNION ALL

SELECT
  'generations',
  COUNT(*),
  COUNT(*) FILTER (WHERE user_profile_id IS NULL),
  COUNT(*) FILTER (WHERE user_profile_id IS NOT NULL)
FROM generations;
```

**Acceptance criteria**: Every count in the `null_*` column must be 0 before
RLS is enabled.

### 5.2 Orphan user_assets Detection

```sql
-- STAGING ONLY — READ ONLY
-- Find asset rows with no matching profile

SELECT
  ua.id,
  ua.user_profile_id,
  ua.asset_type,
  ua.created_at
FROM user_assets ua
LEFT JOIN users_profile up ON ua.user_profile_id = up.id
WHERE up.id IS NULL
ORDER BY ua.created_at DESC;
```

Expected result: 0 rows (no orphan assets). If rows are returned, they must
be deleted before enabling RLS.

### 5.3 Orphan generations Detection

```sql
-- STAGING ONLY — READ ONLY
-- Find generation rows with no matching profile

SELECT
  g.id,
  g.user_profile_id,
  g.status,
  g.created_at
FROM generations g
LEFT JOIN users_profile up ON g.user_profile_id = up.id
WHERE up.id IS NULL
ORDER BY g.created_at DESC;
```

Expected result: 0 rows.

### 5.4 Profiles Without auth_user_id

```sql
-- STAGING ONLY — READ ONLY
-- Identify profiles that will become inaccessible after RLS is enabled

SELECT
  id,
  email,
  created_at,
  auth_user_id
FROM users_profile
WHERE auth_user_id IS NULL
ORDER BY created_at DESC;
```

Expected result: 0 rows before RLS is enabled.

### 5.5 Recent Profile Rows (Verify auth_user_id Population)

```sql
-- STAGING ONLY — READ ONLY
-- Verify that new rows created after anonymous auth is enabled have auth_user_id set

SELECT
  id,
  auth_user_id IS NOT NULL AS has_auth,
  created_at
FROM users_profile
ORDER BY created_at DESC
LIMIT 20;
```

Expected: all recent rows show `has_auth = true`.

### 5.6 Storage Object Audit

```sql
-- STAGING ONLY — READ ONLY
-- Check storage object paths to verify auth.uid() is used as first segment

SELECT
  name,
  bucket_id,
  owner,
  (storage.foldername(name))[1] AS first_path_segment,
  created_at
FROM storage.objects
WHERE bucket_id = 'user-photos'
ORDER BY created_at DESC
LIMIT 20;
```

Expected: `first_path_segment` matches a Supabase Auth user UUID (the session's
`auth.uid()`). If it matches a `users_profile.id` that is different from
`auth.uid()`, the storage policy will not work correctly.

---

## 6. No-Live-SQL Warning

**CRITICAL: None of the SQL in this document may be executed against the
production Supabase project (mira-mvp, ref vtaqyammimmgxlkqwjat) without:**

1. Prior execution and verification in a staging Supabase project.
2. Explicit human review of each SQL statement.
3. Confirmation that staging tests pass for all scenarios in
   MIRA_SUPABASE_SECURITY_TEST_MATRIX.md.
4. A rollback plan ready to execute (see MIRA_SUPABASE_ROLLBACK_PLAN.md).
5. A human present and monitoring during execution.

The read-only diagnostic queries in Section 5 may be run in the Supabase SQL
Editor as read-only queries only. Even read-only queries should not be run
in production during high-traffic periods.

**No automation, no agent, and no scheduled task may execute SQL mutations
against the Supabase project.** All schema changes and RLS changes are
human-executed operations.

---

## 7. Acceptance Criteria Before RLS

All of the following must be true before enabling RLS on any table in
production. Each item requires human verification.

### 7.1 Identity

- [ ] Anonymous Sign-Ins are enabled in Supabase Auth settings.
- [ ] A new onboarding submission in staging creates an auth.users row.
- [ ] The new users_profile row has `auth_user_id` matching the auth.users UUID.
- [ ] The Supabase client SDK sends a valid JWT on all subsequent requests.
- [ ] `auth.uid()` returns the expected UUID when queried in the SQL editor
      with the anon role.

### 7.2 Data Cleanliness

- [ ] `SELECT count(*) FROM users_profile WHERE auth_user_id IS NULL` = 0.
- [ ] `SELECT count(*) FROM user_assets WHERE user_profile_id IS NULL` = 0.
- [ ] `SELECT count(*) FROM generations WHERE user_profile_id IS NULL` = 0.
- [ ] Orphan user_assets query (Section 5.2) returns 0 rows.
- [ ] Orphan generations query (Section 5.3) returns 0 rows.

### 7.3 Storage Paths

- [ ] Scan page is writing to `user-photos/{auth.uid()}/...` paths.
- [ ] Storage object audit (Section 5.6) shows `first_path_segment` = `auth.uid()`.

### 7.4 Service Role

- [ ] `SUPABASE_SERVICE_ROLE_KEY` is set in server environment.
- [ ] `createServiceRoleServer()` is used in generation-store write paths.
- [ ] No service_role key appears in any `NEXT_PUBLIC_*` variable.
- [ ] No service_role key appears in any client-side bundle.

### 7.5 Staging Verification

- [ ] All tests in MIRA_SUPABASE_SECURITY_TEST_MATRIX.md pass in staging.
- [ ] Rollback tested in staging (disable RLS, verify all access restored).
- [ ] Full E2E mock flow passes after RLS is enabled in staging.

---

## Appendix: Data State Timeline

| Phase | users_profile.auth_user_id | user_assets.user_profile_id | generations.user_profile_id | RLS Status |
|---|---|---|---|---|
| Current (pre-auth) | NULL on all rows | Populated (profileId) or NULL | Populated (profileId) or NULL | Disabled |
| After code deploy | NULL on old rows; auth.uid() on new rows | Populated | Populated | Still disabled |
| After Anonymous Auth enabled + test data deleted | auth.uid() on all rows | FK to profile | FK to profile | Ready to enable |
| After RLS enabled | auth.uid() enforced by policy | FK enforced | FK enforced | Enabled |
| After NOT NULL added | auth.uid() required by schema | user_profile_id required | user_profile_id required | Enabled + hardened |
