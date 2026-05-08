"""CLI entry point for Source Monitor agent.

Usage:
    python -m agents.source_monitor.cli --property ai-brief-latam
    python -m agents.source_monitor.cli --property ai-brief-latam --top 5
    python -m agents.source_monitor.cli --property ai-brief-latam --json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Ensure project root is on sys.path
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.source_monitor.agent import SourceMonitorAgent
from agents.source_monitor.schemas import SourceMonitorResult


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_result_table(result: SourceMonitorResult, top_n: int) -> None:
    """Pretty-print the scan result using rich."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text

    console = Console()

    # Header
    console.print()
    console.print(Panel(
        f"[bold]Source Monitor Scan[/bold]\n"
        f"Property: [cyan]{result.property}[/cyan]  |  "
        f"Run: [dim]{result.run_id}[/dim]",
        style="blue",
    ))

    # Stats bar
    s = result.stats
    console.print(
        f"  Sources: [green]{s.sources_checked - s.sources_failed}[/green]"
        f"/[dim]{s.sources_checked}[/dim] OK  |  "
        f"Items: [green]{s.items_found}[/green] found  |  "
        f"Dedup: [yellow]-{s.dedup_removed}[/yellow]  |  "
        f"Unique: [bold green]{s.items_after_dedup}[/bold green]  |  "
        f"Avg score: [cyan]{s.avg_preliminary_score:.1f}[/cyan]"
    )
    console.print()

    # Errors
    if result.errors:
        console.print(f"  [red]Errors ({len(result.errors)}):[/red]")
        for err in result.errors:
            console.print(f"    [red]x[/red] {err.source_name}: {err.message}")
        console.print()

    # Items table
    items = result.items[:top_n]
    if not items:
        console.print("  [dim]No new items found.[/dim]")
        return

    table = Table(show_header=True, header_style="bold", pad_edge=False, box=None)
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Score", width=6, justify="right")
    table.add_column("Source", width=16, style="cyan")
    table.add_column("Title", min_width=40)
    table.add_column("Age", width=6, justify="right")
    table.add_column("Lang", width=4, justify="center")

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    for i, item in enumerate(items, 1):
        # Format score with color
        score = item.preliminary_score
        if score >= 50:
            score_str = f"[bold green]{score:.0f}[/bold green]"
        elif score >= 30:
            score_str = f"[yellow]{score:.0f}[/yellow]"
        else:
            score_str = f"[dim]{score:.0f}[/dim]"

        # Format age
        pub = item.published_at
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        age_hours = (now - pub).total_seconds() / 3600
        if age_hours < 1:
            age_str = f"{int(age_hours * 60)}m"
        elif age_hours < 24:
            age_str = f"{age_hours:.0f}h"
        else:
            age_str = f"{age_hours / 24:.0f}d"

        # Truncate source name
        source = item.source_name[:16]

        # Title with URL hint
        title = item.title[:80]

        table.add_row(str(i), score_str, source, title, age_str, item.language)

    console.print(table)
    console.print()

    # Top item detail
    top = items[0]
    console.print(Panel(
        f"[bold]{top.title}[/bold]\n\n"
        f"{top.snippet[:200]}{'...' if len(top.snippet) > 200 else ''}\n\n"
        f"[dim]URL: {top.url}[/dim]\n"
        f"[dim]Score breakdown: {top.score_breakdown}[/dim]",
        title=f"[green]#1 — {top.preliminary_score:.0f} pts[/green]",
        style="green",
    ))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="source_monitor",
        description="Scan configured sources and produce a ranked shortlist of new items.",
    )
    parser.add_argument(
        "--property", "-p",
        required=True,
        help="Property name (e.g. ai-brief-latam)",
    )
    parser.add_argument(
        "--top", "-n",
        type=int,
        default=15,
        help="Show top N items (default: 15)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output raw JSON instead of formatted table",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: WARNING for clean output)",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=None,
        help="Override project root directory",
    )

    args = parser.parse_args(argv)
    _setup_logging(args.log_level)

    try:
        agent = SourceMonitorAgent(
            property_name=args.property,
            config_dir=args.config_dir,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    result = agent.run()

    if args.json_output:
        print(result.model_dump_json(indent=2))
    else:
        _print_result_table(result, args.top)

    return 0


if __name__ == "__main__":
    sys.exit(main())
