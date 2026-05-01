# AUTOPILOT EXECUTION QUALITY METRICS

**Version:** 1.0  
**Date:** 2026-04-30  
**Owner:** Project Autopilot Control System  
**Status:** ACTIVE

---

## 1. Purpose

This document defines the execution quality metrics that Project Autopilot tracks per cycle. These metrics are the machine-readable record of how the system performed — not just what it produced.

Output quality is tracked in the World-Class Scorecard. This document tracks **operational quality**: efficiency, reliability, cost, and trust.

All metrics should eventually be surfaced in the Control Center dashboard.

---

## 2. Cycle Metrics

### 2.1 Cycle Duration
**Definition:** Total wall-clock time from cycle start to cycle completion (commit or abort)  
**Unit:** Minutes  
**Target:** ≤ 30 min for a standard single-task cycle  
**Warning threshold:** > 45 min  
**Fail threshold:** > 90 min  
**Why it matters:** Long cycles indicate rework loops, unclear briefs, or agent confusion. Trends here signal process problems.

---

### 2.2 Active Time
**Definition:** Time during which Claude was actively generating output, calling tools, or waiting on external processes  
**Unit:** Minutes  
**Target:** ≤ 20 min for a standard single-task cycle  
**Note:** Active time < 5 min for a complex task may indicate the cycle was too shallow.

---

### 2.3 Commands Run
**Definition:** Total number of shell commands, tool calls, and agent invocations executed in the cycle  
**Unit:** Count  
**Target:** ≤ 40 commands for a standard cycle  
**Warning threshold:** > 60  
**Note:** High command counts without proportional output suggest loop behavior.

---

### 2.4 Commands Failed
**Definition:** Number of commands that exited with a non-zero status or produced an error response  
**Unit:** Count  
**Target:** ≤ 2 per cycle  
**Warning threshold:** > 3  
**Fail threshold:** > 5  
**Note:** Repeated failures on the same command indicate a broken assumption that should trigger human escalation.

---

### 2.5 Files Created
**Definition:** Number of new files committed as part of the cycle output  
**Unit:** Count  
**Note:** Track against cycle brief. Unexpected file creation outside authorized paths is a policy violation.

---

### 2.6 Files Modified
**Definition:** Number of existing files changed in the cycle  
**Unit:** Count  
**Note:** High modification counts relative to brief scope indicate scope creep.

---

### 2.7 Validations Passed
**Definition:** Number of automated validation checks that completed successfully (lint, typecheck, build, tests, security scan)  
**Unit:** Count / Total checks run  
**Target:** 100% of checks run must pass before commit  
**Note:** A cycle that skips validations (rather than failing them) is treated as failed.

---

### 2.8 Rework Count
**Definition:** Number of times output was regenerated or revised within the same cycle due to quality failure or policy block  
**Unit:** Count  
**Target:** 0  
**Warning threshold:** 1  
**Fail threshold:** ≥ 2  
**Note:** Rework is the single strongest predictor of world-class score degradation. Monitor closely.

---

### 2.9 Policy Verdicts
**Definition:** Number and type of policy checks triggered and their outcomes (PASS / WARN / BLOCK)  
**Unit:** Count by verdict type  
**Target:** Zero BLOCKs; zero unexpected WARNs  
**Note:** A BLOCK from any director (Design, Research, QA, Privacy) is a policy violation. Track which director issued each verdict.

---

### 2.10 QA Failures
**Definition:** Number of QA checks that failed (test failures, type errors, lint errors, build errors)  
**Unit:** Count  
**Target:** 0 at time of commit  
**Note:** QA failures that are bypassed or ignored are critical policy violations.

---

### 2.11 Design Warnings
**Definition:** Number of WARN-level issues issued by the Design Director during the cycle  
**Unit:** Count  
**Target:** 0  
**Warning threshold:** 1–2  
**Fail threshold:** ≥ 3 or any BLOCK  
**Note:** Accumulated design warnings across cycles indicate a systemic design quality gap, not just one-off issues.

---

### 2.12 Research Blockers
**Definition:** Number of times the Research Director blocked implementation progress  
**Unit:** Count  
**Target:** 0  
**Note:** A research blocker means implementation was attempted before sufficient research was done. This is a process failure, not just a content failure.

---

### 2.13 Cost Per Cycle
**Definition:** Total estimated USD cost of all LLM API calls made during the cycle  
**Unit:** USD (estimated)  
**Target:** Defined per cycle type in the cycle brief  
**Warning threshold:** 1.5x expected cost  
**Fail threshold:** 2x expected cost  
**Note:** Cost overruns often co-occur with rework loops. Correlate with rework count.

---

### 2.14 Token and API Calls
**Definition:** Total input tokens, output tokens, and number of API calls made during the cycle  
**Unit:** Tokens (input/output separately), API call count  
**Target:** Tracked per cycle type for baseline establishment  
**Note:** First 10 cycles of each cycle type establish the baseline. Deviations > 50% from baseline trigger cost review.

---

### 2.15 Commit Quality
**Definition:** Assessment of the git commit(s) produced by the cycle  
**Scoring criteria:**
- Commit message is descriptive and non-generic (e.g., not "update files")
- Commit is atomic (one logical change per commit)
- Commit does not include unrelated files
- Commit does not include env files, secrets, or generated artifacts outside the allowed set
- Commit message includes co-authorship attribution if required

**Unit:** Pass / Warn / Fail  
**Fail criteria:** Any secret detected in diff; any file outside authorized scope in diff

---

### 2.16 Rollback Count
**Definition:** Number of times a committed cycle output was subsequently reverted  
**Unit:** Count  
**Target:** 0  
**Note:** Any rollback triggers mandatory post-mortem. Two rollbacks in the same cycle scope trigger level regression.

---

### 2.17 Human Intervention Count
**Definition:** Number of times a human had to intervene during or after the cycle to correct, unblock, or override an autonomous decision  
**Unit:** Count  
**Target:** ≤ 1 for a standard cycle (e.g., final PR approval)  
**Warning threshold:** 2  
**Fail threshold:** ≥ 3  
**Note:** Human intervention is expected at gated checkpoints (PR approval, production deploy). Unexpected interventions signal that the agent hit an unhandled edge case.

---

### 2.18 Autonomy Score
**Definition:** A 0–100 score measuring how much of the cycle was completed without human intervention relative to the expected automation level for the current capability level  
**Formula:**
```
Autonomy Score = (1 - (unexpected_human_interventions / total_decision_points)) × 100
```
**Target:** ≥ 80 at Level 3+  
**Note:** "Unexpected" intervention excludes gated checkpoints (PR review, deploy approval). Those are by design.

---

### 2.19 Reliability Score
**Definition:** A 0–100 rolling score measuring cycle completion rate, zero-rollback rate, and zero-incident rate over the last 10 cycles  
**Formula:**
```
Reliability Score = (
  (cycles_completed_without_abort / total_cycles) × 40 +
  (cycles_without_rollback / total_cycles) × 40 +
  (cycles_without_incident / total_cycles) × 20
) × 100
```
**Target:** ≥ 85  
**Autonomy level gate:** Reliability Score < 75 blocks level advancement regardless of other metrics.

---

## 3. Metric Aggregation and Reporting

### Per-Cycle Report
Every cycle must produce a structured metrics record including all 19 metrics above. This record is committed to the cycle log alongside the output.

**Minimum required fields per cycle record:**

```
cycle_id:
cycle_type:
date:
duration_minutes:
active_time_minutes:
commands_run:
commands_failed:
files_created:
files_modified:
validations_passed:
validations_total:
rework_count:
policy_verdicts: { pass: 0, warn: 0, block: 0 }
qa_failures:
design_warnings:
research_blockers:
cost_usd_estimated:
tokens_input:
tokens_output:
api_calls:
commit_quality: pass|warn|fail
rollback_count:
human_intervention_count:
autonomy_score:
world_class_score:
```

### Rolling Metrics (Last 10 Cycles)
- Average world-class score
- Average cycle duration
- Total rollbacks
- Total human interventions
- Reliability score
- Autonomy score trend

### Rolling Metrics (Last 20 Cycles)
- Autonomy level eligibility assessment
- Cost trend analysis
- Design warning accumulation
- Research blocker frequency

---

## 4. How These Metrics Should Appear in Control Center

When the Control Center dashboard is built, these metrics must be surfaced as follows:

### Current Cycle Panel
- Status badge: IN PROGRESS / COMPLETE / BLOCKED / FAILED
- Cycle type and brief title
- Duration (live timer or completed duration)
- World-class score (displayed after cycle completes)
- Policy verdicts: icons for each director (Design, Research, QA, Privacy)

### Cycle History Table
| Column | Content |
|---|---|
| Date | Cycle start date |
| Type | Task category |
| Score | World-class score with color coding |
| Duration | Wall-clock minutes |
| Rework | Count with warning indicator if > 0 |
| Cost | USD estimated |
| Verdicts | PASS/WARN/BLOCK badges per director |
| Commit | Link to git commit or PR |
| Interventions | Count of unexpected human interventions |

### Reliability Panel
- Reliability score (large number, color-coded)
- Autonomy score (large number, color-coded)
- Current capability level badge
- Next level: requirements and progress

### Cost Panel
- Cost per cycle (sparkline, last 10 cycles)
- Total cost this month
- Projected monthly cost at current run rate
- Cost per category breakdown (research, implementation, QA)

### Alert Feed
Real-time alerts for:
- Policy BLOCK issued
- Rollback triggered
- Human intervention beyond expected threshold
- Cost exceeded 1.5x expected
- World-class score below 55
- Capability level regression

---

## 5. Metric Integrity Rules

1. Metrics must be recorded by the system, not self-reported by the agent producing the output.
2. Metrics must be immutable once committed — no retroactive edits.
3. If a metric cannot be measured, it must be recorded as `null` with a reason, not omitted.
4. A cycle with more than 3 null metrics is rated as incomplete evidence (WARN on evidence quality).
5. Cost metrics are estimates. They must be labeled as estimates. Actual billing reconciliation is a human responsibility.

---

*This document defines the operational heartbeat of Project Autopilot. Metrics are not bureaucracy — they are the evidence base on which trust in autonomy is built or withdrawn.*
