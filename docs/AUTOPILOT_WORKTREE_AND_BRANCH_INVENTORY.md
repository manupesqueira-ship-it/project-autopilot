# Project Autopilot — Worktree and Branch Inventory

> Generated: 2026-05-01
> Baseline: master @ bdd209d (Add manual Claude sandbox handoff flow)

## Summary

- **Total worktrees:** 20 (1 main + 19 branch worktrees)
- **Total branches:** 22 (master + 19 agent/* + 2 sandbox/*)
- **Merged into master:** 14 branches
- **Not merged into master:** 6 branches
- **Active sandbox:** 1 (sandbox/claude-improve-project-autopilot-docs)

---

## Worktree Inventory

### Main Repository

| Path | Branch | Commit | Status |
|------|--------|--------|--------|
| `C:/Users/manup/projects/mira` | `master` | `bdd209d` | **ACTIVE — DO NOT REMOVE** |

### Merged Branches (Safe to Remove Worktree Later)

These branches are fully merged into master. Their worktrees can be removed after confirmation.

| Path | Branch | Commit | Status |
|------|--------|--------|--------|
| `mira-backend-validation-audit` | `agent/backend-validation-audit` | `ae2eb92` | Merged — safe to remove |
| `mira-browser-qa` | `agent/browser-qa` | `454800d` | Merged — safe to remove |
| `mira-browser-qa-p0` | `agent/browser-qa-p0` | `1ead8f9` | Merged — safe to remove |
| `mira-init-project` | `agent/init-project` | `53857d4` | Merged — safe to remove |
| `mira-flow-alignment` | `agent/mira-flow-alignment` | `ee89217` | Merged — safe to remove |
| `mira-product-flow-readiness` | `agent/mira-product-flow-readiness` | `c83da17` | Merged — safe to remove |
| `mira-security-staging` | `agent/mira-security-staging` | `13b948e` | Merged — safe to remove |
| `mira-visual-qa-polish` | `agent/mira-visual-qa-polish` | `41396a2` | Merged — safe to remove |
| `mira-openai-auditor-loop` | `agent/openai-auditor-loop` | `92a1587` | Merged — safe to remove |
| `mira-product-validation-execution` | `agent/product-validation-execution` | `488da58` | Merged — safe to remove |
| `mira-product-validation-readiness` | `agent/product-validation-readiness` | `299dbfa` | Merged — safe to remove |
| `mira-vps-readiness` | `agent/vps-readiness` | `a2a1fec` | Merged — safe to remove |

### Unmerged Branches (Docs-Only, Pending Review)

These branches have unmerged commits. All appear to be docs-only based on diff analysis.

| Path | Branch | Commit | Unmerged Commits | Files Changed | Status |
|------|--------|--------|-----------------|---------------|--------|
| `mira-autopilot-cloud-plan` | `agent/autopilot-cloud-plan` | `20e8f3c` | 1 (cloud execution arch) | 5 files, +1811 lines | Docs-only pending import |
| `mira-autopilot-finish-line` | `agent/autopilot-finish-line` | `4190da6` | 1 (v1 finish-line plan) | 4 files, +791 lines | Docs-only pending import |
| `mira-autopilot-task-library` | `agent/autopilot-task-library` | `e2d9813` | 1 (task library/prompt catalog) | 5 files, +2247 lines | Docs-only pending import |
| `mira-supabase-sql-drafts` | `agent/supabase-sql-drafts` | `c805890` | 1 (SQL drafts for review) | 4 files, +1704 lines | Docs-only pending import |
| `mira-supabase-staging-pack` | `agent/supabase-staging-pack` | `37c74c5` | 1 (RLS/storage staging) | 5 files, +2504 lines | Docs-only pending import |
| `mira-vps-manual-runner-plan` | `agent/vps-manual-runner-plan` | `188f169` | 1 (VPS manual runner preflight) | 5 files, +1223 lines | Docs-only pending import |

### Active Sandbox

| Path | Branch | Commit | Status |
|------|--------|--------|--------|
| `mira-sandbox-improve-project-autopilot-docs` | `sandbox/claude-improve-project-autopilot-docs` | `b21962c` | **DO NOT REMOVE** — active Claude sandbox, merged but may have unreviewed output |

### Branches Without Worktrees

| Branch | Merged | Notes |
|--------|--------|-------|
| `agent/mira-runtime-auth-hardening` | YES | No worktree — merged, safe to delete branch |
| `sandbox/claude-smoke-20260501062258` | YES | No worktree — smoke test, safe to delete branch |

### Non-Worktree Directories

These directories exist under `projects/` but are NOT listed as git worktrees (may be independent clones or stale):

| Path | Notes |
|------|-------|
| `mira-agent-benchmarks` | Not in worktree list — needs human confirmation |
| `mira-autopilot-final-validation` | Not in worktree list — needs human confirmation |
| `mira-docs-integration` | Not in worktree list — needs human confirmation |

---

## Unknowns / Needs Human Confirmation

1. **`mira-agent-benchmarks`** — exists on disk but not in `git worktree list`. May be an independent clone or manually created directory.
2. **`mira-autopilot-final-validation`** — same as above.
3. **`mira-docs-integration`** — same as above.
4. **`sandbox/claude-improve-project-autopilot-docs`** — branch shows as merged into master, but the worktree is listed as the active sandbox. Confirm whether unreviewed Claude output exists before removing.
5. **Supabase SQL drafts** — marked as docs-only but contain SQL. Confirm these are draft docs, not executable migrations.
