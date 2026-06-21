"""config.py – robust configuration handling with clear validation."""

import os
from dotenv import load_dotenv
load_dotenv()
from typing import Optional

REQUIRED_VARS = ["GROQ_API_KEY"]
OPTIONAL_VARS = {
    "OPENCLAW_API_KEY": None,
    "SLACK_WEBHOOK_URL": None,
    "AUTONOMOUS_INTERVAL_SECONDS": "60",
}


class MissingEnvironmentVariablesError(RuntimeError):
    """Raised when one or more required environment variables are absent."""

    def __init__(self, missing: list):
        self.missing = missing
        msg = "Missing required environment variable(s): " + ", ".join(missing)
        super().__init__(msg)


def get_settings():
    """Collect environment variables and return a Settings instance.
    Raises ``MissingEnvironmentVariablesError`` if any required variable is missing.
    """
    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing:
        raise MissingEnvironmentVariablesError(missing)

    class Settings:
        GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")  # required
        OPENCLAW_API_KEY: Optional[str] = os.getenv("OPENCLAW_API_KEY")
        SLACK_WEBHOOK_URL: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")
        AUTONOMOUS_INTERVAL_SECONDS: int = int(
            os.getenv(
                "AUTONOMOUS_INTERVAL_SECONDS",
                OPTIONAL_VARS["AUTONOMOUS_INTERVAL_SECONDS"]
            )
        )

    return Settings()


# Export a singleton for convenience, but validation happens on first use.
settings: Optional[object] = None

def init_settings():
    """Initialize the global settings object (call before first use)."""
    global settings
    if settings is None:
        settings = get_settings()