# MIRA RLS & Storage Migration Draft

> **WARNING: DO NOT RUN THIS SQL LIVE.** This is a planning document only.
> All SQL in this document is DRAFT and must be reviewed, tested in staging,
> and explicitly approved before execution on the production Supabase project.

Created: 2026-04-29
Status: DRAFT — NOT APPROVED FOR EXECUTION

---

## 1. Current Blockers

Before this migration can proceed:

- [ ] Enable Anonymous Sign-Ins in Supabase Dashboard
- [ ] Confirm auth_user_id is populated for new profiles
- [ ] Set SUPABASE_SERVICE_ROLE_KEY in .env.local
- [ ] Enable CAPTCHA before public testing
- [ ] Set production Site URL and Redirect URLs
- [ ] Decide: auth_user_id direct column vs JOIN policy for user_assets/generations
- [ ] Decide: storage paths {profileId}/... vs {auth.uid()}/...
- [ ] Decide: existing data deletion vs migration
- [ ] Decide: generations bucket public vs private
- [ ] Decide: retention policy for user photos and generated outputs
- [ ] Test all changes in staging with disposable data FIRST

---

## 2. Required Manual Settings (Supabase Dashboard)

These cannot be done via SQL and must be done in the Supabase Dashboard:

1. **Authentication > Settings > Anonymous Sign-Ins**: Enable
2. **Authentication > Settings > Attack Protection**: Enable CAPTCHA (hCaptcha or Turnstile)
3. **Authentication > URL Configuration > Site URL**: Set to production domain
4. **Authentication > URL Configuration > Redirect URLs**: Add production + staging URLs
5. **Project Settings > API > Service Role Key**: Copy to .env.local as SUPABASE_SERVICE_ROLE_KEY
6. **Storage > Buckets > user-photos**: Add file_size_limit and allowed_mime_types
7. **Storage > Buckets > generations**: Add file_size_limit and allowed_mime_types
8. **Storage > Buckets > generations**: Decide public vs private

---

## 3. Proposed DB Migration Order

### Step 1: Ensure auth_user_id is populated

After enabling Anonymous Sign-Ins, verify that new onboarding submissions populate auth_user_id:

```sql
-- VERIFICATION ONLY — do not run as migration
SELECT id, auth_user_id, created_at
FROM users_profile
ORDER BY created_at DESC
LIMIT 10;
```

### Step 2: Decide what to do with existing NULL auth_user_id rows

**Option A: Delete all existing test data (RECOMMENDED for MVP)**
```sql
-- DRAFT — DO NOT RUN LIVE
DELETE FROM generations;
DELETE FROM user_assets;
DELETE FROM users_profile;
```

**Option B: Backfill with anonymous auth users**
- Create anonymous auth users via Supabase Admin API
- UPDATE each row's auth_user_id
- Complex and fragile — not recommended for MVP

**Recommendation: Option A.** Existing data is test data with no production value.

### Step 3: Decide auth_user_id strategy for user_assets and generations

**Option A: Direct column (RECOMMENDED)**
Add auth_user_id directly to user_assets and generations for simpler RLS policies.

```sql
-- DRAFT — DO NOT RUN LIVE
ALTER TABLE user_assets ADD COLUMN auth_user_id UUID REFERENCES auth.users(id);
ALTER TABLE generations ADD COLUMN auth_user_id UUID REFERENCES auth.users(id);
```

**Option B: JOIN-based policy**
RLS policies JOIN through users_profile to check ownership.
More complex but avoids schema changes to user_assets/generations.

```sql
-- DRAFT — DO NOT RUN LIVE
-- Example JOIN policy for user_assets:
CREATE POLICY "Users can access own assets" ON user_assets
  FOR ALL
  USING (
    user_profile_id IN (
      SELECT id FROM users_profile WHERE auth_user_id = auth.uid()
    )
  );
```

**Recommendation: Option A** for simplicity and performance.

### Step 4: Enable RLS on all tables

```sql
-- DRAFT — DO NOT RUN LIVE
ALTER TABLE users_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE users_profile FORCE ROW LEVEL SECURITY;

ALTER TABLE user_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_assets FORCE ROW LEVEL SECURITY;

ALTER TABLE generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE generations FORCE ROW LEVEL SECURITY;
```

### Step 5: Create RLS policies

```sql
-- DRAFT — DO NOT RUN LIVE

-- users_profile: owner can read/write own row
CREATE POLICY "Users can read own profile" ON users_profile
  FOR SELECT USING (auth_user_id = auth.uid());

CREATE POLICY "Users can insert own profile" ON users_profile
  FOR INSERT WITH CHECK (auth_user_id = auth.uid());

CREATE POLICY "Users can update own profile" ON users_profile
  FOR UPDATE USING (auth_user_id = auth.uid());

-- user_assets: owner can read/write own assets (direct column strategy)
CREATE POLICY "Users can read own assets" ON user_assets
  FOR SELECT USING (auth_user_id = auth.uid());

CREATE POLICY "Users can insert own assets" ON user_assets
  FOR INSERT WITH CHECK (auth_user_id = auth.uid());

-- generations: owner can read own generations; server writes via service_role
CREATE POLICY "Users can read own generations" ON generations
  FOR SELECT USING (auth_user_id = auth.uid());

-- Note: INSERT/UPDATE on generations is done server-side via service_role,
-- which bypasses RLS. No client-side INSERT policy needed.
```

---

## 4. Proposed Storage Migration Order

### Step 1: Add bucket constraints

```sql
-- DRAFT — DO NOT RUN LIVE (or use Dashboard)
UPDATE storage.buckets SET file_size_limit = 10485760 WHERE name = 'user-photos';  -- 10 MB
UPDATE storage.buckets SET allowed_mime_types = '{"image/jpeg","image/png","image/webp"}' WHERE name = 'user-photos';

UPDATE storage.buckets SET file_size_limit = 52428800 WHERE name = 'generations';  -- 50 MB
UPDATE storage.buckets SET allowed_mime_types = '{"image/jpeg","image/png","image/webp","video/mp4"}' WHERE name = 'generations';
```

### Step 2: Decide storage path strategy

**Current paths**: `{profileId}/{slot}-{timestamp}.{ext}`

**Option A: Keep profileId paths, use JOIN policy**
- No path changes needed.
- Storage policy JOINs through users_profile to verify ownership.

**Option B: Switch to auth.uid() paths (RECOMMENDED)**
- Paths become `{auth.uid()}/{slot}-{timestamp}.{ext}`.
- Simpler storage policies using `auth.uid() = (storage.foldername(name))[1]`.
- Requires updating scan/page.tsx upload code.

### Step 3: Add storage policies for user-photos

```sql
-- DRAFT — DO NOT RUN LIVE

-- user-photos: authenticated users can upload to their own folder
CREATE POLICY "Users can upload own photos" ON storage.objects
  FOR INSERT
  WITH CHECK (
    bucket_id = 'user-photos'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

-- user-photos: users can read their own photos
CREATE POLICY "Users can read own photos" ON storage.objects
  FOR SELECT
  USING (
    bucket_id = 'user-photos'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );
```

### Step 4: Decide generations bucket visibility

**If generations stays public:** No storage policy needed for reads. Server writes via service_role.

**If generations becomes private:**
```sql
-- DRAFT — DO NOT RUN LIVE
UPDATE storage.buckets SET public = false WHERE name = 'generations';

CREATE POLICY "Users can read own generations" ON storage.objects
  FOR SELECT
  USING (
    bucket_id = 'generations'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );
```

### Step 5: product-images stays public (intentional)

No changes needed. Product images are catalog content, not user data.

---

## 5. Rollback Plan

If migration causes issues:

```sql
-- EMERGENCY ROLLBACK — DO NOT RUN UNLESS NEEDED
-- Disable RLS (all data becomes accessible again)
ALTER TABLE users_profile DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_assets DISABLE ROW LEVEL SECURITY;
ALTER TABLE generations DISABLE ROW LEVEL SECURITY;

-- Drop policies
DROP POLICY IF EXISTS "Users can read own profile" ON users_profile;
DROP POLICY IF EXISTS "Users can insert own profile" ON users_profile;
DROP POLICY IF EXISTS "Users can update own profile" ON users_profile;
DROP POLICY IF EXISTS "Users can read own assets" ON user_assets;
DROP POLICY IF EXISTS "Users can insert own assets" ON user_assets;
DROP POLICY IF EXISTS "Users can read own generations" ON generations;

-- Drop storage policies
DROP POLICY IF EXISTS "Users can upload own photos" ON storage.objects;
DROP POLICY IF EXISTS "Users can read own photos" ON storage.objects;
DROP POLICY IF EXISTS "Users can read own generations" ON storage.objects;
```

---

## 6. Staging/Test Plan

1. **Create a test branch** in Supabase (if on Pro plan) or use a separate project.
2. Enable Anonymous Sign-Ins.
3. Create a test profile via onboarding.
4. Verify auth_user_id is populated.
5. Apply RLS policies.
6. Test: can the user read their own profile? (YES expected)
7. Test: can the user read another user's profile? (NO expected)
8. Test: can the user upload to user-photos? (YES expected)
9. Test: can the user read their own photos? (YES expected)
10. Test: try-on generation works with service_role? (YES expected)
11. Test: user can see their own generation result? (YES expected)
12. Test: user cannot see another user's generation? (YES expected if private)
13. Test: rollback works cleanly? (YES expected)

---

## 7. Code Changes Required

After migration, update these files:

- `app/[locale]/(app)/scan/page.tsx`: Use auth.uid() in storage paths instead of profileId.
- `app/api/tryon/jobs/route.ts`: Write auth_user_id to generations (if direct column strategy).
- `lib/generation-store.ts`: Include auth_user_id in createGeneration.
- `lib/tryon-flow.ts`: Ensure Supabase queries work with RLS (they use anon client, so RLS applies automatically).

---

## 8. Timeline Estimate

This migration should NOT be rushed. Suggested order:

1. **Human decisions**: Answer all questions in HUMAN_QUESTIONS.md.
2. **Enable Anonymous Sign-Ins**: 5 minutes (Dashboard setting).
3. **Verify auth_user_id population**: Test with one onboarding flow.
4. **Delete test data**: If Option A chosen.
5. **Apply RLS in staging**: 30 minutes.
6. **Test with Flow QA**: Run full flow with Playwright.
7. **Apply to production**: Only after staging verification.

---

## 9. Candidate Migration v0.1 — DO NOT RUN

> **DOCUMENTATION ONLY.** Every SQL block below is a draft for review.
> Do NOT execute any of this SQL until human approval and staging test.

### 9.1 Pre-migration diagnostics (safe SELECT queries)

```sql
-- Count rows with NULL auth_user_id (safe to run as read-only)
SELECT 'users_profile' AS tbl, COUNT(*) AS total,
       COUNT(*) FILTER (WHERE auth_user_id IS NULL) AS null_auth
FROM users_profile;

SELECT 'user_assets' AS tbl, COUNT(*) AS total FROM user_assets;
SELECT 'generations' AS tbl, COUNT(*) AS total FROM generations;

-- Identify orphan user_assets (no matching profile)
SELECT ua.id, ua.user_profile_id
FROM user_assets ua
LEFT JOIN users_profile up ON ua.user_profile_id = up.id
WHERE up.id IS NULL;

-- Identify orphan generations (no matching profile)
SELECT g.id, g.user_profile_id
FROM generations g
LEFT JOIN users_profile up ON g.user_profile_id = up.id
WHERE up.id IS NULL;
```

### 9.2 Option: Delete all test data (recommended for MVP fresh start)

```sql
-- DRAFT — DO NOT RUN LIVE
-- Delete in dependency order
DELETE FROM generations;
DELETE FROM user_assets;
DELETE FROM users_profile;

-- Also clean storage objects if needed (do via Dashboard or CLI)
```

### 9.3 Add auth_user_id columns (if direct-column strategy chosen)

```sql
-- DRAFT — DO NOT RUN LIVE
ALTER TABLE user_assets ADD COLUMN IF NOT EXISTS auth_user_id UUID REFERENCES auth.users(id);
ALTER TABLE generations ADD COLUMN IF NOT EXISTS auth_user_id UUID REFERENCES auth.users(id);
```

### 9.4 Enable RLS

```sql
-- DRAFT — DO NOT RUN LIVE
-- Only after auth_user_id is verified populated on new rows

ALTER TABLE users_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE users_profile FORCE ROW LEVEL SECURITY;

ALTER TABLE user_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_assets FORCE ROW LEVEL SECURITY;

ALTER TABLE generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE generations FORCE ROW LEVEL SECURITY;
```

### 9.5 Policy drafts: users_profile

```sql
-- DRAFT — DO NOT RUN LIVE
CREATE POLICY "users_own_profile_select" ON users_profile
  FOR SELECT USING (auth_user_id = auth.uid());

CREATE POLICY "users_own_profile_insert" ON users_profile
  FOR INSERT WITH CHECK (auth_user_id = auth.uid());

CREATE POLICY "users_own_profile_update" ON users_profile
  FOR UPDATE USING (auth_user_id = auth.uid())
  WITH CHECK (auth_user_id = auth.uid());

-- No DELETE policy: users cannot delete their own profile via client
```

### 9.6 Policy drafts: user_assets (direct auth_user_id column)

```sql
-- DRAFT — DO NOT RUN LIVE
CREATE POLICY "users_own_assets_select" ON user_assets
  FOR SELECT USING (auth_user_id = auth.uid());

CREATE POLICY "users_own_assets_insert" ON user_assets
  FOR INSERT WITH CHECK (auth_user_id = auth.uid());

-- No UPDATE/DELETE: assets are immutable from client perspective
```

### 9.7 Policy drafts: generations (direct auth_user_id column)

```sql
-- DRAFT — DO NOT RUN LIVE
-- Users can read their own generations
CREATE POLICY "users_own_generations_select" ON generations
  FOR SELECT USING (auth_user_id = auth.uid());

-- INSERT/UPDATE done server-side via service_role (bypasses RLS)
-- No client-side INSERT policy needed
```

### 9.8 Storage policy draft: user-photos

```sql
-- DRAFT — DO NOT RUN LIVE
-- Assumes storage paths will use {auth.uid()}/... format

CREATE POLICY "users_upload_own_photos" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'user-photos'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

CREATE POLICY "users_read_own_photos" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'user-photos'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

CREATE POLICY "users_delete_own_photos" ON storage.objects
  FOR DELETE USING (
    bucket_id = 'user-photos'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );
```

### 9.9 Rollback

```sql
-- EMERGENCY ROLLBACK — only if migration causes issues
ALTER TABLE users_profile DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_assets DISABLE ROW LEVEL SECURITY;
ALTER TABLE generations DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "users_own_profile_select" ON users_profile;
DROP POLICY IF EXISTS "users_own_profile_insert" ON users_profile;
DROP POLICY IF EXISTS "users_own_profile_update" ON users_profile;
DROP POLICY IF EXISTS "users_own_assets_select" ON user_assets;
DROP POLICY IF EXISTS "users_own_assets_insert" ON user_assets;
DROP POLICY IF EXISTS "users_own_generations_select" ON generations;
DROP POLICY IF EXISTS "users_upload_own_photos" ON storage.objects;
DROP POLICY IF EXISTS "users_read_own_photos" ON storage.objects;
DROP POLICY IF EXISTS "users_delete_own_photos" ON storage.objects;
```

### 9.10 Staging test plan

1. Use a disposable Supabase branch or separate project.
2. Enable Anonymous Sign-Ins.
3. Run onboarding to create a profile with auth_user_id.
4. Apply RLS + policies.
5. Verify: user can read own profile (YES).
6. Verify: user cannot read other user's profile (NO rows returned).
7. Verify: user can upload to user-photos (YES).
8. Verify: try-on generation works via service_role (YES).
9. Verify: user can see own generation result (YES).
10. Verify: rollback works (disable RLS, all data accessible again).
11. Run `mira_full_e2e_mock_flow` to confirm Flow QA still passes.
