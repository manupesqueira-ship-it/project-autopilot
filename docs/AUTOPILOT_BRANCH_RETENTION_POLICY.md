# Project Autopilot — Branch Retention Policy

> Generated: 2026-05-01
> Applies to: All branches in the MIRA repository

## Branch Classes

### Class 1: Main

| Branch | Rule |
|--------|------|
| `master` | **NEVER DELETE.** Always protected. All merges target this branch. |

### Class 2: Active Sandbox

| Branch | Rule |
|--------|------|
| `sandbox/claude-improve-project-autopilot-docs` | **DO NOT DELETE** until human post-builder review is complete. Even if merged, the worktree may contain unreviewed Claude-generated output. |
| Any `sandbox/*` branch with active Claude work | Same rule — retain until human review confirms no unreviewed output. |

### Class 3: Completed Core Feature (Merged)

Branches that are fully merged into master and have no unmerged commits.

**Current members:**
- `agent/backend-validation-audit`
- `agent/browser-qa`
- `agent/browser-qa-p0`
- `agent/init-project`
- `agent/mira-flow-alignment`
- `agent/mira-product-flow-readiness`
- `agent/mira-runtime-auth-hardening`
- `agent/mira-security-staging`
- `agent/mira-visual-qa-polish`
- `agent/openai-auditor-loop`
- `agent/product-validation-execution`
- `agent/product-validation-readiness`
- `agent/vps-readiness`

**Rule:** May be deleted after confirming merge. Use `git branch -d` (lowercase d) which refuses to delete unmerged branches.

### Class 4: Completed Docs-Only (Not Yet Merged)

Branches with only `project_control/` or docs file changes that have not been merged.

**Current members:**
- `agent/autopilot-cloud-plan`
- `agent/autopilot-finish-line`
- `agent/autopilot-task-library`
- `agent/supabase-sql-drafts`
- `agent/supabase-staging-pack`
- `agent/vps-manual-runner-plan`

**Rule:** Retain until merged into master per the Merge Queue Plan. Delete only after successful merge.

### Class 5: Stale / Obsolete

Branches that are merged and have no worktree, or were created for one-time operations.

**Current members:**
- `sandbox/claude-smoke-20260501062258` — smoke test, merged, no worktree

**Rule:** May be deleted immediately. Use `git branch -d`.

### Class 6: Backup / Unknown

Branches or directories that don't fit other classes or whose purpose is unclear.

**Current members (directories, not necessarily git branches):**
- `mira-agent-benchmarks` — not in `git worktree list`
- `mira-autopilot-final-validation` — not in `git worktree list`
- `mira-docs-integration` — not in `git worktree list`

**Rule:** Do not delete. Investigate first — may be independent clones.

---

## Retention Rules

| Class | Retain | Delete When |
|-------|--------|-------------|
| Main | Always | Never |
| Active Sandbox | Until human review complete | After human confirms all output reviewed |
| Completed Core (Merged) | Optional — already merged | Any time, with `git branch -d` |
| Docs-Only (Unmerged) | Until merged | After successful merge into master |
| Stale / Obsolete | No requirement | Any time, with `git branch -d` |
| Backup / Unknown | Until investigated | After human confirms safe to remove |

---

## Evidence Required Before Deleting

Before deleting any branch, the operator must verify:

1. **Merge status:** `git branch --merged master | grep <branch>` returns a match
2. **No unmerged commits:** `git log master..<branch> --oneline` returns empty
3. **No uncommitted changes in worktree:** `git -C <path> status --short` returns empty (if worktree exists)
4. **Worktree removed first:** `git worktree list` does not include the path
5. **Not an active sandbox:** Branch is not in the Active Sandbox class

---

## Cleanup Cadence

| Frequency | Action |
|-----------|--------|
| After each merge batch | Remove worktrees for merged branches |
| Weekly | Review `git worktree list` and `git branch --list` for stale entries |
| After sandbox session ends | Human reviews sandbox output, then removes worktree and branch |
| Monthly | Full inventory audit — compare `git worktree list`, `git branch --list`, and disk directories |

---

## Human Approval Requirements

The following actions **require explicit human approval**:

1. Deleting any sandbox branch or worktree
2. Deleting any branch that appears in Class 6 (Backup / Unknown)
3. Force-deleting any branch (`git branch -D`) — should almost never be needed
4. Deleting directories not in `git worktree list`
5. Running `git worktree prune` when stale references exist
6. Merging Supabase SQL draft branches (review SQL content first)

The following actions **can proceed without approval** (but operator should verify):

1. Deleting merged Class 3 branches with `git branch -d`
2. Removing worktrees for fully merged branches
3. Deleting Class 5 stale branches
