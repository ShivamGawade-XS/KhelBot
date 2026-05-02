"""
KhelBot /today Handler — Shows today's IPL/cricket matches via live web search.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.web_search import search_web
from services.gemini import generate_freeform_answer
from database.users import update_user_query_count
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.today")


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /today command — what matches are on today."""
    user = update.effective_user
    log.info(f"/today from {user.id}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    await safe_reply(update, "📺 Aaj ke matches dhundh raha hoon... 🔍")

    # Search the web for today's cricket matches
    live_context = await search_web("IPL 2026 today match schedule cricket")

    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")

    prompt = f"""Show me all cricket matches happening TODAY ({today}).

QUESTION: What IPL/cricket matches are scheduled for today?

--- LIVE WEB SEARCH RESULTS ---
{live_context}
--- END ---

YOUR TASK:
1. List ALL matches happening TODAY with exact times (IST)
2. For each match show: Teams, Venue, Time
3. If a match is LIVE right now, highlight it with a LIVE emoji
4. Give a quick "match to watch" pick — konsa match sabse exciting hoga?
5. If no matches today, say when the next match is

FORMAT:
📺 Aaj Ke Matches ({today})

1. [Team1] vs [Team2]
   🏟️ Venue: [venue]
   ⏰ Time: [time] IST
   🔥 [quick one-liner about the match]

2. [next match...]

🎯 Match to Watch: [your pick and why]

Keep it crisp, Hinglish, exciting!"""

    answer = await generate_freeform_answer(prompt, live_context=live_context)
    await safe_reply(update, answer, parse_mode="Markdown")
