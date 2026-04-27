"""
KhelBot /trending Handler — Trending cricket topics powered by AI.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.gemini import generate_trending
from services.newsapi import get_cricket_news
from database.users import update_user_query_count
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.trending")


async def trending_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /trending command — what's hot in cricket right now."""
    user = update.effective_user
    log.info(f"/trending from {user.id}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    await safe_reply(update, "🔥 Cricket ka trending scene dhundh raha hoon... ⏳")

    # Fetch latest news headlines to give AI context
    articles = await get_cricket_news(max_articles=5)
    headlines = []
    for a in articles:
        headlines.append(a.get("title", ""))

    trending = await generate_trending(headlines)

    if len(trending) > 4000:
        mid = len(trending) // 2
        await safe_reply(update, trending[:mid], parse_mode="Markdown")
        await safe_reply(update, trending[mid:], parse_mode="Markdown")
    else:
        await safe_reply(update, trending, parse_mode="Markdown")
