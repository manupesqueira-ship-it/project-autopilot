"""Source Monitor Agent — main orchestrator.

Coordinates fetching from all configured sources, deduplication, preliminary
scoring, and output generation. This is the entry point for CLI invocation.

Usage:
    autopilot scan --property ai-brief-latam
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from agents.source_monitor.schemas import (
    RunStats,
    SourceConfig,
    SourceError,
    SourceItem,
    SourceMonitorResult,
)
from agents.source_monitor.scorer import PreliminaryScorer
from agents.source_monitor.sources import SourceFetcher

logger = logging.getLogger(__name__)


class SourceMonitorAgent:
    """Discovers, deduplicates, and ranks new content items from configured sources.

    Lifecycle:
        1. Load config (property sources + agent config)
        2. Fetch items from all enabled sources
        3. Deduplicate against history
        4. Score preliminarily (heuristic, no LLM)
        5. Sort by score descending
        6. Save output to evidence/
    """

    def __init__(self, property_name: str, config_dir: Path | None = None):
        """Initialize the agent for a specific property.

        Args:
            property_name: e.g. "ai-brief-latam"
            config_dir: Override path to project root. Defaults to auto-detect.
        """
        self.property_name = property_name
        self.config_dir = config_dir or self._find_project_root()
        self.fetcher: SourceFetcher | None = None
        self.scorer: PreliminaryScorer | None = None
        self._seen_ids: set[str] = set()

        # TODO: Load agent config from agents/source_monitor/config.yaml
        # TODO: Load property sources from projects/<property>/sources.yaml
        # TODO: Load dedup history from data/source_monitor/seen_items.json

    def run(self) -> SourceMonitorResult:
        """Execute a full scan cycle.

        Returns:
            SourceMonitorResult with all discovered items, errors, and stats.
        """
        run_id = self._generate_run_id()
        logger.info(f"Starting scan run {run_id} for property '{self.property_name}'")

        # TODO: Step 1 — Load source configs
        sources = self._load_sources()

        # TODO: Step 2 — Fetch items from all sources
        all_items, errors = self._fetch_all(sources)

        # TODO: Step 3 — Deduplicate
        unique_items = self._deduplicate(all_items)

        # TODO: Step 4 — Score preliminarily
        scored_items = self._score(unique_items)

        # TODO: Step 5 — Sort by score
        scored_items.sort(key=lambda x: x.preliminary_score, reverse=True)

        # TODO: Step 6 — Build result and save
        stats = self._compute_stats(all_items, unique_items, sources, errors)
        result = SourceMonitorResult(
            run_id=run_id,
            property=self.property_name,
            items=scored_items,
            errors=errors,
            stats=stats,
        )

        self._save_output(result)
        self._update_dedup_history(unique_items)

        logger.info(
            f"Scan complete: {stats.items_found} found, "
            f"{stats.dedup_removed} deduped, "
            f"{len(scored_items)} returned"
        )
        return result

    def _load_sources(self) -> list[SourceConfig]:
        """Load and validate source configs from property's sources.yaml.

        Returns:
            List of enabled SourceConfig objects.
        """
        # TODO: Read projects/<property>/sources.yaml
        # TODO: Parse into SourceConfig objects
        # TODO: Filter to enabled-only
        raise NotImplementedError("M1: Load sources from YAML config")

    def _fetch_all(
        self, sources: list[SourceConfig]
    ) -> tuple[list[SourceItem], list[SourceError]]:
        """Fetch items from all configured sources.

        Handles failures gracefully — one source failing doesn't stop the rest.

        Returns:
            Tuple of (all_items, errors)
        """
        # TODO: Initialize SourceFetcher
        # TODO: Iterate sources, fetch each, collect items + errors
        # TODO: Handle timeouts and rate limits
        raise NotImplementedError("M2: Fetch from all sources")

    def _deduplicate(self, items: list[SourceItem]) -> list[SourceItem]:
        """Remove items already seen in previous runs.

        Uses deterministic ID (hash of url + published_at) to detect duplicates.

        Args:
            items: Raw items from all sources.

        Returns:
            Items not previously seen, with is_duplicate flags set.
        """
        # TODO: Load seen_ids from data/source_monitor/seen_items.json
        # TODO: Mark duplicates (is_duplicate=True, duplicate_of=original_id)
        # TODO: Return only new items
        raise NotImplementedError("M2: Deduplication logic")

    def _score(self, items: list[SourceItem]) -> list[SourceItem]:
        """Apply preliminary heuristic scoring to each item.

        This is fast, deterministic scoring (no LLM). The Signal Scorer
        does the deeper LLM-based scoring later.

        Args:
            items: Deduplicated items.

        Returns:
            Same items with preliminary_score and score_breakdown populated.
        """
        # TODO: Initialize PreliminaryScorer with config
        # TODO: Score each item
        raise NotImplementedError("M3: Preliminary scoring")

    def _compute_stats(
        self,
        all_items: list[SourceItem],
        unique_items: list[SourceItem],
        sources: list[SourceConfig],
        errors: list[SourceError],
    ) -> RunStats:
        """Compute aggregate stats for the run."""
        # TODO: Calculate all stats fields
        raise NotImplementedError("M2: Stats computation")

    def _save_output(self, result: SourceMonitorResult) -> Path:
        """Save result to evidence/{run_id}/source_monitor_output.json.

        Returns:
            Path to the saved file.
        """
        # TODO: Create evidence directory
        # TODO: Serialize result to JSON
        # TODO: Save stats and log separately
        raise NotImplementedError("M2: Evidence output")

    def _update_dedup_history(self, items: list[SourceItem]) -> None:
        """Add newly discovered item IDs to the dedup history file."""
        # TODO: Append new IDs to data/source_monitor/seen_items.json
        # TODO: Prune old entries (>30 days) to prevent unbounded growth
        raise NotImplementedError("M2: Dedup history update")

    def _generate_run_id(self) -> str:
        """Generate a deterministic run ID: {timestamp}_{property}."""
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        return f"{ts}_{self.property_name}"

    def _find_project_root(self) -> Path:
        """Auto-detect the project root directory.

        Walks up from this file's location looking for MASTER_PLAN.md.
        """
        # TODO: Implement root detection
        raise NotImplementedError("M1: Project root detection")

    @staticmethod
    def generate_item_id(url: str, published_at: datetime) -> str:
        """Generate a deterministic, unique ID for a source item.

        Args:
            url: The item's canonical URL.
            published_at: The item's publication timestamp.

        Returns:
            SHA-256 hash (first 16 chars) of url + published_at.
        """
        raw = f"{url}|{published_at.isoformat()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
