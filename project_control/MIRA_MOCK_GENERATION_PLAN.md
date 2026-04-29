# MIRA Mock Generation Plan

## Status: IMPLEMENTED

## Implementation (2026-04-29)

QA mock mode is now fully implemented with the `NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true` environment flag.

### Architecture

1. **`lib/qa-mock.ts`** — Shared utility module:
   - `isQaMockMode()`: Returns true only when `NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true` AND `NODE_ENV !== "production"`.
   - `isQaMockGenerationId(id)`: Checks if a generation ID starts with `qa-mock-generation-`.
   - `QA_MOCK_PREFIX`: The mock generation ID prefix.
   - Production guard: If the flag is set in production, it logs an error and returns false.

2. **`app/api/tryon/jobs/route.ts`** — Mock job creation:
   - When `isQaMockMode()` is true, returns a mock generation ID immediately.
   - Skips product validation (profile, photos).
   - Does NOT call `createGeneration()` (no Supabase write).
   - Does NOT call `generateTryOnImage` or `generateTryOnVideo` (no paid APIs).
   - Returns `{ generationId: "qa-mock-generation-<timestamp>", status: "processing_image", isMock: true }`.

3. **`app/api/tryon/status/[generationId]/route.ts`** — Mock status polling:
   - If `generationId` starts with `qa-mock-generation-`, returns mock completed response.
   - Does NOT call `getGeneration()` (no Supabase read).
   - Returns completed status with `/qa-mock-result.svg` as image URL.
   - Normal generation IDs follow the existing real path.

4. **`public/qa-mock-result.svg`** — Mock result placeholder:
   - Minimal SVG showing "MIRA QA MOCK" text.
   - No external dependencies, no binary files.

### How to Run Full Mock E2E

```bash
# Start dev server with mock mode enabled
NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true npm run dev

# Run full E2E mock flow
python -B project_autopilot/flow_qa.py --project mira --run mira_full_e2e_mock_flow
```

### Safety Guarantees

- Flag defaults OFF (not set = real behavior).
- Production guard: `isQaMockMode()` always returns false when `NODE_ENV === "production"`.
- Mock generation IDs are deterministic (`qa-mock-generation-*`) so they can be detected.
- No paid provider code is called in mock path.
- No Supabase writes in mock path (jobs route skips `createGeneration()`).
- No Supabase reads in mock path (status route skips `getGeneration()` for mock IDs).
- `.env` and `.env.local` are NOT modified.

### Scan Flow Strategy

The scan page already has a "Skip photos" button (`btn-skip-photos`) that navigates directly to catalog without any Supabase writes. Flow QA uses this existing skip path.

The tryon page uses legacy localStorage fallback (`mira_profile` + `mira_photos` keys) when Supabase data is not available. Flow QA sets these in localStorage via Playwright before navigating to the tryon page.

### What This Does NOT Replace

- Real Supabase integration testing (requires RLS, policies, service_role key).
- Real paid generation testing (requires API keys).
- Real customer data flow (requires security alignment).
- Production deployment readiness (requires all blockers resolved).

This mock mode is for **automated QA validation of the user journey** only.
