"""CLI entry point for Content Composer agent."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from agents.content_composer.agent import ContentComposerAgent
from agents.content_composer.schemas import ComposerOutput


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_result(output: ComposerOutput) -> None:
    import io, sys
    from rich.console import Console
    from rich.panel import Panel

    # Force UTF-8 output on Windows to handle emojis
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    console = Console()
    console.print()

    s = output.stats
    console.print(Panel(
        f"[bold]Content Composer[/bold]\n"
        f"Property: [cyan]{output.property}[/cyan]  |  "
        f"Editorial run: [dim]{output.editorial_run_id}[/dim]\n"
        f"Carousels: [green]{s.carousels_generated}[/green]  |  "
        f"Newsletters: [green]{s.newsletters_generated}[/green]  |  "
        f"Reels: [green]{s.reel_scripts_generated}[/green]  |  "
        f"Tokens: {s.total_input_tokens + s.total_output_tokens:,}",
        style="blue",
    ))

    for i, content in enumerate(output.content, 1):
        console.print()

        # Caption
        if content.carousel.caption.full_text:
            console.print(Panel(
                content.carousel.caption.full_text,
                title=f"[cyan]#{i} Caption — {content.brief_title[:50]}[/cyan]",
                style="cyan",
            ))

        # Carousel slides summary
        if content.carousel.slides:
            slides_preview = "\n".join(
                f"  [bold]Slide {s.slide_number}:[/bold] {s.headline}"
                for s in content.carousel.slides
            )
            console.print(Panel(
                slides_preview,
                title=f"[green]Carousel — {content.carousel.slide_count} slides[/green]",
                style="green",
            ))

        # Newsletter preview
        if content.newsletter.headline:
            nl = content.newsletter
            console.print(Panel(
                f"[bold]{nl.headline}[/bold]\n\n"
                f"{nl.intro}\n\n"
                f"[bold]POR QUÉ IMPORTA:[/bold] {nl.por_que_importa[:150]}...\n\n"
                f"[bold]BOTTOM LINE:[/bold] {nl.bottom_line}",
                title="[yellow]Newsletter Section[/yellow]",
                style="yellow",
            ))

        # Reel
        if content.reel_script:
            rs = content.reel_script
            console.print(Panel(
                f"[bold]HOOK (0-3s):[/bold] {rs.hook}\n\n"
                f"[bold]CLOSE:[/bold] {rs.close}\n"
                f"[bold]CTA:[/bold] {rs.cta}\n"
                f"[dim]Duration: {rs.estimated_duration_seconds}s[/dim]",
                title="[magenta]Reel Script[/magenta]",
                style="magenta",
            ))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="content_composer",
        description="Generate publishable content from editorial briefs.",
    )
    parser.add_argument("--property", "-p", required=True)
    parser.add_argument("--run-id", default=None, help="Editorial run ID")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--log-level", default="WARNING",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--config-dir", type=Path, default=None)

    args = parser.parse_args(argv)
    _setup_logging(args.log_level)

    try:
        agent = ContentComposerAgent(
            property_name=args.property,
            config_dir=args.config_dir,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    output = agent.run(editorial_run_id=args.run_id)

    if args.json_output:
        print(output.model_dump_json(indent=2))
    else:
        _print_result(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
