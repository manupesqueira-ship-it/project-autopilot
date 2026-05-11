"""CLI entry point for Signal Scorer agent.

Usage:
    python -m agents.signal_scorer.cli --property ai-brief-latam
    python -m agents.signal_scorer.cli --property ai-brief-latam --top 5
    python -m agents.signal_scorer.cli --property ai-brief-latam --max-items 10
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.signal_scorer.agent import SignalScorerAgent
from agents.signal_scorer.schemas import Classification, SignalScorerResult


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_result(result: SignalScorerResult, top_n: int) -> None:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    console = Console()
    console.print()
    console.print(Panel(
        f"[bold]Signal Scorer[/bold]\n"
        f"Property: [cyan]{result.property}[/cyan]  |  "
        f"Source run: [dim]{result.source_run_id}[/dim]",
        style="blue",
    ))

    s = result.stats
    console.print(
        f"  Scored: [bold]{s.items_scored}[/bold]  |  "
        f"[bold green]Strong: {s.items_strong}[/bold green]  |  "
        f"[yellow]Consider: {s.items_consider}[/yellow]  |  "
        f"[dim]Discard: {s.items_discard}[/dim]  |  "
        f"Avg: [cyan]{s.avg_signal_score:.1f}[/cyan]  |  "
        f"Tokens: {s.total_input_tokens + s.total_output_tokens:,}"
    )
    console.print()

    if result.errors:
        console.print(f"  [red]API errors ({len(result.errors)}):[/red]")
        for err in result.errors[:3]:
            console.print(f"    [red]x[/red] {err[:80]}")
        console.print()

    items = result.items[:top_n]
    if not items:
        console.print("  [dim]No items scored.[/dim]")
        return

    table = Table(show_header=True, header_style="bold", pad_edge=False, box=None)
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Signal", width=7, justify="right")
    table.add_column("Prelim", width=7, justify="right", style="dim")
    table.add_column("Class", width=8)
    table.add_column("Source", width=16, style="cyan")
    table.add_column("Title", min_width=35)

    for i, item in enumerate(items, 1):
        # Classification coloring
        if item.classification == Classification.STRONG:
            cls_str = f"[bold green]{item.classification.value}[/bold green]"
            score_str = f"[bold green]{item.signal_score:.0f}[/bold green]"
        elif item.classification == Classification.CONSIDER:
            cls_str = f"[yellow]{item.classification.value}[/yellow]"
            score_str = f"[yellow]{item.signal_score:.0f}[/yellow]"
        else:
            cls_str = f"[dim]{item.classification.value}[/dim]"
            score_str = f"[dim]{item.signal_score:.0f}[/dim]"

        table.add_row(
            str(i), score_str, f"{item.preliminary_score:.0f}",
            cls_str, item.source_name[:16], item.title[:70],
        )

    console.print(table)
    console.print()

    # Detail panel for top items
    for item in items[:3]:
        if item.classification == Classification.DISCARD:
            continue
        style = "green" if item.classification == Classification.STRONG else "yellow"
        risk_str = f"\n[red]Risks: {', '.join(item.risk_flags)}[/red]" if item.risk_flags else ""
        console.print(Panel(
            f"[bold]{item.title}[/bold]\n\n"
            f"[italic]{item.justification}[/italic]\n\n"
            f"Ángulo: {item.suggested_angle}\n"
            f"[dim]URL: {item.url}[/dim]{risk_str}",
            title=f"[{style}]{item.signal_score:.0f} pts — {item.classification.value}[/{style}]",
            style=style,
        ))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="signal_scorer",
        description="Score source items using LLM-based Signal Scoring Rubric.",
    )
    parser.add_argument("--property", "-p", required=True)
    parser.add_argument("--top", "-n", type=int, default=15)
    parser.add_argument("--run-id", default=None, help="Source Monitor run ID to score")
    parser.add_argument("--max-items", type=int, default=None, help="Max items to score")
    parser.add_argument("--min-score", type=float, default=None, help="Min preliminary score")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--log-level", default="WARNING",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--config-dir", type=Path, default=None)

    args = parser.parse_args(argv)
    _setup_logging(args.log_level)

    try:
        agent = SignalScorerAgent(
            property_name=args.property,
            config_dir=args.config_dir,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    result = agent.run(
        source_run_id=args.run_id,
        min_preliminary_score=args.min_score,
        max_items=args.max_items,
    )

    if args.json_output:
        print(result.model_dump_json(indent=2))
    else:
        _print_result(result, args.top)

    return 0


if __name__ == "__main__":
    sys.exit(main())
