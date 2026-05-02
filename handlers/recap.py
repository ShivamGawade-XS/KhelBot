"""
KhelBot /recap Handler — AI-generated match recap/summary.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.cricapi import get_match_by_team, get_all_matches
from services.gemini import generate_match_recap
from database.users import update_user_query_count
from utils.validators import extract_team_from_args
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.recap")


async def recap_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /recap command — AI match recap."""
    user = update.effective_user
    args = context.args

    log.info(f"/recap from {user.id} | args: {args}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    if not args:
        await safe_reply(update, "📝 Kaunsi team ka match recap chahiye?\n\n"
            "Usage: `/recap <team>`\n"
            "Example: `/recap rcb`",
            parse_mode="Markdown")
        return

    team_name = extract_team_from_args(args)
    if not team_name:
        await safe_reply(update,
            "🤔 Yeh team nahi pehchani!\n\n"
            "Teams: CSK, MI, RCB, KKR, DC, RR, SRH, PBKS, GT, LSG",
            parse_mode="Markdown")
        return

    await safe_reply(update, f"📝 {team_name} ka match recap generate kar raha hoon... 🔍🧠")

    # Search the web for actual match results
    from services.web_search import search_web
    live_context = await search_web(f"{team_name} IPL 2026 last match result scorecard")

    # Find the most recent match for this team
    match_data = await get_match_by_team(team_name)

    if not match_data:
        # Try from all matches
        all_matches = await get_all_matches()
        team_lower = team_name.lower()
        for m in reversed(all_matches):
            for t in m.get("teams", []):
                if team_lower in t.lower() or t.lower() in team_lower:
                    match_data = m
                    break
            if match_data:
                break

    if not match_data and not live_context:
        await safe_reply(update, f"😕 {team_name} ka koi recent match nahi mila.")
        return

    recap = await generate_match_recap(match_data, live_context=live_context)

    if len(recap) > 4000:
        mid = len(recap) // 2
        await safe_reply(update, recap[:mid], parse_mode="Markdown")
        await safe_reply(update, recap[mid:], parse_mode="Markdown")
    else:
        await safe_reply(update, recap, parse_mode="Markdown")
