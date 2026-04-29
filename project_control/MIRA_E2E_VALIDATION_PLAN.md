# MIRA E2E Validation Plan

## Purpose

Validate MIRA as a real product flow, not just as a buildable Next.js app. This checklist confirms that onboarding, scan upload, product selection, try-on generation creation, and result polling work end-to-end with Supabase persistence.

## Preconditions

- Run the app locally with the intended environment loaded:

```bash
npm run dev
```

- Open the local app at `http://localhost:3000/es/onboarding`.
- Confirm `NEXT_PUBLIC_SUPABASE_URL` is present locally.
- Confirm `NEXT_PUBLIC_SUPABASE_ANON_KEY` is present locally.
- Confirm Supabase project access for table and storage inspection.
- Keep browser DevTools open on Console, Network, Application, and Storage views.
- Do not use real customer data.
- Do not use real customer photos.
- Do not share or commit JWTs, cookies, API keys, screenshots, logs, or exported data.
- Do not commit `.env`, `.env.local`, screenshots, logs, or exported Supabase data.

## Required Supabase Tables

- `users_profile`
- `user_assets`
- `generations`

## Required Supabase Bucket

- `user-photos`

## Test User

- Email: `qa-test+manual-001@example.com`
- Name: `QA Test User`
- Height: `170`
- Weight: `68`
- Usual size: `M`
- Build: `regular`
- Gender: `skip` or another fake QA-only value

Use only fake, non-sensitive profile data. Do not use real body data.

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

- Name: `QA Test User`
- Email: `qa-test+manual-001@example.com`
- Height: `170`
- Weight: `68`
- Size: `M`
- Build: `regular`
- Gender: `skip` or another fake QA-only value
- Submit the form.

4. In Supabase, verify `users_profile`:

- A new row exists for the test user.
- Email matches `qa-test+manual-001@example.com`.
- `name`, `height_cm`, `weight_kg`, `usual_size`, `build`, and `gender` match the submitted fake data.
- Timestamps are present if expected.
- No secret values or unrelated user data are exposed in the browser.

5. In browser DevTools, verify local storage:

- `localStorage.mira_profile_id` exists after onboarding.
- The value matches the expected profile/session identifier shape.
- The value does not expose JWTs, API keys, cookies, or unrelated user data.

6. Continue to:

```text
http://localhost:3000/es/scan
```

7. Upload at least one front scan photo using a safe synthetic or sample test image.

Use a dummy image that contains no real person, face, body, license plate, home, workplace, or private metadata.

8. In Supabase Storage, verify `user-photos`:

- A new object exists for the upload.
- The object path is scoped to the test user/session as expected.
- The file is readable only through the intended app/storage policy.
- No `.env`, token, local path, or unrelated user identifier appears in the object path.

9. In Supabase, verify `user_assets`:

- A new row exists for the uploaded photo.
- `asset_type` is correct for the front scan photo.
- `storage_path` points to the object in `user-photos`.
- Any user/session/profile reference matches the test user flow.

10. Open:

```text
http://localhost:3000/es/catalog
```

11. Select a product and navigate to the try-on page.

12. On `/es/tryon/[productId]`, verify the try-on page is ready:

- It should use `localStorage.mira_profile_id` to load the profile from `users_profile`.
- It should load scan assets from `user_assets` using the same profile id.
- If `mira_profile_id` is missing, the page should ask the user to complete onboarding.
- If front scan assets are missing, the page should ask the user to upload a scan.

13. Click the try-on CTA (`Probarme`).

14. In Supabase, verify `generations`:

- A new row exists after clicking the try-on CTA.
- Product identifier matches the selected product if the current implementation supports persisted product linkage.
- `user_profile_id` matches `localStorage.mira_profile_id`.
- If `user_profile_id` is null, record this as a FAIL because the flow should now pass `mira_profile_id` into generation creation.
- If `product_id` is null, document it as the current MVP limitation because local product IDs are not Supabase UUIDs yet.
- Status is present and valid for the mocked generation path.
- Provider metadata does not contain secrets.

15. Verify result polling:

- The app navigates to `/es/result/[generationId]` or otherwise exposes the generated result route.
- The result page polls the status endpoint.
- The page eventually shows the expected mock output.
- No infinite spinner, unhandled exception, or silent failure occurs.

16. Verify current flow-state behavior:

- Confirm `/es/tryon/[productId]` sends populated profile/photo data loaded from `mira_profile_id`, `users_profile`, and `user_assets`.
- Confirm legacy `mira_profile` / `mira_photos` keys are not required for the normal path.
- Confirm whether result display metadata survives a dev server restart. If not, document the in-memory metadata limitation.
- Confirm no generated provider call uses paid APIs during this validation.

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
- `generations` row is created with `user_profile_id` matching the profile id from onboarding.
- Any missing `product_id` linkage is explicitly documented as the local-product MVP limitation.
- Result page polling completes and displays mock output.
- No blocking console or network errors appear.
- No secrets or real customer data are exposed.
- Evidence is captured and attached to the validation report.
- Any manual verification gaps are recorded as `MANUAL_VERIFICATION_REQUIRED`; no unverified behavior is marked PASS.

## FAIL Criteria

- Any required page cannot be opened.
- A form submit appears successful but no Supabase row/object is created.
- Supabase row data does not match submitted test data.
- Storage upload fails or stores the file in the wrong bucket/path.
- Try-on CTA does not create a `generations` row.
- `generations.user_profile_id` is null or does not match `localStorage.mira_profile_id`.
- Result polling never resolves or returns an error state without explanation.
- Browser console/network errors indicate broken product behavior.
- Any secret, token, `.env` value, or unrelated customer data is exposed.
- The validation report claims PASS for Supabase persistence that was not actually checked in Supabase.
- Real customer photos or real personal data are used.

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
- `localStorage.mira_profile_id`
- Browser console screenshot showing no blocking errors, or showing the exact failure.
- Browser network screenshot filtered to failed requests, if any.
- Notes on whether `generations.product_id` and `generations.user_profile_id` were populated or intentionally null.
- Notes that try-on payload contained profile/photo data loaded from Supabase-backed profile/assets, or exact evidence if it did not.
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
- Do not share JWTs, cookies, API keys, refresh tokens, or Supabase service-role credentials.
- Do not paste secret values into reports, screenshots, logs, prompts, or blockers.
- Redact Supabase project identifiers if sharing outside the local repo.
- Delete test data only through explicit, human-approved cleanup steps.
- Do not modify production data.
