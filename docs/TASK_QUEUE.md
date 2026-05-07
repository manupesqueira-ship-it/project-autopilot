# Task Queue

## Current Priority

### Validate MIRA Supabase Persistence End-to-End

Manually test the full MVP flow against the live Supabase instance to confirm that the recently wired persistence actually works.

Acceptance criteria:

- Submit onboarding form at /es/onboarding with all fields filled.
- Confirm a new row exists in users_profile in Supabase.
- Upload at least one scan photo (front) at /es/scan.
- Confirm the file exists in the user-photos storage bucket.
- Confirm a new row exists in user_assets with correct asset_type and storage_path.
- Navigate to /es/catalog, click a product, go to /es/tryon/[productId].
- Click "Probarme" (try-on CTA) to trigger a generation.
- Confirm a new row exists in the generations table.
- Confirm the result page at /es/result/[generationId] polls and shows mock output.
- Document any failures in BLOCKERS.md.

## Next Tasks

### Improve Local Planner Task Selection

Make the local planner smarter about picking the next task: skip completed items, handle multi-task queues, detect when all tasks are done.

### Add Project Init Command

Add a `--init <project_id>` CLI command that scaffolds a new project config and project_control directory from templates.

### Status and Doctor Polish

Improve `--status` and `--doctor` output formatting. Add color when terminal supports it. Add timestamp to status output.

### Add Scheduler (Later)

Add a lightweight scheduler that runs `--cycle` on a cron interval. Not needed yet. Do not implement until the manual workflow is proven.

## Completed

### Adopt Project Autopilot

Completed 2026-04-28. Project Autopilot is implemented with dry-run, cycle, local-plan, status, and doctor modes. Evidence collection, OpenAI supervisor, Telegram alerts, cost controller, and local fallback planner are all operational.

## Paused Product Work

- Provider implementation work (OpenAI image, Seedance video).
- Additional Supabase feature wiring (real products, seller flow).
- Visual design changes.
- New product flows.
- Deployment.
