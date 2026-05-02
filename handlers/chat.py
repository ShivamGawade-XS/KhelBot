"""
KhelBot Natural Language Handler — Respond to plain text cricket queries.
If a user sends a message without a command, KhelBot tries to understand it.
Now with live web search for real-time answers!
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.gemini import generate_freeform_answer
from services.web_search import search_web
from database.users import update_user_query_count
from utils.validators import sanitize_input, extract_team_from_args
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.chat")

# Keywords that indicate a cricket-related message
CRICKET_KEYWORDS = [
    "cricket", "ipl", "match", "score", "team", "player", "batting", "bowling",
    "wicket", "run", "six", "four", "over", "century", "boundary", "fielding",
    "csk", "mi", "rcb", "kkr", "dc", "rr", "srh", "pbks", "gt", "lsg",
    "kohli", "dhoni", "rohit", "bumrah", "jadeja", "pandya", "pant", "gill",
    "virat", "sachin", "tendulkar", "gavaskar", "kapil", "dravid",
    "t20", "odi", "test", "world cup", "ashes", "bcci", "trophy",
    "dream11", "fantasy", "predict", "kaun jeetega", "live", "stats",
    "schedule", "points table", "orange cap", "purple cap", "auction",
    "playoff", "final", "semi final", "qualifier",
]


async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle plain text messages — natural language cricket chat with web search."""
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    text = update.message.text.strip()

    # Ignore very short messages
    if len(text) < 3:
        return

    # Check if it's cricket-related
    text_lower = text.lower()
    is_cricket = any(kw in text_lower for kw in CRICKET_KEYWORDS)

    if not is_cricket:
        # Not cricket related — gentle redirect
        await safe_reply(update,
            "🏏 Bhai main cricket expert hoon!\n\n"
            "Cricket ke baare mein kuch bhi poocho ya commands use karo:\n"
            "Try: `/help` for all commands\n"
            "Ya seedha poocho: \"Who has most IPL centuries?\"",
            parse_mode="Markdown"
        )
        return

    log.info(f"Chat from {user.id}: {text[:50]}...")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    # Check if user is asking about a specific team's score
    words = text_lower.split()
    team = extract_team_from_args(words)
    
    if team and any(w in text_lower for w in ["score", "live", "kya hua", "kya ho raha", "kitne run"]):
        await safe_reply(update, f"Score chahiye? Try karo: `/live {words[0]}`", parse_mode="Markdown")
        return

    # Search the web for real-time context, then get AI answer
    question = sanitize_input(text)
    live_context = await search_web(question)
    answer = await generate_freeform_answer(question, live_context=live_context)
    await safe_reply(update, answer, parse_mode="Markdown")

