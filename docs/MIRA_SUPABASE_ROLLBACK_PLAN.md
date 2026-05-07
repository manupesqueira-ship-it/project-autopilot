# MIRA Supabase RLS Rollback Plan

> **WARNING: DO NOT EXECUTE ANY SQL IN THIS DOCUMENT.**
> Emergency rollback SQL is provided as a reference only.
> It must only be executed by a human, manually, in the Supabase SQL editor,
> in response to a confirmed production incident. No automation may trigger
> a rollback without explicit human authorization.

Created: 2026-04-30
Project: mira-mvp (ref vtaqyammimmgxlkqwjat)
Status: REFERENCE ONLY — NO EXECUTION

---

## 1. What Can Go Wrong

The following failure modes are possible when enabling RLS, storage policies,
or anonymous auth in a production Supabase project.

### 1.1 Table-Level Failures

| Failure | Trigger | Impact |
|---|---|---|
| RLS enabled but no policies created | Enable RLS before policy creation | All client access denied; app breaks completely |
| Policy expression error | Bug in USING/WITH CHECK clause | Policies silently allow or deny wrong rows |
| auth.uid() returns NULL | Anonymous auth not enabled when RLS applied | All RLS policies match nothing; all writes rejected |
| NULL auth_user_id rows locked out | RLS enabled before backfill | Existing rows become inaccessible |
| service_role key not set | Env var missing; generation writes use anon client | generation INSERT fails under RLS; try-on breaks |
| FORCE ROW LEVEL SECURITY misapplied | Applied while server uses postgres role for writes | Server-side writes blocked if they use postgres owner |
| Dangerous privilege revocation causes breaks | REVOKE too broad | App functionality breaks in unexpected places |

### 1.2 Storage-Level Failures

| Failure | Trigger | Impact |
|---|---|---|
| Storage policy wrong path expression | `foldername` logic error | All uploads rejected or all objects accessible |
| Path convention mismatch | App uploads to profileId path, policy expects auth.uid() path | Uploads succeed but user cannot read back their own photos |
| Bucket made private before signed URL code deployed | Timing error | All photo reads break immediately |
| MIME restriction blocks valid uploads | allowed_mime_types too narrow | User cannot upload photos |
| File size limit too small | file_size_limit set below typical phone camera output | User upload rejected with opaque error |

### 1.3 Auth-Level Failures

| Failure | Trigger | Impact |
|---|---|---|
| Anonymous sign-ins enabled but app does not call signInAnonymously() | Timing mismatch between Supabase setting and app code | auth.uid() = NULL; all RLS policies fail |
| Anonymous session not persisted across page reload | SDK configuration error | User loses auth session on navigation; all RLS queries fail |
| CAPTCHA blocks legitimate users | CAPTCHA too aggressive | Real users cannot create anonymous sessions |
| Site URL / Redirect URL not updated | Dashboard config not updated | Email flows and OAuth redirects fail |

### 1.4 Cascading Failures

If any of the above failures occur in production:

1. Onboarding breaks → users cannot create profiles → no data enters the system.
2. Scan breaks → users cannot upload photos → no assets recorded.
3. Try-on breaks → profile/asset reads fail → job cannot start.
4. Result polling breaks → status API returns empty or 404.
5. Multiple failures at once make debugging harder; root cause is unclear.

---

## 2. How to Detect Broken Auth

### 2.1 Symptoms

- Onboarding page: form submit hangs or returns an error.
- Browser console: `{"code": "PGRST301", "message": "...", "details": ""}` or
  similar Supabase RLS rejection errors.
- Network tab: Supabase API calls return HTTP 403 or empty arrays.
- localStorage: `mira_profile_id` is set but profile cannot be read back.

### 2.2 Diagnostic Steps

1. Open browser DevTools > Network tab.
2. Complete onboarding and observe the Supabase REST API request for the
   profile INSERT.
3. Check the response status and body.
4. In the Supabase Dashboard > Authentication > Users, check if a new
   anonymous user was created on the onboarding submission.
5. In the Supabase SQL Editor, run:
   ```sql
   -- STAGING DIAGNOSTIC ONLY
   SELECT id, auth_user_id, created_at
   FROM users_profile
   ORDER BY created_at DESC
   LIMIT 5;
   ```
6. If `auth_user_id` is NULL on the new row: anonymous auth is not working
   or the onboarding code is not calling `getOrCreateAnonymousUser()`.
7. If the row does not appear at all: the INSERT was rejected (RLS blocking it).

### 2.3 Log Evidence to Collect

Before triggering a rollback, collect:

- Browser network log showing the failed Supabase request (URL, status code,
  response body). Redact any JWTs or auth tokens.
- Supabase Dashboard > Logs > API logs filtered to the relevant time window.
- Exact error message returned by the Supabase client SDK.
- Screenshot of the Supabase Auth > Users list (no personal data visible).

---

## 3. How to Detect Broken Uploads

### 3.1 Symptoms

- Scan page: photo upload progress bar hangs or shows error.
- Browser console: storage error from Supabase SDK.
- Network tab: `POST /storage/v1/object/user-photos/...` returns 400, 403,
  or 413 (file too large).
- `user_assets` table has no new row after scan completion.

### 3.2 Diagnostic Steps

1. Attempt a photo upload in the test environment.
2. Check the browser network tab for the storage upload request.
3. Inspect the response body for the storage error code.
4. In Supabase Dashboard > Logs > Storage, check the upload attempt.
5. Verify the upload path: `first_path_segment` should match `auth.uid()`.
6. Run the storage audit query from MIRA_SUPABASE_BACKFILL_AND_OWNERSHIP_PLAN.md
   Section 5.6 to check actual path format.
7. In the Supabase SQL Editor (anon role), test the policy manually:
   ```sql
   -- STAGING DIAGNOSTIC ONLY — use anon role switch
   SELECT auth.uid();
   -- Should return a non-NULL UUID for an authenticated anonymous session
   ```

### 3.3 Common Causes

- `auth.uid()` is NULL → anonymous auth is not active.
- Upload path uses profileId instead of auth.uid() → policy rejects it.
- MIME type not in whitelist → 400 error from bucket constraints.
- File size exceeds limit → 413 error from bucket constraints.
- Storage policy has wrong `bucket_id` check → policy not matching.

---

## 4. How to Detect Broken Result Polling

### 4.1 Symptoms

- Result page: shows loading state indefinitely.
- Network tab: `GET /api/tryon/status/{id}` returns `{ status: "not_found" }`
  or 404.
- The generation row exists in the database but is not returned.

### 4.2 Diagnostic Steps

1. Note the `generationId` from the result page URL.
2. In Supabase Dashboard > Table Editor > generations, manually search for
   the row by ID.
3. If the row exists but the API returns not_found:
   - Check if `user_profile_id` is NULL (orphan row).
   - Check if the status API is using anon client (RLS applies) vs service_role
     (RLS bypassed).
   - Verify the generation row's `user_profile_id` links to a profile with
     the correct `auth_user_id`.
4. If the row does not exist: the INSERT failed (check generate job logs).
5. Check the API route code: `lib/generation-store.ts` `getGeneration()` should
   use service_role to bypass RLS for the status check path.

### 4.3 Expected Behavior After RLS

With RLS enabled and service_role used for status reads:
- Status API reads via service_role, bypasses RLS, returns the row regardless
  of auth state.
- If the API uses anon client with RLS, only the row owner can read it. If the
  session is not established or the ownership chain is broken, the row appears
  missing.

---

## 5. Rollback Philosophy

### 5.1 Core Principle

**Rollback is always safer than extended debugging in production.**

If any of the following occurs, rollback immediately and debug in staging:

- Two or more of the failure modes in Section 1 occur simultaneously.
- User-facing flows are broken for more than 15 minutes.
- Root cause is not identified within 30 minutes.
- An unexpected error type appears that is not covered in this plan.

### 5.2 Rollback Scope

Rollback does not delete data. It only removes access control layers, restoring
the pre-RLS state where all client access is allowed (which is the current
state of the production project). No user data is lost by rolling back.

### 5.3 Post-Rollback State

After rollback:
- All tables are accessible to anon/authenticated roles without restriction.
- This is the current production state (not a regression).
- The app continues to function in its pre-RLS degraded-but-functional mode.
- No real customer data is at risk (no real customers yet).

### 5.4 Rollback Is Not Failure

A rollback means the migration must be re-planned and re-tested in staging.
It does not mean the migration approach is wrong. It means a step was missed
or the staging test did not cover the failure scenario. Update the staging test
matrix (MIRA_SUPABASE_SECURITY_TEST_MATRIX.md) and retry.

---

## 6. Emergency Disable Plan — Human Only

**CRITICAL: Only a human may execute these steps. No agent, automation, or
scheduled task may trigger a rollback. The following SQL must be run manually
in the Supabase SQL Editor by an authorized team member.**

### 6.1 Emergency Rollback — Tables

```sql
-- EMERGENCY ROLLBACK — EXECUTE ONLY IN PRODUCTION INCIDENT
-- Run as postgres (superuser) role in Supabase SQL editor

-- Step 1: Disable RLS on all tables
ALTER TABLE users_profile DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_assets DISABLE ROW LEVEL SECURITY;
ALTER TABLE generations DISABLE ROW LEVEL SECURITY;

-- Step 2: Drop all table policies
DROP POLICY IF EXISTS "users_profile_select_own" ON users_profile;
DROP POLICY IF EXISTS "users_profile_insert_own" ON users_profile;
DROP POLICY IF EXISTS "users_profile_update_own" ON users_profile;
DROP POLICY IF EXISTS "users_profile_delete_own" ON users_profile;

DROP POLICY IF EXISTS "user_assets_select_own" ON user_assets;
DROP POLICY IF EXISTS "user_assets_insert_own" ON user_assets;
DROP POLICY IF EXISTS "user_assets_delete_own" ON user_assets;

DROP POLICY IF EXISTS "generations_select_own" ON generations;
```

### 6.2 Emergency Rollback — Storage

```sql
-- EMERGENCY ROLLBACK — STORAGE — EXECUTE ONLY IN PRODUCTION INCIDENT

DROP POLICY IF EXISTS "user_photos_insert_own" ON storage.objects;
DROP POLICY IF EXISTS "user_photos_select_own" ON storage.objects;
DROP POLICY IF EXISTS "user_photos_delete_own" ON storage.objects;
DROP POLICY IF EXISTS "generations_select_own" ON storage.objects;
```

### 6.3 Emergency Rollback — Restore Grants (if revoked)

```sql
-- EMERGENCY ROLLBACK — GRANT RESTORE — EXECUTE ONLY IF PRIVILEGES WERE REVOKED

-- Restore dangerous grants removed as part of the migration
GRANT TRUNCATE, TRIGGER, REFERENCES ON users_profile TO anon, authenticated;
GRANT TRUNCATE, TRIGGER, REFERENCES ON user_assets TO anon, authenticated;
GRANT TRUNCATE, TRIGGER, REFERENCES ON generations TO anon, authenticated;

-- Note: These grants restore the PRE-MIGRATION state, which is itself unsafe.
-- This is only done to restore app functionality in an emergency.
-- Re-plan the migration before attempting again.
```

### 6.4 Post-Rollback Verification

After running the emergency rollback SQL:

1. Clear browser localStorage.
2. Reload the MIRA app.
3. Complete onboarding and verify a profile is created.
4. Complete scan and verify photo upload works.
5. Initiate a try-on and verify generation reaches a result.
6. Confirm the app behaves as it did before the migration attempt.

If the app is still broken after rollback, the issue is not RLS-related. Check:
- Server environment variables (service_role key may have caused issues).
- Next.js server restart may be needed to pick up env changes.
- Supabase Auth settings (Anonymous Sign-Ins change may persist).

### 6.5 Anonymous Auth Rollback

Anonymous Sign-Ins cannot be "rolled back" in the sense that existing
anonymous auth.users rows do not disappear when the setting is turned off.
Disabling Anonymous Sign-Ins in the Supabase Dashboard prevents new anonymous
sessions from being created but does not invalidate existing sessions.

If Anonymous Sign-Ins must be disabled after being enabled:
1. Toggle off in Supabase Dashboard > Authentication > Settings > Anonymous
   Sign-Ins.
2. Existing anonymous sessions will expire naturally (1-hour access token;
   refresh tokens may extend this but new anon sessions are blocked).
3. The onboarding code will gracefully degrade (auth_user_id set to NULL on
   new profile inserts, app continues to function without auth).

---

## 7. Logs and Evidence Required

Before, during, and after any migration or rollback, the following evidence
must be captured by the human operator:

### 7.1 Before Migration

- [ ] Screenshot of Supabase Dashboard > Table Editor showing current RLS
      status for each table (disabled, 0 policies).
- [ ] Screenshot of Supabase Dashboard > Storage > Policies showing 0 storage
      policies.
- [ ] Result of null ownership summary query (Section 5.1 of backfill plan):
      all null counts must be 0.
- [ ] Confirmation that staging tests pass (test matrix reference).

### 7.2 During Migration

- [ ] Record the timestamp of each SQL statement executed.
- [ ] Capture success/failure response for each statement.
- [ ] Note any unexpected errors immediately.
- [ ] Do not proceed to the next step if the current step produced an error.

### 7.3 After Migration

- [ ] Screenshot of updated RLS status (enabled, policies visible).
- [ ] Result of post-migration functional test (onboarding → scan → try-on → result).
- [ ] Browser network log showing RLS-protected Supabase requests succeed.
- [ ] Confirmation that cross-user read is denied (second browser session
      cannot read first user's profile).

### 7.4 After Rollback (if applicable)

- [ ] Timestamp of rollback execution.
- [ ] Screenshot confirming RLS is disabled again.
- [ ] Record of what went wrong and why.
- [ ] Updated task in TASK_QUEUE.md or HUMAN_QUESTIONS.md for re-planning.

### 7.5 What Not to Log

Per MIRA data policy (MIRA_PRIVACY_LOGGING_GUARDRAILS.md and MIRA_DATA_MAP.md):

- Do NOT log JWTs, refresh tokens, or service_role keys.
- Do NOT log real user names, emails, measurements, or photos.
- Do NOT screenshot table contents with real customer data visible.
- Do NOT paste Supabase secret keys into any log, chat, or issue tracker.
- Redact any auth tokens from network logs before sharing.

---

## Appendix: Rollback Decision Tree

```
Is the app broken after RLS migration?
  |
  YES
  |
  ├── Is it one broken flow or all flows?
  |       ONE FLOW: Targeted debug — check that table's policies
  |       ALL FLOWS: Likely auth.uid() = NULL → rollback immediately
  |
  ├── Has it been broken > 15 minutes?
  |       YES: Rollback. Debug in staging.
  |       NO: Investigate root cause first.
  |
  ├── Is root cause identified?
  |       YES and fixable in < 10 min: Apply targeted fix then verify
  |       NO or fix is complex: Rollback. Debug in staging.
  |
  └── After rollback: Is app restored?
          YES: Document failure, update staging tests, re-plan migration.
          NO: Issue is not RLS-related. Check env vars, server restart, Supabase status.
```
