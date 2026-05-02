"""
KhelBot /compare Handler — Side-by-side player comparison.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.cricapi import get_player_stats
from services.gemini import generate_player_comparison
from database.users import update_user_query_count
from utils.validators import sanitize_input
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.compare")


async def compare_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /compare command — player vs player comparison."""
    user = update.effective_user
    args = context.args

    log.info(f"/compare from {user.id} | args: {args}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    if not args:
        await safe_reply(update, "🔄 Kaunse players ko compare karna hai?\n\n"
            "Usage: `/compare <player1> vs <player2>`\n"
            "Example: `/compare virat kohli vs rohit sharma`",
            parse_mode="Markdown")
        return

    # Parse two players separated by 'vs'
    raw_input = " ".join(args).strip().lower()
    
    player1_name = None
    player2_name = None
    
    for separator in [" vs ", " v ", " versus ", " and "]:
        if separator in raw_input:
            parts = raw_input.split(separator, 1)
            player1_name = sanitize_input(parts[0].strip())
            player2_name = sanitize_input(parts[1].strip())
            break

    if not player1_name or not player2_name:
        await safe_reply(update, 
            "🤔 Dono players ka naam 'vs' se separate karo!\n\n"
            "Usage: `/compare virat kohli vs rohit sharma`",
            parse_mode="Markdown")
        return

    if len(player1_name) < 2 or len(player2_name) < 2:
        await safe_reply(update, "🤔 Player names thoda aur specific batao!")
        return

    await safe_reply(update, 
        f"🔄 {player1_name.title()} vs {player2_name.title()} ka comparison prepare kar raha hoon... 🔍🧠"
    )

    # Search the web for latest player performances
    from services.web_search import search_web
    live_context = await search_web(f"{player1_name} vs {player2_name} IPL 2026 stats comparison")

    # Fetch stats for both players
    stats1 = await get_player_stats(player1_name)
    stats2 = await get_player_stats(player2_name)

    if not stats1 and not stats2:
        await safe_reply(update, "😕 Dono players nahi mile! Spelling check karo.")
        return
    if not stats1:
        await safe_reply(update, f"😕 '{player1_name}' nahi mila. Spelling check karo!")
        return
    if not stats2:
        await safe_reply(update, f"😕 '{player2_name}' nahi mila. Spelling check karo!")
        return

    comparison = await generate_player_comparison(player1_name, player2_name, stats1, stats2, live_context=live_context)

    if len(comparison) > 4000:
        mid = len(comparison) // 2
        await safe_reply(update, comparison[:mid], parse_mode="Markdown")
        await safe_reply(update, comparison[mid:], parse_mode="Markdown")
    else:
        await safe_reply(update, comparison, parse_mode="Markdown")
