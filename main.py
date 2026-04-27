"""
KhelBot — India ka Apna Cricket Intelligence Bot 🏏
Entry point: registers all handlers, sets up scheduler, starts polling.
"""

import logging
import traceback
from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

from config.settings import TELEGRAM_BOT_TOKEN
from handlers.start import start_command
from handlers.live import live_command
from handlers.predict import predict_command
from handlers.dream11 import dream11_command
from handlers.stats import stats_command
from handlers.remind import remind_command, setup_reminder_job
from handlers.news import news_command
from handlers.deletedata import deletedata_command
from handlers.help import help_command
from handlers.schedule import schedule_command
from handlers.points import points_command
from handlers.h2h import h2h_command
from handlers.compare import compare_command
from handlers.ask import ask_command
from handlers.quiz import quiz_command
from handlers.favteam import favteam_command
from handlers.funfact import funfact_command
from handlers.recap import recap_command
from handlers.accuracy import accuracy_command
from handlers.poll import poll_command
from handlers.trending import trending_command
from handlers.callbacks import button_callback
from handlers.chat import chat_handler
from utils.logger import setup_logger

log = setup_logger("main")


# ── Bot Command Menu (shown in Telegram's UI) ────────────
BOT_COMMANDS = [
    BotCommand("start", "🏏 Start KhelBot"),
    BotCommand("help", "❓ All commands"),
    BotCommand("live", "🏏 Live score + AI context"),
    BotCommand("predict", "🔮 Win prediction"),
    BotCommand("dream11", "🏆 Fantasy team suggestion"),
    BotCommand("stats", "📊 Player statistics"),
    BotCommand("h2h", "⚔️ Head-to-head analysis"),
    BotCommand("compare", "🔄 Player comparison"),
    BotCommand("schedule", "📅 Upcoming matches"),
    BotCommand("points", "🏅 IPL points table"),
    BotCommand("ask", "💬 Ask anything cricket"),
    BotCommand("quiz", "🧠 Cricket trivia quiz"),
    BotCommand("recap", "📝 Match recap"),
    BotCommand("trending", "🔥 Trending cricket topics"),
    BotCommand("funfact", "🤯 Random cricket fact"),
    BotCommand("poll", "📊 Match prediction poll"),
    BotCommand("accuracy", "📈 Prediction stats"),
    BotCommand("remind", "⏰ Match reminder"),
    BotCommand("news", "📰 Cricket headlines"),
    BotCommand("favteam", "⭐ Set favorite team"),
    BotCommand("deletedata", "🗑️ Delete your data"),
]


async def post_init(application: Application) -> None:
    """Set bot commands in Telegram's UI after startup."""
    try:
        await application.bot.set_my_commands(BOT_COMMANDS)
        log.info("✅ Bot command menu set in Telegram UI")
    except Exception as e:
        log.warning(f"⚠️ Failed to set bot commands: {e}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler — catches all unhandled exceptions."""
    log.error(f"Exception while handling update: {context.error}")
    log.error(traceback.format_exc())

    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "😅 Oops! Kuch gadbad ho gayi mere end pe.\n"
                "Thodi der mein phir se try karo bhai! 🏏"
            )
        except Exception:
            pass


def main() -> None:
    """Initialize and start the KhelBot."""
    
    log.info("=" * 50)
    log.info("🏏 KhelBot V3 starting up...")
    log.info("=" * 50)

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    # ── Register Command Handlers ─────────────────────────
    commands = [
        ("start", start_command),
        ("help", help_command),
        ("live", live_command),
        ("predict", predict_command),
        ("dream11", dream11_command),
        ("stats", stats_command),
        ("h2h", h2h_command),
        ("compare", compare_command),
        ("schedule", schedule_command),
        ("points", points_command),
        ("ask", ask_command),
        ("quiz", quiz_command),
        ("recap", recap_command),
        ("trending", trending_command),
        ("funfact", funfact_command),
        ("poll", poll_command),
        ("accuracy", accuracy_command),
        ("remind", remind_command),
        ("news", news_command),
        ("favteam", favteam_command),
        ("deletedata", deletedata_command),
    ]

    for cmd_name, cmd_handler in commands:
        app.add_handler(CommandHandler(cmd_name, cmd_handler))

    log.info(f"✅ {len(commands)} command handlers registered")

    # ── Register Callback Handler (inline buttons) ────────
    app.add_handler(CallbackQueryHandler(button_callback))
    log.info("✅ Callback query handler registered")

    # ── Register Natural Language Handler ─────────────────
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, chat_handler
    ))
    log.info("✅ Natural language chat handler registered")

    # ── Register Global Error Handler ─────────────────────
    app.add_error_handler(error_handler)
    log.info("✅ Global error handler registered")

    # ── Set Up Reminder Scheduler ─────────────────────────
    try:
        setup_reminder_job(app)
        log.info("✅ Reminder scheduler set up")
    except Exception as e:
        log.warning(f"⚠️ Reminder scheduler failed (non-critical): {e}")

    # ── Start Polling ─────────────────────────────────────
    log.info("🚀 KhelBot V3 is live! Polling for updates...")
    log.info(f"📋 {len(commands)} commands + chat + callbacks")
    log.info("Press Ctrl+C to stop")
    
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
