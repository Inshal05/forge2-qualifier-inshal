"""Lightweight Hermes-style autonomous agent core.

Manages memory, skill dispatch, configuration, logging and scheduling for the
Forge 2 qualifier demo.
"""

import json
import logging
import threading
import time
from typing import Optional

import schedule

from config import get_settings
from logging_config import (
    configure_logging,
    log_autonomous_event,
    log_error_event,
    log_memory_event,
    log_skill_event,
)
from memory_store import Memory
from openclaw_bridge import OpenClawUnavailableError, send_task_to_openclaw
from skill_loader import discover_skills, get_skill, list_skills

settings = get_settings()

try:
    from groq import Groq
except ImportError:
    Groq = None

client = Groq(api_key=settings.GROQ_API_KEY) if Groq else None

configure_logging()
logger = logging.getLogger("hermes")
memory = Memory()
discover_skills()


def run_skill(name: str, payload: dict | str) -> Optional[dict]:
    """Run a discovered skill and record the result."""
    try:
        result = get_skill(name)(payload)
        log_skill_event("skill_executed", name=name, result=result)
        return result
    except Exception as exc:
        log_error_event("skill_failed", name=name, error=str(exc))
        return None


def auto_status() -> None:
    """Scheduled task that records an autonomous status report."""
    details = {
        "memory": memory.list_all(),
        "available_skills": list_skills(),
    }
    log_autonomous_event(event="status_report", details=details)

    print("\n========================")
    print("[AUTONOMOUS RUN]")
    print("========================")
    print("What I Did:")
    print("- Checked memory and skill status")
    print("\nWhat's Left:")
    print("- None - autonomous loop is self-maintaining")
    print("\nWhat Needs Your Call:")
    print("- Review logs for details")
    print("========================\n")


def start_scheduler() -> None:
    """Start a background scheduler using the interval from configuration."""
    interval = getattr(settings, "AUTONOMOUS_INTERVAL_SECONDS", 60)
    schedule.clear()
    schedule.every(interval).seconds.do(auto_status)
    logger.info(json.dumps({"event": "scheduler_started", "interval_seconds": interval}))

    while True:
        schedule.run_pending()
        time.sleep(1)


def main() -> None:
    threading.Thread(target=start_scheduler, daemon=True).start()

    try:
        while True:
            user = input("\nYou: ").strip()
            command = user.lower()

            if command == "exit":
                print("Goodbye!")
                break
            if command in {"skills", "list skills"}:
                print("Available skills:", ", ".join(list_skills()) or "none")
                continue
            if command.startswith("remember "):
                memory_id = memory.add({"text": user.removeprefix("remember ").strip()})
                log_memory_event("memory_added", memory_id=memory_id)
                print("Remembered:", memory_id)
                continue
            if command == "recall":
                print(json.dumps(memory.list_all(), indent=2))
                continue
            if command.startswith("summarize "):
                result = run_skill("summarize", user.removeprefix("summarize "))
                print(json.dumps(result, indent=2))
                continue
            if command.startswith("openclaw "):
                prompt = user.removeprefix("openclaw ").strip()
                try:
                    result = send_task_to_openclaw(prompt)
                except OpenClawUnavailableError as exc:
                    log_error_event("openclaw_unavailable", error=str(exc))
                    print(str(exc))
                    continue
                except Exception as exc:
                    log_error_event("openclaw_task_failed", error=str(exc))
                    print(f"OpenClaw task failed before execution: {exc}")
                    continue

                print(json.dumps({
                    "task_id": result.task_id,
                    "ok": result.ok,
                    "returncode": result.returncode,
                    "duration_seconds": result.duration_seconds,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }, indent=2))
                continue

            print("Hermes received:", user)
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
