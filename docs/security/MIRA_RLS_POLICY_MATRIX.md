# MIRA RLS Policy Matrix

> Draft policy definitions for all customer-facing tables.
> DO NOT APPLY until staging-tested. See rollback plan.
> Last updated: 2026-04-29

---

## Policy Notation

- `auth.uid()` = Supabase Auth user ID of the requesting client
- `service_role` = server-side key that bypasses RLS
- All server writes (createGeneration, updateGeneration) use `service_role`

---

## users_profile

| Operation | Policy Name | Rule | Notes |
|---|---|---|---|
| SELECT | users_profile_select_own | `auth.uid() = auth_user_id` | User can only read their own profile |
| INSERT | users_profile_insert_own | `auth.uid() = auth_user_id` | User can only create a profile linked to themselves |
| UPDATE | users_profile_update_own | `auth.uid() = auth_user_id` | User can only modify their own profile |
| DELETE | users_profile_delete_own | `auth.uid() = auth_user_id` | User can only delete their own profile |

**Service role**: Server writes bypass RLS. Used by onboarding to set `auth_user_id`.

---

## user_assets

| Operation | Policy Name | Rule | Notes |
|---|---|---|---|
| SELECT | user_assets_select_own | `auth_user_id = auth.uid()` (after denorm) OR `user_profile_id IN (SELECT id FROM users_profile WHERE auth_user_id = auth.uid())` | Owner-only reads |
| INSERT | user_assets_insert_own | Same ownership check | Owner-only inserts |
| UPDATE | user_assets_update_own | Same ownership check | Owner-only updates (e.g., quality_status) |
| DELETE | user_assets_delete_own | Same ownership check | Owner-only deletes |

**Recommendation**: Add `auth_user_id` column to avoid subquery in every policy.

---

## generations

| Operation | Policy Name | Rule | Notes |
|---|---|---|---|
| SELECT | generations_select_own | `auth_user_id = auth.uid()` (after denorm) OR `user_profile_id IN (SELECT id FROM users_profile WHERE auth_user_id = auth.uid())` | Owner-only reads |
| INSERT | N/A — server only | Server uses `service_role` | Clients never insert directly |
| UPDATE | N/A — server only | Server uses `service_role` | Status updates are server-side |
| DELETE | generations_delete_own | Same ownership check as SELECT | Future: allow user to delete their generations |

**Note**: The status endpoint (`/api/tryon/status/[generationId]`) currently uses `createServer()` (anon client). Once RLS is enabled, this will naturally enforce ownership IF the auth context is passed through correctly. However, a server-side ownership check is still recommended as defense-in-depth.

---

## events

| Operation | Policy Name | Rule | Notes |
|---|---|---|---|
| SELECT | events_select_own | `user_profile_id IN (SELECT id FROM users_profile WHERE auth_user_id = auth.uid())` | User can read their own analytics |
| INSERT | events_insert_own | Same ownership check | Client-side event tracking |
| UPDATE | N/A | No client updates | Events are append-only |
| DELETE | N/A | No client deletes | Events are permanent |

---

## sellers / products

| Table | Policy | Notes |
|---|---|---|
| sellers | Public SELECT for active sellers | `status = 'active'` |
| products | Public SELECT for active products | `status = 'active'` |
| INSERT/UPDATE/DELETE | service_role only | Admin operations only |

---

## Policy Dependency Chain

```
1. auth_user_id column exists on users_profile ✓ (already present)
2. auth_user_id column added to user_assets (migration needed)
3. auth_user_id column added to generations (migration needed)
4. Backfill auth_user_id from users_profile JOIN
5. Enable RLS on all tables
6. Apply policies
7. Verify service_role bypass works
8. Test anon client respects policies
```

## Risk: NULL auth_user_id

Existing rows have `auth_user_id = NULL`. After RLS enable:
- These rows become **invisible** to all clients (no policy matches NULL).
- Server (`service_role`) can still access them.
- **Action**: Backfill or accept that pre-auth rows are orphaned from client view.
