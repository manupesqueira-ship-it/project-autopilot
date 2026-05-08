"""CLI entry point for Publisher agent."""

from __future__ import annotations

import argparse
import io
import logging
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.publisher.agent import PublisherAgent
from agents.publisher.schemas import PublisherOutput, PublishChannel, PublishStatus


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_result(output: PublisherOutput) -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    console.print()

    s = output.stats
    console.print(Panel(
        f"[bold]Publisher[/bold]\n"
        f"Property: [cyan]{output.property}[/cyan]\n"
        f"Items: [green]{s.items_ready}[/green] ready  |  "
        f"IG: {s.items_instagram}  |  Newsletter: {s.items_newsletter}  |  "
        f"Files: {s.files_exported}\n"
        f"Export: [dim]{output.export_dir}[/dim]",
        style="blue",
    ))

    for item in output.items:
        console.print()
        console.print(f"  [green]READY[/green] — {item.brief_title}")
        console.print(f"  Channel: [cyan]{item.channel.value}[/cyan]")
        if item.caption_file:
            console.print(f"    [dim]Caption:[/dim] {item.caption_file}")
        if item.slides_file:
            console.print(f"    [dim]Slides:[/dim]  {item.slides_file}")
        if item.newsletter_file:
            console.print(f"    [dim]Newsletter:[/dim] {item.newsletter_file}")
        if item.reel_file:
            console.print(f"    [dim]Reel:[/dim]   {item.reel_file}")

    console.print()
    console.print(f"  [bold]Next steps:[/bold]")
    console.print(f"    1. Open export folder: [cyan]{output.export_dir}[/cyan]")
    console.print(f"    2. Copy caption.txt to Buffer/Instagram")
    console.print(f"    3. Build carousel in Canva from slides.md")
    console.print(f"    4. Copy newsletter.md to Beehiiv")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="publisher",
        description="Export approved content as publish-ready files.",
    )
    parser.add_argument("--property", "-p", required=True)
    parser.add_argument("--run-id", default=None, help="Approval run ID")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--log-level", default="WARNING",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--config-dir", type=Path, default=None)

    args = parser.parse_args(argv)
    _setup_logging(args.log_level)

    try:
        agent = PublisherAgent(property_name=args.property, config_dir=args.config_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    output = agent.run(approval_run_id=args.run_id)

    if args.json_output:
        print(output.model_dump_json(indent=2))
    else:
        _print_result(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
