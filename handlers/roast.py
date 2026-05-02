"""
KhelBot /roast Handler — Roast a cricket team or player based on recent live data.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.web_search import search_web
from services.gemini import generate_freeform_answer
from database.users import update_user_query_count
from utils.validators import sanitize_input
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.roast")


async def roast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /roast command — generate a funny roast."""
    user = update.effective_user
    args = context.args

    log.info(f"/roast from {user.id} | args: {args}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    if not args:
        await safe_reply(update, "🔥 Kisko roast karna hai bhai?\n\n"
            "Usage: `/roast <team ya player>`\n"
            "Example: `/roast rcb` ya `/roast hardik pandya`",
            parse_mode="Markdown")
        return

    target = sanitize_input(" ".join(args))

    await safe_reply(update, f"🔥 {target} ke baare mein masala dhundh raha hoon... thoda wait kar! 😈🔍")

    # Search the web for their recent fails or news to make the roast relevant
    live_context = await search_web(f"{target} cricket recent worst performance troll news")

    prompt = f"""Roast this cricket team or player: {target}

--- LIVE WEB SEARCH DATA (Use this to make the roast relevant!) ---
{live_context}
--- END ---

YOUR TASK:
1. Write a savage, funny, and entertaining "Roast" for {target}.
2. Use the live web search data to mention recent bad performances, trolls, or funny situations.
3. Keep it lighthearted and strictly in Hinglish (no extreme toxicity, just friendly cricket banter).
4. Mention their hardcore fans and how they suffer.
5. Add a funny "Disclaimer" at the end.

FORMAT:
🔥 KhelBot Roast: {target}

[Your 3-4 paragraph savage roast]

🤡 Final verdict: [funny one-liner punchline]

_Disclaimer: Yeh bas mazaak hai bhai, dil pe mat le!_ ✌️"""

    roast_text = await generate_freeform_answer(prompt, live_context=live_context)
    await safe_reply(update, roast_text, parse_mode="Markdown")
