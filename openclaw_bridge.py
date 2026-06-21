"""Bridge from the local Hermes scaffold to the real OpenClaw CLI."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOG_PATH = Path("logs") / "openclaw_tasks.jsonl"


class OpenClawUnavailableError(RuntimeError):
    """Raised when the OpenClaw CLI is not installed or cannot be executed."""


@dataclass
class OpenClawTaskResult:
    task_id: str
    timestamp: str
    prompt: str
    command: list[str]
    returncode: int
    duration_seconds: float
    stdout: str
    stderr: str
    parsed_json: dict[str, Any] | None

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def _append_log(result: OpenClawTaskResult) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(result), ensure_ascii=False) + "\n")


def send_task_to_openclaw(
    prompt: str,
    *,
    agent: str = "main",
    session_key: str = "agent:main:hermes-openclaw",
    timeout_seconds: int = 600,
) -> OpenClawTaskResult:
    """Send one task to OpenClaw through the supported CLI agent command."""
    if not prompt.strip():
        raise ValueError("OpenClaw task prompt cannot be empty.")

    openclaw = shutil.which("openclaw")
    if not openclaw:
        raise OpenClawUnavailableError(
            "OpenClaw CLI is not installed or is not on PATH. Install with: npm install -g openclaw@latest"
        )

    command = [
        openclaw,
        "agent",
        "--agent",
        agent,
        "--session-key",
        session_key,
        "--message",
        prompt,
        "--json",
        "--timeout",
        str(timeout_seconds),
    ]

    start = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=os.getcwd(),
        capture_output=True,
        text=True,
        timeout=timeout_seconds + 10,
        check=False,
    )
    duration = time.monotonic() - start

    parsed_json: dict[str, Any] | None = None
    if completed.stdout.strip():
        try:
            parsed = json.loads(completed.stdout)
            if isinstance(parsed, dict):
                parsed_json = parsed
        except json.JSONDecodeError:
            parsed_json = None

    result = OpenClawTaskResult(
        task_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        prompt=prompt,
        command=command,
        returncode=completed.returncode,
        duration_seconds=round(duration, 3),
        stdout=completed.stdout,
        stderr=completed.stderr,
        parsed_json=parsed_json,
    )
    _append_log(result)
    return result
