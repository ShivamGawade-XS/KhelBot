"""
KhelBot /remind Handler — Match reminders synced with actual match fixtures.
Calculates real fixture times from CricAPI, prevents foreign key violations,
and sends notifications without blocking or hitting Telegram rate limits.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes, Application

from services.cricapi import get_all_matches
from database.reminders import async_create_reminder, async_get_pending_reminders, async_mark_reminder_sent
from database.users import async_update_user_query_count, async_create_or_update_user
from utils.validators import extract_team_from_args
from utils.rate_limiter import rate_limiter
from utils.reply import safe_reply, safe_send
from utils.logger import setup_logger

log = setup_logger("handler.remind")


def _find_next_match_time(all_matches: list[dict], team_name: str) -> tuple[Optional[str], Optional[datetime]]:
    """
    Search match fixtures for the next scheduled match for this team.
    Returns (match_id, match_datetime_utc) or (None, None).
    """
    team_lower = team_name.lower()

    for match in all_matches:
        teams = match.get("teams", [])
        name = match.get("name", "").lower()
        status = match.get("status", "").lower()

        # Skip already completed matches
        if "won" in status or "ended" in status or "result" in status:
            continue

        is_team_match = any(team_lower in t.lower() or t.lower() in team_lower for t in teams) or (team_lower in name)
        if not is_team_match:
            continue

        match_id = match.get("id", f"{team_name}_match")

        # Parse date / dateTimeGMT if provided by CricAPI
        date_str = match.get("dateTimeGMT") or match.get("date")
        if date_str:
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(date_str[:19], fmt)
                    return match_id, dt
                except ValueError:
                    continue

        return match_id, None

    return None, None


async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /remind command — set a match reminder."""
    user = update.effective_user
    args = context.args

    if not user:
        return

    allowed, block_msg = rate_limiter.check(user.id)
    if not allowed:
        await safe_reply(update, block_msg)
        return

    log.info(f"/remind from {user.id} | args: {args}")
    await async_update_user_query_count(user.id)
    # Ensure user is registered to prevent FK constraint failures
    await async_create_or_update_user(user.id, user.username or user.first_name)

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

    await safe_reply(update, f"🔍 {team_name} ka schedule check kar raha hoon... ⏳")

    all_matches = await get_all_matches()
    match_id, match_dt = _find_next_match_time(all_matches, team_name)

    if match_dt and match_dt > datetime.utcnow():
        # Reminder 30 minutes before match start
        remind_time = match_dt - timedelta(minutes=30)
        time_desc = f"{match_dt.strftime('%d %b at %H:%M UTC')} (30 min pehle notification aayega!)"
    else:
        # Fallback if specific time not announced yet
        remind_time = datetime.utcnow() + timedelta(hours=3)
        time_desc = "Jaise hi next match announce hoga (Notification on hai!)"

    success = await async_create_reminder(
        telegram_id=user.id,
        team_name=team_name,
        match_id=match_id or f"{team_name}_next",
        remind_at=remind_time
    )

    if success:
        await safe_reply(update, f"✅ **Done bhai!** {team_name} ka match reminder set ho gaya! 🔔\n\n"
            f"📅 **Timing:** {time_desc}\n\n"
            f"Match se pehle hum live notification bhej denge. Ab tension nahi! 💪",
            parse_mode="Markdown")
    else:
        await safe_reply(update, "😕 Reminder set karne mein problem aayi. Thodi der mein try karo!")


async def check_and_send_reminders(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Periodic job — check for pending reminders and send them safely.
    Processes with pacing to avoid Telegram rate limits.
    """
    try:
        pending = await async_get_pending_reminders()

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
                        f"🏏 **{team_name}** ka match jaldi shuru hone wala hai!\n\n"
                        f"TV on karo, snacks ready karo, aur mujhe `/live {team_name.split()[0].lower()}` "
                        f"bhejo live commentary ke liye! 🔥\n\n"
                        f"_KhelBot — Never miss a match!_"
                    ),
                    parse_mode="Markdown"
                )

                await async_mark_reminder_sent(reminder_id)
                log.info(f"Reminder sent to {telegram_id} for {team_name}")

                # Gentle pacing between messages to comply with Telegram limits
                await asyncio.sleep(0.05)

            except Exception as e:
                log.error(f"Failed to send reminder {reminder_id} to {telegram_id}: {e}")

    except Exception as e:
        log.error(f"Reminder check job failed: {e}")


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
