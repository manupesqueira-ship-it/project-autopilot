# Product Validation Report

## Validation Title

{{PROJECT_NAME}} Product Validation

## Date / Time

{{TIMESTAMP_UTC}}

## Tester / Tool

Project Autopilot / manual product validation

## Project

- Project ID: `{{PROJECT_ID}}`
- Dev server URL used: `{{DEV_SERVER_URL}}`

## Browser QA Result

- Result:
- Mode:
- Report path:

## Routes Checked

- [ ] `/es`
- [ ] `/en`
- [ ] `/es/onboarding`
- [ ] `/es/scan`
- [ ] `/es/catalog`

## Console / Network Checks Available

- Console checks available: no
- Network checks available: HTTP status only unless Playwright is installed
- Notes:

## Supabase Checks Performed

- Performed: no
- `users_profile`:
- `user_assets`:
- `generations`:
- `user-photos` storage:
- `localStorage.mira_profile_id`:

## Manual Steps Performed

- [ ] Opened onboarding route
- [ ] Submitted onboarding with `qa-test+manual-001@example.com`
- [ ] Verified `users_profile`
- [ ] Uploaded safe test photo
- [ ] Verified `user-photos`
- [ ] Verified `user_assets`
- [ ] Selected catalog product
- [ ] Triggered try-on
- [ ] Verified `generations`
- [ ] Verified result polling

## Evidence Captured

- Browser QA report:
- Screenshots:
- Supabase evidence notes:
- Console/network notes:

## Acceptance Criteria

- [ ] Onboarding submits successfully
- [ ] `users_profile` row is created
- [ ] Scan upload succeeds
- [ ] `user-photos` object is created
- [ ] `user_assets` row is created
- [ ] Catalog/product navigation works
- [ ] Try-on creates a generation
- [ ] `generations` row is created
- [ ] Result polling displays mock output
- [ ] No blocking console/network errors
- [ ] No secrets, JWTs, cookies, API keys, or real customer photos are exposed

## Blockers Found

- None

## Risks

- Manual Supabase validation not yet performed unless checked above.
- Browser QA HTTP-only mode cannot detect console errors or screenshot visual regressions.

## Next Recommended Action

Complete the manual Supabase E2E validation plan, then run `--post-builder` on this report.
