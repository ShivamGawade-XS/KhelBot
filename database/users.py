"""
KhelBot Users Database — CRUD operations for the users table.
Provides non-blocking async functions for Telegram event loop and sync fallbacks.
"""

import asyncio
from typing import Optional
from database.client import get_client
from utils.logger import setup_logger

log = setup_logger("db.users")


def create_or_update_user(telegram_id: int, username: str = None) -> bool:
    """
    Create a new user or update existing user's info.
    Uses upsert to handle both cases.
    """
    try:
        client = get_client()
        data = {
            "telegram_id": telegram_id,
            "username": username or "",
        }
        client.table("users").upsert(
            data, 
            on_conflict="telegram_id"
        ).execute()
        log.info(f"User upserted: {telegram_id}")
        return True
    except Exception as e:
        log.error(f"Failed to upsert user {telegram_id}: {e}")
        return False


def update_user_query_count(telegram_id: int) -> bool:
    """
    Increment user's query count via RPC function or fallback update.
    Auto-creates the user record if it doesn't exist yet.
    """
    try:
        client = get_client()
        try:
            client.rpc("increment_query_count", {"uid": telegram_id}).execute()
        except Exception:
            # Fallback if RPC function is not created in Supabase yet
            create_or_update_user(telegram_id)
        return True
    except Exception as e:
        log.error(f"Failed to increment query count for {telegram_id}: {e}")
        return False


def set_favorite_team(telegram_id: int, team: str) -> bool:
    """
    Set a user's favorite team. Auto-creates user if not already registered.
    """
    try:
        create_or_update_user(telegram_id)
        client = get_client()
        client.table("users").update(
            {"favorite_team": team}
        ).eq("telegram_id", telegram_id).execute()
        log.info(f"Favorite team set for {telegram_id}: {team}")
        return True
    except Exception as e:
        log.error(f"Failed to set favorite team for {telegram_id}: {e}")
        return False


def get_user(telegram_id: int) -> Optional[dict]:
    """Fetch a user record by Telegram ID."""
    try:
        client = get_client()
        result = client.table("users").select("*").eq(
            "telegram_id", telegram_id
        ).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        log.error(f"Failed to fetch user {telegram_id}: {e}")
        return None


def delete_user_data(telegram_id: int) -> bool:
    """
    Delete all user data (GDPR/DPDP compliance).
    Removes records from reminders and users tables.
    """
    try:
        client = get_client()
        # Delete reminders first (FK constraint)
        client.table("reminders").delete().eq(
            "telegram_id", telegram_id
        ).execute()
        log.info(f"Reminders deleted for {telegram_id}")

        # Delete user record
        client.table("users").delete().eq(
            "telegram_id", telegram_id
        ).execute()
        log.info(f"User data deleted for {telegram_id}")
        return True
    except Exception as e:
        log.error(f"Failed to delete data for {telegram_id}: {e}")
        return False


# ── Non-blocking Async Wrappers for Event Loop Safety ───────────────────────

async def async_create_or_update_user(telegram_id: int, username: str = None) -> bool:
    """Non-blocking async wrapper with 2-second timeout."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(create_or_update_user, telegram_id, username),
            timeout=2.0
        )
    except Exception as e:
        log.warning(f"Async upsert user timeout or error: {e}")
        return False


async def async_update_user_query_count(telegram_id: int) -> bool:
    """Non-blocking async wrapper with 1.5-second timeout."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(update_user_query_count, telegram_id),
            timeout=1.5
        )
    except Exception as e:
        log.debug(f"Async query count bump skipped: {e}")
        return False


async def async_set_favorite_team(telegram_id: int, team: str) -> bool:
    """Non-blocking async wrapper with 2-second timeout."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(set_favorite_team, telegram_id, team),
            timeout=2.0
        )
    except Exception as e:
        log.error(f"Async set favorite team error: {e}")
        return False


async def async_get_user(telegram_id: int) -> Optional[dict]:
    """Non-blocking async wrapper with 2-second timeout."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(get_user, telegram_id),
            timeout=2.0
        )
    except Exception as e:
        log.error(f"Async get user error: {e}")
        return None


async def async_delete_user_data(telegram_id: int) -> bool:
    """Non-blocking async wrapper with 3-second timeout."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(delete_user_data, telegram_id),
            timeout=3.0
        )
    except Exception as e:
        log.error(f"Async delete user data error: {e}")
        return False
