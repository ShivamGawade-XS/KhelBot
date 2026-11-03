"""
KhelBot Callback Handler — Handles inline keyboard button presses.
Supports server-side quiz verification and safe response sending.
"""

from telegram import Update
from telegram.ext import ContextTypes
from services.cache import cache
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.callbacks")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all inline keyboard button callbacks."""
    query = update.callback_query
    if not query:
        return

    try:
        await query.answer()
    except Exception:
        pass

    data = query.data
    log.info(f"Callback from {query.from_user.id}: {data}")

    # ── Command quick-access buttons (from /start) ──
    if data == "cmd_live":
        await safe_reply(update, 
            "🏏 Kaun si team ka score chahiye?\n\n"
            "Type karo: `/live rcb` ya `/live csk`",
            parse_mode="Markdown"
        )

    elif data == "cmd_predict":
        await safe_reply(update, 
            "🔮 Kaunsi teams ka prediction chahiye?\n\n"
            "Type karo: `/predict csk vs mi`",
            parse_mode="Markdown"
        )

    elif data == "cmd_news":
        from handlers.news import news_command
        context.args = []
        await news_command(update, context)

    elif data == "cmd_points":
        from handlers.points import points_command
        await points_command(update, context)

    elif data == "cmd_quiz":
        from handlers.quiz import quiz_command
        await quiz_command(update, context)

    elif data == "cmd_schedule":
        from handlers.schedule import schedule_command
        context.args = []
        await schedule_command(update, context)

    elif data == "cmd_help":
        from handlers.help import help_command
        await help_command(update, context)

    # ── Secure Server-Side Quiz answer buttons ──
    elif data.startswith("q_"):
        parts = data.split("_")
        if len(parts) >= 3:
            qid = parts[1]
            picked = int(parts[2])

            quiz_info = cache.get(f"quiz:{qid}")
            emojis = ["🅰️", "🅱️", "🅲", "🅳"]

            if quiz_info:
                correct = quiz_info.get("correct", 0)
                explanation = quiz_info.get("explanation", "")
                if picked == correct:
                    await safe_reply(update, 
                        f"✅ **Sahi Jawab!** Bahut badhiya! 🎉🏏\n\n"
                        f"📝 {explanation}\n\n"
                        "Ek aur try karo? `/quiz`",
                        parse_mode="Markdown"
                    )
                else:
                    await safe_reply(update, 
                        f"❌ **Galat!** Sahi jawab tha option {emojis[correct]}\n\n"
                        f"📝 {explanation}\n\n"
                        "Phir se try karo? `/quiz`",
                        parse_mode="Markdown"
                    )
            else:
                await safe_reply(update, "⌛ Yeh quiz expire ho gaya bhai! Naya sawaal ke liye `/quiz` type karo.")

    # ── Legacy Quiz fallback ──
    elif data.startswith("quiz_"):
        parts = data.split("_")
        if len(parts) >= 3:
            correct = int(parts[1])
            picked = int(parts[2])
            explanation = context.user_data.get("quiz_explanation", "") if context.user_data else ""
            emojis = ["🅰️", "🅱️", "🅲", "🅳"]
            
            if picked == correct:
                await safe_reply(update, 
                    f"✅ **Sahi Jawab!** Bahut badhiya! 🎉🏏\n\n"
                    f"📝 {explanation}\n\n"
                    "Ek aur try karo? `/quiz`",
                    parse_mode="Markdown"
                )
            else:
                await safe_reply(update, 
                    f"❌ **Galat!** Sahi jawab tha option {emojis[correct]}\n\n"
                    f"📝 {explanation}\n\n"
                    "Phir se try karo? `/quiz`",
                    parse_mode="Markdown"
                )
