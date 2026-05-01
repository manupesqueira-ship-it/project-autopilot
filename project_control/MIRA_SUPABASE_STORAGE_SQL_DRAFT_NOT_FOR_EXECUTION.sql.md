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

# MIRA Supabase Storage SQL Draft

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

## Current Storage State (as of 2026-04-29 audit)

| Bucket | Public | Policies | file_size_limit | allowed_mime_types | Current Risk |
|---|---|---|---|---|---|
| `user-photos` | false (private) | 0 | none | none | BROKEN: private + 0 policies = no client can upload or download |
| `generations` | true (public) | 0 | none | none | MEDIUM: generation outputs (user try-ons) publicly accessible by URL |
| `product-images` | true (public) | 0 | none | none | LOW: catalog content, intentionally public |

All three buckets have `storage.objects` RLS enabled (Supabase default) with 0 policies.

---

## Storage Path Ownership Strategy

### Current Path Convention

```
user-photos/{profileId}/{asset_type}-{timestamp}.{ext}
```

Where `profileId` is the `users_profile.id` UUID from localStorage `mira_profile_id`.
This path does NOT match `auth.uid()` because no anonymous auth exists yet.

### Option A: Keep profileId paths, use JOIN-based storage policy

Pros: No code change, no file migration required.
Cons: Storage policy must JOIN storage path to users_profile to verify ownership.
     Complex, slower, more error-prone.

```sql
-- DRAFT — DO NOT RUN LIVE
-- Storage policy with JOIN through users_profile to verify folder ownership

-- CREATE POLICY "user_photos_insert_via_profile"
--   ON storage.objects
--   FOR INSERT
--   WITH CHECK (
--     bucket_id = 'user-photos'
--     AND EXISTS (
--       SELECT 1 FROM users_profile
--       WHERE id::text = (storage.foldername(name))[1]
--         AND auth_user_id = auth.uid()
--     )
--   );

-- CREATE POLICY "user_photos_select_via_profile"
--   ON storage.objects
--   FOR SELECT
--   USING (
--     bucket_id = 'user-photos'
--     AND EXISTS (
--       SELECT 1 FROM users_profile
--       WHERE id::text = (storage.foldername(name))[1]
--         AND auth_user_id = auth.uid()
--     )
--   );

-- CREATE POLICY "user_photos_delete_via_profile"
--   ON storage.objects
--   FOR DELETE
--   USING (
--     bucket_id = 'user-photos'
--     AND EXISTS (
--       SELECT 1 FROM users_profile
--       WHERE id::text = (storage.foldername(name))[1]
--         AND auth_user_id = auth.uid()
--     )
--   );
```

### Option B: Switch to auth.uid() paths (RECOMMENDED)

Pros: Simplest storage policies. Directly tied to auth identity.
Cons: Requires code change in `app/[locale]/(app)/scan/page.tsx` to use `auth.uid()` as path prefix.
     Existing uploaded files must be removed or remain under old paths (no policy will cover them).

New path convention would be:
```
user-photos/{auth.uid()}/{asset_type}-{timestamp}.{ext}
```

```sql
-- DRAFT — DO NOT RUN LIVE
-- Simple folder-ownership storage policies for user-photos
-- Requires scan/page.tsx to upload to auth.uid() prefixed paths

-- INSERT: Users can upload files to their own auth.uid() folder
-- CREATE POLICY "user_photos_insert_own"
--   ON storage.objects
--   FOR INSERT
--   WITH CHECK (
--     bucket_id = 'user-photos'
--     AND auth.uid() IS NOT NULL
--     AND (storage.foldername(name))[1] = auth.uid()::text
--   );

-- SELECT: Users can read files from their own auth.uid() folder
-- CREATE POLICY "user_photos_select_own"
--   ON storage.objects
--   FOR SELECT
--   USING (
--     bucket_id = 'user-photos'
--     AND auth.uid() IS NOT NULL
--     AND (storage.foldername(name))[1] = auth.uid()::text
--   );

-- DELETE: Users can delete files from their own auth.uid() folder
-- CREATE POLICY "user_photos_delete_own"
--   ON storage.objects
--   FOR DELETE
--   USING (
--     bucket_id = 'user-photos'
--     AND auth.uid() IS NOT NULL
--     AND (storage.foldername(name))[1] = auth.uid()::text
--   );
```

Code change required in `app/[locale]/(app)/scan/page.tsx`:

```typescript
// DRAFT — DO NOT APPLY WITHOUT RLS DECISION
// Current upload path (uses profileId):
// const path = `${profileId}/${slot}-${Date.now()}.${ext}`;

// New upload path (uses auth.uid()):
// const { data: { user } } = await supabase.auth.getUser();
// const uid = user?.id;
// if (!uid) throw new Error("No auth session — cannot upload");
// const path = `${uid}/${slot}-${Date.now()}.${ext}`;
```

---

## user-photos Bucket: Signed URL Assumptions

Signed URLs allow the server to generate time-limited, authenticated access URLs
for a private bucket without exposing the bucket publicly.

**When to use signed URLs:**
- When a user needs to VIEW their own uploaded photo in the app UI.
- When passing a photo URL to the try-on AI provider (server-side only).

**Signed URL generation (server-side, NOT client-side):**

```typescript
// DRAFT — DO NOT APPLY YET
// Server-side signed URL generation for user photo access
// This must run in an API route with the service_role client (or server client).

// const { data, error } = await supabaseServer
//   .storage
//   .from('user-photos')
//   .createSignedUrl(storagePath, 3600); // 1 hour TTL

// if (error || !data?.signedUrl) throw new Error("Failed to generate signed URL");
// return data.signedUrl;
```

**Assumptions for signed URLs:**
- TTL: 1 hour (3600 seconds) is appropriate for MVP. Reduce for higher security.
- Signed URLs should NOT be stored in the database — generate fresh ones on each request.
- The server client used to generate signed URLs does NOT need service_role;
  the anon client can generate signed URLs for objects the user owns (with storage policies).
- If using service_role to generate signed URLs for any object path,
  ensure the API route validates that the requesting user owns the object
  before generating the URL. Otherwise, any authenticated user could
  request a signed URL for any path.

---

## user-photos Bucket: File Size and MIME Restrictions

Recommended limits for user-uploaded photos:

```sql
-- DRAFT — DO NOT RUN LIVE
-- Set upload constraints on the user-photos bucket.
-- These can also be set in Supabase Dashboard > Storage > user-photos > Edit bucket.

-- UPDATE storage.buckets
--   SET
--     file_size_limit = 10485760,  -- 10 MB maximum per file
--     allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/webp']
--   WHERE id = 'user-photos';
```

Rationale:
- 10 MB: Sufficient for high-quality phone photos; rejects video or document uploads.
- MIME types: jpeg, png, webp cover all standard phone camera formats.
- No `image/gif`, `image/heic`, or `image/heif` — HEIC conversion should happen client-side
  before upload if iOS HEIC support is needed.
- Restricting MIME types prevents abusive file type uploads (PDF, executable, etc.).

---

## product-images Bucket: Public Strategy

The `product-images` bucket contains catalog clothing images.
These are NOT user data. They are intentionally public.

**Decision: Keep public. No storage policies needed.**

Rationale:
- Product images are catalog content with no personal data.
- Public access allows CDN-friendly direct URL usage in the app.
- No user identity required to view product images.
- Risk level: LOW.

Recommended action:

```sql
-- DRAFT — DO NOT RUN LIVE
-- Optional: set file size and MIME limits even on public bucket
-- to prevent abuse of the upload path (if uploads are ever enabled).

-- UPDATE storage.buckets
--   SET
--     file_size_limit = 10485760,  -- 10 MB
--     allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/webp']
--   WHERE id = 'product-images';
```

Note: No storage SELECT/INSERT policies are needed for a public bucket.
Public buckets bypass storage RLS for reads. Writes should only happen
via service_role (admin operations) — no client upload policy is needed.

---

## generations Bucket: Decision Notes

The `generations` bucket stores AI try-on output images/videos.
These may contain a user's likeness (body + clothing composite).

**Current state**: Public bucket, no policies, no file size or MIME limits.

**Decision required: Public vs Private**

| Option | Implication | Recommended |
|---|---|---|
| Keep public (MVP) | Anyone with an output URL can view the generated image. Acceptable for internal test data only. | MVP only |
| Make private + signed URLs | Outputs only accessible via server-generated signed URLs. Required before real user data. | Pre-launch |

### If keeping public (MVP acceptable):

```sql
-- DRAFT — DO NOT RUN LIVE
-- Minimal hardening for public generations bucket: add size/MIME limits.
-- No policy change needed for reads (public bucket).
-- Writes are done via service_role in API routes — no client INSERT policy needed.

-- UPDATE storage.buckets
--   SET
--     file_size_limit = 52428800,  -- 50 MB (allows video outputs)
--     allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/webp', 'video/mp4', 'video/webm']
--   WHERE id = 'generations';
```

### If making private (required before real customer data):

```sql
-- DRAFT — DO NOT RUN LIVE
-- Step 1: Make the bucket private
-- UPDATE storage.buckets SET public = false WHERE id = 'generations';

-- Step 2: Add SELECT policy so users can read their own generation outputs.
-- Assumes generation output files are stored under {auth.uid()}/{generationId}.{ext}
-- If paths use a different convention, adjust (storage.foldername(name))[1].

-- CREATE POLICY "generations_select_own"
--   ON storage.objects
--   FOR SELECT
--   USING (
--     bucket_id = 'generations'
--     AND auth.uid() IS NOT NULL
--     AND (storage.foldername(name))[1] = auth.uid()::text
--   );

-- Step 3: Update generation-store.ts to generate signed URLs
-- instead of returning raw public storage URLs in output columns.
-- See signed URL pattern in user-photos section above.
```

**Generation output path convention (if switching to private):**
- Current: unclear (check `lib/generation-store.ts` and mock provider output paths)
- Recommended: `{auth.uid()}/{generationId}.{ext}` for consistency with user-photos

---

## Rollback Plan for Storage Changes

Storage policy rollback (drop policies):

```sql
-- EMERGENCY ROLLBACK — DO NOT RUN UNLESS NEEDED

-- Drop user-photos policies (Option A: JOIN-based)
-- DROP POLICY IF EXISTS "user_photos_insert_via_profile" ON storage.objects;
-- DROP POLICY IF EXISTS "user_photos_select_via_profile" ON storage.objects;
-- DROP POLICY IF EXISTS "user_photos_delete_via_profile" ON storage.objects;

-- Drop user-photos policies (Option B: direct auth.uid())
-- DROP POLICY IF EXISTS "user_photos_insert_own" ON storage.objects;
-- DROP POLICY IF EXISTS "user_photos_select_own" ON storage.objects;
-- DROP POLICY IF EXISTS "user_photos_delete_own" ON storage.objects;

-- Drop generations policies (if private option was applied)
-- DROP POLICY IF EXISTS "generations_select_own" ON storage.objects;

-- Restore generations bucket to public (if it was made private)
-- UPDATE storage.buckets SET public = true WHERE id = 'generations';
```

**After rollback**: user-photos reverts to 0-policy state (private + no access = broken uploads).
This was the pre-migration state. The app was already failing silently on photo uploads.
Rolling back to 0-policy state is no worse than the current state.

---

## MIME and File Size Recommendations Summary

| Bucket | file_size_limit | allowed_mime_types | Rationale |
|---|---|---|---|
| `user-photos` | 10 MB (10485760 bytes) | image/jpeg, image/png, image/webp | Phone camera photos; reject video/doc |
| `generations` | 50 MB (52428800 bytes) | image/jpeg, image/png, image/webp, video/mp4, video/webm | AI outputs may be video; allow larger |
| `product-images` | 10 MB (10485760 bytes) | image/jpeg, image/png, image/webp | Catalog images; same as user photos |

These limits can be set via Dashboard UI or via the SQL UPDATE statements above.
Dashboard UI is preferred for non-policy changes as it does not require SQL execution.

---

## Storage Policy Execution Order (if applying)

1. Decide path convention: Option A (profileId) or Option B (auth.uid()) — document decision.
2. If Option B: update scan/page.tsx to use auth.uid() upload paths.
3. If switching generations to private: update generation-store.ts to return signed URLs.
4. Set file_size_limit and allowed_mime_types on all buckets (Dashboard or SQL).
5. Apply user-photos INSERT policy (chosen option).
6. Apply user-photos SELECT policy.
7. Apply user-photos DELETE policy.
8. If generations is private: apply generations SELECT policy.
9. Run validation queries from MIRA_SUPABASE_SECURITY_VALIDATION_QUERIES_DRAFT.md.
10. Test upload flow end-to-end in staging.

---

*End of MIRA_SUPABASE_STORAGE_SQL_DRAFT_NOT_FOR_EXECUTION.sql.md*
*This file is a review artifact. Do not execute any SQL contained herein.*
