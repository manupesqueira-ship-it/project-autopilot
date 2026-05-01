# Project Autopilot Definition of Done

Universal completion gates for any Project Autopilot sprint:

1. Repo was clean at start.
2. Scope was respected.
3. Changes stayed inside allowed files.
4. No secrets or env files were touched.
5. No live database mutation occurred unless explicitly approved.
6. No paid APIs were called unless explicitly approved.
7. `python -B -m compileall project_autopilot agent` passed.
8. `npm run lint` passed when applicable.
9. `npm run typecheck` passed when applicable.
10. `npm run build` passed when applicable.
11. Flow QA ran if product flow was affected.
12. Mock E2E ran if the user journey or demo path was affected.
13. Backend audit ran if backend/security/data behavior was affected.
14. Design Director ran if UI/design was affected.
15. Research Director was used if uncertain/vendor/security/paid decisions were affected.
16. Readiness report was updated or re-run.
17. Control Center was generated.
18. Evidence was generated.
19. Blockers were updated when blocking issues appeared.
20. Human questions were updated for non-blocking unresolved decisions.
21. Auto-commit happened only when safe.
22. Generated logs/screenshots were not staged.
23. Final repo was clean after commit, or dirty state was explicitly reported.

## Auto-Commit Rule

Auto-commit is allowed only when all required gates pass and changes are scoped, non-secret, non-destructive, non-deployment, non-paid, and non-live-database work.

## Unified Post-Builder Verdicts

Project Autopilot v2 post-builder policy produces one of:

- `SAFE_TO_COMMIT`: all applicable hard gates passed and commit may proceed if generated logs/screenshots are not staged.
- `NEEDS_FIX`: validation, QA, design, Flow QA, or other fixable gates failed. Generate/use the correction prompt and rerun `--post-builder`.
- `BLOCKED`: a hard safety gate fired, such as secrets/env files, SQL/RLS/live DB mutation, paid APIs, scheduler activation, automatic Claude execution, deployment, or generated logs staged.
- `HUMAN_REVIEW_REQUIRED`: no hard failure, but human decision, design review, research approval, or risk acceptance is required.
- `SAFE_NO_CHANGES`: no working-tree changes were detected; no commit is needed.

## Post-Builder Enforcement

`--post-builder` must evaluate provider, risk, scope, forbidden files, secrets/env, validation, design, research, backend, Flow QA, evidence, Definition of Done, and human approval gates before declaring work safe to commit.

Use:

```bash
python -B project_autopilot/agent_loop.py --project mira --post-builder logs/<builder_report>.md
python -B project_autopilot/agent_loop.py --project mira --policy-check
```

## Stop Conditions

Stop and ask for human approval before secrets, env files, git history, destructive commands, deployment, live Supabase changes, SQL/RLS/storage policies, paid APIs, scheduler enablement, automatic Claude execution, or parallel writes without worktrees.
