# MIRA Security Ownership Findings

> API route and data ownership review.
> Last updated: 2026-04-29

---

## Summary

| Endpoint / Module | Ownership Check | Risk Level | Status |
|---|---|---|---|
| `GET /api/tryon/status/[generationId]` | NONE | HIGH | Documented, fix needed before real data |
| `POST /api/tryon/jobs` | NONE | MEDIUM | profileId from client, no server auth |
| `lib/generation-store.ts` (writes) | N/A — service_role | LOW | Correct: server-side writes bypass RLS |
| `lib/generation-store.ts` (reads) | Anon client | MEDIUM | Will respect RLS once enabled |
| Result page polling | No auth context | MEDIUM | Polls status endpoint without auth |
| Mock mode | Bypasses everything | NONE (intentional) | Production-guarded |

---

## Finding 1: Status Endpoint Has No Ownership Check

**File**: `app/api/tryon/status/[generationId]/route.ts`
**Lines**: 24-41

**Issue**: `getGeneration(id)` fetches any generation by UUID. No check that the requesting user owns it. Any client that knows a generation UUID can read another user's result (image URL, video URL, status, error message).

**Current mitigation**: UUIDs are random (UUIDv4), so guessing is impractical. But this is security-through-obscurity, not a real access control.

**Impact before real data**: LOW — only dev/test data exists.
**Impact with real data**: HIGH — leaks user try-on images.

**Required fix**:
1. Extract auth user from request (via Supabase auth session).
2. Compare `generation.userProfileId` → `users_profile.auth_user_id` with requesting `auth.uid()`.
3. Return 403 if mismatch.
4. OR: Rely on RLS (getGeneration uses anon client, so RLS will filter). But server-side check is defense-in-depth.

**When to fix**: Before storing real user photos / enabling real generation.

---

## Finding 2: Jobs Endpoint Trusts Client-Provided profileId

**File**: `app/api/tryon/jobs/route.ts`
**Lines**: 14-16, 70-78

**Issue**: `profileId` comes from the client request body. The server does not verify that this profileId belongs to the authenticated user. A malicious client could submit someone else's profileId.

**Current mitigation**: profileId is optional and only used as metadata (`userProfileId`). The actual generation is fired by the server, not the client.

**Impact before real data**: LOW — no real user differentiation.
**Impact with real data**: MEDIUM — generation could be attributed to wrong user.

**Required fix**:
1. Extract auth user from request.
2. Verify profileId belongs to `auth.uid()` by querying `users_profile`.
3. Or ignore client profileId entirely and look up profile from auth session.

---

## Finding 3: Generation Store Read Uses Anon Client

**File**: `lib/generation-store.ts`
**Lines**: 84-97

**Detail**: `getGeneration()` uses `createServer()` (anon client). This is actually CORRECT for RLS — once RLS is enabled, this query will only return rows where the auth context matches the policy. However, the status API route does not pass auth context through, so this may not work as expected.

**Action**: Verify that Next.js API routes correctly propagate the Supabase auth session from the request cookies to `createServer()`. If they do, RLS will enforce ownership automatically.

---

## Finding 4: Result Page Polls Without Auth Context

**File**: Result page at `app/[locale]/(app)/result/[generationId]/page.tsx`

**Detail**: The result page polls `/api/tryon/status/[generationId]` on an interval. The fetch call uses the browser's cookies, so if Supabase auth session is in cookies, it should be propagated. But this needs verification.

**Action**: Confirm cookie-based auth propagation in the status route handler.

---

## Finding 5: Mock Mode Intentionally Bypasses All Checks

**Files**: `lib/qa-mock.ts`, both API routes

**Detail**: When `NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true`, the jobs route returns a fake generation ID without any Supabase interaction. The status route returns mock data for mock IDs. This is intentional and correctly guarded:
- Defaults to OFF.
- Blocked in production (`NODE_ENV === "production"`).
- No Supabase writes, no paid API calls.

**Action**: None needed. Design is correct.

---

## Safe Improvements (No Live SQL, No Mock E2E Breakage)

None implemented in this sprint. All ownership fixes require either:
1. RLS to be enabled (which requires Anonymous Sign-Ins + staging test), or
2. Auth session extraction in API routes (which needs end-to-end verification with live Supabase).

Both are blocked on external Supabase Dashboard actions documented in BLOCKERS.md.

---

## Next Sprint Requirements

1. Enable Anonymous Sign-Ins → auth session available in API routes.
2. Add auth verification to status endpoint (extract `auth.uid()`, compare with generation owner).
3. Add auth verification to jobs endpoint (verify profileId belongs to requesting user).
4. Enable RLS as defense-in-depth behind the API-level checks.
5. Test with A/B user matrix from `MIRA_SECURITY_TEST_PLAN.md`.
