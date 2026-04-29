# MIRA Local Auth Verification Plan

> Run this plan after completing Steps A and B of MIRA_SUPABASE_MANUAL_ACTIVATION_CHECKLIST.md.
> This verifies that Anonymous Auth works end-to-end in local development.

Status: PENDING
Last updated: 2026-04-29

---

## Prerequisites

- [ ] Anonymous Sign-Ins enabled in Supabase Dashboard.
- [ ] SUPABASE_SERVICE_ROLE_KEY added to `.env.local`.
- [ ] Dev server restarted after changes.

---

## Step-by-Step Verification

### 1. Restart dev server

```powershell
npm run dev
```

Confirm: server starts without errors at http://localhost:3000.

### 2. Open onboarding

Navigate to: http://localhost:3000/es/onboarding

### 3. Create test profile

Fill in:
- Name: `Auth Verification Test`
- Email: `auth-test@example.com`
- Height: `175`
- Weight: `70`
- Size: M
- Build: Regular
- Gender: Skip

Click the submit button.

### 4. Check users_profile latest row

Open Supabase Dashboard > Table Editor > users_profile.
Sort by `created_at` descending.

**Verify:**
- [ ] New row exists with name "Auth Verification Test".
- [ ] `auth_user_id` is a non-null UUID (e.g., `a1b2c3d4-...`).
- [ ] `id` is a valid UUID (this is the profile ID stored in localStorage).

### 5. Verify auth_user_id is non-null

If `auth_user_id` is null:
- Anonymous Sign-Ins may not be enabled. Check Dashboard > Auth > Providers.
- Check browser console for `[mira/auth] Anonymous sign-in unavailable` warning.
- The `getOrCreateAnonymousUser()` function returns null when anonymous auth is disabled.

### 6. Go to scan

After successful onboarding submit, you should be redirected to `/es/scan`.

### 7. Skip photos

Click "Skip photos" button. This navigates to `/es/catalog` with zero Supabase writes.

### 8. Verify localStorage

Open browser DevTools > Application > Local Storage > http://localhost:3000.

**Verify:**
- [ ] `mira_profile_id` key exists with a UUID value.
- [ ] This UUID matches the `id` from the users_profile row.

### 9. Verify no paid generation

Navigate to any product (e.g., `/es/tryon/adidas-trefoil-tee`).
The "Try on" button should appear but will use mock mode only if `NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true`.
Do NOT click "Try on" unless running in mock mode — it will attempt paid generation.

### 10. Run Flow QA checks

```powershell
python -B project_autopilot/flow_qa.py --project mira --run mira_route_readiness
python -B project_autopilot/flow_qa.py --project mira --run mira_selector_readiness
python -B project_autopilot/flow_qa.py --project mira --run mira_onboarding_safe_dry_flow
```

**Expected:** All PASS (dev server must be running).

### 11. Run backend audit

```powershell
python -B project_autopilot/agent_loop.py --project mira --backend-audit
```

**Expected:** PARTIAL_READY (RLS still disabled, which is expected).

### 12. Expected results summary

| Check | Expected |
|---|---|
| Onboarding submit | Success, redirects to /scan |
| users_profile.auth_user_id | Non-null UUID |
| localStorage mira_profile_id | Present, matches profile ID |
| Server logs | No service_role key errors |
| Flow QA route readiness | PASS |
| Flow QA selector readiness | PASS or WARN (result page skipped) |
| Backend audit | PARTIAL_READY |

### 13. Failure diagnosis

**If auth_user_id is null:**
- Check Supabase Dashboard > Auth > Providers > Anonymous Sign-Ins is ON.
- Check browser console for auth warnings.
- Ensure dev server was restarted after enabling anonymous sign-ins.

**If onboarding fails to submit:**
- Check browser console for Supabase errors.
- Verify `.env.local` has correct `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
- Check Supabase Dashboard > Table Editor for users_profile table access.

**If generation-store errors appear:**
- Check `.env.local` has `SUPABASE_SERVICE_ROLE_KEY`.
- If not set, generation writes will fail with "SUPABASE_SERVICE_ROLE_KEY is not set" unless `ALLOW_SUPABASE_ANON_SERVER_FALLBACK=true` is set.

**If Flow QA fails:**
- Check dev server is running on port 3000.
- Check Playwright is installed: `pip install playwright && playwright install`
