"""Managed Next.js dev server for Flow QA.

Starts a Next.js dev server as a subprocess with specific env vars
(e.g., NEXT_PUBLIC_MIRA_ENABLE_QA_MOCKS=true) without modifying .env files.
Stops the server cleanly when done.

Safety:
- Does NOT modify .env or .env.local.
- Sets env vars only for the subprocess.
- Kills subprocess on cleanup.
- Does not kill unrelated user processes.
"""
from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PORT = 3000
STARTUP_TIMEOUT = 60  # seconds
SHUTDOWN_TIMEOUT = 10  # seconds


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def wait_for_server(port: int, timeout: int = STARTUP_TIMEOUT) -> bool:
    """Wait until the dev server responds on the given port."""
    import urllib.request
    import urllib.error

    base = f"http://localhost:{port}"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            req = urllib.request.Request(base, method="GET")
            resp = urllib.request.urlopen(req, timeout=5)
            if resp.status < 500:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


class DevServer:
    """Managed Next.js dev server subprocess."""

    def __init__(self, port: int = DEFAULT_PORT, extra_env: dict[str, str] | None = None):
        self.port = port
        self.extra_env = extra_env or {}
        self.process: subprocess.Popen[bytes] | None = None
        self._started_by_us = False

    @property
    def base_url(self) -> str:
        return f"http://localhost:{self.port}"

    def start(self) -> tuple[bool, str]:
        """Start the dev server. Returns (success, message)."""
        if is_port_in_use(self.port):
            return False, f"PORT_BUSY: Port {self.port} already in use. Cannot start managed dev server."

        env = os.environ.copy()
        env.update(self.extra_env)
        env["PORT"] = str(self.port)

        # Use npm run dev
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        try:
            self.process = subprocess.Popen(
                [npm_cmd, "run", "dev"],
                cwd=str(REPO_ROOT),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                # On Windows, create a new process group so we can kill it cleanly
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
            )
        except Exception as e:
            return False, f"Failed to start dev server: {e}"

        print(f"[dev-server] Starting on port {self.port} (PID {self.process.pid})...")

        if wait_for_server(self.port):
            self._started_by_us = True
            print(f"[dev-server] Ready at {self.base_url}")
            return True, f"Dev server started at {self.base_url} (PID {self.process.pid})"
        else:
            # Server didn't come up in time
            self.stop()
            return False, f"Dev server did not respond within {STARTUP_TIMEOUT}s"

    def stop(self) -> None:
        """Stop the dev server if we started it."""
        if self.process is None:
            return

        print(f"[dev-server] Stopping (PID {self.process.pid})...")
        try:
            if sys.platform == "win32":
                # On Windows, send CTRL_BREAK to the process group
                self.process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                self.process.terminate()

            try:
                self.process.wait(timeout=SHUTDOWN_TIMEOUT)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        except Exception as e:
            print(f"[dev-server] Error stopping: {e}")
            try:
                self.process.kill()
            except Exception:
                pass

        self.process = None
        self._started_by_us = False
        print("[dev-server] Stopped.")

    def __enter__(self) -> "DevServer":
        return self

    def __exit__(self, *args: Any) -> None:
        self.stop()
