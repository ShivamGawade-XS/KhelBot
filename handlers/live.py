"""
KhelBot /live Handler — Live score with AI-powered Hinglish context.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.cricapi import get_match_by_team, get_live_matches
from services.gemini import generate_live_context
from database.users import update_user_query_count
from utils.validators import extract_team_from_args
from utils.formatters import format_score, format_match_list
from utils.logger import setup_logger

from telegram.error import BadRequest
async def safe_reply(update, text, **kwargs):
    try:
        await update.message.reply_text(text, **kwargs)
    except BadRequest as e:
        if "parse entities" in str(e).lower():
            # Fallback without markdown
            kwargs.pop("parse_mode", None)
            await update.message.reply_text(text, **kwargs)
        else:
            raise e

log = setup_logger("handler.live")


async def live_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /live command — fetch live score + AI context."""
    user = update.effective_user
    args = context.args

    log.info(f"/live from {user.id} | args: {args}")

    # Track query
    try:
        update_user_query_count(user.id)
    except Exception:
        pass  # Non-critical

    # If no team specified, show all live matches
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
            await safe_reply(update, format_match_list(matches),
                parse_mode="Markdown")
        else:
            await safe_reply(update, "😴 Abhi koi live match nahi chal raha. Thodi der mein check karo!"
            )
        return

    # Resolve team name
    team_name = extract_team_from_args(args)
    
    if not team_name:
        await safe_reply(update, 
            "🤔 Yeh team toh humne nahi suni bhai!\n\n"
            "Try karo: `csk`, `mi`, `rcb`, `kkr`, `dc`, `rr`, `srh`, `pbks`, `gt`, `lsg`\n\n"
            "Ya player names bhi chalte hain: `dhoni`, `kohli`, `rohit`",
            parse_mode="Markdown"
        )
        return

    # Send "typing" indicator
    await safe_reply(update, f"🔍 {team_name} ka score dhundh raha hoon... ⏳")

    # Fetch match data
    match_data = await get_match_by_team(team_name)

    if not match_data:
        await safe_reply(update, 
            f"😕 Abhi {team_name} ka koi live match nahi chal raha.\n\n"
            "Shayad match khatam ho gaya ya abhi shuru nahi hua. "
            "Thodi der mein try karo! 🏏"
        )
        return

    # Format scorecard
    scorecard = format_score(match_data)

    # Generate AI context
    ai_context = await generate_live_context(match_data)

    # Combine and send
    response = f"{scorecard}\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n🤖 **KhelBot ka Take:**\n\n{ai_context}"

    # Telegram has 4096 char limit
    if len(response) > 4000:
        # Split into two messages
        await safe_reply(update, scorecard, parse_mode="Markdown")
        await safe_reply(update, f"🤖 **KhelBot ka Take:**\n\n{ai_context}",
            parse_mode="Markdown")
    else:
        await safe_reply(update, response, parse_mode="Markdown")
