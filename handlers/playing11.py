"""
KhelBot /playing11 Handler — Probable or confirmed playing 11 via live web search.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.web_search import search_web
from services.gemini import generate_freeform_answer
from database.users import update_user_query_count
from utils.validators import sanitize_input
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.playing11")


async def playing11_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /playing11 command — get team line-ups."""
    user = update.effective_user
    args = context.args

    log.info(f"/playing11 from {user.id} | args: {args}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    if not args:
        await safe_reply(update, "🏏 Kaunsi team ka Playing 11 dekhna hai?\n\n"
            "Usage: `/playing11 <team1 vs team2>` ya `/playing11 <team>`\n"
            "Example: `/playing11 rcb vs csk`",
            parse_mode="Markdown")
        return

    query = sanitize_input(" ".join(args))

    await safe_reply(update, f"🏏 {query} ka Playing 11 dhundh raha hoon... 🔍📋")

    live_context = await search_web(f"{query} playing 11 probable confirmed today match")

    prompt = f"""Show the Playing 11 for: {query}

--- LIVE WEB SEARCH DATA ---
{live_context}
--- END ---

YOUR TASK:
1. List the probable or confirmed Playing 11 for the requested team(s).
2. Clearly state if it's "Probable" or "Confirmed" based on the search data.
3. List the 11 players in batting order if possible.
4. Mention the possible Impact Players (for IPL).
5. Add a quick one-line comment on the team strength.

FORMAT:
🏏 Playing 11: {query}
*(Status: Probable/Confirmed)*

1. [Player 1]
2. [Player 2]
[... up to 11]

💥 **Impact Players:** [List 3-4 options]

💬 **KhelBot ka Take:** [Quick thought on the lineup]

Use REAL data from the search! Hinglish mein bolo."""

    lineup_text = await generate_freeform_answer(prompt, live_context=live_context)
    await safe_reply(update, lineup_text, parse_mode="Markdown")
