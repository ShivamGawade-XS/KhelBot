"""
KhelBot /points Handler — IPL points table.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.cricapi import get_points_table
from database.users import update_user_query_count
from utils.formatters import format_points_table
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.points")


async def points_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /points command — show IPL points table."""
    user = update.effective_user

    log.info(f"/points from {user.id}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    await safe_reply(update, "🏅 IPL points table la raha hoon... ⏳")

    standings = await get_points_table()

    if not standings:
        await safe_reply(update, 
            "😕 Points table abhi available nahi hai.\n"
            "Season shuru hone ka wait karo ya thodi der mein try karo!"
        )
        return

    table_text = format_points_table(standings)
    await safe_reply(update, table_text, parse_mode="Markdown")
