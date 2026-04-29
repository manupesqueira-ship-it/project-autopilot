# MIRA E2E Validation Plan

## Purpose

Validate MIRA as a real product flow, not just as a buildable Next.js app. This checklist confirms that onboarding, scan upload, product selection, try-on generation creation, and result polling work end-to-end with Supabase persistence.

## Preconditions

- Run the app locally with the intended environment loaded.
- Confirm `NEXT_PUBLIC_SUPABASE_URL` is present locally.
- Confirm `NEXT_PUBLIC_SUPABASE_ANON_KEY` is present locally.
- Confirm Supabase project access for table and storage inspection.
- Do not use real customer data.
- Do not commit `.env`, `.env.local`, screenshots, logs, or exported Supabase data.

## Required Supabase Tables

- `users_profile`
- `user_assets`
- `generations`

## Required Supabase Bucket

- `user-photos`

## Test User

- Email: `qa-test+manual-001@example.com`

Use obviously fake, non-sensitive profile data for all other fields.

## Flow

`onboarding -> scan -> catalog/product -> tryon -> result polling`

## Manual Validation Steps

1. Start the app:

```bash
npm run dev
```

2. Open:

```text
http://localhost:3000/es/onboarding
```

3. Complete onboarding with the test user:

- Email: `qa-test+manual-001@example.com`
- Use fake/non-sensitive values for name, body profile, sizing, preferences, and any optional fields.
- Submit the form.

4. In Supabase, verify `users_profile`:

- A new row exists for the test user.
- Email matches `qa-test+manual-001@example.com`.
- Profile fields match the submitted fake data.
- Timestamps are present if expected.
- No secret values or unrelated user data are exposed in the browser.

5. Continue to:

```text
http://localhost:3000/es/scan
```

6. Upload at least one front scan photo using a safe test image.

7. In Supabase Storage, verify `user-photos`:

- A new object exists for the upload.
- The object path is scoped to the test user/session as expected.
- The file is readable only through the intended app/storage policy.
- No `.env`, token, local path, or unrelated user identifier appears in the object path.

8. In Supabase, verify `user_assets`:

- A new row exists for the uploaded photo.
- `asset_type` is correct for the front scan photo.
- `storage_path` points to the object in `user-photos`.
- Any user/session/profile reference matches the test user flow.

9. Open:

```text
http://localhost:3000/es/catalog
```

10. Select a product and navigate to the try-on page.

11. On `/es/tryon/[productId]`, click the try-on CTA (`Probarme`).

12. In Supabase, verify `generations`:

- A new row exists after clicking the try-on CTA.
- Product identifier matches the selected product.
- User/session/profile reference matches the test flow.
- Status is present and valid for the mocked generation path.
- Provider metadata does not contain secrets.

13. Verify result polling:

- The app navigates to `/es/result/[generationId]` or otherwise exposes the generated result route.
- The result page polls the status endpoint.
- The page eventually shows the expected mock output.
- No infinite spinner, unhandled exception, or silent failure occurs.

## Console And Network Checks

During the full flow, watch browser DevTools for:

- JavaScript console errors.
- React hydration errors.
- Failed route loads.
- Failed Supabase requests.
- 401/403/404/500 responses.
- CORS errors.
- Requests containing secret values.
- Repeated polling that never resolves.

## PASS Criteria

- Onboarding form submits successfully.
- `users_profile` row is created with correct fake test data.
- Scan upload succeeds.
- `user-photos` contains the uploaded test image.
- `user_assets` row is created with correct asset type and storage path.
- Catalog/product navigation works.
- Try-on CTA creates a generation.
- `generations` row is created with correct product and user/session linkage.
- Result page polling completes and displays mock output.
- No blocking console or network errors appear.
- No secrets or real customer data are exposed.
- Evidence is captured and attached to the validation report.

## FAIL Criteria

- Any required page cannot be opened.
- A form submit appears successful but no Supabase row/object is created.
- Supabase row data does not match submitted test data.
- Storage upload fails or stores the file in the wrong bucket/path.
- Try-on CTA does not create a `generations` row.
- Result polling never resolves or returns an error state without explanation.
- Browser console/network errors indicate broken product behavior.
- Any secret, token, `.env` value, or unrelated customer data is exposed.

## Evidence To Capture

- Screenshot of each app step:
  - onboarding completed
  - scan upload completed
  - catalog/product selected
  - try-on CTA/result transition
  - result page output
- Supabase screenshots or redacted notes for:
  - `users_profile`
  - `user_assets`
  - `generations`
  - `user-photos`
- Browser console screenshot showing no blocking errors, or showing the exact failure.
- Browser network screenshot filtered to failed requests, if any.
- Current git status after validation.
- A short summary of PASS/FAIL with timestamps.

## What To Write To BLOCKERS.md If Failure Occurs

Use this format:

```md
### YYYY-MM-DD HH:MM UTC - MIRA E2E validation failure: short title

Status: open
Severity: blocking
Source: manual-e2e

Question or blocker:
Describe the failing step, route, Supabase table/bucket, expected result, and actual result.

Evidence:
- Screenshot/report path or brief redacted evidence note.
- Console/network error if relevant.

Recommended action:
Specific next fix or investigation step.
```

## Customer Data Safety Rules

- Use only the fake test user `qa-test+manual-001@example.com`.
- Do not upload real personal photos.
- Do not paste secret values into reports, screenshots, logs, prompts, or blockers.
- Redact Supabase project identifiers if sharing outside the local repo.
- Delete test data only through explicit, human-approved cleanup steps.
- Do not modify production data.
