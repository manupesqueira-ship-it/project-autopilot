# MIRA RLS Decision Matrix

> Compare options for each security/ownership decision.
> These decisions must be made BEFORE enabling RLS.

Status: PENDING HUMAN DECISIONS
Last updated: 2026-04-29

---

## 1. user_assets Ownership Strategy

How does RLS determine which user owns a user_assets row?

| Option | Security | Impl. Complexity | Migration | Flow QA Impact | MVP Rec. |
|---|---|---|---|---|---|
| **A. JOIN via users_profile** | Good. Policy JOINs `user_profile_id` to `users_profile.auth_user_id`. | Low (no schema change). | None. | Transparent. | Acceptable |
| **B. Direct auth_user_id column** | Better. Direct `auth_user_id = auth.uid()` check, no JOIN. | Medium (ALTER TABLE + code change in scan). | Need to backfill or delete orphan rows. | Transparent. | **Recommended** |

**Trade-off:** Option B is faster for queries and simpler policies, but requires adding a column and updating the scan upload code. Option A avoids schema changes but policies are more complex and slower.

---

## 2. generations Ownership Strategy

How does RLS determine which user owns a generations row?

| Option | Security | Impl. Complexity | Migration | Flow QA Impact | MVP Rec. |
|---|---|---|---|---|---|
| **A. JOIN via users_profile** | Good. `user_profile_id` JOINs to `users_profile.auth_user_id`. | Low. | None. | Transparent. | Acceptable |
| **B. Direct auth_user_id column** | Better. Direct ownership check. | Medium (ALTER TABLE + code change in generation-store). | Backfill needed. | Transparent. | **Recommended** |
| **C. Server-only via service_role** | Different model. No RLS SELECT policy for users; server reads/writes with service_role, client reads via API route. | Low (no RLS needed if all access is server-side). | None. | Must ensure status API route exists and works. | Not recommended for MVP (limits future flexibility). |

**Trade-off:** Option C avoids RLS on generations entirely but moves all access to server API routes. This works today (status endpoint already exists) but limits future features like direct client queries.

---

## 3. Storage Path Strategy

What folder structure should storage objects use?

| Option | Security | Impl. Complexity | Migration | Flow QA Impact | MVP Rec. |
|---|---|---|---|---|---|
| **A. Keep {profileId}/...** | Requires JOIN policy to verify ownership. | Low (no code change). | None. | Transparent. | Acceptable for MVP |
| **B. Switch to {auth.uid()}/...** | Simple folder-based ownership: `(storage.foldername(name))[1] = auth.uid()`. | Medium (update scan code). | Must move or re-upload existing files. | Flow QA skip-photos unaffected. | **Recommended long-term** |
| **C. Hybrid** | Keep existing paths, add new uploads with auth.uid(). | Complex (two path formats, two policies). | Gradual. | Complex to test. | Not recommended |

**Trade-off:** Option B gives the simplest storage policies but requires migrating existing files. For MVP with disposable test data, Option B is cleanest (just delete old files).

---

## 4. generations Bucket Visibility

Should the generations bucket (try-on outputs) remain public?

| Option | Security | Impl. Complexity | Migration | Flow QA Impact | MVP Rec. |
|---|---|---|---|---|---|
| **A. Keep public** | Anyone with URL can view any user's try-on results. | None. | None. | Transparent. | **Acceptable for MVP** |
| **B. Make private + signed URLs** | Only the owner can access results. Server generates signed URLs. | Medium (add signed URL generation in status API route). | None (just flip bucket setting). | Mock mode unaffected (uses local SVG). | Recommended for launch |

**Trade-off:** For MVP with test data, public is fine. Before real user photos are generated, switch to private.

---

## 5. product-images Bucket Visibility

Should product images remain public?

| Option | Security | Impl. Complexity | Migration | Flow QA Impact | MVP Rec. |
|---|---|---|---|---|---|
| **A. Keep public** | Product images are catalog content, not user data. Intentionally public. | None. | None. | Transparent. | **Recommended** |
| **B. Make private** | Unnecessary restriction on catalog content. | Medium. | None. | Would break image loading. | Not recommended |

**Decision:** Keep public. Product images are not sensitive.

---

## Summary of Recommendations for MVP

| Decision | Recommended Option | Status |
|---|---|---|
| user_assets ownership | B. Direct auth_user_id column | PENDING |
| generations ownership | B. Direct auth_user_id column | PENDING |
| Storage paths | B. Switch to {auth.uid()}/... | PENDING |
| generations bucket | A. Keep public for MVP | PENDING |
| product-images bucket | A. Keep public | DECIDED |

---

## How to Finalize

1. Human reviews this matrix and marks decisions.
2. Update MIRA_RLS_STORAGE_MIGRATION_DRAFT.md with chosen options.
3. Implement schema changes (ALTER TABLE) in a staging branch.
4. Test with disposable data.
5. Apply to production only after staging verification.
