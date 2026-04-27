"""
KhelBot — India ka Apna Cricket Intelligence Bot 🏏
Entry point: registers all handlers, sets up scheduler, starts polling.
"""

import logging
import traceback
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

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
from handlers.callbacks import button_callback
from utils.logger import setup_logger

log = setup_logger("main")


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
    log.info("🏏 KhelBot V2 starting up...")
    log.info("=" * 50)

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

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
    log.info("🚀 KhelBot V2 is live! Polling for updates...")
    log.info(f"📋 Commands: {', '.join(f'/{c[0]}' for c in commands)}")
    log.info("Press Ctrl+C to stop")
    
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
