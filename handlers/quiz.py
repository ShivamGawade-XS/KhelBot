"""
KhelBot /quiz Handler — Cricket trivia quiz with secure inline keyboard buttons.
Keeps the correct answer server-side in TTL cache to prevent client-side inspection.
"""

import hashlib
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.gemini import generate_quiz_question
from database.users import async_update_user_query_count
from services.cache import cache
from utils.rate_limiter import rate_limiter
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.quiz")


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /quiz command — generate a cricket trivia question."""
    user = update.effective_user
    if not user:
        return

    allowed, block_msg = rate_limiter.check(user.id)
    if not allowed:
        await safe_reply(update, block_msg)
        return

    log.info(f"/quiz from {user.id}")
    await async_update_user_query_count(user.id)

    await safe_reply(update, "🧠 Cricket ka sawaal generate kar raha hoon... ⏳")

    quiz_data = await generate_quiz_question()

    if not quiz_data:
        await safe_reply(update, "😕 Quiz generate nahi ho paya. Thodi der mein try karo!")
        return

    question = quiz_data.get("question", "Unknown question")
    options = quiz_data.get("options", ["A", "B", "C", "D"])
    correct = quiz_data.get("correct", 0)
    explanation = quiz_data.get("explanation", "")

    # Generate a unique short quiz ID and store answer server-side
    qid = hashlib.md5(f"{question}:{correct}".encode()).hexdigest()[:8]
    cache.set(f"quiz:{qid}", {"correct": correct, "explanation": explanation}, ttl=600)

    # Create inline keyboard without leaking correct answer index
    keyboard = []
    emojis = ["🅰️", "🅱️", "🅲", "🅳"]
    for i, option in enumerate(options[:4]):
        short_data = f"q_{qid}_{i}"
        keyboard.append([InlineKeyboardButton(f"{emojis[i]} {option}", callback_data=short_data)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await safe_reply(update, 
        f"🧠 **Cricket Quiz Time!**\n\n"
        f"❓ {question}\n\n"
        f"Neeche se apna jawab chuno! 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
