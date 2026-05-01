# AUTOPILOT FINAL EVIDENCE CHECKLIST
**Version:** v1.0  
**Project:** Project Autopilot  
**Purpose:** Single-page checklist to record evidence of each validation passing before declaring Project Autopilot v1 complete.  
**Instructions:** Fill in date, result (PASS / FAIL / N/A), and any relevant notes for each item. A single FAIL with no resolution is a NO-GO.

---

## VALIDATION RUN METADATA

| Field | Value |
|-------|-------|
| Run date | |
| Runner | |
| Branch | |
| Commit hash (start) | |
| Commit hash (end) | |
| Overall result | GO / NO-GO |

---

## SECTION 1 — HEALTH AND STATUS

### 1.1 Latest Health Report

| Field | Value |
|-------|-------|
| Command | `python project_autopilot/health.py --check` |
| Date run | |
| Result | PASS / FAIL |
| All subsystems OK? | YES / NO |
| Notes | |
| Output file / paste location | |

---

### 1.2 Latest v2 Check

| Field | Value |
|-------|-------|
| Command | `python project_autopilot/v2_check.py --report` |
| Date run | |
| Result | PASS / FAIL |
| Blockers found? | YES / NO |
| Blocker list (if any) | |
| Notes | |
| Output file / paste location | |

---

## SECTION 2 — POLICY AND CONFIGURATION

### 2.1 Latest Policy Fixtures

| Field | Value |
|-------|-------|
| Command | `python -m pytest project_autopilot/tests/test_policy_fixtures.py -v` |
| Date run | |
| Tests passed | / total |
| Tests failed | |
| Result | PASS / FAIL |
| Notes | |

---

### 2.2 Provider Registry Check

| Field | Value |
|-------|-------|
| Command | `python project_autopilot/provider_registry.py --list` |
| Date run | |
| All providers OK? | YES / NO |
| Disabled providers (if any) | |
| Result | PASS / FAIL |
| Notes | |

---

## SECTION 3 — CONTROL CENTER AND FLOW QA

### 3.1 Latest Control Center

| Field | Value |
|-------|-------|
| Command | `python project_autopilot/control_center.py --generate` |
| Date run | |
| Report generated? | YES / NO |
| Result | PASS / FAIL |
| Report location | |
| Notable findings | |

---

### 3.2 Latest Flow QA

| Field | Value |
|-------|-------|
| Command | `python project_autopilot/flow_qa.py --mock-e2e` |
| Date run | |
| All stages completed? | YES / NO |
| Real external calls made? | YES / NO — expected: NO |
| Result | PASS / FAIL |
| Notes | |

---

## SECTION 4 — SANDBOX VALIDATION

### 4.1 Latest Sandbox Preflight

| Field | Value |
|-------|-------|
| Command | `python project_autopilot/claude_sandbox.py --preflight` |
| Date run | |
| All preflight checks passed? | YES / NO |
| Isolation mode | |
| Result | PASS / FAIL |
| Notes | |

---

### 4.2 Latest Sandbox Simulation

| Field | Value |
|-------|-------|
| Command | `python project_autopilot/claude_sandbox.py --simulate --dry-run` |
| Date run | |
| Simulation completed? | YES / NO |
| Real Claude invoked? | YES / NO — expected: NO |
| Result | PASS / FAIL |
| Notes | |

---

### 4.3 Sandbox Approval Preflight

| Field | Value |
|-------|-------|
| Command | `python project_autopilot/claude_sandbox.py --approval-preflight` |
| Date run | |
| Approval gate active? | YES / NO — expected: YES |
| Auto-approve enabled? | YES / NO — expected: NO |
| Result | PASS / FAIL |
| Notes | |

---

## SECTION 5 — RUNNER VALIDATION

### 5.1 Latest Runner Dry-Run

| Field | Value |
|-------|-------|
| Command | `python project_autopilot/sandbox_runner.py --dry-run --task "validation-test"` |
| Date run | |
| Task completed in dry-run? | YES / NO |
| Real Claude invoked? | YES / NO — expected: NO |
| Result | PASS / FAIL |
| Notes | |

---

### 5.2 Runner Status

| Field | Value |
|-------|-------|
| Command | `python project_autopilot/sandbox_runner.py --status` |
| Date run | |
| Runner state | idle / active |
| Scheduler state | disabled / enabled — expected: disabled |
| Result | PASS / FAIL |
| Notes | |

---

## SECTION 6 — WORKTREE AND GIT

### 6.1 Latest Worktree Smoke Test

| Field | Value |
|-------|-------|
| Commands | `git worktree list` + `python project_autopilot/worktree_manager.py --simulate --dry-run` |
| Date run | |
| Worktrees found (count) | |
| Real worktree created during test? | YES / NO — expected: NO |
| Result | PASS / FAIL |
| Notes | |

---

### 6.2 Final Git Status

| Field | Value |
|-------|-------|
| Command | `git status --short` |
| Date run | |
| Only allowed docs modified? | YES / NO |
| Any env/secret files listed? | YES / NO — expected: NO |
| Any log files listed? | YES / NO — expected: NO |
| Result | PASS / FAIL |
| Output (paste) | |

---

### 6.3 Final Worktree List

| Field | Value |
|-------|-------|
| Command | `git worktree list` |
| Date run | |
| Unexpected worktrees? | YES / NO — expected: NO |
| Result | PASS / FAIL |
| Output (paste) | |

---

## SECTION 7 — MANUAL HANDOFF

### 7.1 Latest Manual Handoff Packet (if available)

| Field | Value |
|-------|-------|
| Command | `python project_autopilot/manual_handoff.py --dry-run` |
| Date run | |
| Module present? | YES / NO |
| If present — packet generated? | YES / NO |
| Real delivery triggered? | YES / NO — expected: NO |
| Result | PASS / FAIL / N/A |
| Notes | |

---

## SECTION 8 — BACKEND AND MIRA READINESS

### 8.1 Latest Backend Audit

| Field | Value |
|-------|-------|
| Command | `python project_autopilot/backend_audit.py --run` |
| Date run | |
| All backend checks passed? | YES / NO |
| Unexpected queue contents? | YES / NO — expected: NO |
| Result | PASS / FAIL |
| Notable warnings | |

---

### 8.2 Latest MIRA Readiness

| Field | Value |
|-------|-------|
| Command | `python project_autopilot/mira_readiness.py --check` |
| Date run | |
| Overall readiness | GO / NO-GO |
| Blocking items | |
| Advisory items | |
| Result | PASS / FAIL |
| Notes | |

---

## SECTION 9 — FRONTEND BUILD VALIDATION

| Check | Date run | Result | Notes |
|-------|----------|--------|-------|
| `npm run lint` | | PASS / FAIL | |
| `npm run typecheck` | | PASS / FAIL | |
| `npm run build` | | PASS / FAIL | |
| `git diff --check` | | PASS / FAIL | |

---

## SECTION 10 — SAFETY GATES CONFIRMATION

These are binary YES/NO items. All must be NO (except scheduler confirmed off).

| Gate | Expected | Actual | 
|------|----------|--------|
| Source code touched? | NO | |
| `.env*` files touched? | NO | |
| Secrets committed? | NO | |
| Scheduler enabled? | NO | |
| Auto-Claude enabled? | NO | |
| Real Claude API calls made during validation? | NO | |
| Real writes to production DB? | NO | |

---

## FINAL GO / NO-GO DECISION

| Criteria | Met? |
|----------|------|
| All SECTION 1–9 checks PASS or N/A | YES / NO |
| All SECTION 10 safety gates confirmed | YES / NO |
| No unresolved FAIL items | YES / NO |
| **FINAL DECISION** | **GO / NO-GO** |

**Decision made by:**  
**Date:**  
**Notes:**

---

*End of AUTOPILOT FINAL EVIDENCE CHECKLIST v1.0*
