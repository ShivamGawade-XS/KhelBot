"""
KhelBot /funfact Handler — Random cricket fun facts via AI + web search.
Grounds fun facts with real web search results and applies rate limiting.
"""

import random
from telegram import Update
from telegram.ext import ContextTypes

from services.gemini import generate_funfact
from services.web_search import search_web
from database.users import async_update_user_query_count
from utils.rate_limiter import rate_limiter
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.funfact")

# Random topics to search for variety
FUNFACT_TOPICS = [
    "cricket world record broken 2026",
    "IPL records most runs wickets catches",
    "rare cricket facts nobody knows",
    "cricket funny moments history",
    "India cricket historical facts",
    "IPL auction records expensive players",
    "cricket coincidences unbelievable stats",
    "youngest oldest cricket records",
    "IPL 2026 milestone records broken",
    "cricket facts did you know",
]

LOADING_MESSAGES = [
    "🤯 Ek mast cricket fact dhundh raha hoon... 🔍",
    "🧠 Dimag mein cricket ka gyaan load ho raha hai... 🔍",
    "🏏 History ke pages palat raha hoon... 🔍",
    "📚 Cricket ka encyclopedia khol raha hoon... 🔍",
]


async def funfact_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /funfact command — random cricket fun fact with web search."""
    user = update.effective_user
    if not user:
        return

    allowed, block_msg = rate_limiter.check(user.id)
    if not allowed:
        await safe_reply(update, block_msg)
        return

    log.info(f"/funfact from {user.id}")
    await async_update_user_query_count(user.id)

    await safe_reply(update, random.choice(LOADING_MESSAGES))

    # Search for a random fun fact topic
    topic = random.choice(FUNFACT_TOPICS)
    live_context = await search_web(topic)

    # Pass live_context into generator
    fact = await generate_funfact(live_context=live_context)
    await safe_reply(update, fact, parse_mode="Markdown")
