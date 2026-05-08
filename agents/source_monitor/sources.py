"""Source fetching — RSS feeds + selective scraping.

Each source type has its own fetch method. All return normalized SourceItem objects.
Failures are captured as SourceError, never raised — the scan must be resilient.
"""

from __future__ import annotations

import hashlib
import html as html_module
import logging
import re
import time
from calendar import timegm
from datetime import datetime, timezone
from typing import Any

import feedparser
import httpx
from bs4 import BeautifulSoup
from dateutil import parser as dateutil_parser

from agents.source_monitor.schemas import (
    ErrorType,
    SourceConfig,
    SourceError,
    SourceItem,
    SourceType,
)

logger = logging.getLogger(__name__)

# feedparser uses its own HTTP client by default. We override with httpx
# for consistent timeout/retry behavior and to set a proper User-Agent.
_USER_AGENT = "SourceMonitor/0.1 (Project Autopilot; +https://github.com/manupesqueira-ship-it/project-autopilot)"


class SourceFetcher:
    """Fetches items from configured sources, dispatching by source type.

    Usage:
        fetcher = SourceFetcher(timeout=30)
        items, errors = fetcher.fetch(source_config)
    """

    def __init__(self, timeout: int = 30, max_items_per_source: int = 50):
        """Initialize the fetcher.

        Args:
            timeout: HTTP request timeout in seconds.
            max_items_per_source: Cap items returned per source to avoid floods.
        """
        self.timeout = timeout
        self.max_items = max_items_per_source
        self._client = httpx.Client(
            timeout=timeout,
            headers={"User-Agent": _USER_AGENT},
            follow_redirects=True,
        )

    def close(self) -> None:
        """Close the HTTP client. Call when done fetching."""
        self._client.close()

    def fetch(self, source: SourceConfig) -> tuple[list[SourceItem], list[SourceError]]:
        """Fetch items from a single source, dispatching by type.

        Args:
            source: Configuration for the source to fetch.

        Returns:
            Tuple of (items, errors). Errors are informational, not exceptions.
        """
        try:
            if source.type == SourceType.RSS:
                items = self._fetch_rss(source)
                return items, []
            elif source.type == SourceType.SCRAPE:
                items = self._fetch_scrape(source)
                return items, []
            elif source.type == SourceType.INOREADER:
                logger.info(f"Skipping Inoreader source '{source.name}' (deferred)")
                return [], []
            else:
                return [], [SourceError(
                    source_name=source.name,
                    error_type=ErrorType.UNKNOWN,
                    message=f"Unknown source type: {source.type}",
                )]
        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching '{source.name}' ({source.url})")
            return [], [SourceError(
                source_name=source.name,
                error_type=ErrorType.CONNECTION,
                message=f"HTTP timeout after {self.timeout}s",
            )]
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP {e.response.status_code} from '{source.name}'")
            return [], [SourceError(
                source_name=source.name,
                error_type=ErrorType.CONNECTION,
                message=f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
            )]
        except httpx.ConnectError as e:
            logger.warning(f"Connection error for '{source.name}': {e}")
            return [], [SourceError(
                source_name=source.name,
                error_type=ErrorType.CONNECTION,
                message=f"Connection failed: {e}",
            )]
        except Exception as e:
            logger.error(f"Unexpected error fetching '{source.name}': {e}", exc_info=True)
            return [], [SourceError(
                source_name=source.name,
                error_type=ErrorType.UNKNOWN,
                message=f"Unexpected: {type(e).__name__}: {e}",
            )]

    def _fetch_rss(self, source: SourceConfig) -> list[SourceItem]:
        """Fetch and parse an RSS/Atom feed.

        Uses httpx for HTTP (consistent timeouts) and feedparser for parsing.

        Args:
            source: RSS source configuration with feed URL.

        Returns:
            List of parsed SourceItem objects.
        """
        logger.debug(f"Fetching RSS: {source.name} ({source.url})")
        response = self._client.get(source.url)
        response.raise_for_status()

        feed = feedparser.parse(response.text)

        if feed.bozo and not feed.entries:
            raise ValueError(f"Malformed feed (bozo): {feed.bozo_exception}")

        items: list[SourceItem] = []
        for entry in feed.entries[: self.max_items]:
            try:
                item = self._entry_to_item(entry, source)
                items.append(item)
            except Exception as e:
                logger.debug(f"Skipping unparseable entry in '{source.name}': {e}")
                continue

        logger.info(f"Fetched {len(items)} items from '{source.name}'")
        return items

    def _entry_to_item(self, entry: Any, source: SourceConfig) -> SourceItem:
        """Convert a feedparser entry to a SourceItem.

        Args:
            entry: A feedparser entry dict.
            source: The source config this entry came from.

        Returns:
            Normalized SourceItem.
        """
        title = html_module.unescape(entry.get("title", "")).strip()
        link = entry.get("link", "").strip()

        if not title or not link:
            raise ValueError(f"Entry missing title or link: {entry.get('id', '?')}")

        published_at = self._parse_entry_date(entry)
        snippet = self._extract_snippet(entry)
        authors = self._extract_authors(entry)
        tags = self._extract_tags(entry)

        item_id = _generate_item_id(link, published_at)

        return SourceItem(
            id=item_id,
            title=title,
            url=link,
            source_name=source.name,
            source_category=source.category,
            published_at=published_at,
            snippet=snippet,
            authors=authors,
            tags=tags,
            language=self._guess_language(title, snippet),
            raw_metadata={
                "feed_id": entry.get("id", ""),
                "source_weight": source.weight,
            },
        )

    def _parse_entry_date(self, entry: Any) -> datetime:
        """Extract and normalize the publication date from a feed entry.

        Tries feedparser's parsed date first, then falls back to dateutil.

        Args:
            entry: A feedparser entry.

        Returns:
            UTC datetime.
        """
        # feedparser pre-parses dates into struct_time
        for field in ("published_parsed", "updated_parsed"):
            parsed = entry.get(field)
            if parsed:
                try:
                    ts = timegm(parsed)
                    return datetime.fromtimestamp(ts, tz=timezone.utc)
                except (ValueError, OverflowError):
                    continue

        # Fall back to raw string parsing
        for field in ("published", "updated"):
            raw = entry.get(field)
            if raw:
                try:
                    dt = dateutil_parser.parse(raw)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
                except (ValueError, OverflowError):
                    continue

        # Last resort: now
        logger.debug(f"No parseable date for entry '{entry.get('title', '?')}', using now")
        return datetime.now(tz=timezone.utc)

    def _extract_snippet(self, entry: Any) -> str:
        """Extract a text snippet from the entry summary/content.

        Strips HTML tags and truncates to ~300 chars.
        """
        raw = ""
        # Prefer summary, fall back to content
        if entry.get("summary"):
            raw = entry["summary"]
        elif entry.get("content"):
            # content is a list of dicts with 'value' key
            raw = entry["content"][0].get("value", "")

        # Strip HTML
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:500]

    def _extract_authors(self, entry: Any) -> list[str]:
        """Extract author names from feed entry."""
        authors = []
        if entry.get("author"):
            authors.append(entry["author"].strip())
        if entry.get("authors"):
            for a in entry["authors"]:
                name = a.get("name", "").strip()
                if name and name not in authors:
                    authors.append(name)
        return authors

    def _extract_tags(self, entry: Any) -> list[str]:
        """Extract tags/categories from feed entry."""
        tags = []
        if entry.get("tags"):
            for t in entry["tags"]:
                term = t.get("term", "").strip()
                if term:
                    tags.append(term.lower())
        return tags

    # ------------------------------------------------------------------
    # Scraping
    # ------------------------------------------------------------------

    def _fetch_scrape(self, source: SourceConfig) -> list[SourceItem]:
        """Scrape a web page for items using a source-specific parser.

        Dispatches to a parser based on source.name. Only sources with
        registered parsers are supported — no generic scraping.

        Args:
            source: Scrape source config with target URL.

        Returns:
            List of parsed SourceItem objects.
        """
        parser_map = {
            "Anthropic Blog": self._scrape_anthropic,
        }
        parser = parser_map.get(source.name)
        if parser is None:
            logger.warning(f"No scraper registered for '{source.name}', skipping")
            return []
        return parser(source)

    def _scrape_anthropic(self, source: SourceConfig) -> list[SourceItem]:
        """Scrape Anthropic's /news page for blog post items.

        The page has two sections:
        1. FeaturedGrid: top featured posts with <h2>/<h4> titles, <time> dates, <p> snippets
        2. PublicationList: chronological list with <time> dates, <span> titles

        Both are server-rendered, no JS needed.
        """
        logger.debug(f"Scraping: {source.name} ({source.url})")
        response = self._client.get(source.url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        items: list[SourceItem] = []
        seen_hrefs: set[str] = set()

        # Find all links to /news/* articles
        for a_tag in soup.select("a[href*='/news/']"):
            href = a_tag.get("href", "")
            if not href or href in ("/news", "/news/") or href in seen_hrefs:
                continue
            seen_hrefs.add(href)

            # Extract title from heading or span
            title_el = (
                a_tag.find(["h2", "h4"])
                or a_tag.select_one("[class*='title']")
            )
            title = title_el.get_text(strip=True) if title_el else ""
            if not title or len(title) < 5:
                continue

            # Extract date from <time> element
            time_el = a_tag.find("time")
            published_at = datetime.now(tz=timezone.utc)
            if time_el:
                date_text = time_el.get("datetime", "") or time_el.get_text(strip=True)
                if date_text:
                    try:
                        published_at = dateutil_parser.parse(date_text)
                        if published_at.tzinfo is None:
                            published_at = published_at.replace(tzinfo=timezone.utc)
                    except (ValueError, OverflowError):
                        pass

            # Extract snippet from <p> element
            snippet_el = a_tag.find("p")
            snippet = snippet_el.get_text(strip=True)[:500] if snippet_el else ""

            # Extract category from span with "caption bold" or "subject"
            category_el = a_tag.select_one("span[class*='caption'], span[class*='subject']")
            tags = []
            if category_el:
                cat_text = category_el.get_text(strip=True).lower()
                if cat_text and cat_text not in title.lower():
                    tags.append(cat_text)

            # Build full URL
            full_url = href if href.startswith("http") else f"https://www.anthropic.com{href}"
            item_id = _generate_item_id(full_url, published_at)

            try:
                item = SourceItem(
                    id=item_id,
                    title=title,
                    url=full_url,
                    source_name=source.name,
                    source_category=source.category,
                    published_at=published_at,
                    snippet=snippet,
                    tags=tags,
                    language="en",
                    raw_metadata={"source_weight": source.weight},
                )
                items.append(item)
            except Exception as e:
                logger.debug(f"Skipping unparseable Anthropic entry '{title}': {e}")
                continue

            if len(items) >= self.max_items:
                break

        logger.info(f"Scraped {len(items)} items from '{source.name}'")
        return items

    def _guess_language(self, title: str, snippet: str) -> str:
        """Simple language detection based on common Spanish markers.

        Not a real NLP detector — just checks for obvious Spanish patterns.
        Good enough for preliminary scoring; Signal Scorer can refine.
        """
        text = (title + " " + snippet).lower()
        es_markers = [
            " de ", " en ", " con ", " los ", " las ", " del ", " para ",
            " una ", " por ", " que ", " como ", " más ", " esta ", " sobre ",
        ]
        es_count = sum(1 for m in es_markers if m in text)
        if es_count >= 3:
            return "es"
        return "en"


def _generate_item_id(url: str, published_at: datetime) -> str:
    """Generate a deterministic, unique ID for a source item."""
    raw = f"{url}|{published_at.isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
