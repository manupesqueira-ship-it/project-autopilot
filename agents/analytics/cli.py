"""CLI entry point for Analytics agent."""

from __future__ import annotations

import argparse
import io
import logging
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.analytics.agent import AnalyticsAgent
from agents.analytics.schemas import AnalyticsOutput


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_result(output: AnalyticsOutput) -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    console.print()

    wr = output.weekly_report
    if wr:
        console.print(Panel(
            f"[bold]Analytics Report[/bold]\n"
            f"Property: [cyan]{output.property}[/cyan]  |  "
            f"Period: {wr.week_start} to {wr.week_end}\n\n"
            f"Scans: [bold]{wr.total_scans}[/bold]  |  "
            f"Items discovered: [bold]{wr.total_items_discovered}[/bold]  |  "
            f"Published: [bold]{wr.total_pieces_published}[/bold]\n"
            f"API tokens: {wr.total_api_tokens:,}  |  "
            f"Est. cost: [cyan]${wr.total_api_cost_estimate:.2f}[/cyan]",
            style="blue",
        ))

        if wr.recommendations:
            console.print()
            console.print("  [bold]Recommendations:[/bold]")
            for rec in wr.recommendations:
                console.print(f"    - {rec}")
    else:
        console.print("[dim]No weekly report available.[/dim]")

    if output.pipeline_runs:
        console.print()
        table = Table(title="Pipeline Runs", show_header=True, pad_edge=False)
        table.add_column("Date", width=12)
        table.add_column("Items", justify="right", width=7)
        table.add_column("Tokens", justify="right", width=10)
        table.add_column("Cost", justify="right", width=8)

        for run in output.pipeline_runs[-10:]:  # Last 10
            table.add_row(
                run.date,
                str(run.source_items_found),
                f"{run.total_api_tokens:,}",
                f"${run.total_api_cost_estimate:.3f}",
            )
        console.print(table)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="analytics",
        description="View pipeline analytics and performance metrics.",
    )
    parser.add_argument("--property", "-p", required=True)
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--log-level", default="WARNING",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--config-dir", type=Path, default=None)

    args = parser.parse_args(argv)
    _setup_logging(args.log_level)

    try:
        agent = AnalyticsAgent(property_name=args.property, config_dir=args.config_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    output = agent.run()

    if args.json_output:
        print(output.model_dump_json(indent=2))
    else:
        _print_result(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
