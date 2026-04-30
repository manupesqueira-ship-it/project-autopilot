# MIRA Internal Demo Ready Report

Generated: 2026-04-29

## Verdict

**INTERNAL_DEMO_READY_REALDATA_BLOCKED**

The internal demo is functional, visible, and usable locally.
Real customer data remains blocked until RLS, storage policies, and privacy decisions are complete.

## How to Run Locally

```bash
# 1. Start dev server with mock mode
NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true npm run dev

# 2. Open the demo dashboard
# http://localhost:3000/es/demo  (Spanish)
# http://localhost:3000/en/demo  (English)

# 3. Click "Start full demo" to experience the flow
```

## What to Click

1. **Open** `http://localhost:3000/es/demo`
2. **Click** "Iniciar demo completo" (loads mock profile, navigates to catalog)
3. **Browse** the catalog — 18 products across 6 brands
4. **Click** any product card to open the try-on page
5. **Select** a size and click "Probarme esta prenda"
6. **See** the mock result page with a placeholder SVG image
7. **Rate** the result (stars), click "Probar otra prenda" to try again

Alternative paths:
- Click "Ver resultado mock" on the demo page to skip directly to a mock result
- Click "Ir a onboarding" to test the real Supabase auth + profile insert flow
- Switch language with the EN/ES toggle in the nav

## What Is Real

- Full UI and navigation (Next.js 14, Tailwind, Fraunces/Geist fonts)
- Anonymous auth with Supabase (signInAnonymously)
- Profile insert into Supabase users_profile table (with auth_user_id)
- Bilingual routing (ES default, EN available)
- 18 products with real brand data (Adidas, Nike, ON, Lululemon, Alo, Brooks Brothers)
- File upload validation (MIME type, size limits)
- Graceful error handling on all pages

## What Is Mocked

- User photos (scan step can be skipped; demo seeds mock photo paths)
- Image/video generation (returns immediately with SVG placeholder)
- Try-on result (static mock SVG, no paid API calls)
- Generation IDs prefixed with `qa-mock-generation-` are handled deterministically

## What Is Blocked for Real Users

- **RLS and storage policies** — disabled on all tables, no row ownership
- **Real customer data** — must not store until security model is complete
- **Paid APIs** — OpenAI image generation and Seedance video generation disabled
- **Production deploy** — no staging/prod separation yet
- **CAPTCHA/abuse protection** — not configured
- **Privacy/retention policy** — not written
- **Signed URLs** — strategy not decided
- **Budget gates** — no per-user generation limits

## Validation Commands

```bash
# Environment preflight
python -B project_autopilot/env_preflight.py --project mira

# Static auth verification (20/20 checks)
python -B project_autopilot/supabase_auth_verify.py --project mira

# Live auth verification (24/24 checks)
python -B project_autopilot/supabase_auth_verify.py --project mira --live-dev-check

# Runtime diagnostics
python -B project_autopilot/dev_runtime_diagnose.py --project mira

# Internal demo check
python -B project_autopilot/internal_demo_check.py --project mira

# Full readiness report
python -B project_autopilot/mira_readiness.py --project mira

# Lint + typecheck + build
npm run lint && npm run typecheck && npm run build
```

## Security Boundaries

Real customer data is blocked until:
- RLS enabled and tested in staging/disposable project
- users_profile / user_assets / generations policies exist and pass A/B tests
- user-photos storage policies exist
- Object path strategy uses auth.uid() or equivalent
- Signed URL strategy is decided
- Bucket MIME and size limits exist
- Result/status ownership checks are implemented and tested
- Privacy/retention policy exists
- CAPTCHA/attack protection/site URLs/redirects are configured
- Paid generation budget gates exist
- Staging/prod deploy separation exists

## Next Sprint

**RLS/storage + ownership enforcement sprint** — apply candidate SQL drafts in a disposable Supabase project, run the 30-case security test plan, and implement server-side ownership checks.
