# AUTOPILOT WORLD-CLASS SCORECARD

**Version:** 1.0  
**Date:** 2026-04-30  
**Owner:** Project Autopilot Control System  
**Status:** ACTIVE

---

## 1. Purpose

This scorecard defines what "world-class" means for every cycle Project Autopilot runs. It is the authoritative benchmark used to decide whether output is acceptable, needs rework, or must be blocked before delivery.

The goal is not to produce software that works. The goal is to produce software that is excellent — in design, architecture, privacy, innovation, and user experience — at the same standard a senior founding team would hold itself to.

---

## 2. What "World-Class" Means

A world-class output satisfies all of the following:

- A senior designer would use it as a reference example, not a starting point.
- A security engineer would not flag privacy or data concerns.
- A product manager would immediately understand the value and clarity.
- A principal engineer would not need to refactor it before shipping.
- A researcher would cite the decisions as well-reasoned and evidence-backed.
- A user would describe it as "obviously the right way to do it."

World-class means the output competes with the best-funded startups and internal tools at companies like Linear, Vercel, Stripe, or Notion — not just with average SaaS.

---

## 3. What Is NOT Enough

The following are explicitly insufficient and will not be accepted as passing:

| Condition | Why It Fails |
|---|---|
| Compiles without errors | Minimum bar, not a quality signal |
| Passes lint | Hygiene only, not quality |
| Looks okay on first glance | Subjective mediocrity |
| Generic SaaS card layout | No design ambition; cookie-cutter |
| Shallow research (1-2 sources) | Insufficient basis for decisions |
| "It works" as the only QA | Covers happy path only |
| No privacy analysis | Unacceptable in any user-facing product |
| No competitor benchmark | Cannot claim design or UX quality without it |
| Inline secrets or hardcoded config | Automatic block |
| No evidence of design iteration | First idea is rarely the best |

---

## 4. Score Categories

Each category is scored 0–10. The total is weighted into a final 0–100 score.

### 4.1 Product Usefulness (Weight: 12%)
Does this actually solve a real problem for the target user? Would a user pay for it?

- **10:** Solves a precise, validated pain point. User outcome is demonstrably better.
- **5:** Useful feature but partially addresses the real need.
- **0:** Technically implemented but unclear why anyone would want it.

### 4.2 Design Quality (Weight: 12%)
Visual craft, typography, spacing, hierarchy, color use, component quality.

- **10:** Reference-quality. Would appear in design inspiration galleries.
- **5:** Clean but unremarkable. No design errors but no design ambition.
- **0:** Generic, inconsistent, or clearly from a default template.

### 4.3 Innovation (Weight: 8%)
Does this bring a novel approach, pattern, or experience?

- **10:** Solves the problem in a way not seen in the competitive set.
- **5:** Solid execution of a known pattern.
- **0:** Copies an existing pattern without adaptation or thought.

### 4.4 UX Clarity (Weight: 10%)
Is the user's path obvious? Are errors clear? Are empty states handled?

- **10:** User never needs to think. Every state is designed.
- **5:** Main flow is clear but edge cases are confusing.
- **0:** User could easily get stuck or confused.

### 4.5 Technical Correctness (Weight: 10%)
Is the implementation sound? No logic errors, no dead code, no time-bombs.

- **10:** Clean, correct, handles edge cases.
- **5:** Works for main cases; minor issues in edge cases.
- **0:** Contains bugs, incorrect assumptions, or broken logic.

### 4.6 Backend and Data Safety (Weight: 10%)
Are writes safe? Are reads scoped correctly? Are race conditions handled?

- **10:** All mutations validated and idempotent. Data access is correctly scoped.
- **5:** Basic safety; some edge case risks.
- **0:** Unsafe writes, missing validation, or potential data corruption.

### 4.7 Privacy (Weight: 10%)
Is user data collected minimally? Are PII flows analyzed?

- **10:** Data minimization applied. No unnecessary collection. PII flows documented.
- **5:** No obvious violations but no explicit analysis.
- **0:** PII exposed, logged, or collected without justification.

### 4.8 QA Coverage (Weight: 8%)
Are meaningful tests present? Do they cover failure paths?

- **10:** Critical paths covered, failure modes tested, edge cases addressed.
- **5:** Happy path covered only.
- **0:** No tests, or tests that cannot catch real failures.

### 4.9 Research Rigor (Weight: 8%)
Were decisions backed by credible evidence?

- **10:** Multiple strong sources, tradeoffs documented, alternatives considered.
- **5:** Some research but incomplete or single-source.
- **0:** No research or research was post-hoc rationalization.

### 4.10 Execution Speed (Weight: 4%)
Did the cycle complete efficiently without unnecessary loops?

- **10:** Completed in expected cycle time with no rework loops.
- **5:** Minor rework; acceptable duration.
- **0:** Multiple rework loops; cycle time exceeded 3x baseline.

### 4.11 Cost Control (Weight: 4%)
Was API and compute usage appropriate for the scope?

- **10:** Efficient use. No unnecessary API calls or token waste.
- **5:** Slightly over expected but within acceptable range.
- **0:** Cost exceeded 2x expected for equivalent scope.

### 4.12 Evidence Quality (Weight: 6%)
Are decisions traceable? Are screenshots, comparisons, or logs available?

- **10:** All major decisions documented with before/after or citations.
- **5:** Some decisions documented; others are opaque.
- **0:** No trail. Decisions are unverifiable.

### 4.13 Maintainability (Weight: 8%)
Will a future developer be able to understand and extend this in 6 months?

- **10:** Self-documenting structure, clean abstractions, no magic.
- **5:** Understandable with effort; some unexplained choices.
- **0:** Tangled, brittle, or requires original author to understand.

---

## 5. Scoring Model

```
Final Score = sum(category_score × category_weight) × 10
```

All category scores are 0–10. Weights sum to 100%. Final score is 0–100.

### Minimum Category Thresholds

The following categories have hard minimums regardless of total score:

| Category | Minimum Score to Pass |
|---|---|
| Privacy | 6 |
| Backend and Data Safety | 6 |
| Technical Correctness | 5 |
| Design Quality | 5 |

Scoring below the minimum in any of these categories **automatically downgrades** the overall result regardless of total score.

---

## 6. Pass / Warn / Fail Thresholds

| Score | Status | Meaning |
|---|---|---|
| 85–100 | **PASS — WORLD CLASS** | Output meets or exceeds standard. Eligible for deployment. |
| 70–84 | **PASS — ACCEPTABLE** | Solid output. Minor gaps. May proceed with noted improvements. |
| 55–69 | **WARN — REWORK REQUIRED** | Below standard. Must address flagged categories before shipping. |
| 40–54 | **FAIL — BLOCKED** | Output does not meet bar. Cycle must restart with fresh brief. |
| 0–39 | **FAIL — CRITICAL** | Fundamental failure. Escalate to human review immediately. |

---

## 7. When Human Review Is Mandatory

Human review is **required** before any commit, PR merge, or deployment when:

1. Final score is below 70.
2. Privacy score is below 6.
3. Backend/Data Safety score is below 6.
4. Any inline secret, API key, or credential is detected.
5. A migration, schema change, or RLS policy is included.
6. The cycle introduced a new external vendor or API dependency.
7. The Design Director issued a BLOCK verdict.
8. The Research Director issued a BLOCK verdict.
9. The cycle touched authentication, authorization, or session logic.
10. Cost exceeded 2x the expected baseline for the cycle scope.
11. A rollback was triggered during the cycle.
12. More than 2 rework loops occurred in a single cycle.

---

## 8. How Score Affects Post-Builder Policy

| Score Range | Post-Cycle Action |
|---|---|
| 85–100 | Auto-commit allowed. Cycle closes. Summary filed. |
| 70–84 | Commit allowed. One improvement task added to next cycle. |
| 55–69 | Commit blocked. Rework task created. Cycle not closed. |
| 40–54 | Commit blocked. Full cycle restart with revised brief. |
| 0–39 | Immediate human escalation. No automated action taken. |

---

## 9. How Score Affects Future Autonomy

The scorecard feeds the Autonomy Score (see AUTOPILOT_EXECUTION_QUALITY_METRICS.md).

| Rolling Average (Last 5 Cycles) | Autonomy Adjustment |
|---|---|
| 85+ | Autonomy level may increase by 1 step |
| 70–84 | Autonomy level maintained |
| 55–69 | Autonomy level reduced by 1 step |
| Below 55 | Autonomy suspended pending human review and remediation plan |

**Autonomy is earned incrementally and lost quickly.** A single catastrophic failure (score below 40) resets to Level 1 regardless of prior history.

---

*This document is the single source of truth for what counts as world-class in Project Autopilot. All agents, directors, and QA systems must reference it.*
