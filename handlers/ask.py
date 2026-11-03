"""
KhelBot /ask Handler — Free-form AI cricket chat with live web search.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.gemini import generate_freeform_answer
from services.web_search import search_web
from database.users import async_update_user_query_count
from utils.validators import sanitize_input
from utils.rate_limiter import rate_limiter
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.ask")


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /ask command — free-form cricket AI chat with live web search."""
    user = update.effective_user
    args = context.args

    if not user:
        return

    allowed, block_msg = rate_limiter.check(user.id)
    if not allowed:
        await safe_reply(update, block_msg)
        return

    log.info(f"/ask from {user.id} | args: {args}")
    await async_update_user_query_count(user.id)

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

    await safe_reply(update, "🔍 Web search + AI brain dono laga raha hoon... 🧠⚡")

    # Search the web for real-time context
    live_context = await search_web(question)
    log.info(f"Web search returned {len(live_context)} chars for: {question[:40]}")

    answer = await generate_freeform_answer(question, live_context=live_context)
    await safe_reply(update, answer, parse_mode="Markdown")
