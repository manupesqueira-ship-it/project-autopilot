# Current State

## Repository Snapshot

MIRA is a Next.js 14.2.35 App Router project using TypeScript, Tailwind CSS, next-intl, Motion, Supabase client/schema, and mocked image/video provider modules.

## MVP State

Implemented areas include:

- Bilingual routes for English and Spanish.
- Premium landing pages and app flow pages.
- App pages for onboarding, photo scan, catalog, product try-on, result, and seller view.
- API routes for creating try-on jobs and reading generation status.
- Mock image and video provider modules.
- Supabase schema for user profiles, assets, sellers, products, generations, and events.
- Supabase persistence wired for onboarding (users_profile insert), scan (user-photos storage upload + user_assets rows), and generations (generations table via server client).
- Live end-to-end validation of Supabase persistence is still pending.

## Validation State

- `npm run build` passes.
- `npm run typecheck` passes.
- `npm run lint` passes (ESLint config is now deterministic via .eslintrc.json).
- Provider implementations remain mocked or skeletal.

## Project Autopilot State

Project Autopilot baseline is implemented and operational. It is a reusable system; MIRA is the first configured project.

Working capabilities:

- `--dry-run` works: reads config, collects git evidence, skips OpenAI, writes builder prompt.
- `--local-plan` works: generates deterministic builder prompt from local state and real evidence without any API calls.
- `--cycle` works: calls OpenAI when credentials and budget allow, falls back to local plan on failure.
- `--status` works: prints project config, budget, cycles, git status, recent logs.
- `--doctor` works: validates environment, credentials, config, control files, scripts, git state.
- Telegram alerts work (test confirmed).
- Iteration logs are written under `logs/` and ignored by git.
- OpenAI `--cycle` previously hit HTTP 429 (rate limit). Error handling now exists: failure log, blocker record, Telegram alert, local fallback plan, clean exit.
- Cost controller tracks estimated model usage, paid API calls, and budget limits.
- Local planning is always free and never blocked by budget.

## Workflow State

Project Autopilot is operational. The next priority is validating MIRA Supabase persistence end-to-end, then resuming product feature development.
