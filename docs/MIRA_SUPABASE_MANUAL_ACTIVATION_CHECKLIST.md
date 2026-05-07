# MIRA Supabase Manual Activation Checklist

> These steps must be performed manually in the Supabase Dashboard.
> Do NOT automate these. Do NOT run SQL from this document.
> Complete each step in order and verify before proceeding.

Status: PENDING
Last updated: 2026-04-29

---

## A. Enable Anonymous Sign-Ins

**Where:** Supabase Dashboard > Authentication > Providers > Anonymous Sign-Ins

**Steps:**
1. Open https://supabase.com/dashboard/project/vtaqyammimmgxlkqwjat/auth/providers
2. Find "Anonymous Sign-Ins" toggle.
3. Enable it.
4. Save.

**Expected effect:**
- `getOrCreateAnonymousUser()` in `lib/supabase/auth.ts` will now succeed.
- New onboarding submissions will populate `auth_user_id` in `users_profile`.
- `auth.uid()` becomes available for future RLS policies.

**How to verify:**
1. Restart dev server: `npm run dev`
2. Open http://localhost:3000/es/onboarding
3. Fill out and submit a test profile.
4. In Supabase Dashboard > Table Editor > users_profile, check the latest row.
5. `auth_user_id` should be a non-null UUID.

---

## B. Set SUPABASE_SERVICE_ROLE_KEY Locally

**Where:** Your local `.env.local` file (NEVER commit this)

**Steps:**
1. Open https://supabase.com/dashboard/project/vtaqyammimmgxlkqwjat/settings/api
2. Copy the `service_role` secret key (the one labeled "secret", NOT the publishable one).
3. Add to `.env.local`:
   ```
   SUPABASE_SERVICE_ROLE_KEY=your-copied-key-here
   ```
4. Restart dev server.

**Expected effect:**
- `createServiceRoleServer()` in `lib/supabase/server.ts` will use the real service_role key.
- Server-side writes to `generations` will work correctly.
- The `ALLOW_SUPABASE_ANON_SERVER_FALLBACK` workaround is no longer needed.

**How to verify:**
1. Start dev server, complete onboarding + scan flow.
2. On the tryon page, click "Try on" for a product.
3. Check server logs — no "SUPABASE_SERVICE_ROLE_KEY is not set" error.
4. Check `generations` table — new row should appear.

**Safety:**
- NEVER commit `.env.local`.
- NEVER paste the key into chat, logs, or screenshots.
- `.env.local` is already in `.gitignore`.

---

## C. CAPTCHA / Attack Protection

**Where:** Supabase Dashboard > Authentication > Attack Protection

**When:** Before any public-facing testing or sharing URLs externally.

**Steps:**
1. Open Auth > Attack Protection.
2. Enable hCaptcha or Cloudflare Turnstile.
3. Add the site key to your frontend configuration if required.

**Why it matters:**
- Without CAPTCHA, anonymous sign-in and email sign-up endpoints are unprotected.
- Bots can create unlimited `auth.users` rows.
- This is low-risk for private local dev but critical before any public URL is shared.

**MVP recommendation:** Enable Turnstile (simpler) before first external test.

---

## D. Site URL / Redirect URLs

**Where:** Supabase Dashboard > Authentication > URL Configuration

**Current state:**
- Site URL: `http://localhost:3000`
- Redirect URLs: empty

**Steps for dev:**
- Site URL is fine as `http://localhost:3000` for local dev.
- No changes needed until deployment.

**Steps for production (future):**
1. Set Site URL to your production domain (e.g., `https://mira.yourdomain.com`).
2. Add Redirect URLs for:
   - Production: `https://mira.yourdomain.com/**`
   - Staging: `https://staging.mira.yourdomain.com/**`
   - Local: `http://localhost:3000/**`
3. This affects email confirmation links, password reset, and OAuth callbacks.

---

## E. Bucket Restrictions

**Where:** Supabase Dashboard > Storage > Buckets

**Current state:**
- All 3 buckets have no `file_size_limit` or `allowed_mime_types`.

**Do NOT change yet.** Wait until the storage path strategy is decided (see MIRA_RLS_DECISION_MATRIX.md).

**Planned restrictions (for future sprint):**

| Bucket | file_size_limit | allowed_mime_types |
|---|---|---|
| user-photos | 10 MB | image/jpeg, image/png, image/webp |
| generations | 50 MB | image/jpeg, image/png, image/webp, video/mp4 |
| product-images | 10 MB | image/jpeg, image/png, image/webp |

---

## F. RLS (Row Level Security)

**DO NOT ENABLE YET.**

RLS must be tested on staging or with disposable data before enabling on the live project.

**Prerequisites before enabling RLS:**
1. Anonymous Sign-Ins enabled and verified (Step A).
2. `auth_user_id` confirmed populated on new rows.
3. Decision made on ownership strategy (see MIRA_RLS_DECISION_MATRIX.md).
4. Existing test data cleaned or backfilled.
5. SQL reviewed and approved.
6. Staging test completed.

See: `project_control/MIRA_RLS_STORAGE_MIGRATION_DRAFT.md`

---

## Completion Tracking

| Step | Status | Verified by | Date |
|---|---|---|---|
| A. Anonymous Sign-Ins | PENDING | | |
| B. Service Role Key | PENDING | | |
| C. CAPTCHA | PENDING | | |
| D. Site URL | PENDING (dev OK) | | |
| E. Bucket restrictions | DEFERRED | | |
| F. RLS | DEFERRED | | |
