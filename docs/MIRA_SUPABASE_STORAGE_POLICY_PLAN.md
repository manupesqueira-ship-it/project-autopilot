# MIRA Supabase Storage Policy Plan

> **WARNING: DO NOT EXECUTE ANY SQL OR MODIFY SUPABASE SETTINGS.**
> This is a planning document only. All SQL is DRAFT.
> No storage policies may be created, no bucket settings changed, and no
> bucket visibility toggled until staging tests pass and a human approves.

Created: 2026-04-30
Project: mira-mvp (ref vtaqyammimmgxlkqwjat)
Status: PLANNING ONLY — NO EXECUTION

---

## 1. Buckets Overview

### 1.1 Current State

| Bucket | Public | Policies | file_size_limit | allowed_mime_types | Sensitivity |
|---|---|---|---|---|---|
| generations | YES | 0 | none | none | MEDIUM — may contain user try-on images/videos |
| product-images | YES | 0 | none | none | LOW — catalog content, intentionally public |
| user-photos | NO | 0 | none | none | HIGH — body photos, biometric data |

**Critical issue**: `storage.objects` has Supabase's default RLS enabled but
zero policies. This means `user-photos` (private bucket) currently blocks all
reads and writes from anon/authenticated clients. Photo upload is silently
failing or falling back to localStorage. No storage is secure or functional.

### 1.2 Target State

| Bucket | Public | Policies | file_size_limit | allowed_mime_types | Access model |
|---|---|---|---|---|---|
| generations | YES (MVP) | 0 (MVP) | 50 MB | image/jpeg, image/png, image/webp, video/mp4, video/webm | Public URL for MVP; private + signed URLs post-MVP |
| product-images | YES | 0 | 5 MB | image/jpeg, image/png, image/webp | Public URL, no user data |
| user-photos | NO | 3 (INSERT/SELECT/DELETE) | 10 MB | image/jpeg, image/png, image/webp | Signed URLs, owner-only access |

---

## 2. user-photos Private Policy Strategy

### 2.1 Threat Model

`user-photos` stores body photos used as inputs to AI try-on generation. These
are among the most sensitive data MIRA handles:

- Body shape and physical appearance.
- Potentially identifiable even without face content.
- If leaked, cannot be un-leaked.

The bucket is already marked private (correct), but has zero policies, meaning
the client cannot read or write it at all. The fix is to add storage policies
that allow authenticated owners to upload and read their own photos.

### 2.2 Path Convention (Prerequisite)

Storage policies for user-photos rely on the first path segment being the
user's `auth.uid()`. The current path convention uses `{profileId}` as the
first segment. These are different UUIDs unless specifically aligned.

**Required before storage policies can be applied:**

The scan page (`app/[locale]/(app)/scan/page.tsx`) must be updated to use
`auth.uid()` as the first path segment:

```
Current:  user-photos/{profileId}/{slot}-{timestamp}.{ext}
Required: user-photos/{auth.uid()}/{slot}-{timestamp}.{ext}
```

This path change must be made and tested before storage policies are added.
Existing files stored under profileId paths will not be accessible via the new
policies and must be deleted (test data only — acceptable).

### 2.3 Policy Drafts

```sql
-- DRAFT — DO NOT RUN

-- Allow authenticated owners to upload photos under their own folder
CREATE POLICY "user_photos_insert_own"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id = 'user-photos'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

-- Allow authenticated owners to read their own photos
CREATE POLICY "user_photos_select_own"
  ON storage.objects FOR SELECT
  USING (
    bucket_id = 'user-photos'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

-- Allow authenticated owners to delete their own photos
CREATE POLICY "user_photos_delete_own"
  ON storage.objects FOR DELETE
  USING (
    bucket_id = 'user-photos'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

-- No UPDATE policy: photos are write-once and replaced by new uploads
```

### 2.4 Anonymous Auth Requirement

The INSERT policy checks `auth.role() = 'authenticated'`. Anonymous sign-in
sessions are classified as `authenticated` by Supabase (they hold a valid JWT
with a non-null `sub` field). Anon-key requests with no session are classified
as `anon`. This policy correctly allows anonymous-auth users to upload while
blocking completely unauthenticated requests.

### 2.5 Signed URL Strategy

Because `user-photos` is private, the application cannot use public URLs to
display photos to users. Signed URLs must be generated server-side:

```
Server action or API route:
  supabase_service_role.storage
    .from('user-photos')
    .createSignedUrl(path, expiresIn: 300)   // 5-minute TTL
```

**Rules for signed URLs:**
- Generated only in server-side code (API routes or server components).
- TTL: 300 seconds (5 minutes) for display purposes.
- Never logged or returned in error messages.
- Never stored in the database or localStorage.
- Regenerated on each page load that needs to display a photo.

The scan page currently displays photos from browser memory (data URLs from
the camera/file picker) and does not need to read them back from storage.
Signed URLs are primarily needed if a future flow displays previously uploaded
photos (e.g., a "your scan" review screen).

---

## 3. product-images Public Strategy

### 3.1 Decision

`product-images` remains public with no storage policies. This is intentional.

Product images are catalog content, not user data. They are the same for every
user, have no sensitivity, and must be fast to load. Making them private would
require signed URLs for all product image display, adding latency and server
load with no security benefit.

### 3.2 Bucket Constraints Still Required

Even though the bucket is public, file size and MIME type restrictions must be
set to prevent abuse (e.g., a bad actor using the bucket as free file hosting
by exploiting the anon upload path if any such path exists in the app).

```sql
-- DRAFT — DO NOT RUN
UPDATE storage.buckets
SET
  file_size_limit = 5242880,  -- 5 MB
  allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/webp']
WHERE id = 'product-images';
```

### 3.3 Write Access

No application code writes to `product-images` from the client. Product images
are uploaded manually via the Supabase Dashboard by the team. No storage INSERT
policy is needed for `product-images`. If a policy is added in the future, it
should restrict inserts to service_role only.

---

## 4. generations Bucket — Public/Private Decision

### 4.1 Current State

The `generations` bucket is public. Generated try-on output images and videos
are stored here. Anyone with the URL can access any generation output, including
outputs that contain a user's body likeness.

### 4.2 Decision Matrix

| Option | Security | Complexity | MVP Recommendation |
|---|---|---|---|
| Keep public | LOW — outputs accessible to anyone with URL | None | Acceptable for MVP with test data only |
| Make private + signed URLs | HIGH — outputs accessible only to owner | Medium — add signed URL generation in status API route | Recommended before real user data |

### 4.3 MVP Decision

Keep `generations` public for MVP with the following conditions:

1. Only test/synthetic data is stored in generations during MVP.
2. Before any real user try-on photos are processed and outputs stored, the
   bucket must be made private and the status API route updated to return
   signed URLs instead of direct storage URLs.
3. This decision must be revisited before public beta launch.

### 4.4 Post-MVP Private Configuration (Draft, Do Not Execute)

```sql
-- DRAFT — DO NOT RUN — FUTURE SPRINT ONLY

-- Make bucket private
UPDATE storage.buckets SET public = false WHERE id = 'generations';

-- Allow owners to read their own generation outputs
CREATE POLICY "generations_select_own"
  ON storage.objects FOR SELECT
  USING (
    bucket_id = 'generations'
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

-- Server writes via service_role (bypasses RLS, no policy needed)
```

The status API route (`app/api/tryon/status/[generationId]/route.ts`) must also
be updated to call `createSignedUrl()` on the output paths before returning
them to the client.

---

## 5. MIME Restrictions

### 5.1 Purpose

MIME restrictions prevent:
- Upload of executable files, scripts, or malicious content.
- Use of Supabase storage as a file hosting service for non-image content.
- Unexpected content types reaching the AI provider API.

### 5.2 Restrictions by Bucket

| Bucket | Allowed MIME types | Rationale |
|---|---|---|
| user-photos | image/jpeg, image/png, image/webp | Body scan inputs; no video needed |
| generations | image/jpeg, image/png, image/webp, video/mp4, video/webm | Try-on outputs may be images or short videos |
| product-images | image/jpeg, image/png, image/webp | Catalog product images only |

### 5.3 How Supabase Enforces MIME

The `allowed_mime_types` field on `storage.buckets` causes Supabase to reject
uploads that do not match the whitelist. This is enforced server-side before
the object is stored. Client-side MIME validation is an additional UX layer
but is not a security control.

### 5.4 Draft SQL for All Buckets

```sql
-- DRAFT — DO NOT RUN

UPDATE storage.buckets
SET
  file_size_limit = 10485760,  -- 10 MB
  allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/webp']
WHERE id = 'user-photos';

UPDATE storage.buckets
SET
  file_size_limit = 52428800,  -- 50 MB
  allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/webp', 'video/mp4', 'video/webm']
WHERE id = 'generations';

UPDATE storage.buckets
SET
  file_size_limit = 5242880,   -- 5 MB
  allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/webp']
WHERE id = 'product-images';
```

These can be applied via the Supabase Dashboard bucket settings (preferred for
clarity and audit trail) or via SQL. Dashboard changes do not require a
migration script or staging test — they are safe to apply directly.

---

## 6. File Size Restrictions

### 6.1 Rationale

Without file size limits:
- Users can upload very large files, consuming storage quota.
- Large files increase AI provider API costs and processing time.
- No protection against automated abuse uploading multi-GB files.

### 6.2 Limits by Bucket

| Bucket | Limit | Rationale |
|---|---|---|
| user-photos | 10 MB (10,485,760 bytes) | Phone camera JPEGs are typically 3-8 MB; 10 MB gives headroom |
| generations | 50 MB (52,428,800 bytes) | Short AI-generated video clips may be larger; 50 MB is generous |
| product-images | 5 MB (5,242,880 bytes) | Product catalog images should be web-optimized; 5 MB is sufficient |

### 6.3 Client-Side Validation

The scan page should also validate file size client-side before attempting
upload, to give immediate feedback to users. Client-side validation is a UX
improvement but is not a security control — the bucket-level limit is the
authoritative enforcement.

Recommended client-side check in `app/[locale]/(app)/scan/page.tsx`:

```typescript
const MAX_PHOTO_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB
if (file.size > MAX_PHOTO_SIZE_BYTES) {
  // Show user error; do not attempt upload
}
```

---

## 7. Path Ownership Strategy

### 7.1 Current Paths (Unsafe)

```
user-photos/{profileId}/{slot}-{timestamp}.{ext}
```

`profileId` is a `users_profile.id` UUID, not a Supabase Auth UUID. It is
stored in localStorage and can be forged. A storage policy based on profileId
cannot be expressed using `auth.uid()` without a database join, which
`storage.objects` policies cannot perform (no cross-table joins in storage
policies).

### 7.2 Required Paths (Safe)

```
user-photos/{auth.uid()}/{slot}-{timestamp}.{ext}
```

Using `auth.uid()` as the first path segment allows the simple and performant
policy expression: `(storage.foldername(name))[1] = auth.uid()::text`

This means the folder name is always the authenticated user's Supabase Auth UUID.

### 7.3 Migration

**For test data (current state):** Delete existing files in `user-photos` bucket.
No path migration needed. Old profileId-based paths are discarded with the test data.

**For future production data:** If a migration ever occurs, objects must be moved
from `{profileId}/...` to `{auth.uid()}/...`. Supabase Storage does not have a
native move/rename operation; files must be downloaded and re-uploaded. This is
complex and error-prone. The recommended approach is a clean start with the
new path convention, not a live migration.

### 7.4 Path for generations Bucket

If `generations` is made private in a future sprint, the same convention applies:

```
generations/{auth.uid()}/{generationId}-{slot}.{ext}
```

Server-side writes (via service_role) must write to this path. The status API
route must generate signed URLs for the specific path when returning results
to the authenticated client.

---

## 8. Signed URL Strategy

### 8.1 When Signed URLs Are Used

| Bucket | Signed URLs | Context |
|---|---|---|
| user-photos | YES — required | Private bucket; any display of previously uploaded photos needs a signed URL |
| generations | NO (MVP) / YES (post-MVP) | Public bucket for MVP; private + signed URLs when bucket is made private |
| product-images | NO | Public bucket; public URLs used directly |

### 8.2 Signed URL Generation (Server-Side Only)

Signed URLs must be generated only in server-side code:

```typescript
// DRAFT — Reference only, not for execution
// In an API route or server component:
const { data, error } = await supabaseServiceRole.storage
  .from('user-photos')
  .createSignedUrl(
    `${authUserId}/${slot}-${timestamp}.jpg`,
    300  // 5-minute TTL
  );
```

### 8.3 TTL Policy

| Use case | Recommended TTL | Rationale |
|---|---|---|
| Display photo in scan review | 300 seconds (5 min) | Short session; photo is shown once |
| Display photo in try-on context | 300 seconds (5 min) | Single page load |
| Download by user | 3600 seconds (1 hour) | User-initiated download |
| Admin/support review | 3600 seconds (1 hour) | Internal use; time-limited |

Signed URLs must never be stored in the database, localStorage, or returned in
logs. They expire automatically and a fresh URL must be generated on each use.

### 8.4 Anti-Patterns

The following are forbidden:

- Generating signed URLs in browser-side code using the anon key.
- Returning raw storage paths to the client for private buckets.
- Storing signed URLs in `generations.image_output_path` (paths must be stored
  without tokens; signed URLs generated at read time).
- Setting TTL > 24 hours for user-facing access.

---

## 9. Deletion/Retention Strategy

### 9.1 Current State

No deletion endpoint exists. No retention policy is enforced. Files uploaded
to `user-photos` are retained indefinitely. Generated outputs in `generations`
are retained indefinitely.

### 9.2 Recommended Retention Policy

| Data type | Retention | Enforcement |
|---|---|---|
| User photos (user-photos) | Delete on user request or account deletion | User-initiated deletion endpoint; admin can trigger via service_role |
| Generation outputs (generations) | 90 days from creation date | Scheduled cleanup job or cron trigger |
| users_profile row | Delete on user request | Cascading delete or manual service_role operation |
| user_assets rows | Delete with user photos | Cascade from users_profile or explicit deletion |
| generations rows | 90 days | Scheduled cleanup |

### 9.3 Deletion Order (Dependencies)

Deletion must respect foreign key constraints:

```
1. Delete storage objects in user-photos (bucket)
2. Delete rows in user_assets (references users_profile)
3. Delete storage objects in generations (bucket)
4. DELETE rows in generations (references users_profile)
5. DELETE row in users_profile
6. Optionally delete auth.users row via Supabase Admin API
```

### 9.4 MVP Scope

User-initiated deletion is out of scope for the current sprint. The plan must
document the intended deletion path so it can be implemented before public launch.
A `DELETE /api/account` endpoint is the recommended approach.

### 9.5 Test Data Cleanup

Before enabling anonymous auth in production, all test data (rows and storage
objects) must be deleted. The deletion sequence above applies. Test storage
objects in `user-photos` can be deleted via the Supabase Dashboard > Storage
UI or via the Supabase CLI (`supabase storage rm`).

---

## 10. Abuse Prevention

### 10.1 Threats to Storage

| Threat | Risk | Mitigation |
|---|---|---|
| Anonymous user uploads unlimited files | Storage cost abuse | File size limits; MIME restrictions; rate limiting via CAPTCHA |
| Automated creation of anonymous sessions to bypass per-user limits | Cost abuse | CAPTCHA on anonymous sign-in (hCaptcha or Turnstile) |
| Upload of malicious files (scripts, executables) | None if MIME is enforced | MIME whitelist enforced at bucket level |
| Path traversal in storage names | LOW — Supabase sanitizes paths | Still use strict path prefix enforcement in policies |
| Public generation URLs shared externally | User likeness exposure | Accept for MVP; privatize before real users |
| Large file upload consuming storage quota | Cost | file_size_limit on all buckets |

### 10.2 CAPTCHA Requirement

Before public beta, hCaptcha or Cloudflare Turnstile must be enabled in
Supabase Auth settings to rate-limit anonymous session creation. Without
CAPTCHA, automated bots can create unlimited anonymous sessions and upload
content up to the per-session file limits.

Dashboard path: Supabase Dashboard > Authentication > Settings > Bot and Abuse
Protection > Enable CAPTCHA Provider.

### 10.3 Storage Policy as Last Defense

Storage policies on `storage.objects` are the authoritative enforcement layer.
Client-side MIME checking, path construction, and file size checking are UX
conveniences only. The bucket-level settings and storage policies are the true
security boundary.

### 10.4 No Cross-Bucket Leakage

Policies are bucket-scoped. A policy for `user-photos` explicitly checks
`bucket_id = 'user-photos'`. This prevents a policy from accidentally
permitting access to objects in other buckets.

### 10.5 Server-Side Writes to generations Bucket

The `generations` bucket is written to by the AI provider or by the generation
pipeline, not by the client. When the bucket becomes private, server-side writes
must use service_role. No client-side INSERT policy should be created for the
`generations` bucket.

---

## Appendix: Quick Reference — Policy Names

| Policy name | Table | Operation | Bucket |
|---|---|---|---|
| user_photos_insert_own | storage.objects | INSERT | user-photos |
| user_photos_select_own | storage.objects | SELECT | user-photos |
| user_photos_delete_own | storage.objects | DELETE | user-photos |
| generations_select_own (future) | storage.objects | SELECT | generations |

## Appendix: Supabase Dashboard Actions Required (Not SQL)

The following settings must be changed in the Supabase Dashboard and cannot be
applied via SQL in most cases:

| Setting | Location | Value |
|---|---|---|
| user-photos file_size_limit | Storage > Buckets > user-photos > Edit | 10485760 |
| user-photos allowed_mime_types | Storage > Buckets > user-photos > Edit | image/jpeg, image/png, image/webp |
| generations file_size_limit | Storage > Buckets > generations > Edit | 52428800 |
| generations allowed_mime_types | Storage > Buckets > generations > Edit | image/jpeg, image/png, image/webp, video/mp4, video/webm |
| product-images file_size_limit | Storage > Buckets > product-images > Edit | 5242880 |
| product-images allowed_mime_types | Storage > Buckets > product-images > Edit | image/jpeg, image/png, image/webp |
