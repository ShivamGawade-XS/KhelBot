"""
KhelBot /dream11 Handler — AI-powered Dream11 fantasy team suggestions.
Always includes mandatory disclaimer about financial risk.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.cricapi import get_match_by_team
from services.gemini import generate_dream11
from database.users import update_user_query_count
from utils.validators import extract_two_teams, extract_team_from_args
from utils.logger import setup_logger

log = setup_logger("handler.dream11")

DISCLAIMER = (
    "\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚠️ **Disclaimer:** Fantasy sports mein financial risk hota hai. "
    "Apni research bhi karo aur responsibly khelo!\n"
    "🎮 Dream11 pe team banao → [dream11.com](https://dream11.com)"
)


async def dream11_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /dream11 command — generate fantasy team suggestion."""
    user = update.effective_user
    args = context.args

    log.info(f"/dream11 from {user.id} | args: {args}")

    # Track query
    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    if not args:
        await update.message.reply_text(
            "🏆 Kaunsi match ka Dream11 team chahiye?\n\n"
            "Usage: `/dream11 <team1> vs <team2>`\n"
            "Example: `/dream11 kkr vs pbks`",
            parse_mode="Markdown"
        )
        return

    # Parse two teams
    team1, team2 = extract_two_teams(args)

    if not team1 or not team2:
        single_team = extract_team_from_args(args)
        if single_team:
            await update.message.reply_text(
                f"🤔 {single_team} ka Dream11 chahiye, but dusri team bhi batao!\n\n"
                f"Usage: `/dream11 {single_team} vs <team2>`",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "🤔 Teams samajh nahi aaye bhai!\n\n"
                "Usage: `/dream11 csk vs mi`\n"
                "Teams: CSK, MI, RCB, KKR, DC, RR, SRH, PBKS, GT, LSG",
                parse_mode="Markdown"
            )
        return

    # Send loading message
    await update.message.reply_text(
        f"🏆 {team1} vs {team2} ka Dream11 team bana raha hoon... 🧠⏳"
    )

    # Fetch match data for context
    match_data = await get_match_by_team(team1)
    if not match_data:
        match_data = await get_match_by_team(team2)

    # Generate Dream11 team
    dream11_team = await generate_dream11(team1, team2, match_data)

    # Send with disclaimer
    response = f"{dream11_team}{DISCLAIMER}"

    if len(response) > 4000:
        await update.message.reply_text(dream11_team, parse_mode="Markdown")
        await update.message.reply_text(DISCLAIMER, parse_mode="Markdown")
    else:
        await update.message.reply_text(response, parse_mode="Markdown")
