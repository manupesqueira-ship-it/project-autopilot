# Project Autopilot — Merge Queue Plan

> Generated: 2026-05-01
> Baseline: master @ bdd209d (Add manual Claude sandbox handoff flow)

## Current Merge Baseline

Master includes all core feature branches through the sandbox handoff flow:
- `bdd209d` — Manual Claude sandbox handoff flow
- `b21962c` — Human-approved sandbox worktree creation flow
- `c77927d` — Claude sandbox runner approval interface
- `0604a83` — Claude sandboxed builder boundary preflight
- `c00d59c` — Merge of agent/openai-auditor-loop

All 14 merged branches are fully integrated. No further action needed for those.

---

## Branches Already Merged — No Action Needed

These branches are ancestors of master. Do NOT re-merge:

1. `agent/backend-validation-audit`
2. `agent/browser-qa`
3. `agent/browser-qa-p0`
4. `agent/init-project`
5. `agent/mira-flow-alignment`
6. `agent/mira-product-flow-readiness`
7. `agent/mira-runtime-auth-hardening`
8. `agent/mira-security-staging`
9. `agent/mira-visual-qa-polish`
10. `agent/openai-auditor-loop`
11. `agent/product-validation-execution`
12. `agent/product-validation-readiness`
13. `agent/vps-readiness`
14. `sandbox/claude-improve-project-autopilot-docs`
15. `sandbox/claude-smoke-20260501062258`

---

## Recommended Merge/Import Order

All 6 unmerged branches are docs-only (project_control/*.md files). Recommended order based on dependency and risk:

### Priority 1 — Autopilot Core Docs (no cross-dependencies)

| Order | Branch | Files | Risk |
|-------|--------|-------|------|
| 1 | `agent/autopilot-finish-line` | 4 files (+791 lines) — go/no-go decision, completion checklist | Low — standalone planning docs |
| 2 | `agent/autopilot-task-library` | 5 files (+2247 lines) — task taxonomy, prompt catalog | Low — standalone reference docs |
| 3 | `agent/autopilot-cloud-plan` | 5 files (+1811 lines) — VPS runner plan, worktree sandbox strategy | Low — architecture planning docs |

### Priority 2 — VPS and Infra Docs

| Order | Branch | Files | Risk |
|-------|--------|-------|------|
| 4 | `agent/vps-manual-runner-plan` | 5 files (+1223 lines) — VPS security checklist, Telegram escalation | Low — preflight planning docs |

### Priority 3 — Supabase Docs (Review SQL content carefully)

| Order | Branch | Files | Risk |
|-------|--------|-------|------|
| 5 | `agent/supabase-sql-drafts` | 4 files (+1704 lines) — security validation queries, storage SQL | **Medium** — contains SQL drafts; confirm these are review docs, not executable |
| 6 | `agent/supabase-staging-pack` | 5 files (+2504 lines) — RLS/storage staging, security test matrix | **Medium** — policy planning docs with SQL context |

---

## Merge Procedure Per Branch

```
# 1. Verify branch is docs-only
git diff master...<branch> --stat
# Confirm all files are in project_control/ or docs paths

# 2. Check for conflicts
git merge --no-commit --no-ff <branch>
git diff --cached --stat
# If only project_control/ files: safe

# 3. Complete merge
git merge --no-ff <branch> -m "Merge branch '<branch>'"

# 4. If conflicts in non-docs files: ABORT
git merge --abort
```

---

## Post-Merge Validation

After each merge:

1. `git status --short` — must be clean
2. `git diff --check` — no whitespace errors
3. `ls project_control/` — verify new docs landed
4. Confirm no changes to: `app/`, `lib/`, `components/`, `.env*`, `package*.json`

After all merges complete:

1. `npm run lint` — verify no lint regressions
2. `npm run typecheck` — verify no type regressions
3. `git log --oneline -20` — verify merge history looks correct

---

## Dangerous Conflict Scenarios

- **File overlap:** If two branches added the same filename in `project_control/`, a merge conflict will occur. Based on current analysis, all branch file sets appear distinct — but verify before each merge.
- **Non-docs changes:** If any branch unexpectedly touches `app/`, `lib/`, `components/`, or config files, ABORT that merge and escalate for human review.
- **Supabase SQL branches:** Even though files are `.md` or `.sql.md`, review content to ensure no executable SQL was accidentally included in migration paths.

---

## Summary

| Category | Count |
|----------|-------|
| Already merged (no action) | 15 branches |
| Docs-only pending import | 6 branches |
| Estimated total new docs | ~28 files, ~10,280 lines |
| Expected conflicts | None (all target distinct files in project_control/) |
| Risk level | Low (docs-only, medium for SQL draft branches) |
