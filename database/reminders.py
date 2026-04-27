"""
KhelBot Reminders Database — CRUD operations for match reminders.
"""

from datetime import datetime
from typing import Optional
from database.client import get_client
from utils.logger import setup_logger

log = setup_logger("db.reminders")


def create_reminder(telegram_id: int, team_name: str, match_id: str = None, remind_at: datetime = None) -> bool:
    """
    Create a match reminder for a user.
    
    Args:
        telegram_id: Telegram user ID
        team_name: Team to remind about
        match_id: Optional match ID
        remind_at: When to send the reminder
    
    Returns:
        True if successful, False otherwise
    """
    try:
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
    """
    Fetch all unsent reminders that are due now.
    
    Returns:
        List of reminder dicts
    """
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
    """
    Mark a reminder as sent.
    
    Args:
        reminder_id: Reminder ID
    
    Returns:
        True if successful, False otherwise
    """
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
    """
    Fetch all active (unsent) reminders for a user.
    
    Args:
        telegram_id: Telegram user ID
    
    Returns:
        List of reminder dicts
    """
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
