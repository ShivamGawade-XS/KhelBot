"""
KhelBot — India ka Apna Cricket Intelligence Bot 🏏
Entry point: registers all handlers, sets up scheduler, starts polling.
"""

import logging
from telegram.ext import Application, CommandHandler

from config.settings import TELEGRAM_BOT_TOKEN
from handlers.start import start_command
from handlers.live import live_command
from handlers.predict import predict_command
from handlers.dream11 import dream11_command
from handlers.stats import stats_command
from handlers.remind import remind_command, setup_reminder_job
from handlers.news import news_command
from handlers.deletedata import deletedata_command
from utils.logger import setup_logger

log = setup_logger("main")


def main() -> None:
    """Initialize and start the KhelBot."""
    
    log.info("=" * 50)
    log.info("🏏 KhelBot starting up...")
    log.info("=" * 50)

    # Build the application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # ── Register Command Handlers ─────────────────────────
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("live", live_command))
    app.add_handler(CommandHandler("predict", predict_command))
    app.add_handler(CommandHandler("dream11", dream11_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("remind", remind_command))
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(CommandHandler("deletedata", deletedata_command))

    log.info("✅ 8 command handlers registered")

    # ── Set Up Reminder Scheduler ─────────────────────────
    try:
        setup_reminder_job(app)
        log.info("✅ Reminder scheduler set up")
    except Exception as e:
        log.warning(f"⚠️ Reminder scheduler failed (non-critical): {e}")

    # ── Start Polling ─────────────────────────────────────
    log.info("🚀 KhelBot is live! Polling for updates...")
    log.info("Press Ctrl+C to stop")
    
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
