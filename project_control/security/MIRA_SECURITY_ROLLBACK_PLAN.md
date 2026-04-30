# MIRA Security Rollback Plan

> How to safely revert RLS, storage policies, and schema changes.
> Keep this document updated as policies are applied.
> Last updated: 2026-04-29

---

## Rollback Priority

If anything goes wrong after enabling security:
1. **Disable RLS first** (restores open access, stops lockouts).
2. **Drop problematic policies** (targeted fix if only one table is broken).
3. **Revert storage policies** (if uploads/downloads fail).
4. **Revert schema changes** (only if columns cause errors).

---

## Phase B Rollback: RLS

### Disable RLS on all tables (emergency)

```sql
-- EMERGENCY ROLLBACK: Disables RLS on all customer tables
-- Run only if users are locked out of their data

ALTER TABLE users_profile DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_assets DISABLE ROW LEVEL SECURITY;
ALTER TABLE generations DISABLE ROW LEVEL SECURITY;
ALTER TABLE events DISABLE ROW LEVEL SECURITY;
```

### Drop specific policies

```sql
-- Drop all policies on users_profile
DROP POLICY IF EXISTS users_profile_select_own ON users_profile;
DROP POLICY IF EXISTS users_profile_insert_own ON users_profile;
DROP POLICY IF EXISTS users_profile_update_own ON users_profile;
DROP POLICY IF EXISTS users_profile_delete_own ON users_profile;

-- Drop all policies on user_assets
DROP POLICY IF EXISTS user_assets_select_own ON user_assets;
DROP POLICY IF EXISTS user_assets_insert_own ON user_assets;
DROP POLICY IF EXISTS user_assets_update_own ON user_assets;
DROP POLICY IF EXISTS user_assets_delete_own ON user_assets;

-- Drop all policies on generations
DROP POLICY IF EXISTS generations_select_own ON generations;
DROP POLICY IF EXISTS generations_delete_own ON generations;

-- Drop all policies on events
DROP POLICY IF EXISTS events_select_own ON events;
DROP POLICY IF EXISTS events_insert_own ON events;
```

---

## Phase C Rollback: Storage Policies

```sql
-- Drop all storage policies
DROP POLICY IF EXISTS user_photos_select_own ON storage.objects;
DROP POLICY IF EXISTS user_photos_insert_own ON storage.objects;
DROP POLICY IF EXISTS user_photos_update_own ON storage.objects;
DROP POLICY IF EXISTS user_photos_delete_own ON storage.objects;

DROP POLICY IF EXISTS generations_select_own ON storage.objects;
DROP POLICY IF EXISTS generations_delete_own ON storage.objects;

DROP POLICY IF EXISTS product_images_public_read ON storage.objects;
```

### Revert generations bucket to public
- Dashboard > Storage > generations > Settings > Toggle to Public

---

## Phase A Rollback: Schema Changes

```sql
-- Only if the new columns cause issues
ALTER TABLE user_assets DROP COLUMN IF EXISTS auth_user_id;
ALTER TABLE generations DROP COLUMN IF EXISTS auth_user_id;
```

**Warning**: Dropping columns is destructive. Only do this if the columns are causing application errors. Leaving unused columns is safer.

---

## Verification After Rollback

1. Check all tables accessible: `SELECT count(*) FROM users_profile;`
2. Check storage uploads work: Upload test file to each bucket.
3. Check API routes work: Hit `/api/tryon/status/[id]` with known generation.
4. Check onboarding flow: Create new profile.
5. Run mock E2E: `python -B project_autopilot/flow_qa.py --project mira --validate-mock-e2e`

---

## Communication

If rollback is triggered during beta:
1. Note the time and symptom in `project_control/BLOCKERS.md`.
2. Identify which policy/change caused the issue.
3. Fix the specific policy rather than disabling everything.
4. Re-test with the security test plan before re-enabling.

---

## Rollback Decision Matrix

| Symptom | Action |
|---|---|
| All users locked out | Disable RLS on all tables |
| One table inaccessible | Drop policies on that table only |
| Uploads fail | Drop storage policies, check bucket setting |
| Server writes fail | Check service_role key is set, check RLS bypass |
| Performance degradation | Check policy subqueries, consider adding auth_user_id denorm |
| Single user locked out | Check auth_user_id is populated on their rows |
