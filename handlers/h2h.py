"""
KhelBot /h2h Handler — Head-to-head analysis between two teams.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.cricapi import get_match_by_team
from services.gemini import generate_h2h_analysis
from database.users import update_user_query_count
from utils.validators import extract_two_teams, extract_team_from_args
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.h2h")


async def h2h_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /h2h command — head-to-head team analysis."""
    user = update.effective_user
    args = context.args

    log.info(f"/h2h from {user.id} | args: {args}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    if not args:
        await safe_reply(update, "⚔️ Kaunsi teams ka head-to-head chahiye?\n\n"
            "Usage: `/h2h <team1> vs <team2>`\n"
            "Example: `/h2h csk vs mi`",
            parse_mode="Markdown")
        return

    team1, team2 = extract_two_teams(args)

    if not team1 or not team2:
        single_team = extract_team_from_args(args)
        if single_team:
            await safe_reply(update, 
                f"🤔 {single_team} ka H2H chahiye, but dusri team bhi batao!\n\n"
                f"Usage: `/h2h {single_team} vs <team2>`",
                parse_mode="Markdown"
            )
        else:
            await safe_reply(update, 
                "🤔 Teams samajh nahi aaye bhai!\n\n"
                "Usage: `/h2h csk vs mi`\n"
                "Teams: CSK, MI, RCB, KKR, DC, RR, SRH, PBKS, GT, LSG",
                parse_mode="Markdown"
            )
        return

    await safe_reply(update, f"⚔️ {team1} vs {team2} ka head-to-head analysis kar raha hoon... 🧠⏳")

    # Fetch match data for additional context
    match_data = await get_match_by_team(team1)
    if not match_data:
        match_data = await get_match_by_team(team2)

    analysis = await generate_h2h_analysis(team1, team2, match_data)

    response = f"{analysis}"

    if len(response) > 4000:
        mid = len(response) // 2
        await safe_reply(update, response[:mid], parse_mode="Markdown")
        await safe_reply(update, response[mid:], parse_mode="Markdown")
    else:
        await safe_reply(update, response, parse_mode="Markdown")
