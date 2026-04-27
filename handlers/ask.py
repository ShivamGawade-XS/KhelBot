"""
KhelBot /ask Handler — Free-form AI cricket chat.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.gemini import generate_freeform_answer
from database.users import update_user_query_count
from utils.validators import sanitize_input
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.ask")


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /ask command — free-form cricket AI chat."""
    user = update.effective_user
    args = context.args

    log.info(f"/ask from {user.id} | args: {args}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    if not args:
        await safe_reply(update, "💬 Cricket ke baare mein kuch bhi poocho!\n\n"
            "Usage: `/ask <your question>`\n"
            "Example: `/ask who has most IPL centuries?`\n"
            "Example: `/ask RCB ne last time trophy kab jeeti?`",
            parse_mode="Markdown")
        return

    question = sanitize_input(" ".join(args))

    if not question or len(question) < 3:
        await safe_reply(update, "🤔 Thoda aur detail mein poocho bhai!")
        return

    await safe_reply(update, "💬 Soch raha hoon... 🧠⏳")

    answer = await generate_freeform_answer(question)

    if len(answer) > 4000:
        mid = len(answer) // 2
        await safe_reply(update, answer[:mid], parse_mode="Markdown")
        await safe_reply(update, answer[mid:], parse_mode="Markdown")
    else:
        await safe_reply(update, answer, parse_mode="Markdown")
