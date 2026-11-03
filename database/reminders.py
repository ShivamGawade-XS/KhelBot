"""
KhelBot Reminders Database — CRUD operations for match reminders.
Includes auto-registration safeguards for foreign keys and non-blocking async execution.
"""

import asyncio
from datetime import datetime
from typing import Optional, List
from database.client import get_client
from database.users import create_or_update_user
from utils.logger import setup_logger

log = setup_logger("db.reminders")


def create_reminder(telegram_id: int, team_name: str, match_id: str = None, remind_at: datetime = None) -> bool:
    """
    Create a match reminder for a user.
    Ensures user exists in users table first to avoid FK constraint errors.
    """
    try:
        # Pre-flight check: ensure parent user row exists
        create_or_update_user(telegram_id)

        client = get_client()
        data = {
            "telegram_id": telegram_id,
            "team_name": team_name,
            "match_id": match_id or "",
            "remind_at": remind_at.isoformat() if remind_at else datetime.utcnow().isoformat(),
            "sent": False,
        }
        
        client.table("reminders").insert(data).execute()
        log.info(f"Reminder created for {telegram_id}: {team_name}")
        return True
    except Exception as e:
        log.error(f"Failed to create reminder for {telegram_id}: {e}")
        return False


def get_pending_reminders() -> list[dict]:
    """Fetch all unsent reminders that are due now."""
    try:
        client = get_client()
        now = datetime.utcnow().isoformat()
        
        result = client.table("reminders").select("*").eq(
            "sent", False
        ).lte(
            "remind_at", now
        ).execute()
        
        return result.data or []
    except Exception as e:
        log.error(f"Failed to fetch pending reminders: {e}")
        return []


def mark_reminder_sent(reminder_id: int) -> bool:
    """Mark a reminder as sent."""
    try:
        client = get_client()
        client.table("reminders").update(
            {"sent": True}
        ).eq("id", reminder_id).execute()
        log.info(f"Reminder {reminder_id} marked as sent")
        return True
    except Exception as e:
        log.error(f"Failed to mark reminder {reminder_id} as sent: {e}")
        return False


def get_user_reminders(telegram_id: int) -> list[dict]:
    """Fetch all active (unsent) reminders for a user."""
    try:
        client = get_client()
        result = client.table("reminders").select("*").eq(
            "telegram_id", telegram_id
        ).eq(
            "sent", False
        ).execute()
        return result.data or []
    except Exception as e:
        log.error(f"Failed to fetch reminders for {telegram_id}: {e}")
        return []


# ── Non-blocking Async Wrappers for Event Loop Safety ───────────────────────

async def async_create_reminder(telegram_id: int, team_name: str, match_id: str = None, remind_at: datetime = None) -> bool:
    """Non-blocking async create reminder with 3.0s timeout."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(create_reminder, telegram_id, team_name, match_id, remind_at),
            timeout=3.0
        )
    except Exception as e:
        log.error(f"Async create reminder error: {e}")
        return False


async def async_get_pending_reminders() -> list[dict]:
    """Non-blocking async fetch pending reminders."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(get_pending_reminders),
            timeout=4.0
        )
    except Exception as e:
        log.error(f"Async get pending reminders error: {e}")
        return []


async def async_mark_reminder_sent(reminder_id: int) -> bool:
    """Non-blocking async mark reminder sent."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(mark_reminder_sent, reminder_id),
            timeout=2.0
        )
    except Exception as e:
        log.error(f"Async mark reminder sent error: {e}")
        return False
