"""
KhelBot /trending Handler — Trending cricket topics powered by AI + live web search.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.gemini import generate_trending
from services.newsapi import get_cricket_news
from services.web_search import search_cricket_news
from database.users import async_update_user_query_count
from utils.rate_limiter import rate_limiter
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.trending")


async def trending_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /trending command — what's hot in cricket right now."""
    user = update.effective_user
    if not user:
        return

    allowed, block_msg = rate_limiter.check(user.id)
    if not allowed:
        await safe_reply(update, block_msg)
        return

    log.info(f"/trending from {user.id}")
    await async_update_user_query_count(user.id)

    await safe_reply(update, "🔥 Cricket ka trending scene dhundh raha hoon... 🔍⏳")

    articles = await get_cricket_news(max_articles=5)
    headlines = [a.get("title", "") for a in articles]

    live_context = await search_cricket_news("IPL cricket trending news today")
    trending = await generate_trending(headlines, live_context=live_context)
    await safe_reply(update, trending, parse_mode="Markdown")
