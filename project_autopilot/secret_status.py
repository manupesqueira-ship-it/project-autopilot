from __future__ import annotations

import os
from typing import Any


def env_var_status(name: str, min_length: int = 8) -> dict[str, Any]:
    """Return redacted environment variable presence status.

    This helper intentionally never returns the value, length, prefix, suffix, or
    any other material that could leak a secret into logs or reports.
    """
    raw = os.environ.get(name)
    if raw is None:
        status = "MISSING"
        present = False
        empty = False
        meets_threshold = False
    elif raw.strip() == "":
        status = "EMPTY"
        present = True
        empty = True
        meets_threshold = False
    else:
        status = "PRESENT_VALUE_HIDDEN"
        present = True
        empty = False
        meets_threshold = len(raw.strip()) >= min_length

    return {
        "name": name,
        "status": status,
        "present": present,
        "empty": empty,
        "meets_length_threshold": meets_threshold,
    }
