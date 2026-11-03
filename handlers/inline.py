"""
KhelBot Inline Handler — Share live scores, schedules & stats in any Telegram chat.
Users can type `@khelbot <query>` anywhere to get quick cricket cards.
"""

import uuid
from typing import List
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from services.cricapi import get_live_matches, get_all_matches, get_player_stats, get_points_table
from utils.logger import setup_logger

log = setup_logger("handler.inline")


async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline queries from Telegram (e.g. @khelbot live, @khelbot kohli)."""
    if not update.inline_query:
        return

    query = (update.inline_query.query or "").strip().lower()
    results: List[InlineQueryResultArticle] = []

    try:
        # 1. Live Matches or Default Card
        if not query or "live" in query or "score" in query:
            live_matches = await get_live_matches()
            if live_matches:
                for idx, m in enumerate(live_matches[:5]):
                    name = m.get("name", "Cricket Match")
                    status = m.get("status", "Match in progress")
                    score_info = ""
                    for s in m.get("score", []):
                        score_info += f"• *{s.get('inning', '')}*: {s.get('r', 0)}/{s.get('w', 0)} ({s.get('o', 0)} ov)\n"

                    msg_text = (
                        f"🏏 *LIVE CRICKET UPDATE* 🏏\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"⚔️ *{name}*\n"
                        f"📊 *Status:* {status}\n\n"
                        f"{score_info}\n"
                        f"⚡ _Via @khelbot — India ka Apna Cricket Bot_"
                    )
                    results.append(
                        InlineQueryResultArticle(
                            id=f"live_{idx}_{uuid.uuid4().hex[:6]}",
                            title=f"🏏 LIVE: {name}",
                            description=status[:80],
                            input_message_content=InputTextMessageContent(
                                message_text=msg_text,
                                parse_mode="Markdown"
                            ),
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("🏏 More Live Stats", url="https://t.me/khelbot")]
                            ])
                        )
                    )

        # 2. Today / Upcoming Schedule
        if "today" in query or "schedule" in query or not query:
            all_matches = await get_all_matches()
            upcoming = [m for m in all_matches if not m.get("matchEnded", False)][:5]
            if upcoming:
                schedule_text = "📅 *UPCOMING MATCHES* 📅\n━━━━━━━━━━━━━━━━━━\n"
                for m in upcoming:
                    m_name = m.get("name", "Match")
                    m_status = m.get("status", "Upcoming")
                    schedule_text += f"• *{m_name}*\n  _{m_status}_\n\n"
                schedule_text += "⚡ _Via @khelbot — India ka Apna Cricket Bot_"

                results.append(
                    InlineQueryResultArticle(
                        id=f"sched_{uuid.uuid4().hex[:6]}",
                        title="📅 Today & Upcoming Matches",
                        description=f"{len(upcoming)} matches scheduled",
                        input_message_content=InputTextMessageContent(
                            message_text=schedule_text,
                            parse_mode="Markdown"
                        )
                    )
                )

        # 3. Points Table
        if "point" in query or "table" in query or "ipl" in query:
            standings = await get_points_table()
            if standings:
                table_text = "🏅 *IPL POINTS TABLE* 🏅\n━━━━━━━━━━━━━━━━━━\n"
                for i, row in enumerate(standings[:8], 1):
                    t_name = row.get("teamName") or row.get("name", f"Team {i}")
                    pts = row.get("points", 0)
                    won = row.get("won", row.get("matchesWon", 0))
                    table_text += f"`{i:2d}.` *{t_name[:15]}* — {pts} pts ({won}W)\n"
                table_text += "\n⚡ _Via @khelbot — India ka Apna Cricket Bot_"

                results.append(
                    InlineQueryResultArticle(
                        id=f"pts_{uuid.uuid4().hex[:6]}",
                        title="🏅 IPL Points Table",
                        description="Top teams standings and points",
                        input_message_content=InputTextMessageContent(
                            message_text=table_text,
                            parse_mode="Markdown"
                        )
                    )
                )

        # 4. Player Stats Search (if query is at least 3 chars and not generic keyword)
        if len(query) >= 3 and query not in ["live", "today", "schedule", "points", "table", "ipl", "score"]:
            player = await get_player_stats(query)
            if player:
                p_name = player.get("name", query.title())
                country = player.get("country", "")
                role = player.get("role", "Cricketer")
                batting = player.get("battingStyle", "")
                bowling = player.get("bowlingStyle", "")

                player_text = (
                    f"🌟 *PLAYER STATS — {p_name.upper()}* 🌟\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"🇮🇳 *Country:* {country}\n"
                    f"🏏 *Role:* {role}\n"
                )
                if batting:
                    player_text += f"🏏 *Batting:* {batting}\n"
                if bowling:
                    player_text += f"🎯 *Bowling:* {bowling}\n"
                player_text += "\n⚡ _Via @khelbot — India ka Apna Cricket Bot_"

                results.append(
                    InlineQueryResultArticle(
                        id=f"player_{uuid.uuid4().hex[:6]}",
                        title=f"🌟 {p_name} ({role})",
                        description=f"Stats & info for {country} player",
                        input_message_content=InputTextMessageContent(
                            message_text=player_text,
                            parse_mode="Markdown"
                        )
                    )
                )

        # 5. Fallback Help Card if no results generated
        if not results:
            help_text = (
                "🏏 *KHELBOOT INLINE QUICK SHARE*\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "Try typing in any chat:\n"
                "• `@khelbot live` — Live match scores\n"
                "• `@khelbot today` — Upcoming matches\n"
                "• `@khelbot points` — IPL points table\n"
                "• `@khelbot <player>` — Player information\n\n"
                "🔥 _Open @khelbot for AI predictions, roasts, and voice notes!_"
            )
            results.append(
                InlineQueryResultArticle(
                    id=f"help_{uuid.uuid4().hex[:6]}",
                    title="🏏 Share KhelBot Cricket Intelligence",
                    description="Type 'live', 'today', 'points', or a player name",
                    input_message_content=InputTextMessageContent(
                        message_text=help_text,
                        parse_mode="Markdown"
                    )
                )
            )

        await update.inline_query.answer(results[:10], cache_time=15)

    except Exception as e:
        log.error(f"Error handling inline query '{query}': {e}")

