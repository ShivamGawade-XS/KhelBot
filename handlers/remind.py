"""
KhelBot /remind Handler — Match reminders via APScheduler.
"""

from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes, Application

from database.reminders import create_reminder, get_pending_reminders, mark_reminder_sent
from database.users import update_user_query_count
from utils.validators import extract_team_from_args
from utils.reply import safe_reply, safe_send
from utils.logger import setup_logger

log = setup_logger("handler.remind")


async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /remind command — set a match reminder."""
    user = update.effective_user
    args = context.args

    log.info(f"/remind from {user.id} | args: {args}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    if not args:
        await safe_reply(update, "⏰ Kaunsi team ka reminder set karna hai?\n\n"
            "Usage: `/remind <team>`\n"
            "Example: `/remind mi`\n\n"
            "Hum match se 30 min pehle yaad dila denge! 🔔",
            parse_mode="Markdown")
        return

    team_name = extract_team_from_args(args)

    if not team_name:
        await safe_reply(update, 
            "🤔 Yeh team toh samajh nahi aayi!\n\n"
            "Teams: CSK, MI, RCB, KKR, DC, RR, SRH, PBKS, GT, LSG",
            parse_mode="Markdown"
        )
        return

    remind_time = datetime.utcnow() + timedelta(hours=2)

    try:
        success = create_reminder(
            telegram_id=user.id,
            team_name=team_name,
            remind_at=remind_time
        )

        if success:
            await safe_reply(update, f"✅ Done bhai! {team_name} ka match reminder set ho gaya! 🔔\n\n"
                f"Match se pehle hum yaad dila denge. Ab tension nahi! 💪\n\n"
                f"_Reminder check hota hai har 30 min mein_",
                parse_mode="Markdown")
        else:
            await safe_reply(update, "😕 Reminder set karne mein problem aayi. Thodi der mein try karo!")

    except Exception as e:
        log.error(f"Remind error for {user.id}: {e}")
        await safe_reply(update, 
            "😕 Kuch gadbad ho gayi reminder set karte waqt. Phir se try karo!"
        )


async def check_and_send_reminders(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Periodic job — check for pending reminders and send them.
    Called by APScheduler every 30 minutes.
    """
    try:
        pending = get_pending_reminders()

        if not pending:
            return

        log.info(f"Processing {len(pending)} pending reminders")

        for reminder in pending:
            telegram_id = reminder.get("telegram_id")
            team_name = reminder.get("team_name", "your team")
            reminder_id = reminder.get("id")

            try:
                await safe_send(
                    context.bot,
                    chat_id=telegram_id,
                    text=(
                        f"🔔 **Match Reminder!**\n\n"
                        f"🏏 {team_name} ka match jaldi shuru hone wala hai!\n\n"
                        f"TV on karo, snacks ready karo, aur mujhe `/live {team_name.split()[0].lower()}` "
                        f"bhejo live updates ke liye! 🔥\n\n"
                        f"_KhelBot — Never miss a match!_"
                    ),
                    parse_mode="Markdown"
                )

                mark_reminder_sent(reminder_id)
                log.info(f"Reminder sent to {telegram_id} for {team_name}")

            except Exception as e:
                log.error(f"Failed to send reminder {reminder_id} to {telegram_id}: {e}")

    except Exception as e:
        log.error(f"Reminder check failed: {e}")


def setup_reminder_job(app: Application) -> None:
    """Register the periodic reminder check job."""
    from config.settings import REMINDER_CHECK_INTERVAL

    app.job_queue.run_repeating(
        check_and_send_reminders,
        interval=REMINDER_CHECK_INTERVAL * 60,
        first=30,
        name="reminder_check"
    )
    log.info(f"Reminder job scheduled: every {REMINDER_CHECK_INTERVAL} minutes")
