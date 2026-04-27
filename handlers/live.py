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
        await update.message.reply_text(
            "🏏 Kaun si team ka score chahiye?\n\n"
            "Usage: `/live <team>`\n"
            "Example: `/live rcb` ya `/live mumbai`\n\n"
            "Ruko, abhi sab live matches dikhata hoon...",
            parse_mode="Markdown"
        )

        matches = await get_live_matches()
        if matches:
            await update.message.reply_text(
                format_match_list(matches),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "😴 Abhi koi live match nahi chal raha. Thodi der mein check karo!"
            )
        return

    # Resolve team name
    team_name = extract_team_from_args(args)
    
    if not team_name:
        await update.message.reply_text(
            "🤔 Yeh team toh humne nahi suni bhai!\n\n"
            "Try karo: `csk`, `mi`, `rcb`, `kkr`, `dc`, `rr`, `srh`, `pbks`, `gt`, `lsg`\n\n"
            "Ya player names bhi chalte hain: `dhoni`, `kohli`, `rohit`",
            parse_mode="Markdown"
        )
        return

    # Send "typing" indicator
    await update.message.reply_text(f"🔍 {team_name} ka score dhundh raha hoon... ⏳")

    # Fetch match data
    match_data = await get_match_by_team(team_name)

    if not match_data:
        await update.message.reply_text(
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
        await update.message.reply_text(scorecard, parse_mode="Markdown")
        await update.message.reply_text(
            f"🤖 **KhelBot ka Take:**\n\n{ai_context}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(response, parse_mode="Markdown")
