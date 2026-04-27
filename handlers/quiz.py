"""
KhelBot /quiz Handler — Cricket trivia quiz with inline keyboard buttons.
"""

import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.gemini import generate_quiz_question
from database.users import update_user_query_count
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.quiz")


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /quiz command — generate a cricket trivia question."""
    user = update.effective_user

    log.info(f"/quiz from {user.id}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    await safe_reply(update, "🧠 Cricket ka sawaal generate kar raha hoon... ⏳")

    quiz_data = await generate_quiz_question()

    if not quiz_data:
        await safe_reply(update, "😕 Quiz generate nahi ho paya. Thodi der mein try karo!")
        return

    question = quiz_data.get("question", "Unknown question")
    options = quiz_data.get("options", ["A", "B", "C", "D"])
    correct = quiz_data.get("correct", 0)
    explanation = quiz_data.get("explanation", "")

    # Create inline keyboard with options
    keyboard = []
    emojis = ["🅰️", "🅱️", "🅲", "🅳"]
    for i, option in enumerate(options[:4]):
        callback_data = json.dumps({"type": "quiz", "correct": correct, "picked": i, "exp": explanation[:100]})
        # Telegram limits callback_data to 64 bytes, so keep it short
        short_data = f"quiz_{correct}_{i}"
        keyboard.append([InlineKeyboardButton(f"{emojis[i]} {option}", callback_data=short_data)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await safe_reply(update, 
        f"🧠 **Cricket Quiz Time!**\n\n"
        f"❓ {question}\n\n"
        f"Neeche se apna jawab chuno! 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

    # Store explanation in context for callback
    if context.user_data is not None:
        context.user_data["quiz_explanation"] = explanation
