"""
KhelBot Configuration — Single source of truth for all environment variables.
Validates required vars at startup so we fail fast, not mid-conversation.
"""

import os
import sys
from dotenv import load_dotenv

# Load .env file (no-op in production where env vars are set directly)
load_dotenv()


def _require(var_name: str) -> str:
    """Get a required environment variable or exit with a clear error."""
    value = os.getenv(var_name)
    if not value:
        print(f"❌ FATAL: Missing required environment variable: {var_name}")
        print(f"   → Copy .env.example to .env and fill in your API keys.")
        sys.exit(1)
    return value


# ── Telegram ──────────────────────────────────────────────
TELEGRAM_BOT_TOKEN: str = _require("TELEGRAM_BOT_TOKEN")

# ── CricAPI ───────────────────────────────────────────────
CRICAPI_KEY: str = _require("CRICAPI_KEY")
CRICAPI_BASE_URL: str = "https://api.cricapi.com/v1"

# ── Meta Llama 3 via Groq ──────────────────────────────────
GROQ_API_KEY: str = _require("GROQ_API_KEY")
GROQ_MODEL: str = "llama3-70b-8192"

# ── Supabase ──────────────────────────────────────────────
SUPABASE_URL: str = _require("SUPABASE_URL")
SUPABASE_KEY: str = _require("SUPABASE_KEY")

# ── NewsAPI ───────────────────────────────────────────────
NEWSAPI_KEY: str = _require("NEWSAPI_KEY")
NEWSAPI_BASE_URL: str = "https://newsapi.org/v2"

# ── Cache TTLs (seconds) ─────────────────────────────────
CACHE_TTL_LIVE_SCORES: int = 60       # CricAPI live data
CACHE_TTL_PLAYER_STATS: int = 300     # CricAPI player stats
CACHE_TTL_NEWS: int = 3600            # NewsAPI headlines

# ── Bot Settings ──────────────────────────────────────────
BOT_NAME: str = "KhelBot 🏏"
MAX_INPUT_LENGTH: int = 200           # Max user input length
REMINDER_CHECK_INTERVAL: int = 30     # Minutes between reminder checks
