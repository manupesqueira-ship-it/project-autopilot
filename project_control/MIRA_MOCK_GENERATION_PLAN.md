# MIRA Mock Generation Plan

## Status: EXISTING MOCK MODE AVAILABLE

## Current State

Both generation providers already have built-in mock modes that activate when API keys are absent:

### `lib/providers/openai-image.ts`
- If `OPENAI_API_KEY` is not set, returns a mock placeholder image URL after a 1.5s delay.
- No paid API call is made.
- This is the default in local development.

### `lib/providers/seedance-video.ts`
- If the BytePlus/Seedance API key is not set, returns a mock placeholder video URL.
- No paid API call is made.
- This is the default in local development.

## How Flow QA Should Avoid Paid Generation

1. **Don't set API keys in test environment.** The providers automatically mock.
2. **Playwright `page.route` interception** is the preferred approach for CI/E2E testing:
   - Intercept `POST /api/tryon/jobs` and return `{ generationId: "mock-qa-id", status: "processing_image" }`.
   - Intercept `GET /api/tryon/status/mock-qa-id` and return a mock completed generation.
   - This avoids any database writes and any provider calls.

## What API Endpoints Should Return in Mock Mode

### `POST /api/tryon/jobs` (mock intercept response)
```json
{
  "generationId": "mock-qa-00000000",
  "status": "processing_image"
}
```

### `GET /api/tryon/status/mock-qa-00000000` (mock intercept response)
```json
{
  "generationId": "mock-qa-00000000",
  "status": "completed",
  "imageUrl": "https://placehold.co/800x1000/1a1a1a/d9ff43?text=MIRA+QA",
  "videoUrl": null,
  "productName": "QA Test Product",
  "brandName": "QA Brand",
  "buyUrl": "https://example.com",
  "errorMessage": null
}
```

## Future: MOCK_GENERATION Environment Flag

A `MOCK_GENERATION=true` flag could be added to `app/api/tryon/jobs/route.ts` to:
- Skip database writes entirely.
- Return a hardcoded mock response.
- Allow the result page to be tested without any Supabase or provider dependency.

### Safety Rules for This Flag
- Must default to OFF (not set = real behavior).
- Must NOT be set in production (enforce via build check or runtime `NODE_ENV` guard).
- Must NOT call any paid API.
- Must NOT hide real errors in production.
- Must be clearly documented.

### Implementation Approach (Next Sprint)
```typescript
// In app/api/tryon/jobs/route.ts
if (process.env.MOCK_GENERATION === "true" && process.env.NODE_ENV !== "production") {
  return NextResponse.json({
    generationId: "mock-qa-" + crypto.randomUUID().slice(0, 8),
    status: "completed",
  });
}
```

## Preventing Accidental Production Use

- Guard with `NODE_ENV !== "production"`.
- Never include `MOCK_GENERATION` in production `.env`.
- Add a build-time check or lint rule if desired.
- Document in BLOCKERS.md.

## Decision: NOT implementing in this sprint

The existing mock behavior (no API keys = mock responses) is sufficient for local development. The `MOCK_GENERATION` flag and Playwright route interception are deferred to the next sprint when E2E Flow QA with form submission is unblocked.
