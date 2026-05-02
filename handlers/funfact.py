"""
KhelBot /funfact Handler — Random cricket fun facts via AI + web search.
"""

import random
from telegram import Update
from telegram.ext import ContextTypes

from services.gemini import generate_funfact
from services.web_search import search_web
from database.users import update_user_query_count
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
    log.info(f"/funfact from {user.id}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    await safe_reply(update, random.choice(LOADING_MESSAGES))

    # Search for a random fun fact topic
    topic = random.choice(FUNFACT_TOPICS)
    live_context = await search_web(topic)

    fact = await generate_funfact()
    await safe_reply(update, fact, parse_mode="Markdown")

