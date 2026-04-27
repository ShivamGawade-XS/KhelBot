"""
KhelBot /help Handler — Quick command reference.
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.help")

HELP_TEXT = """❓ **KhelBot — Quick Help**

🏏 `/live <team>` — Live score + AI analysis
🔮 `/predict <t1> vs <t2>` — Win prediction
🏆 `/dream11 <t1> vs <t2>` — Fantasy team
📊 `/stats <player>` — Player stats
⚔️ `/h2h <t1> vs <t2>` — Head-to-head
🔄 `/compare <p1> vs <p2>` — Player comparison
📅 `/schedule [team]` — Upcoming matches
🏅 `/points` — IPL points table
💬 `/ask <question>` — Ask anything cricket
🧠 `/quiz` — Cricket trivia
⏰ `/remind <team>` — Match reminder
📰 `/news [team]` — Headlines
⭐ `/favteam <team>` — Favorite team set karo
🗑️ `/deletedata` — Privacy: data delete

━━━━━━━━━━━━━━━━━━━━━━
📍 Teams: CSK MI RCB KKR DC RR SRH PBKS GT LSG
🏏 Built with ❤️ by KhelBot"""


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    log.info(f"/help from {update.effective_user.id}")
    await safe_reply(update, HELP_TEXT, parse_mode="Markdown")
