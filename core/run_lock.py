"""Run lock — prevents concurrent Project Autopilot cycles.

File-based lock under logs/locks/<project_id>.lock.
No external dependencies.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCKS_DIR = REPO_ROOT / "logs" / "locks"

# Default: 4 hours. A cycle should never take this long.
DEFAULT_MAX_AGE_SECONDS = 4 * 60 * 60


class LockActiveError(Exception):
    """Raised when a lock is already held and not stale."""

    def __init__(self, project_id: str, lock_path: Path, lock_info: dict) -> None:
        self.project_id = project_id
        self.lock_path = lock_path
        self.lock_info = lock_info
        pid = lock_info.get("pid", "?")
        started = lock_info.get("started_at", "?")
        super().__init__(
            f"Project Autopilot cycle already running for '{project_id}'.\n"
            f"  Lock file: {lock_path}\n"
            f"  PID: {pid}\n"
            f"  Started: {started}\n"
            f"If you are sure no other cycle is running, delete the lock file manually."
        )


def _lock_path(project_id: str) -> Path:
    return LOCKS_DIR / f"{project_id}.lock"


def _read_lock(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _is_stale(lock_info: dict, max_age_seconds: int) -> bool:
    created = lock_info.get("created_epoch")
    if created is None:
        return True
    return (time.time() - created) > max_age_seconds


def acquire_lock(project_id: str, max_age_seconds: int = DEFAULT_MAX_AGE_SECONDS) -> Path:
    """Acquire a run lock. Raises LockActiveError if already held (and not stale)."""
    path = _lock_path(project_id)
    existing = _read_lock(path)

    if existing is not None:
        if _is_stale(existing, max_age_seconds):
            # Stale lock — remove and re-acquire
            path.unlink(missing_ok=True)
        else:
            raise LockActiveError(project_id, path, existing)

    path.parent.mkdir(parents=True, exist_ok=True)
    lock_info = {
        "project_id": project_id,
        "pid": os.getpid(),
        "created_epoch": time.time(),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    path.write_text(json.dumps(lock_info, indent=2), encoding="utf-8")
    return path


def release_lock(project_id: str) -> None:
    """Release a run lock. Safe to call even if no lock exists."""
    path = _lock_path(project_id)
    path.unlink(missing_ok=True)


def is_locked(project_id: str, max_age_seconds: int = DEFAULT_MAX_AGE_SECONDS) -> bool:
    """Check if a non-stale lock exists."""
    path = _lock_path(project_id)
    existing = _read_lock(path)
    if existing is None:
        return False
    if _is_stale(existing, max_age_seconds):
        return False
    return True


def lock_status(project_id: str, max_age_seconds: int = DEFAULT_MAX_AGE_SECONDS) -> dict:
    """Return lock status dict: locked, stale, pid, started_at, lock_path."""
    path = _lock_path(project_id)
    existing = _read_lock(path)
    if existing is None:
        return {"locked": False, "stale": False, "pid": None, "started_at": None, "lock_path": str(path)}
    stale = _is_stale(existing, max_age_seconds)
    return {
        "locked": not stale,
        "stale": stale,
        "pid": existing.get("pid"),
        "started_at": existing.get("started_at"),
        "lock_path": str(path),
    }
