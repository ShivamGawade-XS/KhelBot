"""
KhelBot /help Handler — Shows available commands.
"""

from telegram import Update
from telegram.ext import ContextTypes

from database.users import async_update_user_query_count
from utils.rate_limiter import rate_limiter
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.help")

HELP_TEXT = """🏏 **KhelBot V4 Commands** 🏏

*Real-Time Web Search & Llama 3.3 Powered!* ⚡🔍

🎯 **Daily Action:**
/today — 📺 Aaj ke matches aur timings
/live `<team>` — Live score + AI commentary
/playing11 `<team>` — 📋 Playing 11 & Lineups
/pitch `<match>` — 🏟️ Pitch & Weather report
/remind `<team>` — Match reminder set karo

🔥 **AI Analysis (Live Web Search):**
/predict `<team1> vs <team2>` — Win prediction
/dream11 `<team1> vs <team2>` — Fantasy team
/h2h `<team1> vs <team2>` — Head-to-head records
/compare `<player1> vs <player2>` — Player comparison
/stats `<player>` — Career statistics

🏆 **IPL Specials:**
/points — 🏅 IPL points table
/orangecap — 🧡 Orange Cap race
/purplecap — 💜 Purple Cap race
/schedule `[team]` — Upcoming matches

💬 **Just For Fun:**
/roast `<team/player>` — 🔥 Roast em! (Savage mode)
/ask `<question>` — Ask me anything!
/trending — 🔥 What's hot in cricket
/news `[team]` — Cricket headlines
/quiz — 🧠 Cricket trivia (Interactive buttons)
/funfact — 🤯 Random cricket fact
/recap `<team>` — 📝 Match summary
/poll `<team1> vs <team2>` — Prediction poll
/accuracy — 📈 Verified prediction stats

⚙️ **Settings:**
/favteam `<team>` — Set favorite team
/deletedata — 🗑️ Delete your data (Privacy/GDPR)

_Bina command ke bhi kuch type kar sakte ho, main samajh jaunga!_ 😉"""


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command — show all available commands."""
    user = update.effective_user
    if not user:
        return

    allowed, block_msg = rate_limiter.check(user.id)
    if not allowed:
        await safe_reply(update, block_msg)
        return

    log.info(f"/help from {user.id}")
    await async_update_user_query_count(user.id)
    await safe_reply(update, HELP_TEXT, parse_mode="Markdown")
