# MIRA Supabase Security Test Matrix

> This matrix defines the complete set of security and functional tests that
> must pass in a Supabase STAGING project before any RLS or storage policy
> changes are applied to the production project (mira-mvp).
>
> Tests are manual (browser + Supabase Dashboard) or automated (Playwright/Flow QA).
> Each test must be recorded with a pass/fail result and the date of execution.
>
> DO NOT use this matrix in production until all tests pass in staging.

Created: 2026-04-30
Project: mira-mvp (ref vtaqyammimmgxlkqwjat) — staging only
Status: TEST DEFINITIONS — NOT YET EXECUTED

---

## Test Environment Requirements

Before running tests:

- [ ] Supabase staging project created (separate from mira-mvp production).
- [ ] Staging project has all schema objects: users_profile, user_assets,
      generations, storage buckets (user-photos, generations, product-images).
- [ ] Anonymous Sign-Ins enabled in staging Supabase Auth settings.
- [ ] CAPTCHA disabled in staging (to allow automated test flows).
- [ ] App configured to point to staging Supabase URL and anon key.
- [ ] `SUPABASE_SERVICE_ROLE_KEY` set to staging project service_role key.
- [ ] RLS and all policies applied to staging project only.
- [ ] Storage policies applied to staging project only.
- [ ] All data in staging tables is synthetic/test data only.
- [ ] Two separate browser sessions available (Browser A = User 1, Browser B = User 2).

---

## Section A: Database Row-Level Security Tests

### A1. User Can Read Own Profile

**Test ID**: A1
**Priority**: P0 Critical
**Mechanism under test**: `users_profile` RLS SELECT policy
**Policy**: `users_profile_select_own` — `USING (auth_user_id = auth.uid())`

**Steps:**
1. Open Browser A.
2. Complete onboarding → profile created with `auth_user_id` = User 1's `auth.uid()`.
3. Note the `mira_profile_id` from localStorage.
4. Navigate to a page that reads the profile (try-on page or any profile display).
5. Verify the profile is returned successfully.

**Expected result**: User 1's profile row is returned. No error.

**Failure mode**: Empty result set or RLS policy error → auth_user_id not
populated or RLS policy expression is wrong.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### A2. User Cannot Read Another User's Profile

**Test ID**: A2
**Priority**: P0 Critical
**Mechanism under test**: `users_profile` RLS SELECT policy — isolation

**Steps:**
1. Open Browser A → complete onboarding → note User 1's profile UUID.
2. Open Browser B → complete onboarding → now User 2 has a different auth.uid().
3. In Browser B, attempt to directly query User 1's profile using a direct
   Supabase client call with User 1's profile UUID.
   (Simulate via: `supabase.from('users_profile').select().eq('id', user1ProfileId)`)
4. Observe the result.

**Expected result**: Empty array `[]`. No rows returned. No error thrown
(RLS returns empty, not 403 — this is Supabase's default behaviour).

**Failure mode**: User 1's profile row is returned in Browser B's session →
RLS policy is missing or not evaluating `auth.uid()` correctly.

**Alternative test via SQL editor:**
```sql
-- Run as anon role in staging SQL editor (simulate User 2's session)
-- First set auth context to User 2's JWT, then query User 1's UUID
SELECT * FROM users_profile WHERE id = '<user1-profile-uuid>';
-- Expected: 0 rows
```

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### A3. User Can Upload Own Photo (Storage INSERT)

**Test ID**: A3
**Priority**: P0 Critical
**Mechanism under test**: `user_photos_insert_own` storage policy

**Steps:**
1. Browser A: complete onboarding (User 1 authenticated).
2. Navigate to scan page.
3. Select a test photo (safe synthetic image, <10 MB, image/jpeg or image/png).
4. Submit the scan form.
5. Verify the upload completes successfully (no error shown).
6. In Supabase Dashboard > Storage > user-photos, verify the object exists
   at path `{user1-auth-uid}/{slot}-{timestamp}.{ext}`.
7. Verify a `user_assets` row was created with `user_profile_id` = User 1's profile ID.

**Expected result**: Upload succeeds. Object stored under User 1's auth.uid() path.
user_assets row created.

**Failure mode**: Upload rejected (403 or storage error) → storage policy wrong
or auth.uid() path not being used by scan page.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### A4. User Cannot Read Another User's Photo

**Test ID**: A4
**Priority**: P0 Critical
**Mechanism under test**: `user_photos_select_own` storage policy

**Steps:**
1. Browser A: complete scan → photo uploaded to `user-photos/{user1-uid}/front-...jpg`.
2. Note the full storage path.
3. Browser B (User 2, different auth.uid()): attempt to read User 1's photo.
   Method 1: Attempt `supabase.storage.from('user-photos').download(user1PhotoPath)`.
   Method 2: Construct the storage URL and attempt a direct HTTP fetch with
             User 2's Bearer token.

**Expected result**: Download fails with a storage policy rejection. The bucket
is private, so direct public URL access also fails. Signed URL for User 1's
photo is not accessible with User 2's JWT.

**Failure mode**: User 1's photo is returned to User 2's session → storage
policy is missing or path expression is wrong.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### A5. Result Polling Requires Ownership

**Test ID**: A5
**Priority**: P0 Critical
**Mechanism under test**: `generations` RLS SELECT policy and/or status API
ownership check

**Steps:**
1. Browser A (User 1): complete try-on flow → generation created → note
   the `generationId` from the result page URL.
2. Browser B (User 2): navigate directly to `/result/{user1-generationId}`.
3. Observe whether User 2 can see User 1's result.

**Expected result**: User 2 sees "not found" or an error state for User 1's
generation. User 2 cannot view User 1's try-on result.

**Note on implementation**: This test's expected behavior depends on whether
the status API (`/api/tryon/status/[id]`) uses service_role or anon client
to read generations. If service_role is used, the API must add its own
ownership check (validate the request's auth.uid() matches the generation's
owner's auth.uid() via the profile join). If anon client is used, RLS
handles the isolation automatically.

**Failure mode**: User 2 sees User 1's try-on result → either RLS policy is
missing or the API route does not check ownership.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### A6. Anonymous User Cannot TRUNCATE Arbitrary Tables

**Test ID**: A6
**Priority**: P0 Critical
**Mechanism under test**: REVOKE TRUNCATE grant + RLS as defence-in-depth

**Steps:**
1. Using the Supabase anon key directly (no browser session), attempt to
   truncate the users_profile table:
   ```sql
   -- Attempt via raw Supabase REST API or SQL editor with anon role
   TRUNCATE users_profile;
   ```
2. Observe the result.

**Expected result**: TRUNCATE is rejected. Error: permission denied for table
`users_profile` (TRUNCATE privilege has been revoked from anon and authenticated).

**Prerequisite**: The REVOKE statement must have been applied before this test:
```sql
-- DRAFT — applied to staging only
REVOKE TRUNCATE ON users_profile FROM anon, authenticated;
REVOKE TRUNCATE ON user_assets FROM anon, authenticated;
REVOKE TRUNCATE ON generations FROM anon, authenticated;
```

**Failure mode**: TRUNCATE succeeds → REVOKE was not applied or RLS alone
does not block TRUNCATE (which it doesn't — TRUNCATE bypasses RLS in Postgres).
REVOKE is mandatory, not optional.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### A7. Anonymous User Cannot DELETE Arbitrary Rows

**Test ID**: A7
**Priority**: P0 Critical
**Mechanism under test**: `users_profile` RLS DELETE policy

**Steps:**
1. Browser A (User 1): complete onboarding → profile created.
2. Browser B (User 2): using User 2's auth session, attempt to delete User 1's
   profile row:
   ```javascript
   supabase.from('users_profile').delete().eq('id', user1ProfileId)
   ```
3. Verify the operation's result.
4. Confirm User 1's profile still exists by re-fetching it in Browser A.

**Expected result**: DELETE returns success but 0 rows affected (RLS silently
filters out the row — User 2 has no DELETE policy matching User 1's row).
User 1's profile still exists.

**Also test**: Unauthenticated anon DELETE (no session, raw anon key):
```javascript
// No signInAnonymously() called first
supabase.from('users_profile').delete().eq('id', user1ProfileId)
```
**Expected**: 0 rows deleted. RLS policy on DELETE uses `auth_user_id = auth.uid()`;
with auth.uid() = NULL (no session), no rows match.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### A8. service_role Is Only Used Server-Side

**Test ID**: A8
**Priority**: P0 Critical
**Mechanism under test**: Environment variable hygiene and code review

**Steps:**
1. Build the Next.js application in production mode: `npm run build`.
2. Search the built client bundle for the service_role key pattern:
   ```bash
   grep -r "service_role" .next/static/ 2>/dev/null | head -20
   grep -r "SUPABASE_SERVICE_ROLE" .next/static/ 2>/dev/null | head -20
   ```
3. Verify `SUPABASE_SERVICE_ROLE_KEY` is NOT in any `NEXT_PUBLIC_*` env var:
   ```bash
   grep -r "NEXT_PUBLIC_SUPABASE_SERVICE_ROLE" . --include="*.env*" 2>/dev/null
   grep -r "NEXT_PUBLIC_SUPABASE_SERVICE_ROLE" . --include="*.ts" 2>/dev/null
   grep -r "NEXT_PUBLIC_SUPABASE_SERVICE_ROLE" . --include="*.tsx" 2>/dev/null
   ```
4. Verify `createServiceRoleServer()` is only called from `app/api/**` files
   and `lib/generation-store.ts`.

**Expected result**: 
- No service_role key or pattern in client bundles.
- No `NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY` variable anywhere.
- `createServiceRoleServer()` not imported in any client component.

**Failure mode**: service_role key found in client bundle → CRITICAL security
incident. Rotate key immediately. Audit what was exposed.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

## Section B: Storage Security Tests

### B1. Signed URLs Expire

**Test ID**: B1
**Priority**: P1 High
**Mechanism under test**: Supabase signed URL TTL enforcement

**Steps:**
1. Generate a signed URL for a file in `user-photos` with a 10-second TTL
   (use a short TTL only for testing):
   ```typescript
   // In a server context (API route or script)
   const { data } = await supabaseServiceRole.storage
     .from('user-photos')
     .createSignedUrl(testFilePath, 10); // 10-second TTL
   ```
2. Immediately fetch the signed URL → should succeed (HTTP 200).
3. Wait 15 seconds.
4. Fetch the signed URL again → should fail (HTTP 400 or 403 with expiry error).

**Expected result**: First fetch succeeds; second fetch (after expiry) fails.

**Failure mode**: Second fetch succeeds after TTL → signed URL expiry is not
enforced. This is a Supabase infrastructure issue; escalate to Supabase support.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### B2. Invalid MIME Type Blocked

**Test ID**: B2
**Priority**: P1 High
**Mechanism under test**: `allowed_mime_types` bucket constraint

**Steps:**
1. Browser A (User 1 authenticated).
2. Attempt to upload a `.pdf` file to the `user-photos` bucket:
   ```javascript
   const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
   await supabase.storage.from('user-photos').upload(
     `${authUid}/test.pdf`, file
   );
   ```
3. Observe the result.

**Also test with**:
- `text/html` (potential XSS vector if served with wrong Content-Type)
- `application/javascript`
- `image/svg+xml` (can contain script tags)

**Expected result**: Upload rejected with a storage error. The file is not stored.

**Failure mode**: Upload accepted → `allowed_mime_types` not set or set incorrectly.
Apply the bucket constraint update from the storage policy plan.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### B3. Oversized Files Blocked

**Test ID**: B3
**Priority**: P1 High
**Mechanism under test**: `file_size_limit` bucket constraint

**Steps:**
1. Browser A (User 1 authenticated).
2. Attempt to upload a file larger than 10 MB (e.g., 11 MB synthetic binary)
   to `user-photos`.
3. Observe the result.

**Note**: Creating an 11 MB test file can be done with:
```javascript
const bigFile = new File([new ArrayBuffer(11 * 1024 * 1024)], 'big.jpg', { type: 'image/jpeg' });
```

**Expected result**: Upload rejected. HTTP 413 or Supabase error indicating
file size limit exceeded. The file is not stored.

**Failure mode**: Upload accepted → `file_size_limit` not set. Apply the bucket
constraint update.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### B4. User Cannot Upload to Another User's Storage Folder

**Test ID**: B4
**Priority**: P0 Critical
**Mechanism under test**: `user_photos_insert_own` storage policy

**Steps:**
1. Browser A (User 1): note User 1's `auth.uid()`.
2. Browser B (User 2): attempt to upload a file to User 1's folder:
   ```javascript
   await supabase.storage.from('user-photos').upload(
     `${user1AuthUid}/attack-photo.jpg`,
     testImageFile
   );
   ```
3. Observe the result.

**Expected result**: Upload rejected. Policy `(storage.foldername(name))[1] = auth.uid()::text`
rejects the upload because User 2's `auth.uid()` does not match User 1's folder.

**Failure mode**: Upload succeeds → storage policy is missing or path expression
is wrong. User 2 can overwrite or inject files into User 1's folder.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

## Section C: Full Flow Regression Tests

### C1. Full E2E Mock Flow Passes After RLS Enabled

**Test ID**: C1
**Priority**: P0 Critical
**Mechanism under test**: End-to-end flow with RLS active in staging

**Steps:**
1. With RLS enabled in staging, run the `mira_full_e2e_mock_flow` Flow QA test:
   ```bash
   python -B project_autopilot/flow_qa.py --project mira --flow mira_full_e2e_mock_flow
   ```
2. The mock flow must complete all steps without error.

**Expected result**: All flow steps pass. Mock generation result displayed.

**Failure mode**: Any step fails → RLS is blocking a required operation.
Debug which table/policy is causing the failure.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### C2. Onboarding Creates Profile With auth_user_id Populated

**Test ID**: C2
**Priority**: P0 Critical
**Mechanism under test**: Anonymous auth integration in onboarding page

**Steps:**
1. Clear browser localStorage to start with a fresh session.
2. Open the app at `/` and navigate to onboarding.
3. Complete onboarding with test data.
4. In Supabase Dashboard > Table Editor > users_profile, find the new row.
5. Verify `auth_user_id` is non-NULL and matches the user's anonymous auth UUID
   visible in Supabase Dashboard > Authentication > Users.

**Expected result**: New profile row has `auth_user_id` set to the anonymous
user's UUID.

**Failure mode**: `auth_user_id` is NULL → `getOrCreateAnonymousUser()` failed
or is not called, or Anonymous Sign-Ins are not enabled.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### C3. Try-On Generation Succeeds With Service Role

**Test ID**: C3
**Priority**: P0 Critical
**Mechanism under test**: `createGeneration()` server-side write via service_role

**Steps:**
1. User 1 (Browser A): complete onboarding and scan.
2. Navigate to a product page and initiate a try-on.
3. Observe the result page.
4. In Supabase Dashboard > Table Editor > generations, verify a new row was
   created with `user_profile_id` set and `status` not NULL.

**Expected result**: Generation row created. Result page shows generation status.
No "permission denied" error in server logs.

**Failure mode**: Generation row not created → service_role client not configured
or INSERT rejected. Check server logs for Supabase error codes.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### C4. Rollback Restores Full Functionality

**Test ID**: C4
**Priority**: P0 Critical
**Mechanism under test**: Emergency rollback SQL (MIRA_SUPABASE_ROLLBACK_PLAN.md Section 6)

**Steps:**
1. With RLS enabled in staging and all prior tests passing:
2. Execute the emergency rollback SQL (tables + storage) in the staging SQL editor.
3. Clear browser localStorage.
4. Reload the app and complete the full flow: onboarding → scan → try-on → result.
5. Verify all steps complete successfully.
6. Verify data is intact (no rows were deleted by rollback).

**Expected result**: Full app flow works after rollback. Data is preserved.
RLS status shows disabled (verified in Dashboard > Table Editor > RLS column).

**Failure mode**: App still broken after rollback → issue is not RLS-related.
Investigate environment variables or Supabase Auth settings.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

## Section D: Negative Tests — Escalating Attacks

### D1. Unauthenticated Client Cannot Read Any Table

**Test ID**: D1
**Priority**: P0 Critical
**Mechanism under test**: RLS with NULL auth.uid()

**Steps:**
1. Using the Supabase anon key directly (no anonymous sign-in, no JWT):
   ```javascript
   const { createClient } = require('@supabase/supabase-js');
   const supabase = createClient(stagingUrl, stagingAnonKey);
   // No signInAnonymously() called
   const { data } = await supabase.from('users_profile').select('*');
   console.log(data);
   ```
2. Observe the result.

**Expected result**: Empty array `[]`. RLS policies require `auth_user_id = auth.uid()`
and `auth.uid()` is NULL without a session, so no rows match.

**Failure mode**: Rows returned → RLS is not enabled or anon SELECT grant
was not revoked and RLS fallback allows reads.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### D2. Unauthenticated Client Cannot INSERT Any Row

**Test ID**: D2
**Priority**: P0 Critical
**Mechanism under test**: RLS INSERT policy WITH CHECK with NULL auth.uid()

**Steps:**
1. Using the Supabase anon key with no session:
   ```javascript
   const { error } = await supabase.from('users_profile').insert({
     name: 'Attack User',
     email: 'attack@example.com',
     auth_user_id: null
   });
   console.log(error);
   ```
2. Observe the result.

**Expected result**: INSERT fails. Error message indicates RLS rejection.
WITH CHECK clause fails because `auth.uid()` is NULL and `null = null` is NULL/FALSE.

**Failure mode**: INSERT succeeds → RLS INSERT policy is missing or allows
NULL auth_user_id.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

### D3. Authenticated User Cannot Access Admin Functions

**Test ID**: D3
**Priority**: P1 High
**Mechanism under test**: Role boundaries — anon/authenticated vs service_role

**Steps:**
1. Browser A (User 1, authenticated anonymous session).
2. Attempt to call `service_role`-protected operations via the anon client:
   - Try to DELETE a row owned by another user (covered by A7).
   - Try to call any admin-only PostgreSQL functions (if any exist).
   - Try to read `auth.users` directly:
     ```javascript
     const { data } = await supabase.from('auth.users').select('*');
     ```

**Expected result**:
- Read of `auth.users` fails — the `auth` schema is not accessible via REST.
- DELETE of another user's row: 0 rows affected (covered by A7).
- No admin functions are callable.

**Failure mode**: `auth.users` is accessible → Supabase should block this by
default; verify no custom RLS or API override was introduced.

| Run date | Tester | Result | Notes |
|---|---|---|---|
| | | PENDING | |

---

## Test Execution Checklist

### Pre-Execution Sign-Off

- [ ] All tests reviewed by a human team member before execution.
- [ ] Staging environment configured and isolated from production.
- [ ] Service_role key for staging is different from production service_role key.
- [ ] All test data is synthetic (no real customer data in staging).
- [ ] Rollback plan (MIRA_SUPABASE_ROLLBACK_PLAN.md) reviewed and ready.

### Pass/Fail Summary

| Test ID | Description | Priority | Status |
|---|---|---|---|
| A1 | User can read own profile | P0 | PENDING |
| A2 | User cannot read another user's profile | P0 | PENDING |
| A3 | User can upload own photo | P0 | PENDING |
| A4 | User cannot read another user's photo | P0 | PENDING |
| A5 | Result polling requires ownership | P0 | PENDING |
| A6 | anon cannot TRUNCATE tables | P0 | PENDING |
| A7 | anon cannot DELETE arbitrary rows | P0 | PENDING |
| A8 | service_role only used server-side | P0 | PENDING |
| B1 | Signed URLs expire | P1 | PENDING |
| B2 | Invalid MIME type blocked | P1 | PENDING |
| B3 | Oversized files blocked | P1 | PENDING |
| B4 | User cannot upload to another user's folder | P0 | PENDING |
| C1 | Full E2E mock flow passes after RLS | P0 | PENDING |
| C2 | Onboarding creates profile with auth_user_id | P0 | PENDING |
| C3 | Try-on generation succeeds with service_role | P0 | PENDING |
| C4 | Rollback restores full functionality | P0 | PENDING |
| D1 | Unauthenticated client cannot read any table | P0 | PENDING |
| D2 | Unauthenticated client cannot INSERT any row | P0 | PENDING |
| D3 | Authenticated user cannot access admin functions | P1 | PENDING |

### Gate: All P0 Tests Must Pass

**No production RLS migration may proceed until all P0 tests pass in staging.**
P1 tests must also pass, but may be retested after targeted fixes if they fail
in isolation without indicating a systemic policy problem.

### Sign-Off

Production migration may proceed when:

- [ ] All 19 tests above show "PASS" in the staging environment.
- [ ] A human team member has signed off on the results.
- [ ] The rollback plan has been tested (C4).
- [ ] No outstanding questions in `project_control/HUMAN_QUESTIONS.md` block the migration.
- [ ] A human is present and monitoring during production migration.
