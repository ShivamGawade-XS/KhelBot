"""
KhelBot /favteam Handler — Set favorite IPL team with automatic user registration.
"""

from telegram import Update
from telegram.ext import ContextTypes

from database.users import async_set_favorite_team, async_get_user, async_create_or_update_user
from utils.validators import extract_team_from_args
from utils.rate_limiter import rate_limiter
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.favteam")


async def favteam_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /favteam command — set favorite team."""
    user = update.effective_user
    args = context.args

    if not user:
        return

    allowed, block_msg = rate_limiter.check(user.id)
    if not allowed:
        await safe_reply(update, block_msg)
        return

    log.info(f"/favteam from {user.id} | args: {args}")

    if not args:
        user_data = await async_get_user(user.id)
        current = user_data.get("favorite_team") if user_data else None
        if current:
            await safe_reply(update, 
                f"⭐ Tumhari favorite team: **{current}**\n\n"
                "Change karna hai? `/favteam <team>`\n"
                "Example: `/favteam rcb`",
                parse_mode="Markdown")
        else:
            await safe_reply(update,
                "⭐ Apni favorite IPL team set karo!\n\n"
                "Usage: `/favteam <team>`\n"
                "Example: `/favteam csk`\n\n"
                "Teams: CSK, MI, RCB, KKR, DC, RR, SRH, PBKS, GT, LSG",
                parse_mode="Markdown")
        return

    team_name = extract_team_from_args(args)

    if not team_name:
        await safe_reply(update, 
            "🤔 Yeh team nahi pehchani!\n\n"
            "Teams: CSK, MI, RCB, KKR, DC, RR, SRH, PBKS, GT, LSG",
            parse_mode="Markdown")
        return

    # Ensure user exists and update preference
    await async_create_or_update_user(user.id, user.username or user.first_name)
    success = await async_set_favorite_team(user.id, team_name)

    if success:
        team_emojis = {
            "Chennai Super Kings": "💛",
            "Mumbai Indians": "💙",
            "Royal Challengers Bengaluru": "❤️",
            "Kolkata Knight Riders": "💜",
            "Delhi Capitals": "🔵",
            "Rajasthan Royals": "💗",
            "Sunrisers Hyderabad": "🧡",
            "Punjab Kings": "🔴",
            "Gujarat Titans": "🩵",
            "Lucknow Super Giants": "💚",
        }
        emoji = team_emojis.get(team_name, "🏏")
        await safe_reply(update, 
            f"{emoji} **Done!** Tumhari favorite team ab **{team_name}** hai!\n\n"
            "Ab jab bhi tumhari team khele, hum extra passionate commentary denge! 🔥",
            parse_mode="Markdown")
    else:
        await safe_reply(update, "😕 Team set nahi ho payi. Thodi der mein try karo!")
