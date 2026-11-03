"""
KhelBot /live Handler — Live score with AI-powered Hinglish context.
Includes rate limiting, async non-blocking execution, and automatic message chunking.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.cricapi import get_match_by_team, get_live_matches
from services.gemini import generate_live_context
from database.users import async_update_user_query_count
from utils.validators import extract_team_from_args
from utils.formatters import format_score, format_match_list
from utils.rate_limiter import rate_limiter
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.live")


async def live_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /live command — fetch live score + AI context."""
    user = update.effective_user
    args = context.args

    if not user:
        return

    allowed, block_msg = rate_limiter.check(user.id)
    if not allowed:
        await safe_reply(update, block_msg)
        return

    log.info(f"/live from {user.id} | args: {args}")
    await async_update_user_query_count(user.id)

    if not args:
        await safe_reply(update, 
            "🏏 Kaun si team ka score chahiye?\n\n"
            "Usage: `/live <team>`\n"
            "Example: `/live rcb` ya `/live mumbai`\n\n"
            "Ruko, abhi sab live matches dikhata hoon...",
            parse_mode="Markdown"
        )

        matches = await get_live_matches()
        if matches:
            await safe_reply(update, format_match_list(matches), parse_mode="Markdown")
        else:
            await safe_reply(update, "😴 Abhi koi live match nahi chal raha. Thodi der mein check karo!")
        return

    team_name = extract_team_from_args(args)
    
    if not team_name:
        await safe_reply(update, 
            "🤔 Yeh team toh humne nahi suni bhai!\n\n"
            "Try karo: `csk`, `mi`, `rcb`, `kkr`, `dc`, `rr`, `srh`, `pbks`, `gt`, `lsg`\n\n"
            "Ya player names bhi chalte hain: `dhoni`, `kohli`, `rohit`",
            parse_mode="Markdown"
        )
        return

    await safe_reply(update, f"🔍 {team_name} ka score dhundh raha hoon... ⏳")

    match_data = await get_match_by_team(team_name)

    if not match_data:
        await safe_reply(update, 
            f"😕 Abhi {team_name} ka koi live match nahi chal raha.\n\n"
            "Shayad match khatam ho gaya ya abhi shuru nahi hua. "
            "Thodi der mein try karo! 🏏"
        )
        return

    scorecard = format_score(match_data)
    ai_context = await generate_live_context(match_data)

    response = f"{scorecard}\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n🤖 **KhelBot ka Take:**\n\n{ai_context}"
    await safe_reply(update, response, parse_mode="Markdown")
