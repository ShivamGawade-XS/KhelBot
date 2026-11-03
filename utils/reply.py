"""
KhelBot Reply Utility — Centralized safe message sending.
Handles message chunking (>4000 chars), fallback for invalid Telegram Markdown,
and supports both standard messages and callback queries.
"""

from typing import List, Optional
from telegram import Update, Message
from telegram.error import BadRequest
from utils.logger import setup_logger

log = setup_logger("reply")

MAX_TELEGRAM_MESSAGE_LENGTH = 4000


def _split_text(text: str, max_length: int = MAX_TELEGRAM_MESSAGE_LENGTH) -> List[str]:
    """
    Split text into chunks smaller than max_length, preserving line breaks if possible.
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    remaining = text

    while len(remaining) > max_length:
        # Try to split at a newline within the first max_length characters
        split_idx = remaining.rfind("\n", 0, max_length)
        if split_idx == -1 or split_idx < max_length // 2:
            # If no good newline, try to split at a space
            split_idx = remaining.rfind(" ", 0, max_length)

        if split_idx == -1:
            # Hard split if no suitable whitespace
            split_idx = max_length

        chunk = remaining[:split_idx].strip()
        if chunk:
            chunks.append(chunk)
        remaining = remaining[split_idx:].strip()

    if remaining:
        chunks.append(remaining)

    return chunks


async def _send_chunk(target_send_fn, text_chunk: str, **kwargs) -> Optional[Message]:
    """Helper to send a single chunk with markdown fallback."""
    try:
        return await target_send_fn(text_chunk, **kwargs)
    except BadRequest as e:
        err_msg = str(e).lower()
        if "parse" in err_msg or "entities" in err_msg or "can't parse" in err_msg:
            log.warning(f"Telegram parse mode failed, retrying plain text: {e}")
            fallback_kwargs = dict(kwargs)
            fallback_kwargs.pop("parse_mode", None)
            try:
                return await target_send_fn(text_chunk, **fallback_kwargs)
            except Exception as inner_e:
                log.error(f"Failed to send even without parse mode: {inner_e}")
                return None
        else:
            log.error(f"Telegram BadRequest: {e}")
            return None
    except Exception as e:
        log.error(f"Send failed unexpectedly: {e}")
        return None


async def safe_reply(update: Update, text: str, **kwargs) -> List[Message]:
    """
    Send a reply message with automatic chunking (>4000 chars) and Markdown fallback.
    Gracefully handles both update.message and update.callback_query.

    Args:
        update: Telegram Update object
        text: Message text to send
        **kwargs: Additional args passed to reply_text (e.g., parse_mode, reply_markup)
    """
    if not update:
        return []

    # Get target message or chat
    message = update.effective_message
    if not message and update.callback_query:
        message = update.callback_query.message

    if not message:
        log.error("safe_reply: No effective message found in update to reply to.")
        return []

    chunks = _split_text(text)
    sent_messages = []

    for i, chunk in enumerate(chunks):
        # Only attach reply_markup to the final chunk
        chunk_kwargs = dict(kwargs)
        if i < len(chunks) - 1:
            chunk_kwargs.pop("reply_markup", None)

        sent = await _send_chunk(message.reply_text, chunk, **chunk_kwargs)
        if sent:
            sent_messages.append(sent)

    return sent_messages


async def safe_send(bot, chat_id: int, text: str, **kwargs) -> List[Message]:
    """
    Send a message to a specific chat_id with chunking and Markdown fallback.
    Used for reminders and background notifications.

    Args:
        bot: Telegram Bot instance
        chat_id: Target chat ID
        text: Message text
        **kwargs: Additional args
    """
    chunks = _split_text(text)
    sent_messages = []

    async def _send(chunk_text: str, **kw):
        return await bot.send_message(chat_id=chat_id, text=chunk_text, **kw)

    for i, chunk in enumerate(chunks):
        chunk_kwargs = dict(kwargs)
        if i < len(chunks) - 1:
            chunk_kwargs.pop("reply_markup", None)

        sent = await _send_chunk(_send, chunk, **chunk_kwargs)
        if sent:
            sent_messages.append(sent)

    return sent_messages
