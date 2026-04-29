# MIRA Supabase Security Alignment Plan v1

Created: 2026-04-29
Status: ACTIVE
Sprint type: Planning/audit only — no live database mutations

---

## A. Executive Summary

**Verdict: BLOCKED_FOR_REAL_CUSTOMER_DATA**

MIRA's Supabase project (mira-mvp, ref vtaqyammimmgxlkqwjat) has a P0 security gap. All three customer-facing tables (`users_profile`, `user_assets`, `generations`) have Row Level Security disabled, zero policies, and the `anon` role has all 7 Postgres privileges (SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER) on every table.

This means anyone who obtains the public anon key — which is embedded in the frontend JavaScript bundle — can read, modify, delete, or truncate all customer data. This includes personal profile data, body measurements, uploaded photos, and generated try-on outputs.

Storage is inconsistent: `user-photos` is marked private but has zero policies so authenticated/anon clients cannot read or write; the `generations` and `product-images` buckets are public with no size or MIME restrictions.

**MIRA must not store real customer photos, personal data, or body measurements until RLS, policies, and an identity model are in place.** The current state is acceptable only for internal testing with synthetic/test data.

---

## B. Latest Manual Supabase Audit Findings

Audit date: 2026-04-29
Mode: SELECT-only, 0 mutations

### Tables

| Table | RLS | force_rls | Policies | anon privileges | authenticated privileges |
|---|---|---|---|---|---|
| users_profile | disabled | false | 0 | ALL 7 | ALL 7 |
| user_assets | disabled | false | 0 | ALL 7 | ALL 7 |
| generations | disabled | false | 0 | ALL 7 | ALL 7 |

### Storage Buckets

| Bucket | Public | Policies | file_size_limit | allowed_mime_types |
|---|---|---|---|---|
| generations | true | 0 | none | none |
| product-images | true | 0 | none | none |
| user-photos | false | 0 | none | none |

### Other

- 0 triggers on target tables
- 0 public functions
- 0 public views
- No SECURITY DEFINER functions discovered
- storage.objects has RLS enabled (Supabase default) with 0 policies

---

## C. Current Code Data Flow

### C1. Onboarding — Profile Creation

| Aspect | Detail |
|---|---|
| Files | `app/[locale]/(app)/onboarding/page.tsx` |
| Client type | Browser client (anon key via `lib/supabase/client.ts`) |
| Table | `users_profile` |
| Operation | INSERT: name, email, height_cm, weight_kg, usual_size, build, gender |
| Identity | None. Supabase generates `id` (uuid). No `auth_user_id` set. |
| localStorage | Sets `mira_profile_id` = returned profile UUID |
| Service role | No |
| Risk | **HIGH** — client-side INSERT with anon key. Anyone can create profiles. No auth. Identity stored only in localStorage. |

### C2. Scan — Photo Upload

| Aspect | Detail |
|---|---|
| Files | `app/[locale]/(app)/scan/page.tsx` |
| Client type | Browser client (anon key) |
| Bucket | `user-photos` (private) |
| Table | `user_assets` |
| Storage operation | `storage.from("user-photos").upload(file)` with path `{profileId}/{slot}-{timestamp}.{ext}` |
| DB operation | INSERT: user_profile_id, asset_type (front_photo/side_photo/back_photo), storage_path |
| Identity | `profileId` from localStorage `mira_profile_id` |
| Service role | No |
| Risk | **HIGH** — uploads use anon key to a private bucket. Currently likely fails silently because `user-photos` has RLS on `storage.objects` with 0 policies. If upload somehow succeeds, path is predictable: knowing a profileId exposes other users' photos. |

### C3. Try-On Job Creation

| Aspect | Detail |
|---|---|
| Files | `app/[locale]/(app)/tryon/[productId]/page.tsx`, `lib/tryon-flow.ts`, `app/api/tryon/jobs/route.ts`, `lib/generation-store.ts` |
| Client type | Browser reads via anon client; job creation via API route with server client (anon key, not service_role) |
| Tables | `users_profile` (SELECT), `user_assets` (SELECT), `generations` (INSERT + UPDATE) |
| Read operation | `tryon-flow.ts`: SELECT users_profile by id, SELECT user_assets by user_profile_id |
| Write operation | `generation-store.ts`: INSERT into generations with user_profile_id, status. UPDATE status/paths during processing. |
| Identity | `profileId` from localStorage; passed in POST body; server uses it as-is without validation |
| Service role | **No** — server.ts uses anon key |
| localStorage fallback | If DB load fails, falls back to legacy `mira_profile`, `mira_photos` localStorage keys |
| Risk | **HIGH** — API route accepts any profileId from client. No ownership validation. Server writes to `generations` with anon-level Supabase client. Generation IDs are UUIDs but predictable if enumerated. |

### C4. Result Polling

| Aspect | Detail |
|---|---|
| Files | `app/[locale]/(app)/result/[generationId]/page.tsx`, `app/api/tryon/status/[generationId]/route.ts`, `lib/generation-store.ts` |
| Client type | API route with server client (anon key) |
| Table | `generations` (SELECT) |
| Operation | SELECT by generation id |
| Identity | generationId from URL path — no user ownership check |
| Service role | No |
| Risk | **MEDIUM** — anyone with a generation UUID can poll its status and see output URLs. No auth check. |

### C5. Product Image Display

| Aspect | Detail |
|---|---|
| Files | `lib/data/products.ts`, catalog page |
| Bucket | `product-images` (public) |
| Operation | Public URLs used directly; no Supabase query |
| Risk | **LOW** — product images are intentionally public. No customer data involved. |

### C6. Generation Output Display

| Aspect | Detail |
|---|---|
| Files | Result page, generation-store |
| Bucket | `generations` (public) |
| Operation | Output URLs stored in `generations.image_output_path` / `video_output_path`; accessed via public URLs |
| Risk | **MEDIUM** — generation outputs (try-on images/videos of users) are in a public bucket. Anyone with the URL can view. These may contain user likeness. |

---

## D. Source-of-Truth Assessment

| Question | Answer |
|---|---|
| Current source of truth for user identity | localStorage `mira_profile_id` (a Supabase-generated UUID, not an auth token) |
| Is localStorage used as identity? | **Yes** — it is the sole identity mechanism |
| Is Supabase Auth used? | **No** — no sign-in, no auth.users rows, no JWT |
| Is auth_user_id populated? | **No** — onboarding INSERT does not set auth_user_id |
| Can auth.uid() be used now? | **No** — no auth session exists |
| Can current rows be mapped to users? | **No** — there is no authenticated identity to map to. Rows are linked by profile UUID stored in localStorage only. |
| Is anonymous auth needed? | **Yes** — to establish auth.uid() without requiring login, Supabase Anonymous Auth is the simplest path |

---

## E. RLS Feasibility

### users_profile

| Aspect | Detail |
|---|---|
| Feasible owner column | `auth_user_id` (uuid, nullable) |
| Policy pattern | `auth.uid() = auth_user_id` |
| Blockers | Column is nullable. No rows have auth_user_id populated. No FK constraint to auth.users. Must backfill or migrate. |
| INSERT policy | Allow insert where `auth_user_id = auth.uid()` — requires app to set auth_user_id on create |

### user_assets

| Aspect | Detail |
|---|---|
| Feasible owner path | `user_profile_id` -> `users_profile.id` -> `auth_user_id` -> `auth.uid()` |
| Policy pattern | `EXISTS (SELECT 1 FROM users_profile WHERE id = user_assets.user_profile_id AND auth_user_id = auth.uid())` |
| Blockers | user_profile_id is nullable. Requires join-based policy (slower). No direct auth_user_id column. |
| Alternative | Add `auth_user_id` column directly to user_assets for simpler/faster policy |

### generations

| Aspect | Detail |
|---|---|
| Feasible owner path | `user_profile_id` -> `users_profile.id` -> `auth_user_id` -> `auth.uid()` |
| Policy pattern | Same join pattern as user_assets |
| Blockers | user_profile_id is nullable. Server-side writes need service_role to bypass RLS, or a permissive INSERT policy. |
| Alternative | Add `auth_user_id` column directly; or use service_role for server-side writes |

### storage.objects (user-photos)

| Aspect | Detail |
|---|---|
| Current path convention | `{profileId}/{slot}-{timestamp}.{ext}` |
| Feasible policy | `auth.uid()::text = (storage.foldername(name))[1]` if path prefix matches auth.uid() |
| Blockers | Current paths use profile UUID, not auth.uid(). If profile.id != auth.uid(), paths must be migrated. With anonymous auth, auth.uid() could be set equal to profile id, or paths restructured. |

---

## F. What Would Break If RLS Were Enabled Today

### users_profile
- **INSERT**: Would fail. Onboarding page inserts with anon key. With RLS enabled and 0 policies, no rows can be inserted.
- **SELECT**: Would return empty. tryon-flow.ts reads profile by id. With 0 policies, returns nothing.
- **Result**: Onboarding breaks completely. Try-on flow falls back to localStorage (degraded).

### user_assets
- **INSERT**: Would fail. Scan page inserts asset records with anon key.
- **SELECT**: Would return empty. tryon-flow.ts reads assets by profile id.
- **Result**: Photo persistence breaks. Try-on flow uses localStorage fallback photos if available.

### generations
- **INSERT**: Would fail. generation-store.ts inserts via server client (anon key).
- **SELECT**: Would return empty. Status polling returns 404.
- **UPDATE**: Would fail. Background processing cannot update status.
- **Result**: Try-on flow breaks completely. No generation can be created, tracked, or completed.

### user-photos bucket
- **Already partially broken**. Private bucket + RLS on storage.objects + 0 policies = uploads/downloads likely fail for anon/authenticated. App may be silently failing on photo storage today.

### generations bucket
- **Reads continue**. Public bucket, public URLs work regardless of policies.
- **Writes**: If any code writes here via Supabase client (none found), it would fail.
- **Result**: No immediate breakage for reads.

### product-images bucket
- **No breakage**. Public bucket, public URLs. No writes from app code.

---

## G. Risk Register

| # | Risk | Severity | Evidence | Mitigation |
|---|---|---|---|---|
| G1 | anon can DELETE/TRUNCATE all customer tables | **P0 Critical** | RLS disabled, anon has all 7 privileges on all 3 tables | Enable RLS, revoke dangerous grants |
| G2 | anon can read all customer profiles, photos metadata, generations | **P0 Critical** | RLS disabled, anon SELECT on all tables | Enable RLS with owner policies |
| G3 | anon can INSERT arbitrary rows into any table | **P1 High** | RLS disabled, anon INSERT on all tables | Enable RLS, require auth.uid() |
| G4 | No authentication — localStorage UUID is sole identity | **P1 High** | No Supabase Auth usage in code; onboarding does not set auth_user_id | Implement anonymous auth |
| G5 | Nullable owner columns prevent RLS policies | **P1 High** | auth_user_id, user_profile_id all nullable, unpopulated | Backfill, add NOT NULL constraints |
| G6 | localStorage identity can be tampered | **P1 High** | Any user can set mira_profile_id to another user's UUID | Replace with auth-based identity |
| G7 | user-photos bucket private but no policies — client access broken | **P2 Medium** | 0 policies on storage.objects; private bucket blocks anon | Add storage policies or use signed URLs |
| G8 | Generation outputs in public bucket contain user likeness | **P2 Medium** | generations bucket is public; output images/videos accessible by URL | Make private or accept public for MVP |
| G9 | No file size or MIME restrictions on any bucket | **P2 Medium** | All 3 buckets have null file_size_limit and null allowed_mime_types | Set limits |
| G10 | API route accepts any profileId without validation | **P2 Medium** | jobs/route.ts trusts client-provided profileId | Validate ownership via auth |
| G11 | Sensitive body data (height, weight, build, photos) unprotected | **P1 High** | Data stored in open tables with no access control | RLS + auth required before real data |
| G12 | No data retention or deletion policy enforced | **P3 Low** | No TTL, no deletion endpoint, no retention enforcement | Implement before launch |
| G13 | In-memory generation metadata cache lost on server restart | **P3 Low** | generation-store.ts uses Map<> for product display metadata | Persist in DB or recover gracefully |

---

## H. Recommended MVP Security Model

### Recommendation: Option 1 — Supabase Anonymous Auth + RLS + Signed URLs

**Why this option:**

1. **Supabase Anonymous Auth** creates a real `auth.users` row and JWT session without requiring user login. This gives every visitor a stable `auth.uid()` that can drive RLS policies. It is the minimum viable identity layer.

2. **RLS with owner policies** on all 3 tables ensures data isolation. Each user can only read/write their own rows. The anon role's dangerous privileges become irrelevant because RLS checks auth.uid() on every query.

3. **Signed URLs** for `user-photos` bucket allow the server to generate time-limited access URLs without making the bucket public. Client uploads use storage policies tied to auth.uid().

4. **Server-side writes with service_role** for `generations` table during background processing. The API route already runs server-side; switching to service_role for writes is minimal change.

**Why not Option 2 (server-owned everything):** Would require rewriting onboarding and scan to go through API routes instead of direct Supabase calls. More code change, same security outcome. Can be done later if needed.

**Why not Option 3 (mock-only):** MIRA already has working Supabase persistence. Reverting to mock-only loses progress. Better to add the auth layer on top.

**Trade-offs:**
- Anonymous auth means users lose data if they clear browser storage (no login to recover)
- Acceptable for MVP; proper auth (email/social) can be added later
- Anonymous sessions can be "upgraded" to full accounts later via Supabase linking

---

## I. Production-Ready Target State

1. **Identity**: Supabase Auth as sole identity source. Anonymous auth for pre-login MVP; email/social auth for production.
2. **users_profile.auth_user_id**: NOT NULL, FK to auth.users(id). Set on profile creation.
3. **user_assets.user_profile_id**: NOT NULL, FK to users_profile(id).
4. **generations.user_profile_id**: NOT NULL, FK to users_profile(id).
5. **RLS enabled** on users_profile, user_assets, generations.
6. **Least-privilege grants**: Revoke TRUNCATE, TRIGGER, REFERENCES from anon and authenticated. Grant only SELECT, INSERT, UPDATE, DELETE as needed.
7. **user-photos bucket**: Private. Storage policies allow upload/read only for owner paths matching auth.uid().
8. **Storage paths**: `{auth.uid()}/{asset_type}-{timestamp}.{ext}` convention.
9. **Signed URLs**: Generated server-side with short TTL for user-photos access.
10. **No service_role in client**: Only used in API routes for server-side generation writes.
11. **No localStorage as security source**: localStorage used for UX convenience only; auth JWT is the security boundary.
12. **File restrictions**: user-photos max 10MB, image/* MIME only. Generations bucket max 50MB, image/* and video/* only.
13. **Consent, retention, deletion**: Explicit consent before photo upload. 90-day retention for generations. User-initiated deletion endpoint.

---

## J. Proposed SQL / Policy Drafts

> **DO NOT RUN WITHOUT REVIEW.**
> These are documentation-only drafts. They must be tested in a staging project first.
> They assume Supabase Anonymous Auth is enabled and auth_user_id is populated.

### J1. Revoke Dangerous Grants

```sql
-- Revoke TRUNCATE, TRIGGER, REFERENCES from anon and authenticated
-- These are never needed by application clients
REVOKE TRUNCATE, TRIGGER, REFERENCES ON users_profile FROM anon, authenticated;
REVOKE TRUNCATE, TRIGGER, REFERENCES ON user_assets FROM anon, authenticated;
REVOKE TRUNCATE, TRIGGER, REFERENCES ON generations FROM anon, authenticated;
```

### J2. Enable RLS

```sql
ALTER TABLE users_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE generations ENABLE ROW LEVEL SECURITY;
```

### J3. users_profile Policies

```sql
-- Users can read their own profile
CREATE POLICY "users_profile_select_own"
  ON users_profile FOR SELECT
  USING (auth_user_id = auth.uid());

-- Users can insert their own profile (auth_user_id must match)
CREATE POLICY "users_profile_insert_own"
  ON users_profile FOR INSERT
  WITH CHECK (auth_user_id = auth.uid());

-- Users can update their own profile
CREATE POLICY "users_profile_update_own"
  ON users_profile FOR UPDATE
  USING (auth_user_id = auth.uid())
  WITH CHECK (auth_user_id = auth.uid());

-- Users can delete their own profile
CREATE POLICY "users_profile_delete_own"
  ON users_profile FOR DELETE
  USING (auth_user_id = auth.uid());
```

### J4. user_assets Policies

```sql
-- Users can read their own assets (via profile join)
CREATE POLICY "user_assets_select_own"
  ON user_assets FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM users_profile
      WHERE users_profile.id = user_assets.user_profile_id
        AND users_profile.auth_user_id = auth.uid()
    )
  );

-- Users can insert assets linked to their own profile
CREATE POLICY "user_assets_insert_own"
  ON user_assets FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM users_profile
      WHERE users_profile.id = user_assets.user_profile_id
        AND users_profile.auth_user_id = auth.uid()
    )
  );

-- Users can delete their own assets
CREATE POLICY "user_assets_delete_own"
  ON user_assets FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM users_profile
      WHERE users_profile.id = user_assets.user_profile_id
        AND users_profile.auth_user_id = auth.uid()
    )
  );
```

### J5. generations Policies

```sql
-- Users can read their own generations
CREATE POLICY "generations_select_own"
  ON generations FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM users_profile
      WHERE users_profile.id = generations.user_profile_id
        AND users_profile.auth_user_id = auth.uid()
    )
  );

-- Server-side INSERT/UPDATE uses service_role (bypasses RLS).
-- No client-side INSERT policy needed if only API routes write.

-- If client-side INSERT is needed:
-- CREATE POLICY "generations_insert_own"
--   ON generations FOR INSERT
--   WITH CHECK (
--     EXISTS (
--       SELECT 1 FROM users_profile
--       WHERE users_profile.id = generations.user_profile_id
--         AND users_profile.auth_user_id = auth.uid()
--     )
--   );
```

### J6. Storage Policies (user-photos)

```sql
-- Users can upload photos to their own folder
CREATE POLICY "user_photos_insert_own"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id = 'user-photos'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

-- Users can read their own photos
CREATE POLICY "user_photos_select_own"
  ON storage.objects FOR SELECT
  USING (
    bucket_id = 'user-photos'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

-- Users can delete their own photos
CREATE POLICY "user_photos_delete_own"
  ON storage.objects FOR DELETE
  USING (
    bucket_id = 'user-photos'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );
```

### J7. Bucket Configuration

```sql
-- Set file size and MIME restrictions
UPDATE storage.buckets SET file_size_limit = 10485760, allowed_mime_types = ARRAY['image/jpeg','image/png','image/webp'] WHERE id = 'user-photos';
UPDATE storage.buckets SET file_size_limit = 52428800, allowed_mime_types = ARRAY['image/jpeg','image/png','image/webp','video/mp4','video/webm'] WHERE id = 'generations';
UPDATE storage.buckets SET file_size_limit = 10485760, allowed_mime_types = ARRAY['image/jpeg','image/png','image/webp'] WHERE id = 'product-images';
```

---

## K. Required Backfill / Migration Plan

### K1. Identify Rows with NULL auth_user_id

```sql
-- DO NOT RUN IN PRODUCTION WITHOUT REVIEW
-- Count profiles without auth identity
SELECT count(*) FROM users_profile WHERE auth_user_id IS NULL;
-- Expect: ALL rows currently have NULL auth_user_id
```

### K2. Identify Rows with NULL user_profile_id

```sql
SELECT count(*) FROM user_assets WHERE user_profile_id IS NULL;
SELECT count(*) FROM generations WHERE user_profile_id IS NULL;
```

### K3. What Cannot Be Automatically Backfilled

- **auth_user_id on existing profiles**: These profiles were created without Supabase Auth. There is no auth.users row to link to. Options:
  - Delete all test data (acceptable if MVP with no real users)
  - Create anonymous auth users for each profile and backfill (complex, fragile)
  - Leave old rows orphaned and start fresh with auth

- **Storage paths**: Current paths use `{profileId}/...`. If RLS policies require `{auth.uid()}/...` and profile.id != auth.uid(), existing files must be renamed or the policy must accommodate both patterns.

### K4. Recommended Approach

1. **If no real customers yet**: Delete all test data. Start clean with anonymous auth.
2. **If test data must be preserved**: Create a migration script that:
   - Creates anonymous auth users
   - Sets auth_user_id = new auth.uid() on each profile
   - Renames storage paths if needed
   - Validates no orphaned rows remain

### K5. How to Test RLS in Staging

1. Create a Supabase staging project (or use local Supabase CLI)
2. Apply schema + RLS policies + grants from Section J
3. Enable Anonymous Auth in project settings
4. Run MIRA against staging project
5. Verify:
   - Onboarding creates profile with auth_user_id = auth.uid()
   - Scan uploads succeed to user-photos under auth.uid() path
   - Try-on creates generation linked to profile
   - Result polling returns only own generations
   - Cross-user access denied (use two anonymous sessions)
6. Only after staging verification: apply to production

---

## L. Manual Verification Checklist

Before going live with RLS, a human must verify each item:

### Auth
- [ ] Supabase Auth > Settings: Anonymous sign-ins enabled
- [ ] Supabase Auth > Settings: Captcha/abuse protection configured (hCaptcha or Turnstile)
- [ ] Confirm auth.users rows are created on app visit

### Grants
- [ ] TRUNCATE, TRIGGER, REFERENCES revoked from anon and authenticated
- [ ] Only SELECT, INSERT, UPDATE, DELETE remain for anon/authenticated
- [ ] service_role retains all privileges

### RLS
- [ ] RLS enabled on users_profile
- [ ] RLS enabled on user_assets
- [ ] RLS enabled on generations
- [ ] force_rls = true if service_role bypass is NOT wanted (typically leave false for API routes)

### Policies
- [ ] users_profile: SELECT/INSERT/UPDATE/DELETE own policies active
- [ ] user_assets: SELECT/INSERT/DELETE own policies active
- [ ] generations: SELECT own policy active; INSERT/UPDATE via service_role
- [ ] storage.objects: INSERT/SELECT/DELETE own policies active for user-photos bucket

### Functional Tests
- [ ] Onboarding creates profile with auth_user_id set
- [ ] Scan uploads photo to user-photos bucket successfully
- [ ] Scan creates user_assets row linked to profile
- [ ] Try-on flow reads own profile and assets
- [ ] Try-on creates generation via API route
- [ ] Result polling returns own generation status
- [ ] Result polling returns 404 for other user's generation
- [ ] Cross-user read denied (different anonymous session cannot read other's profile)
- [ ] Cross-user write denied (cannot insert into another user's profile)
- [ ] Cross-user storage denied (cannot read/upload to another user's folder)

### Storage
- [ ] user-photos bucket: private, policies active
- [ ] generations bucket: public intentional, size/MIME limits set
- [ ] product-images bucket: public intentional, size/MIME limits set
- [ ] File size limit enforced (upload > limit rejected)
- [ ] MIME type enforced (upload non-image rejected for user-photos)

### Data Safety
- [ ] Deletion endpoint exists or is planned
- [ ] Retention period documented
- [ ] No secrets in client bundle (check NEXT_PUBLIC_SUPABASE_ANON_KEY is anon, not service_role)
- [ ] service_role key not in any NEXT_PUBLIC_ variable

---

## M. Recommended Next Implementation Sprint

### Sprint: "Supabase Anonymous Auth Foundation"

**Goal**: Establish auth.uid() identity so RLS policies can be applied.

**Scope**:
1. Enable Anonymous Auth in Supabase project settings
2. Add `supabase.auth.signInAnonymously()` call on app load (before onboarding)
3. Modify onboarding to set `auth_user_id = auth.uid()` when creating profile
4. Store profile ID in both localStorage (UX) and link to auth.uid() (security)
5. Modify scan to use `auth.uid()` as storage path prefix
6. Modify generation-store.ts to use service_role client for server-side writes
7. Apply RLS policies from Section J in staging first
8. Run manual verification checklist (Section L)
9. Apply to production only after staging passes

**Not in scope** (save for later sprint):
- Email/social auth
- Deletion endpoint
- Data retention enforcement
- Generation bucket privatization
- Cost tracking

**Estimated files to modify**:
- `lib/supabase/client.ts` — add auth init
- `lib/supabase/server.ts` — add service_role client option
- `app/[locale]/(app)/onboarding/page.tsx` — set auth_user_id
- `app/[locale]/(app)/scan/page.tsx` — use auth.uid() path prefix
- `lib/generation-store.ts` — use service_role client
- `supabase/schema.sql` — update RLS documentation
- New: auth provider/hook for anonymous session management

**Prerequisites**:
- Human decision on questions in HUMAN_QUESTIONS.md (Section 4 of this plan)
- Staging Supabase project for testing
- Backup of current test data (or agreement to delete)

---

## Appendix: Files Inspected

| File | Supabase operations found |
|---|---|
| `lib/supabase/client.ts` | createBrowserClient with anon key |
| `lib/supabase/server.ts` | createServerClient with anon key |
| `lib/generation-store.ts` | INSERT/UPDATE/SELECT on generations |
| `lib/tryon-flow.ts` | SELECT on users_profile, user_assets |
| `app/[locale]/(app)/onboarding/page.tsx` | INSERT on users_profile |
| `app/[locale]/(app)/scan/page.tsx` | storage.upload to user-photos, INSERT on user_assets |
| `app/api/tryon/jobs/route.ts` | Uses generation-store (INSERT/UPDATE generations) |
| `app/api/tryon/status/[generationId]/route.ts` | Uses generation-store (SELECT generations) |
| `supabase/schema.sql` | Schema definitions, RLS comments |
| `middleware.ts` | next-intl routing only, no auth |
| `.env`, `.env.example` | Environment variable definitions |
