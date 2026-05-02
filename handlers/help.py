"""
KhelBot /help Handler — Shows available commands.
"""

from telegram import Update
from telegram.ext import ContextTypes

from database.users import update_user_query_count
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.help")

HELP_TEXT = """🏏 **KhelBot V3 Commands** 🏏

*Real-Time & Live Search Powered!* ⚡🔍

🎯 **Daily Action:**
/today — 📺 Aaj ke matches
/live `<team>` — Live score + AI context
/remind `<team>` — Match reminder set karo

🔥 **AI Analysis (Web Search Enabled):**
/predict `<team1> vs <team2>` — Win prediction
/dream11 `<team1> vs <team2>` — Fantasy team
/h2h `<team1> vs <team2>` — Head-to-head records
/compare `<player1> vs <player2>` — Player comparison
/stats `<player>` — Player stats & latest news

🏆 **IPL Specials:**
/points — 🏅 Points table
/orangecap — 🧡 Orange Cap race
/purplecap — 💜 Purple Cap race
/schedule `[team]` — Upcoming matches

💬 **Just For Fun:**
/ask `<question>` — Ask me anything!
/trending — 🔥 What's hot in cricket
/news `[team]` — Cricket headlines
/quiz — 🧠 Cricket trivia
/funfact — 🤯 Random cricket fact
/recap `<team>` — 📝 Match summary
/poll `<team1> vs <team2>` — Prediction poll

⚙️ **Settings:**
/favteam `<team>` — Set favorite team
/deletedata — 🗑️ Delete your data

_Bina command ke bhi kuch type kar sakte ho, main samajh jaunga!_ 😉"""


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command — show all available commands."""
    user = update.effective_user
    log.info(f"/help from {user.id}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    await safe_reply(update, HELP_TEXT, parse_mode="Markdown")
