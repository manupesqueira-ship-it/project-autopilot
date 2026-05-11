# Source Monitor — Implementation Plan

**Approach:** Incremental milestones. Each milestone is independently testable and delivers visible value. No milestone should take more than one focused session.

---

## M1 — Config loading + project root detection
**Objective:** Agent can read its own config and the property's sources.yaml.

**Files to touch:**
- `agents/source_monitor/agent.py` — `_find_project_root()`, `_load_sources()`, `__init__()`
- `agents/source_monitor/schemas.py` — minor adjustments if needed

**Work:**
1. Implement `_find_project_root()` — walk up from `__file__` looking for `MASTER_PLAN.md`
2. Implement `_load_sources()` — read `projects/<property>/sources.yaml`, parse into `SourceConfig` list
3. Load `agents/source_monitor/config.yaml` into agent config dict
4. Load API keys from `.env` (using `os.environ` or `python-dotenv`)

**Definition of done:**
- `agent = SourceMonitorAgent("ai-brief-latam")` succeeds
- `agent._load_sources()` returns a list of `SourceConfig` objects matching sources.yaml
- Agent config dict has scoring weights loaded

**Blocks:** Nothing. This is the starting point.

---

## M2 — RSS fetching + Inoreader + dedup + evidence output
**Objective:** Agent can fetch real items from sources and produce output.

**Files to touch:**
- `agents/source_monitor/sources.py` — `_fetch_rss()`, `_fetch_inoreader()`, `fetch()`, `_normalize_datetime()`
- `agents/source_monitor/agent.py` — `_fetch_all()`, `_deduplicate()`, `_save_output()`, `_update_dedup_history()`, `_compute_stats()`

**Work:**
1. Implement `_fetch_rss()` using `feedparser`
2. Implement `_fetch_inoreader()` using `httpx` against Inoreader REST API
3. Implement `fetch()` dispatch (RSS vs Inoreader vs scrape)
4. Implement error handling — catch exceptions per-source, convert to `SourceError`
5. Implement `_deduplicate()` — load `seen_items.json`, filter by ID
6. Implement `_save_output()` — serialize to `evidence/{run_id}/`
7. Implement `_update_dedup_history()` — append new IDs, prune old
8. Implement `_compute_stats()`

**Definition of done:**
- Tests T1, T2, T4 pass
- Running against a real RSS feed (e.g., Hacker News) returns parsed items
- Dedup correctly filters items across runs
- Output JSON is valid and parseable

**Blocks:** M1 (needs config loading)

**Decision needed from Manuel:**
- **Inoreader auth flow:** Do you have an Inoreader API application created? Need app_id, app_key, and an OAuth token. If not, we start RSS-only and add Inoreader when credentials are ready.
- **Mark as read:** Should the agent mark Inoreader items as read after fetching? (Default: no, to be safe)

---

## M3 — Preliminary scoring
**Objective:** Items come back ranked by relevance.

**Files to touch:**
- `agents/source_monitor/scorer.py` — all `_score_*()` methods, `score_item()`, `score_batch()`
- `agents/source_monitor/agent.py` — `_score()`

**Work:**
1. Implement `_score_recency()` — linear decay from max_score_hours to zero_score_hours
2. Implement `_score_source_weight()` — lookup from source config weight field
3. Implement `_score_keywords()` — case-insensitive match against title + snippet
4. Implement `_score_language()` — exact match scoring
5. Implement `_score_length()` — snippet length threshold
6. Implement `_score_category()` — category bonus lookup
7. Wire `score_batch()` and `score_item()`
8. Wire agent `_score()` method

**Definition of done:**
- Test T3 passes
- Items are sorted by score
- Score breakdown is populated and sum matches total
- Running against real data produces sensible rankings (manual check)

**Blocks:** M2 (needs items to score)

**Decision needed from Manuel:**
- **Keyword list review:** The default keywords in config.yaml — are they the right set? Want to add/remove any?
- **Weight tuning:** Default weights feel right? Or should some dimensions weigh more?

---

## M4 — CLI integration + end-to-end run
**Objective:** `autopilot scan --property ai-brief-latam` works.

**Files to touch:**
- New: `agents/source_monitor/cli.py` (or integrate into existing CLI if one exists)
- `agents/source_monitor/agent.py` — wire `run()` method end-to-end

**Work:**
1. Create CLI entry point (argparse or click)
2. Wire `run()` to call all steps in sequence
3. Pretty-print shortlist to terminal (using `rich`)
4. Handle missing config gracefully (clear error messages)

**Definition of done:**
- Test T5 passes
- CLI command produces a readable shortlist in terminal
- Evidence file is saved
- Running twice deduplicates correctly

**Blocks:** M3

---

## M5 — Selective scraping (Anthropic Blog + others)
**Objective:** Sources without RSS are covered.

**Files to touch:**
- `agents/source_monitor/sources.py` — `_fetch_scrape()`, per-source parsers

**Work:**
1. Implement Anthropic Blog parser (custom HTML parsing)
2. Add scraper dispatch by `source.name`
3. Add any other non-RSS sources from the sources.yaml

**Definition of done:**
- Anthropic Blog items appear in scan results
- Scraped items have the same SourceItem quality as RSS items

**Blocks:** M4 (nice to have, not critical path)

**Decision needed from Manuel:**
- **Which non-RSS sources matter?** Anthropic Blog is the obvious one. Any others?
- **Scraping frequency:** Same as RSS, or less frequent to be polite?

---

## M6 — Integration with Signal Scorer
**Objective:** Source Monitor output feeds directly into Signal Scorer.

**Files to touch:**
- `agents/source_monitor/agent.py` — output format alignment
- `agents/signal_scorer/` — input consumption (if started)

**Work:**
1. Verify output schema matches Signal Scorer's expected input
2. Add pipeline mode: `autopilot scan --property ai-brief-latam --pipe-to-scorer`
3. Or: Signal Scorer reads `evidence/{run_id}/source_monitor_output.json` directly

**Definition of done:**
- Signal Scorer can consume Source Monitor output without transformation
- Full scan → score pipeline runs with one command

**Blocks:** M4 + Signal Scorer implementation started

---

## Dependency graph

```
M1 (config)
 └→ M2 (fetch + dedup)
     └→ M3 (scoring)
         └→ M4 (CLI + e2e)
             ├→ M5 (scraping) — optional, non-blocking
             └→ M6 (signal_scorer integration) — requires signal_scorer work
```

---

## Open decisions requiring Manuel's input

1. **Inoreader API credentials** — Do you have an app registered at inoreader.com/developers? Need: app_id, app_key, OAuth token.
2. **Inoreader mark-as-read** — Should fetched items be marked as read in Inoreader? Recommend NO until pipeline is stable.
3. **Keyword list for ai-brief-latam** — Review the defaults in config.yaml. Add LATAM-specific terms?
4. **Scoring weights** — Are the default weights (recency=20, source=20, keywords=20, language=10, length=10, category=10) reasonable? Or should we emphasize something else?
5. **Non-RSS sources** — Which sources from sources.yaml don't have RSS and need custom scrapers?
6. **Evidence directory** — Is `evidence/` the right place? Or should Source Monitor output go somewhere else?
7. **Dedup window** — 30 days of dedup history seems right? Too long? Too short?
