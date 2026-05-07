# Project Autopilot — Worktree Cleanup Playbook

> Generated: 2026-05-01
> Audience: Human operator only. Do not automate.

## Safety Principles

1. **Never remove a worktree without verifying its branch is fully merged.**
2. **Never remove the active sandbox worktree before post-builder review.**
3. **Never use `rm -rf` on worktree directories.** Always use `git worktree remove`.
4. **Never force-delete worktrees with unknown or uncommitted changes.**
5. **Always verify from the main repo**, not from inside the worktree being removed.
6. **The main repo (`mira/`) must never be removed or treated as a worktree.**

---

## Pre-Cleanup Checklist

Before removing any worktree, confirm ALL of these:

- [ ] You are running commands from the **main repo** (`C:/Users/manup/projects/mira`)
- [ ] The branch is fully merged: `git branch --merged master` includes it
- [ ] The worktree has no uncommitted changes: `git -C <worktree-path> status --short` is empty
- [ ] The worktree is not the active Claude sandbox (currently: `mira-sandbox-improve-project-autopilot-docs`)
- [ ] You have reviewed any Claude-generated output in the worktree

---

## How to Check Worktree Status

```bash
# List all worktrees
git worktree list

# Check if a specific worktree has uncommitted changes
git -C /c/Users/manup/projects/<worktree-name> status --short

# Check if a branch is merged into master
git branch --merged master | grep "<branch-name>"
```

---

## How to Check if a Branch is Merged

```bash
# Method 1: List merged branches
git branch --merged master

# Method 2: Check specific branch
git merge-base --is-ancestor <branch-name> master && echo "MERGED" || echo "NOT MERGED"

# Method 3: See unmerged commits
git log master..<branch-name> --oneline
# If output is empty, branch is merged
```

---

## How to Safely Remove a Worktree

### Step 1: Verify clean state

```bash
# From main repo
git -C /c/Users/manup/projects/<worktree-name> status --short
# Must be empty
```

### Step 2: Verify branch is merged

```bash
git branch --merged master | grep "<branch-name>"
# Must show the branch
```

### Step 3: Remove worktree

```bash
# From main repo (C:/Users/manup/projects/mira)
git worktree remove /c/Users/manup/projects/<worktree-name>
```

### Step 4: Optionally delete the branch

```bash
# Only after worktree is removed
git branch -d <branch-name>
# -d (lowercase) will refuse to delete unmerged branches — this is a safety net
```

### Step 5: Verify

```bash
git worktree list
git branch --list
```

---

## How to Prune Stale Worktree References

If a worktree directory was manually deleted (not recommended), git may have stale references:

```bash
# Show stale worktrees
git worktree list
# Look for entries pointing to non-existent paths

# Prune stale references
git worktree prune

# Verify
git worktree list
```

---

## What NOT to Do

| Action | Why |
|--------|-----|
| `rm -rf /c/Users/manup/projects/mira-*` | Destroys worktrees without git cleanup; leaves stale refs |
| `git worktree remove --force <path>` on unknown worktrees | May destroy uncommitted work |
| `git branch -D <branch>` (uppercase D) | Force-deletes even unmerged branches — use `-d` instead |
| Remove `mira-sandbox-improve-project-autopilot-docs` without review | Active Claude sandbox — may have unreviewed generated output |
| Remove `mira/` (main repo) | This is the main repository, not a worktree |
| Automate worktree deletion in scripts | Always human-supervised |
| Delete directories not in `git worktree list` without investigating | May be independent clones (e.g., `mira-agent-benchmarks`, `mira-docs-integration`) |

---

## Recommended Cleanup Order

Process merged-and-clean worktrees first, in any order:

1. `mira-init-project` — earliest/simplest, good first test
2. `mira-backend-validation-audit`
3. `mira-browser-qa`
4. `mira-browser-qa-p0`
5. `mira-flow-alignment`
6. `mira-product-flow-readiness`
7. `mira-security-staging`
8. `mira-visual-qa-polish`
9. `mira-openai-auditor-loop`
10. `mira-product-validation-execution`
11. `mira-product-validation-readiness`
12. `mira-vps-readiness`

**Do not remove until unmerged branches are imported:**

13. `mira-autopilot-cloud-plan`
14. `mira-autopilot-finish-line`
15. `mira-autopilot-task-library`
16. `mira-supabase-sql-drafts`
17. `mira-supabase-staging-pack`
18. `mira-vps-manual-runner-plan`

**Do not remove without explicit human review:**

19. `mira-sandbox-improve-project-autopilot-docs`

---

## Quick Reference: Safe Cleanup Batch Script

**HUMAN-ONLY — Do not run automatically. Review each line before executing.**

```bash
# From main repo: C:/Users/manup/projects/mira

# Verify all are merged first
git branch --merged master

# Remove merged worktrees one at a time
git worktree remove /c/Users/manup/projects/mira-init-project
git worktree remove /c/Users/manup/projects/mira-backend-validation-audit
# ... continue for each confirmed-merged worktree

# Delete merged branches
git branch -d agent/init-project
git branch -d agent/backend-validation-audit
# ... continue for each

# Prune any stale refs
git worktree prune

# Final verification
git worktree list
git branch --list
```
