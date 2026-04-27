"""
KhelBot Reply Utility — Centralized safe message sending.
Handles Telegram's strict Markdown parser gracefully.
"""

from telegram import Update
from telegram.error import BadRequest
from utils.logger import setup_logger

log = setup_logger("reply")


async def safe_reply(update: Update, text: str, **kwargs) -> None:
    """
    Send a reply message with automatic Markdown fallback.
    If Telegram can't parse Markdown entities, retries without parse_mode.

    Args:
        update: Telegram Update object
        text: Message text to send
        **kwargs: Additional args passed to reply_text (e.g., parse_mode, reply_markup)
    """
    try:
        await update.message.reply_text(text, **kwargs)
    except BadRequest as e:
        if "parse" in str(e).lower() or "entities" in str(e).lower():
            log.warning(f"Markdown parse failed, retrying plain: {e}")
            kwargs.pop("parse_mode", None)
            try:
                await update.message.reply_text(text, **kwargs)
            except Exception as inner_e:
                log.error(f"Failed even without markdown: {inner_e}")
        else:
            log.error(f"BadRequest (non-parse): {e}")
            raise e
    except Exception as e:
        log.error(f"Reply failed: {e}")


async def safe_send(bot, chat_id: int, text: str, **kwargs) -> None:
    """
    Send a message to a specific chat_id with Markdown fallback.
    Used for reminders and proactive messages.

    Args:
        bot: Telegram Bot instance
        chat_id: Target chat ID
        text: Message text
        **kwargs: Additional args
    """
    try:
        await bot.send_message(chat_id=chat_id, text=text, **kwargs)
    except BadRequest as e:
        if "parse" in str(e).lower() or "entities" in str(e).lower():
            log.warning(f"Markdown parse failed for chat {chat_id}, retrying plain: {e}")
            kwargs.pop("parse_mode", None)
            try:
                await bot.send_message(chat_id=chat_id, text=text, **kwargs)
            except Exception as inner_e:
                log.error(f"Send failed even without markdown for {chat_id}: {inner_e}")
        else:
            raise e
    except Exception as e:
        log.error(f"Send to {chat_id} failed: {e}")
