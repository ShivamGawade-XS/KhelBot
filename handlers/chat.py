"""
KhelBot Natural Language Handler — Respond to plain text cricket queries.
If a user sends a message without a command, KhelBot understands cricket banter,
live match queries, and questions using DuckDuckGo search + Groq Llama 3.3.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.gemini import generate_freeform_answer
from services.web_search import search_web
from database.users import async_update_user_query_count
from utils.validators import sanitize_input, extract_team_from_args
from utils.rate_limiter import rate_limiter
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.chat")

# Common cricket conversational keywords
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
    if not user:
        return

    text = update.message.text.strip()

    # Ignore single character spam
    if len(text) < 2:
        return

    # Rate limiting
    allowed, block_msg = rate_limiter.check(user.id)
    if not allowed:
        await safe_reply(update, block_msg)
        return

    log.info(f"Chat from {user.id}: {text[:50]}...")
    await async_update_user_query_count(user.id)

    text_lower = text.lower()

    # Fast path for basic greetings (no expensive web search or LLM needed)
    greetings = ["hi", "hello", "hey", "namaste", "kaise ho", "kya haal", "sup", "good morning", "good evening", "khelbot"]
    if text_lower in greetings or any(text_lower.startswith(g + " ") for g in greetings):
        await safe_reply(update, 
            "Namaste bhai! 🙏 Main **KhelBot** hoon — India ka live cricket intelligence bot!\n\n"
            "Aaj cricket mein kya jaanna hai? Score, predictions, Dream11 ya news?\n"
            "Try: `/help` ya seedha poocho: *'Aaj kiska match hai?'*",
            parse_mode="Markdown"
        )
        return

    # Check if user is asking for live score directly
    words = text_lower.split()
    team = extract_team_from_args(words)
    if team and any(w in text_lower for w in ["score", "live", "kya hua", "kya ho raha", "kitne run"]):
        await safe_reply(update, f"🏏 {team} ka live score chahiye? Seedha try karo: `/live {words[0]}`", parse_mode="Markdown")
        return

    # Send typing / thinking notification
    await safe_reply(update, "🤔 Thoda soch raha hoon... 🔍", parse_mode="Markdown")

    # Search web for real-time context
    question = sanitize_input(text)
    live_context = await search_web(question)

    # Generate grounded response
    answer = await generate_freeform_answer(question, live_context=live_context)
    await safe_reply(update, answer, parse_mode="Markdown")
