"""
KhelBot /orangecap & /purplecap Handlers — IPL cap race via live web search.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.web_search import search_web
from services.gemini import generate_freeform_answer
from database.users import update_user_query_count
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.caps")


async def orangecap_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /orangecap command — IPL Orange Cap race."""
    user = update.effective_user
    log.info(f"/orangecap from {user.id}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    await safe_reply(update, "🧡 Orange Cap race dhundh raha hoon... 🔍")

    live_context = await search_web("IPL 2026 orange cap holder most runs list")

    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")

    prompt = f"""Show the IPL 2026 Orange Cap race (most runs scorers).

TODAY'S DATE: {today}

--- LIVE WEB SEARCH RESULTS ---
{live_context}
--- END ---

YOUR TASK:
1. Show the TOP 5-7 run scorers in IPL 2026 with their stats
2. For each player: Name, Team, Matches, Runs, Average, Strike Rate
3. Highlight the current ORANGE CAP HOLDER
4. Mention who is in hot form and who might overtake
5. Give your take — "Mera prediction hai final tak _____ Orange Cap leke jayega"

FORMAT:
🧡 IPL 2026 Orange Cap Race

👑 1. [Name] ([Team]) — [Runs] runs in [M] matches
   Avg: [avg] | SR: [sr]
   
2. [Name] ([Team]) — [Runs] runs
   [stats]

[... top 5-7]

🔥 Form Check: [who's hot right now]
🏏 KhelBot Prediction: [who will win the Orange Cap]

Use REAL numbers from search results! Hinglish mein bolo!"""

    answer = await generate_freeform_answer(prompt, live_context=live_context)
    await safe_reply(update, answer, parse_mode="Markdown")


async def purplecap_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /purplecap command — IPL Purple Cap race."""
    user = update.effective_user
    log.info(f"/purplecap from {user.id}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    await safe_reply(update, "💜 Purple Cap race dhundh raha hoon... 🔍")

    live_context = await search_web("IPL 2026 purple cap holder most wickets list")

    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")

    prompt = f"""Show the IPL 2026 Purple Cap race (most wickets takers).

TODAY'S DATE: {today}

--- LIVE WEB SEARCH RESULTS ---
{live_context}
--- END ---

YOUR TASK:
1. Show the TOP 5-7 wicket takers in IPL 2026 with their stats
2. For each player: Name, Team, Matches, Wickets, Average, Economy
3. Highlight the current PURPLE CAP HOLDER
4. Mention who is bowling fire and who might overtake
5. Give your take — "Mera prediction hai final tak _____ Purple Cap leke jayega"

FORMAT:
💜 IPL 2026 Purple Cap Race

👑 1. [Name] ([Team]) — [Wickets] wickets in [M] matches
   Avg: [avg] | Econ: [econ]
   
2. [Name] ([Team]) — [Wickets] wickets
   [stats]

[... top 5-7]

🔥 Form Check: [who's bowling fire]
🏏 KhelBot Prediction: [who will win the Purple Cap]

Use REAL numbers from search results! Hinglish mein bolo!"""

    answer = await generate_freeform_answer(prompt, live_context=live_context)
    await safe_reply(update, answer, parse_mode="Markdown")
