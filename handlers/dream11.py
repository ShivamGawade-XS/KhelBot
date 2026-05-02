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
from utils.reply import safe_reply
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

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    if not args:
        await safe_reply(update, "🏆 Kaunsi match ka Dream11 team chahiye?\n\n"
            "Usage: `/dream11 <team1> vs <team2>`\n"
            "Example: `/dream11 kkr vs pbks`",
            parse_mode="Markdown")
        return

    team1, team2 = extract_two_teams(args)

    if not team1 or not team2:
        single_team = extract_team_from_args(args)
        if single_team:
            await safe_reply(update, 
                f"🤔 {single_team} ka Dream11 chahiye, but dusri team bhi batao!\n\n"
                f"Usage: `/dream11 {single_team} vs <team2>`",
                parse_mode="Markdown"
            )
        else:
            await safe_reply(update, 
                "🤔 Teams samajh nahi aaye bhai!\n\n"
                "Usage: `/dream11 csk vs mi`\n"
                "Teams: CSK, MI, RCB, KKR, DC, RR, SRH, PBKS, GT, LSG",
                parse_mode="Markdown"
            )
        return

    await safe_reply(update, f"🏆 {team1} vs {team2} ka Dream11 team bana raha hoon... 🔍🧠")

    # Search the web for squads, form, injuries, pitch report
    from services.web_search import search_web
    live_context = await search_web(f"{team1} vs {team2} dream11 team prediction playing 11 today")

    match_data = await get_match_by_team(team1)
    if not match_data:
        match_data = await get_match_by_team(team2)

    dream11_team = await generate_dream11(team1, team2, match_data, live_context=live_context)

    response = f"{dream11_team}{DISCLAIMER}"

    if len(response) > 4000:
        await safe_reply(update, dream11_team, parse_mode="Markdown")
        await safe_reply(update, DISCLAIMER, parse_mode="Markdown")
    else:
        await safe_reply(update, response, parse_mode="Markdown")
