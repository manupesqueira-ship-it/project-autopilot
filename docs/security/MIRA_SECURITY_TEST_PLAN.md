# MIRA Security Test Plan

> A/B user test matrix for verifying RLS and storage policies.
> Execute ONLY in a disposable Supabase project or staging branch.
> Last updated: 2026-04-29

---

## Prerequisites

- [ ] Disposable Supabase project created (NOT the production project)
- [ ] Anonymous Sign-Ins enabled
- [ ] RLS enabled on all tables
- [ ] Policies applied from `supabase/drafts/rls_candidate_policies.sql`
- [ ] Storage policies applied from `supabase/drafts/storage_candidate_policies.sql`
- [ ] `generations` bucket switched to private

---

## Test Users

| User | Description | Setup |
|---|---|---|
| User A | Anonymous auth user | `signInAnonymously()` in Browser A / Incognito |
| User B | Different anonymous auth user | `signInAnonymously()` in Browser B / different Incognito |
| Service | Server-side (service_role) | API routes using `createServiceRoleServer()` |
| Anon (no auth) | No Supabase auth session | Direct REST call with only anon key |

---

## A/B User Security Test Matrix

### Table: users_profile

| # | Test | Actor | Expected | Pass? |
|---|---|---|---|---|
| T1 | User A creates profile | User A | SUCCESS — row has auth_user_id = A.uid | |
| T2 | User A reads own profile | User A | SUCCESS — returns own row | |
| T3 | User A reads User B profile | User A | FAIL — empty result | |
| T4 | User A updates own profile | User A | SUCCESS | |
| T5 | User A updates User B profile | User A | FAIL — 0 rows affected | |
| T6 | User A deletes User B profile | User A | FAIL — 0 rows affected | |
| T7 | No-auth reads any profile | Anon | FAIL — RLS blocks | |

### Table: user_assets

| # | Test | Actor | Expected | Pass? |
|---|---|---|---|---|
| T8 | User A inserts asset for own profile | User A | SUCCESS | |
| T9 | User A reads own assets | User A | SUCCESS | |
| T10 | User A reads User B assets | User A | FAIL — empty result | |
| T11 | User A deletes User B asset | User A | FAIL — 0 rows affected | |

### Table: generations

| # | Test | Actor | Expected | Pass? |
|---|---|---|---|---|
| T12 | Server creates generation for User A | Service | SUCCESS — service_role bypasses RLS | |
| T13 | User A reads own generation | User A | SUCCESS | |
| T14 | User A reads User B generation | User A | FAIL — empty result | |
| T15 | User A reads generation via status API | User A | SUCCESS — server verifies ownership | |
| T16 | User A reads User B generation via status API | User A | FAIL — 403 Forbidden | |
| T17 | Server updates generation status | Service | SUCCESS | |

### Storage: user-photos

| # | Test | Actor | Expected | Pass? |
|---|---|---|---|---|
| T18 | User A uploads to own path | User A | SUCCESS | |
| T19 | User A uploads to User B path | User A | FAIL — policy denies | |
| T20 | User A reads own photo | User A | SUCCESS | |
| T21 | User A reads User B photo | User A | FAIL — policy denies | |
| T22 | No-auth reads any photo | Anon | FAIL — private bucket | |
| T23 | Upload non-image MIME | User A | FAIL — MIME restriction | |
| T24 | Upload >10 MB file | User A | FAIL — size restriction | |

### Storage: generations

| # | Test | Actor | Expected | Pass? |
|---|---|---|---|---|
| T25 | Server uploads generation output | Service | SUCCESS | |
| T26 | User A reads own generation output | User A | SUCCESS (via signed URL) | |
| T27 | User A reads User B generation output | User A | FAIL — policy denies | |
| T28 | Direct URL access (no auth) | Anon | FAIL — bucket now private | |

### Storage: product-images

| # | Test | Actor | Expected | Pass? |
|---|---|---|---|---|
| T29 | Any user reads product image | User A | SUCCESS — public read | |
| T30 | User A uploads product image | User A | FAIL — service_role only | |

---

## Edge Cases

| # | Test | Expected |
|---|---|---|
| E1 | User with NULL auth_user_id reads tables | Empty results (no policy matches NULL) |
| E2 | Anonymous user converts to email | Same auth.uid(), all data accessible |
| E3 | Concurrent generation creation | Each generation linked to correct auth.uid() |
| E4 | Service role operations during RLS | All CRUD works (service_role bypasses) |
| E5 | Token refresh during long polling | SDK auto-refreshes, no access loss |

---

## Execution Protocol

1. Run all tests in disposable Supabase project.
2. Record pass/fail in this document.
3. If ANY T-test fails unexpectedly, STOP and review policies.
4. If ALL tests pass, schedule production rollout with rollback plan.
5. Production rollout must follow the migration sequence in the staging plan.
