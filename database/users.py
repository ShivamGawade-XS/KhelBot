"""
KhelBot Users Database — CRUD operations for the users table.
"""

from typing import Optional
from database.client import get_client
from utils.logger import setup_logger

log = setup_logger("db.users")


def create_or_update_user(telegram_id: int, username: str = None) -> bool:
    """
    Create a new user or update existing user's info.
    Uses upsert to handle both cases.
    
    Args:
        telegram_id: Telegram user ID
        username: Telegram username (optional)
    
    Returns:
        True if successful, False otherwise
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
        
        log.info(f"User upserted: {telegram_id} (@{username})")
        return True
        
    except Exception as e:
        log.error(f"Failed to upsert user {telegram_id}: {e}")
        return False


def update_user_query_count(telegram_id: int) -> bool:
    """
    Increment user's query count via RPC function.
    
    Args:
        telegram_id: Telegram user ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_client()
        client.rpc("increment_query_count", {"uid": telegram_id}).execute()
        return True
        
    except Exception as e:
        log.error(f"Failed to increment query count for {telegram_id}: {e}")
        return False


def set_favorite_team(telegram_id: int, team: str) -> bool:
    """
    Set a user's favorite team.
    
    Args:
        telegram_id: Telegram user ID
        team: Official team name
    
    Returns:
        True if successful, False otherwise
    """
    try:
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
    """
    Fetch a user record by Telegram ID.
    
    Args:
        telegram_id: Telegram user ID
    
    Returns:
        User dict or None
    """
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
    Delete all user data (GDPR compliance).
    Removes from users and reminders tables.
    Does NOT delete from predictions (no personal data there).
    
    Args:
        telegram_id: Telegram user ID
    
    Returns:
        True if successful, False otherwise
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
