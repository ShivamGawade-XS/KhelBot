"""
KhelBot /poll Handler — Create a match prediction poll in group chats.
"""

from telegram import Update
from telegram.ext import ContextTypes

from database.users import update_user_query_count
from utils.validators import extract_two_teams, extract_team_from_args
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.poll")


async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /poll command — create a match prediction poll."""
    user = update.effective_user
    args = context.args

    log.info(f"/poll from {user.id} | args: {args}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    if not args:
        await safe_reply(update, "📊 Kaunsi match ka poll banana hai?\n\n"
            "Usage: `/poll <team1> vs <team2>`\n"
            "Example: `/poll csk vs mi`",
            parse_mode="Markdown")
        return

    team1, team2 = extract_two_teams(args)

    if not team1 or not team2:
        single_team = extract_team_from_args(args)
        if single_team:
            await safe_reply(update,
                f"🤔 {single_team} ka poll chahiye, but dusri team bhi batao!\n\n"
                f"Usage: `/poll {single_team} vs <team2>`",
                parse_mode="Markdown")
        else:
            await safe_reply(update,
                "🤔 Teams samajh nahi aaye!\n\n"
                "Usage: `/poll csk vs mi`",
                parse_mode="Markdown")
        return

    # Create a native Telegram poll
    try:
        await update.message.reply_poll(
            question=f"🏏 {team1} vs {team2} — Kaun jeetega?",
            options=[
                f"🏆 {team1}",
                f"🏆 {team2}",
                "🤝 Tie / No Result",
            ],
            is_anonymous=False,
            allows_multiple_answers=False,
        )
        log.info(f"Poll created: {team1} vs {team2}")
    except Exception as e:
        log.error(f"Poll creation error: {e}")
        await safe_reply(update, "😕 Poll bana nahi paya. Thodi der mein try karo!")
