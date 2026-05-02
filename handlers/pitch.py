"""
KhelBot /pitch Handler — Detailed pitch report and weather conditions via live web search.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.web_search import search_web
from services.gemini import generate_freeform_answer
from database.users import update_user_query_count
from utils.validators import sanitize_input
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.pitch")


async def pitch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /pitch command — detailed pitch report."""
    user = update.effective_user
    args = context.args

    log.info(f"/pitch from {user.id} | args: {args}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    if not args:
        await safe_reply(update, "🏟️ Kaunse match ka pitch report chahiye?\n\n"
            "Usage: `/pitch <team1 vs team2>` ya `/pitch <stadium>`\n"
            "Example: `/pitch csk vs mi`",
            parse_mode="Markdown")
        return

    query = sanitize_input(" ".join(args))

    await safe_reply(update, f"🏟️ {query} ka pitch and weather report nikaal raha hoon... 🔍🌱")

    live_context = await search_web(f"{query} today match pitch report weather conditions toss prediction")

    prompt = f"""Give a detailed Pitch and Weather Report for: {query}

--- LIVE WEB SEARCH DATA ---
{live_context}
--- END ---

YOUR TASK:
1. Analyze the pitch report based on the real search data (Batting friendly? Spin friendly?).
2. Give the weather conditions (Rain chances, dew factor?).
3. What should the toss winner do? (Bat first or bowl first based on stats).
4. Dream11 Tip: Which type of players will succeed here? (Pacers, spinners, top-order?).
5. Keep it strictly in Hinglish and sound like a cricket expert.

FORMAT:
🏟️ Pitch & Weather Report: {query}

🌱 **Pitch Conditions:** [detailed breakdown]
🌤️ **Weather & Dew:** [weather report]
🪙 **Toss Factor:** [what captain should do]
💡 **Fantasy Tip:** [who to pick]

Use REAL data from the search!"""

    pitch_text = await generate_freeform_answer(prompt, live_context=live_context)
    await safe_reply(update, pitch_text, parse_mode="Markdown")
