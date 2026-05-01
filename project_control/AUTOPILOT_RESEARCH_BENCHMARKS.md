# AUTOPILOT RESEARCH BENCHMARKS

**Version:** 1.0  
**Date:** 2026-04-30  
**Owner:** Project Autopilot — Research Director  
**Status:** ACTIVE

---

## 1. Research Quality Levels

Research is not a formality. It is the basis on which design, implementation, and vendor decisions are made. Poor research produces poor decisions regardless of how well they are executed.

The Research Director maintains five quality levels:

| Level | Name | Description |
|---|---|---|
| **R0** | No Research | Decision made from assumption only. Never acceptable. |
| **R1** | Quick Scan | 2–3 sources reviewed. Adequate for low-risk, reversible decisions. |
| **R2** | Standard Research | 5+ sources, tradeoffs documented, alternatives considered. Required for most decisions. |
| **R3** | Deep Research | 10+ sources, primary evidence preferred, expert or user validation included. Required for high-stakes decisions. |
| **R4** | Investigative Research | Original analysis: interviews, user testing, data analysis, or competitive teardowns. Required for product-defining decisions. |

---

## 2. When Quick Research (R1) Is Enough

Quick research is acceptable when ALL of the following are true:

- The decision is easily reversible (can be changed without migration or user impact)
- The scope is limited (1 component, 1 function, 1 styling decision)
- There is no privacy, security, or data implication
- The decision does not affect a new vendor, external API, or infrastructure
- A similar decision was previously researched (and the prior research is cited)

**Examples of R1-appropriate decisions:**
- Which Tailwind spacing value to use for a gap
- Whether to use `useCallback` or inline for a simple handler
- Which icon to use for a UI element with no semantic ambiguity

---

## 3. When Deep Research (R3) Is Mandatory

Deep research is required when ANY of the following are true:

- A new external vendor or API is being evaluated for integration
- A security mechanism (auth, session, encryption, key storage) is being implemented or changed
- A privacy-sensitive feature is being designed (data collection, PII handling, tracking)
- A major architectural pattern is being introduced (e.g., event sourcing, CQRS, queue-based processing)
- A decision will be expensive or disruptive to reverse (schema changes, API contracts, pricing model)
- A user-facing interaction pattern is novel and has not been validated in the competitive set
- Legal or compliance implications exist (GDPR, SOC2, data residency)
- A performance tradeoff affects more than 10% of active users

**R3 failures are blocking.** Implementation cannot proceed until R3 is complete.

---

## 4. What Counts as Strong Evidence

Strong evidence is:

- **Primary sources:** Official documentation, RFC specifications, research papers, vendor security whitepapers
- **Benchmarks with methodology:** Published performance comparisons with clear test conditions
- **Real user data:** User interviews, survey results, session recordings (with consent)
- **Expert consensus:** Multiple independent experts reaching the same conclusion
- **Reproducible results:** Code, commands, or tests that can be re-run

Weak evidence (not sufficient on its own):

- Stack Overflow answers without source verification
- Blog posts without cited data
- Reddit opinions or Discord conversations
- Documentation that is more than 2 years old for a fast-moving ecosystem
- Single-vendor marketing materials

**Weak evidence can supplement strong evidence but cannot replace it.**

---

## 5. Vendor and API Selection Research Criteria

Before any new vendor or API is selected, the Research Director must produce evidence on all of the following:

| Criterion | Questions to Answer |
|---|---|
| **Pricing model** | What is the cost at 1x, 10x, and 100x current usage? Are there unexpected rate limits or overages? |
| **Data handling** | Where is data stored? Is it used for training? What is the retention policy? |
| **Privacy compliance** | Is the vendor GDPR-compliant? SOC2 Type II certified? What is their breach notification process? |
| **Lock-in risk** | How difficult is migration away from this vendor? Are data exports available? |
| **Reliability** | What is the SLA? What is the historical uptime? Are there known incidents? |
| **API stability** | How often do breaking changes occur? What is the deprecation policy? |
| **Alternatives** | What are 2–3 alternatives? Why was this one chosen over them? |
| **Security posture** | Is the API key system granular? Are there IP allowlists or audit logs? |

All eight criteria must be addressed. Missing criteria auto-triggers a Research Director BLOCK.

---

## 6. Security and Privacy Research Criteria

Security and privacy research is never optional. For any feature that touches user data, authentication, or external services:

### Security Research Must Cover:
- Threat model: What are the top 3 ways this could be attacked?
- OWASP relevance: Which OWASP Top 10 categories apply?
- Data in transit: Is TLS used correctly? Certificate validation?
- Data at rest: Is sensitive data encrypted at rest?
- Access control: Is the principle of least privilege applied?
- Audit trail: Are security-relevant actions logged?
- Known vulnerabilities: Has the library/vendor had CVEs in the last 12 months?

### Privacy Research Must Cover:
- Data minimization: Is only the necessary data collected?
- Consent model: Is collection transparent and consented?
- PII classification: What data qualifies as PII in this feature?
- Retention: How long is data kept? Is deletion supported?
- Third-party exposure: Does any PII flow to a third party?
- User rights: Can users access, correct, or delete their data?

Incomplete security or privacy research auto-triggers R3 requirement.

---

## 7. UX and Competitive Benchmark Research Criteria

Before a new UI pattern, user flow, or interaction is implemented, the Research Director must confirm:

| Criterion | Standard |
|---|---|
| **Competitive set reviewed** | At minimum 3 direct competitors and 2 best-in-class non-competitors reviewed |
| **Pattern prevalence** | Is this a known pattern? Emerging pattern? Novel pattern? |
| **User expectation** | Does this pattern match what users have learned from dominant apps? |
| **Accessibility** | Does the pattern meet WCAG AA at minimum? |
| **Edge case inventory** | What are the empty state, error state, and loading state behaviors? |
| **Mobile behavior** | How does this pattern behave on 375px viewport? |
| **Prior art documented** | Screenshots or links from 3+ real implementations |

---

## 8. Source Quality Requirements

| Source Type | Quality Rating | Usage |
|---|---|---|
| Official vendor docs, RFCs, W3C specs | Tier 1 | Cite directly |
| Peer-reviewed papers, security whitepapers | Tier 1 | Cite directly |
| Well-maintained OSS project docs | Tier 2 | Cite with version pinned |
| Technical blog posts from known experts | Tier 2 | Corroborate with Tier 1 |
| Case studies from major companies | Tier 2 | Note potential bias |
| Stack Overflow, forums, Reddit | Tier 3 | Never sole source; must corroborate |
| Vendor marketing materials | Tier 3 | Acknowledge bias; use for claim starting points only |
| Anonymous or undated content | Not acceptable | Do not use |

A research document citing only Tier 3 sources is rated R0 (No Research) regardless of volume.

---

## 9. Citation Requirements

Every research output must include:

1. **Source URL or document reference** (not "as seen on the internet")
2. **Date accessed or publication date**
3. **Quoted or paraphrased excerpt** supporting the claim
4. **Tier classification** of the source
5. **How the source informed the decision** (not just that it was read)

Uncited claims are assumptions, not research. The Research Director must flag uncited claims as R0.

---

## 10. How Research Updates Decisions

Research does not just support decisions — it can change them.

The Research Director must actively compare research findings against the current implementation plan and flag divergences:

| Finding | Required Action |
|---|---|
| Research contradicts the planned approach | Implementation BLOCKED pending plan revision |
| Research reveals a better alternative | Alternative must be evaluated; decision documented |
| Research reveals a security risk | Security Director notified; implementation BLOCKED |
| Research reveals a privacy issue | Privacy review mandatory before any implementation |
| Research is inconclusive | Escalate to human; do not proceed on assumption |

---

## 11. What Poor Research Looks Like

The Research Director must recognize and block these failure modes:

- **Confirmation bias research:** Sources selected because they support the pre-decided approach
- **Speed-researching:** 5 Google results opened for 30 seconds each
- **Citation laundering:** Citing a blog post that cites another blog post; original source never checked
- **Outdated citations:** Using 3-year-old benchmarks for a fast-moving area (LLM APIs, cloud pricing, React patterns)
- **Narrow framing:** Researching only the chosen approach, not alternatives
- **Missing the question:** Researching how to implement X without asking whether X is the right thing to build
- **False precision:** Using numbers from unverified sources as if they are authoritative data

---

## 12. How the Research Director Should Block Implementation

When research is insufficient, the Research Director issues one of three verdicts:

### PASS
Research is complete, well-sourced, and the recommendation is clear. Implementation may proceed.

### WARN — PROCEED WITH CAUTION
Research is adequate for low-risk decisions but has gaps. Implementation may proceed with flagged gaps documented in the cycle log. Gaps must be resolved before the next cycle referencing the same decision.

### BLOCK — DO NOT IMPLEMENT
Research is insufficient for the decision's risk level. Implementation must stop.

Block triggers are:
- Any security/privacy research criterion is unaddressed
- Vendor selection missing 2+ required criteria
- All sources are Tier 3
- Research contradicts the implementation plan and contradiction is unresolved
- R3 was required and only R1 was produced
- Key alternative not considered for a decision with high lock-in risk

A BLOCK from the Research Director overrides a PASS from any other director. Implementation resumes only when the Research Director upgrades its verdict.

---

*This document defines the research bar that protects MIRA from building things that are wrong, unsafe, or uninformed. The Research Director's authority is final on research quality.*
