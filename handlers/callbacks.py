"""
KhelBot Callback Handler — Handles inline keyboard button presses.
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import setup_logger

log = setup_logger("handler.callbacks")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all inline keyboard button callbacks."""
    query = update.callback_query
    await query.answer()

    data = query.data
    log.info(f"Callback from {query.from_user.id}: {data}")

    # ── Command quick-access buttons (from /start) ──
    if data == "cmd_live":
        await query.message.reply_text(
            "🏏 Kaun si team ka score chahiye?\n\n"
            "Type karo: `/live rcb` ya `/live csk`",
            parse_mode="Markdown"
        )

    elif data == "cmd_predict":
        await query.message.reply_text(
            "🔮 Kaunsi teams ka prediction chahiye?\n\n"
            "Type karo: `/predict csk vs mi`",
            parse_mode="Markdown"
        )

    elif data == "cmd_news":
        # Trigger news directly
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

    # ── Quiz answer buttons ──
    elif data.startswith("quiz_"):
        parts = data.split("_")
        if len(parts) >= 3:
            correct = int(parts[1])
            picked = int(parts[2])
            
            explanation = context.user_data.get("quiz_explanation", "") if context.user_data else ""
            
            if picked == correct:
                await query.message.reply_text(
                    f"✅ **Sahi Jawab!** Bahut badhiya! 🎉🏏\n\n"
                    f"📝 {explanation}\n\n"
                    "Ek aur try karo? `/quiz`",
                    parse_mode="Markdown"
                )
            else:
                emojis = ["🅰️", "🅱️", "🅲", "🅳"]
                await query.message.reply_text(
                    f"❌ **Galat!** Sahi jawab tha option {emojis[correct]}\n\n"
                    f"📝 {explanation}\n\n"
                    "Phir se try karo? `/quiz`",
                    parse_mode="Markdown"
                )
