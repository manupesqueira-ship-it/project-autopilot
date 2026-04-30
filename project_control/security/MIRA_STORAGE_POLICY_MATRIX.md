# MIRA Storage Policy Matrix

> Draft storage policies for all Supabase Storage buckets.
> DO NOT APPLY until staging-tested. See rollback plan.
> Last updated: 2026-04-29

---

## Bucket Overview

| Bucket | Current | Target | Reason |
|---|---|---|---|
| user-photos | private, 0 policies | private, owner-only | Contains personal body photos |
| generations | public, 0 policies | PRIVATE, owner-only + signed URLs | Contains try-on outputs tied to user photos |
| product-images | public, 0 policies | public read, service_role write | Product catalog images, no PII |

---

## user-photos Bucket

### Path Convention
```
user-photos/{auth.uid()}/front_photo.{ext}
user-photos/{auth.uid()}/side_photo.{ext}
user-photos/{auth.uid()}/back_photo.{ext}
```

### Policies

| Operation | Policy Name | Rule |
|---|---|---|
| SELECT | user_photos_select_own | `bucket_id = 'user-photos' AND (storage.foldername(name))[1] = auth.uid()::text` |
| INSERT | user_photos_insert_own | `bucket_id = 'user-photos' AND (storage.foldername(name))[1] = auth.uid()::text` |
| UPDATE | user_photos_update_own | `bucket_id = 'user-photos' AND (storage.foldername(name))[1] = auth.uid()::text` |
| DELETE | user_photos_delete_own | `bucket_id = 'user-photos' AND (storage.foldername(name))[1] = auth.uid()::text` |

### Restrictions
- MIME: `image/jpeg`, `image/png`, `image/webp`
- Max size: 10 MB
- Rationale: Body photos should be high quality but not unlimited

---

## generations Bucket

### Path Convention
```
generations/{auth.uid()}/{generation_id}/output.png
generations/{auth.uid()}/{generation_id}/output.mp4
```

### Policies

| Operation | Policy Name | Rule |
|---|---|---|
| SELECT | generations_select_own | `bucket_id = 'generations' AND (storage.foldername(name))[1] = auth.uid()::text` |
| INSERT | N/A — server only | Server uses service_role for uploads |
| UPDATE | N/A — server only | Server uses service_role |
| DELETE | generations_delete_own | `bucket_id = 'generations' AND (storage.foldername(name))[1] = auth.uid()::text` |

### Signed URL Strategy
- Server generates signed URL (60-min expiry) for result page.
- Client never accesses generation files directly.
- Sharing: Future feature — generate longer-expiry signed URL or public share link.

### Restrictions
- MIME: `image/png`, `image/webp`, `video/mp4`
- Max size: 50 MB
- Rationale: Video outputs can be large

---

## product-images Bucket

### Path Convention
```
product-images/{product_id}/{variant}.{ext}
```

### Policies

| Operation | Policy Name | Rule |
|---|---|---|
| SELECT | product_images_public_read | `bucket_id = 'product-images'` (any authenticated or anon) |
| INSERT | N/A — service_role only | Admin uploads only |
| UPDATE | N/A — service_role only | Admin updates only |
| DELETE | N/A — service_role only | Admin deletes only |

### Restrictions
- MIME: `image/jpeg`, `image/png`, `image/webp`
- Max size: 5 MB

---

## Migration Steps

1. Apply storage policies via SQL (see `supabase/drafts/storage_candidate_policies.sql`).
2. Switch `generations` bucket from public to private in Dashboard.
3. Update generation-store to upload to `{auth.uid()}/{gen_id}/` path.
4. Update result page to fetch via signed URL instead of direct public URL.
5. Update scan page to upload to `{auth.uid()}/` path.
6. Test upload/download with anonymous auth user.
7. Test that cross-user access is denied.

---

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Existing files not in `{auth.uid()}/` path | Files become inaccessible after policies | Backfill paths or grandfather old files |
| Anonymous user token expires | User loses access to their files | Token refresh handled by Supabase SDK automatically |
| Large video uploads timeout | Generation fails | Server-side upload with service_role, chunked if needed |
