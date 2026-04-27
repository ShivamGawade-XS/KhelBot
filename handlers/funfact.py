"""
KhelBot /funfact Handler — Random cricket fun facts via AI.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.gemini import generate_funfact
from database.users import update_user_query_count
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.funfact")


async def funfact_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /funfact command — random cricket fun fact."""
    user = update.effective_user
    log.info(f"/funfact from {user.id}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    await safe_reply(update, "🤯 Ek mast cricket fact dhundh raha hoon... ⏳")

    fact = await generate_funfact()
    await safe_reply(update, fact, parse_mode="Markdown")
