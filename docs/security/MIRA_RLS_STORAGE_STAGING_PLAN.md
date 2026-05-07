# MIRA RLS & Storage Staging Plan

> Master plan for enabling Row Level Security and Storage policies.
> All changes here are DRAFT. No live SQL execution until staging-tested.
> Last updated: 2026-04-29

---

## 1. Current State

| Item | Status |
|---|---|
| RLS enabled | NO — disabled on all tables |
| Table policies | 0 |
| Storage policies | 0 |
| Buckets | generations (public), product-images (public), user-photos (private) |
| Identity model | Anonymous Auth code ready, auth_user_id nullable |
| Ownership enforcement | None — status endpoint has no auth check |

## 2. Ownership Model

### 2a. users_profile

- **Primary key**: `id` (UUID)
- **Auth link**: `auth_user_id` references `auth.users(id)`
- **RLS strategy**: `auth.uid() = auth_user_id`
- **Anonymous users**: Get an `auth_user_id` via `signInAnonymously()` at onboarding.
- **Email conversion**: When anonymous user converts (email/OAuth), `auth_user_id` stays the same — Supabase handles identity linking. No profile migration needed.
- **localStorage compatibility**: `mira_profile_id` (localStorage) stores the Supabase `users_profile.id`. Used for client-side routing only. Not a security boundary.

### 2b. user_assets

- **Current FK**: `user_profile_id` references `users_profile(id)`
- **RLS strategy**: JOIN-based — `user_profile_id IN (SELECT id FROM users_profile WHERE auth_user_id = auth.uid())`
- **Recommended improvement**: Add `auth_user_id UUID REFERENCES auth.users(id)` directly to avoid JOIN overhead. Denormalization is acceptable for a security boundary.
- **Decision needed**: Direct column (recommended) vs JOIN-only.

### 2c. generations

- **Current FK**: `user_profile_id` references `users_profile(id)` — nullable
- **RLS strategy**: Same JOIN approach or direct `auth_user_id` column.
- **Recommended improvement**: Add `auth_user_id UUID REFERENCES auth.users(id)` directly.
- **Risk**: Status endpoint currently returns any generation by UUID with no ownership check. See Section 8.

### 2d. profile_id vs auth_user_id Decision

| Approach | Pros | Cons |
|---|---|---|
| `auth_user_id` (recommended) | Supabase-native, RLS uses `auth.uid()` directly, survives profile deletion | Requires backfill for existing rows |
| `profile_id` via JOIN | No schema change | Slower, complex policies, breaks if profile deleted |

**Recommendation**: Use `auth_user_id` as the ownership column everywhere. Backfill existing rows with `UPDATE ... SET auth_user_id = (SELECT auth_user_id FROM users_profile WHERE id = user_profile_id)`.

## 3. Storage Path Strategy

### 3a. Path Convention: `{auth.uid()}/{category}/{filename}`

Examples:
- `user-photos/{auth.uid()}/front_photo.jpg`
- `user-photos/{auth.uid()}/side_photo.jpg`
- `generations/{auth.uid()}/{generation_id}/output.png`

Using `auth.uid()` instead of `profile_id` because:
- Storage policies reference `auth.uid()` natively.
- Survives profile recreation.
- No need to look up profile before upload.

### 3b. Bucket Strategies

| Bucket | Access | Strategy |
|---|---|---|
| user-photos | PRIVATE | Owner-only read/write via `auth.uid()` path prefix |
| generations | Switch to PRIVATE | Owner-only read, signed URLs for sharing |
| product-images | PUBLIC read | Anyone can read, only service_role writes |

### 3c. Signed URL Strategy

- Generation outputs: Server generates signed URLs (60-minute expiry) via service_role.
- User photos: Never exposed publicly. Client reads via authenticated Supabase storage SDK.
- Product images: Public bucket, no signing needed.

### 3d. MIME / File Size Recommendations

| Bucket | Allowed MIME | Max Size |
|---|---|---|
| user-photos | image/jpeg, image/png, image/webp | 10 MB |
| generations | image/png, image/webp, video/mp4 | 50 MB |
| product-images | image/jpeg, image/png, image/webp | 5 MB |

## 4. Anonymous User Lifecycle

```
1. User opens MIRA → signInAnonymously() → gets auth.uid()
2. Onboarding → creates users_profile with auth_user_id = auth.uid()
3. Scan → uploads to user-photos/{auth.uid()}/...
4. Try-on → creates generation with auth_user_id = auth.uid()
5. Result → status endpoint verified against auth.uid()
6. (Future) Email conversion → auth.uid() unchanged, profile persists
```

## 5. Migration Sequence

**Phase A — Schema prep (requires staging test)**:
1. Add `auth_user_id` column to `user_assets` and `generations`.
2. Backfill from `users_profile` JOIN.
3. Add indexes on new columns.

**Phase B — Enable RLS**:
1. Enable RLS on `users_profile`, `user_assets`, `generations`, `events`.
2. Apply SELECT/INSERT/UPDATE/DELETE policies per table.
3. Verify service_role bypass works for server-side writes.

**Phase C — Storage policies**:
1. Apply storage policies per bucket.
2. Switch `generations` bucket to private.
3. Update result page to use signed URLs.

**Phase D — Hardening**:
1. Enable CAPTCHA.
2. Set production Site URL.
3. Configure redirect URLs.
4. Enable leaked-password protection.

## 6. Rollback Plan

See: `project_control/security/MIRA_SECURITY_ROLLBACK_PLAN.md`

## 7. Test Plan

See: `project_control/security/MIRA_SECURITY_TEST_PLAN.md`

## 8. Ownership Risk: Status Endpoint

**Critical finding**: `GET /api/tryon/status/[generationId]` returns generation data for ANY UUID. No auth check. Any client that knows or guesses a generation ID can see another user's result, including image/video URLs.

**Current mitigation**: Generation IDs are UUIDv4 (unguessable), but this is security-through-obscurity, not a real access control.

**Required fix before real data**:
1. Add auth verification to status endpoint.
2. Compare `generation.auth_user_id` with requesting user's `auth.uid()`.
3. Return 403 if mismatch.

**Safe interim fix implemented**: See `MIRA_SECURITY_OWNERSHIP_FINDINGS.md`.

## 9. Dependencies

- Anonymous Sign-Ins must be enabled in Supabase Dashboard.
- `SUPABASE_SERVICE_ROLE_KEY` must be available server-side.
- All existing rows need `auth_user_id` backfill before RLS enable.
- Client storage upload code needs path convention update.
