"""
KhelBot /stats Handler — Player statistics with AI summary.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.cricapi import get_player_stats
from services.gemini import generate_player_summary
from database.users import update_user_query_count
from utils.formatters import format_player_stats
from utils.validators import sanitize_input
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.stats")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /stats command — fetch player stats + AI summary."""
    user = update.effective_user
    args = context.args

    log.info(f"/stats from {user.id} | args: {args}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    if not args:
        await safe_reply(update, "📊 Kaunse player ka stats chahiye?\n\n"
            "Usage: `/stats <player name>`\n"
            "Example: `/stats virat kohli`",
            parse_mode="Markdown")
        return

    player_name = sanitize_input(" ".join(args))

    if not player_name or len(player_name) < 2:
        await safe_reply(update, "🤔 Player name thoda aur specific batao!\n"
            "Example: `/stats ms dhoni`",
            parse_mode="Markdown")
        return

    await safe_reply(update, f"📊 {player_name} ka stats dhundh raha hoon... 🔍⏳")

    # Search the web for latest player form and news
    from services.web_search import search_player_info
    live_context = await search_player_info(player_name)

    player_data = await get_player_stats(player_name)

    if not player_data:
        await safe_reply(update, 
            f"😕 '{player_name}' nahi mila database mein.\n\n"
            "Spelling check karo ya full name try karo!\n"
            "Example: `/stats virat kohli`",
            parse_mode="Markdown")
        return

    stats_text = format_player_stats(player_data)
    ai_summary = await generate_player_summary(player_name, player_data, live_context=live_context)

    response = f"{stats_text}\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n🤖 **KhelBot ka Take:**\n\n{ai_summary}"

    if len(response) > 4000:
        await safe_reply(update, stats_text, parse_mode="Markdown")
        await safe_reply(update, f"🤖 **KhelBot ka Take:**\n\n{ai_summary}", parse_mode="Markdown")
    else:
        await safe_reply(update, response, parse_mode="Markdown")
