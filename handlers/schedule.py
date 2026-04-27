"""
KhelBot /schedule Handler — Upcoming match schedule.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.cricapi import get_all_matches
from database.users import update_user_query_count
from utils.validators import extract_team_from_args
from utils.formatters import format_schedule
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.schedule")


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /schedule command — show upcoming matches."""
    user = update.effective_user
    args = context.args

    log.info(f"/schedule from {user.id} | args: {args}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    team_name = None
    if args:
        team_name = extract_team_from_args(args)

    if team_name:
        await safe_reply(update, f"📅 {team_name} ka schedule dhundh raha hoon... ⏳")
    else:
        await safe_reply(update, "📅 Upcoming matches dhundh raha hoon... ⏳")

    all_matches = await get_all_matches()

    if not all_matches:
        await safe_reply(update, "😕 Abhi koi match data nahi mila. Thodi der mein try karo!")
        return

    # Filter for upcoming/not started matches, or if team specified, filter by team
    upcoming = []
    for match in all_matches:
        if team_name:
            # Check if team is in this match
            teams = match.get("teams", [])
            name = match.get("name", "").lower()
            team_lower = team_name.lower()
            
            found = False
            for t in teams:
                if team_lower in t.lower() or t.lower() in team_lower:
                    found = True
                    break
            if team_lower in name:
                found = True
            
            if found:
                upcoming.append(match)
        else:
            upcoming.append(match)

    if not upcoming:
        msg = f"😕 {team_name} ka koi upcoming match nahi mila!" if team_name else "😕 Koi upcoming match nahi mila!"
        await safe_reply(update, msg)
        return

    schedule_text = format_schedule(upcoming[:10], team_name)
    await safe_reply(update, schedule_text, parse_mode="Markdown")
