"""Centralized .env loading for Project Autopilot.

Loads .env and .env.local from the repo root.  Empty values in .env.local
do NOT clobber real values from .env — this handles the common case where
.env.local has ``OPENAI_API_KEY=`` (placeholder) while .env has the real key.
"""
from __future__ import annotations

import os
from pathlib import Path

_loaded = False

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_env() -> None:
    """Load environment variables from .env and .env.local exactly once."""
    global _loaded
    if _loaded:
        return
    _loaded = True

    _apply_dotenv(REPO_ROOT / ".env")
    _apply_dotenv(REPO_ROOT / ".env.local")


def _apply_dotenv(path: Path) -> None:
    """Parse a .env file and set values in os.environ.

    Rules:
    - Lines starting with # are comments.
    - Empty lines are skipped.
    - Values are trimmed.  Surrounding quotes (' or ") are stripped.
    - An empty value never overwrites a non-empty existing value.
    """
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        eq = line.find("=")
        if eq < 0:
            continue
        key = line[:eq].strip()
        value = line[eq + 1:].strip()
        # Strip surrounding quotes
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        # Never let an empty value clobber a real one
        if not value and os.environ.get(key):
            continue
        os.environ[key] = value
