#!/usr/bin/env python3
"""Project Autopilot — CLI dispatcher.

Top-level entry point that routes subcommands to the appropriate agent.

Usage:
    python autopilot.py scan --property ai-brief-latam
    python autopilot.py scan --property ai-brief-latam --top 10
    python autopilot.py scan --property ai-brief-latam --json
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python autopilot.py <command> [options]")
        print()
        print("Commands:")
        print("  scan    Run Source Monitor to discover and rank new items")
        print("  score   Run Signal Scorer on Source Monitor output (requires ANTHROPIC_API_KEY)")
        print("  brief   Generate editorial briefs from scored items (requires ANTHROPIC_API_KEY)")
        return 1

    command = sys.argv[1]

    if command == "scan":
        from agents.source_monitor.cli import main as scan_main
        return scan_main(sys.argv[2:])
    elif command == "score":
        from agents.signal_scorer.cli import main as score_main
        return score_main(sys.argv[2:])
    elif command == "brief":
        from agents.editorial.cli import main as brief_main
        return brief_main(sys.argv[2:])
    else:
        print(f"Unknown command: {command}")
        print("Available: scan, score, brief")
        return 1


if __name__ == "__main__":
    sys.exit(main())
