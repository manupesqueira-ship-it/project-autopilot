# MIRA Supabase Security Validation Queries

**Status**: DRAFT — READ-ONLY QUERIES FOR HUMAN USE
**Created**: 2026-04-30
**Author**: MIRA Project Autopilot (review-only agent)
**Target project**: mira-mvp (ref vtaqyammimmgxlkqwjat, AWS us-west-2)

---

## Purpose

This document contains read-only SQL queries that a human can run in the
Supabase Dashboard SQL Editor (or psql) to verify the security state of
the database before and after applying RLS policies.

**These queries make NO changes. They only read system catalog tables.**

All queries are labeled READ-ONLY and are safe to run at any time.

---

## Section 1: Null Ownership Column Checks

These queries check whether ownership columns are populated.
RLS policies will fail to match rows where these are NULL.

### 1A. Count users_profile rows with NULL auth_user_id

```sql
-- READ-ONLY — Safe to run
-- Expected BEFORE enabling RLS: all rows will have NULL auth_user_id
-- Expected AFTER Anonymous Auth is enabled and app is used: 0 rows should have NULL auth_user_id for new rows

SELECT
  COUNT(*) AS total_rows,
  COUNT(*) FILTER (WHERE auth_user_id IS NULL) AS null_auth_user_id,
  COUNT(*) FILTER (WHERE auth_user_id IS NOT NULL) AS has_auth_user_id,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE auth_user_id IS NOT NULL) / NULLIF(COUNT(*), 0),
    1
  ) AS pct_owned
FROM users_profile;
```

Expected result before RLS is safe to enable:
- `null_auth_user_id` = 0 (or confirmed to be only deleted test rows)

---

### 1B. Count user_assets rows with NULL user_profile_id

```sql
-- READ-ONLY — Safe to run
-- user_profile_id is the link to ownership chain.
-- NULL user_profile_id means RLS join policies cannot match these rows.

SELECT
  COUNT(*) AS total_rows,
  COUNT(*) FILTER (WHERE user_profile_id IS NULL) AS null_user_profile_id,
  COUNT(*) FILTER (WHERE user_profile_id IS NOT NULL) AS has_user_profile_id
FROM user_assets;
```

---

### 1C. Count generations rows with NULL user_profile_id

```sql
-- READ-ONLY — Safe to run

SELECT
  COUNT(*) AS total_rows,
  COUNT(*) FILTER (WHERE user_profile_id IS NULL) AS null_user_profile_id,
  COUNT(*) FILTER (WHERE user_profile_id IS NOT NULL) AS has_user_profile_id
FROM generations;
```

---

### 1D. Summary of all ownership gaps

```sql
-- READ-ONLY — Safe to run
-- Single query showing all ownership gaps across all three tables.

SELECT 'users_profile' AS table_name,
       COUNT(*) AS total,
       COUNT(*) FILTER (WHERE auth_user_id IS NULL) AS null_owner
FROM users_profile

UNION ALL

SELECT 'user_assets',
       COUNT(*),
       COUNT(*) FILTER (WHERE user_profile_id IS NULL)
FROM user_assets

UNION ALL

SELECT 'generations',
       COUNT(*),
       COUNT(*) FILTER (WHERE user_profile_id IS NULL)
FROM generations;
```

---

## Section 2: Orphan Row Checks

Orphan rows are rows whose FK reference points to a non-existent parent.
These cannot be matched by any join-based RLS policy.

### 2A. Orphan user_assets (no matching users_profile row)

```sql
-- READ-ONLY — Safe to run
-- Returns user_assets rows that reference a user_profile_id that does not exist in users_profile.

SELECT ua.id, ua.user_profile_id, ua.created_at
FROM user_assets ua
LEFT JOIN users_profile up ON ua.user_profile_id = up.id
WHERE up.id IS NULL
ORDER BY ua.created_at DESC;
```

Expected result before RLS is safe to enable: 0 rows (no orphans).

---

### 2B. Orphan generations (no matching users_profile row)

```sql
-- READ-ONLY — Safe to run

SELECT g.id, g.user_profile_id, g.status, g.created_at
FROM generations g
LEFT JOIN users_profile up ON g.user_profile_id = up.id
WHERE up.id IS NULL
ORDER BY g.created_at DESC;
```

---

### 2C. users_profile rows with no matching auth.users entry

```sql
-- READ-ONLY — Safe to run
-- Identifies profiles where auth_user_id is set but there is no corresponding
-- row in auth.users (broken FK reference).

SELECT up.id, up.auth_user_id, up.created_at
FROM users_profile up
LEFT JOIN auth.users au ON up.auth_user_id = au.id
WHERE up.auth_user_id IS NOT NULL
  AND au.id IS NULL
ORDER BY up.created_at DESC;
```

Expected result: 0 rows. Any row here indicates a data integrity problem.

---

## Section 3: Grant / Privilege Checks

These queries inspect what privileges the `anon` and `authenticated` roles
currently hold on the target tables.

### 3A. Current table-level privileges for anon and authenticated

```sql
-- READ-ONLY — Safe to run

SELECT
  grantee,
  table_name,
  privilege_type,
  is_grantable
FROM information_schema.role_table_grants
WHERE table_schema = 'public'
  AND table_name IN ('users_profile', 'user_assets', 'generations')
  AND grantee IN ('anon', 'authenticated')
ORDER BY table_name, grantee, privilege_type;
```

Expected result AFTER dangerous grants revoked:
- No rows with privilege_type in ('TRUNCATE', 'TRIGGER', 'REFERENCES') for anon/authenticated.
- SELECT, INSERT, UPDATE, DELETE should remain.

---

### 3B. Verify service_role retains all privileges

```sql
-- READ-ONLY — Safe to run
-- service_role should never lose privileges (it bypasses RLS by design).

SELECT
  grantee,
  table_name,
  privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'public'
  AND table_name IN ('users_profile', 'user_assets', 'generations')
  AND grantee = 'service_role'
ORDER BY table_name, privilege_type;
```

---

## Section 4: RLS State Checks

### 4A. Current RLS enabled/disabled state for all target tables

```sql
-- READ-ONLY — Safe to run

SELECT
  schemaname,
  tablename,
  rowsecurity AS rls_enabled,
  forcerowsecurity AS force_rls
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('users_profile', 'user_assets', 'generations')
ORDER BY tablename;
```

Expected result BEFORE migration:
- rls_enabled = false for all three tables.

Expected result AFTER migration:
- rls_enabled = true for all three tables.
- force_rls = true if FORCE ROW LEVEL SECURITY was applied.

---

### 4B. Comprehensive RLS check including all public tables

```sql
-- READ-ONLY — Safe to run
-- Shows RLS state for ALL tables in the public schema.

SELECT
  tablename,
  rowsecurity AS rls_enabled,
  forcerowsecurity AS force_rls
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```

---

## Section 5: Policy Count Checks

### 5A. Count of active RLS policies per table

```sql
-- READ-ONLY — Safe to run

SELECT
  schemaname,
  tablename,
  COUNT(*) AS policy_count
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('users_profile', 'user_assets', 'generations')
GROUP BY schemaname, tablename
ORDER BY tablename;
```

Expected result BEFORE migration: 0 policies on all three tables.
Expected result AFTER migration: at least 3 policies on users_profile, 3 on user_assets, 1 on generations.

---

### 5B. List all active RLS policies with detail

```sql
-- READ-ONLY — Safe to run

SELECT
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('users_profile', 'user_assets', 'generations')
ORDER BY tablename, policyname;
```

---

### 5C. List storage.objects policies

```sql
-- READ-ONLY — Safe to run

SELECT
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE schemaname = 'storage'
  AND tablename = 'objects'
ORDER BY policyname;
```

Expected result BEFORE migration: 0 storage policies.
Expected result AFTER migration: at least 3 policies for user-photos bucket.

---

## Section 6: Storage Bucket Configuration Checks

### 6A. Current bucket configuration

```sql
-- READ-ONLY — Safe to run

SELECT
  id,
  name,
  public,
  file_size_limit,
  allowed_mime_types,
  created_at,
  updated_at
FROM storage.buckets
ORDER BY name;
```

Expected result BEFORE migration:
- user-photos: public=false, file_size_limit=NULL, allowed_mime_types=NULL, 0 policies
- generations: public=true, file_size_limit=NULL, allowed_mime_types=NULL, 0 policies
- product-images: public=true, file_size_limit=NULL, allowed_mime_types=NULL, 0 policies

Expected result AFTER migration:
- user-photos: file_size_limit=10485760, allowed_mime_types set, 3 policies
- generations: file_size_limit=52428800, allowed_mime_types set
- product-images: file_size_limit=10485760, allowed_mime_types set

---

### 6B. Check if storage.objects has RLS enabled

```sql
-- READ-ONLY — Safe to run
-- Supabase enables RLS on storage.objects by default.
-- This query verifies it is still enabled.

SELECT
  schemaname,
  tablename,
  rowsecurity AS rls_enabled
FROM pg_tables
WHERE schemaname = 'storage'
  AND tablename = 'objects';
```

Expected result: rls_enabled = true (always, should never be disabled).

---

## Section 7: Storage Object Count by Bucket

### 7A. Count objects in each bucket

```sql
-- READ-ONLY — Safe to run
-- Useful for understanding data volume before any cleanup.

SELECT
  bucket_id,
  COUNT(*) AS object_count,
  SUM(metadata->>'size')::bigint AS total_bytes
FROM storage.objects
GROUP BY bucket_id
ORDER BY bucket_id;
```

---

### 7B. List user-photos objects (for path convention verification)

```sql
-- READ-ONLY — Safe to run
-- Shows the first 50 objects in user-photos to verify path convention.
-- Do NOT share this output outside secure environments (paths contain profile IDs).

SELECT
  name,
  bucket_id,
  owner,
  created_at,
  metadata->>'size' AS size_bytes,
  metadata->>'mimetype' AS mime_type
FROM storage.objects
WHERE bucket_id = 'user-photos'
ORDER BY created_at DESC
LIMIT 50;
```

---

## Section 8: Auth State Checks

### 8A. Count auth.users rows

```sql
-- READ-ONLY — Safe to run
-- Shows total auth users and breakdown by type.
-- Anonymous users have is_anonymous = true.

SELECT
  COUNT(*) AS total_auth_users,
  COUNT(*) FILTER (WHERE is_anonymous = true) AS anonymous_users,
  COUNT(*) FILTER (WHERE is_anonymous = false OR is_anonymous IS NULL) AS identified_users,
  COUNT(*) FILTER (WHERE last_sign_in_at > NOW() - INTERVAL '7 days') AS active_last_7_days
FROM auth.users;
```

---

### 8B. Verify Anonymous Sign-Ins are enabled

```sql
-- READ-ONLY — Safe to run
-- Checks the auth configuration for anonymous sign-in setting.
-- Note: This may not be accessible in all Supabase configurations.
-- Alternative: verify in Supabase Dashboard > Authentication > Settings.

SELECT
  config_key,
  config_value
FROM auth.config
WHERE config_key ILIKE '%anonymous%';
```

Note: If `auth.config` is not accessible, verify Anonymous Sign-Ins via Dashboard only.

---

## Section 9: Pre-Migration Baseline Snapshot

Run this combined query to capture a snapshot of the current state for comparison.

```sql
-- READ-ONLY — Safe to run
-- Pre-migration baseline snapshot.
-- Save the output before making any changes.

SELECT 'rls_state' AS category, tablename AS item, rowsecurity::text AS value
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('users_profile', 'user_assets', 'generations')

UNION ALL

SELECT 'policy_count', tablename, COUNT(*)::text
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('users_profile', 'user_assets', 'generations')
GROUP BY tablename

UNION ALL

SELECT 'null_auth_user_id', 'users_profile',
       COUNT(*) FILTER (WHERE auth_user_id IS NULL)::text
FROM users_profile

UNION ALL

SELECT 'null_user_profile_id', 'user_assets',
       COUNT(*) FILTER (WHERE user_profile_id IS NULL)::text
FROM user_assets

UNION ALL

SELECT 'null_user_profile_id', 'generations',
       COUNT(*) FILTER (WHERE user_profile_id IS NULL)::text
FROM generations

UNION ALL

SELECT 'bucket_policies', 'storage.objects',
       COUNT(*)::text
FROM pg_policies
WHERE schemaname = 'storage' AND tablename = 'objects'

ORDER BY category, item;
```

---

## Section 10: Post-Migration Verification Queries

Run these after applying RLS and policies to confirm the migration succeeded.

### 10A. Confirm RLS is enabled on all target tables

```sql
-- READ-ONLY

SELECT tablename, rowsecurity, forcerowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('users_profile', 'user_assets', 'generations')
ORDER BY tablename;
-- Expected: rowsecurity = true for all three
```

### 10B. Confirm expected policy count

```sql
-- READ-ONLY

SELECT tablename, COUNT(*) AS policy_count
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('users_profile', 'user_assets', 'generations')
GROUP BY tablename
ORDER BY tablename;
-- Expected: users_profile >= 3, user_assets >= 2, generations >= 1
```

### 10C. Confirm dangerous grants revoked

```sql
-- READ-ONLY

SELECT grantee, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'public'
  AND table_name IN ('users_profile', 'user_assets', 'generations')
  AND grantee IN ('anon', 'authenticated')
  AND privilege_type IN ('TRUNCATE', 'TRIGGER', 'REFERENCES')
ORDER BY table_name, grantee;
-- Expected: 0 rows (all dangerous grants revoked)
```

### 10D. Confirm storage policies are in place

```sql
-- READ-ONLY

SELECT policyname, cmd
FROM pg_policies
WHERE schemaname = 'storage'
  AND tablename = 'objects'
ORDER BY policyname;
-- Expected: at least INSERT, SELECT, DELETE policies for user-photos
```

---

*End of MIRA_SUPABASE_SECURITY_VALIDATION_QUERIES_DRAFT.md*
*All queries in this document are read-only. None make changes to the database.*
*Safe to run in the Supabase Dashboard SQL Editor or psql at any time.*
