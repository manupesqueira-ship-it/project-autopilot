"""Source Monitor agent — Wave 1, Capa 2.

Discovers and ranks new content items from configured sources (RSS, Inoreader, selective scraping).
Delivers a deduplicated, scored shortlist to the Signal Scorer or directly to human review.

See DESIGN.md for full specification.
"""

from agents.source_monitor.agent import SourceMonitorAgent
from agents.source_monitor.schemas import SourceItem, SourceMonitorResult

__all__ = ["SourceMonitorAgent", "SourceItem", "SourceMonitorResult"]
