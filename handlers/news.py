"""
KhelBot /news Handler — Cricket news headlines.
Only shows headline + source + URL — never full article body.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.newsapi import get_cricket_news
from database.users import update_user_query_count
from utils.validators import extract_team_from_args
from utils.formatters import format_news_list
from utils.logger import setup_logger

from telegram.error import BadRequest
async def safe_reply(update, text, **kwargs):
    try:
        await safe_reply(update, text, **kwargs)
    except BadRequest as e:
        if "parse entities" in str(e).lower():
            # Fallback without markdown
            kwargs.pop("parse_mode", None)
            await safe_reply(update, text, **kwargs)
        else:
            raise e

log = setup_logger("handler.news")


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /news command — fetch cricket headlines."""
    user = update.effective_user
    args = context.args

    log.info(f"/news from {user.id} | args: {args}")

    # Track query
    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    # Optional team filter
    team_name = None
    if args:
        team_name = extract_team_from_args(args)

    # Send loading message
    if team_name:
        await safe_reply(update, f"📰 {team_name} ki latest news dhundh raha hoon... ⏳"
        )
    else:
        await safe_reply(update, 
            "📰 Latest cricket news dhundh raha hoon... ⏳"
        )

    # Fetch news
    articles = await get_cricket_news(team_name=team_name)

    if not articles:
        await safe_reply(update, 
            "😕 Abhi koi cricket news nahi mili.\n"
            "Thodi der mein try karo ya doosri team try karo!"
        )
        return

    # Format and send
    news_text = format_news_list(articles)
    await safe_reply(update, news_text, parse_mode="Markdown")
