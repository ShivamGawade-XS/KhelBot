"""
KhelBot /start Handler — Onboarding and welcome message with inline keyboards.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.users import create_or_update_user
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.start")

WELCOME_MESSAGE = """🏏 **Namaste! Main hoon KhelBot — India ka apna cricket buddy!**

Mere saath cricket aur bhi mast ho jayega! 🔥

🎯 **Commands:**

🏏 /live `<team>` — Live score + AI context
🔮 /predict `<team1> vs <team2>` — Win prediction
🏆 /dream11 `<team1> vs <team2>` — Fantasy team
📊 /stats `<player>` — Player stats + AI summary
⚔️ /h2h `<team1> vs <team2>` — Head-to-head analysis
🔄 /compare `<player1> vs <player2>` — Player comparison
📅 /schedule `[team]` — Upcoming matches
🏅 /points — IPL points table
💬 /ask `<question>` — Ask anything cricket
🧠 /quiz — Cricket trivia quiz
⏰ /remind `<team>` — Match reminder
📰 /news `[team]` — Cricket headlines
⭐ /favteam `<team>` — Set favorite team
❓ /help — Quick command list
🗑️ /deletedata — Delete your data

━━━━━━━━━━━━━━━━━━━━━━
📍 **Teams:** CSK, MI, RCB, KKR, DC, RR, SRH, PBKS, GT, LSG
   Short names bhi chalega — `csk`, `mumbai`, `kohli`, etc.

🔒 **Privacy:** Sirf Telegram ID aur username store hota hai.
   Kabhi bhi /deletedata se hata sakte ho.

Ab bolo, kaunsi team ka scene dekhna hai? 🏏🔥"""


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard with quick-access buttons."""
    keyboard = [
        [
            InlineKeyboardButton("🏏 Live Scores", callback_data="cmd_live"),
            InlineKeyboardButton("🔮 Predict", callback_data="cmd_predict"),
        ],
        [
            InlineKeyboardButton("📰 News", callback_data="cmd_news"),
            InlineKeyboardButton("🏅 Points Table", callback_data="cmd_points"),
        ],
        [
            InlineKeyboardButton("🧠 Quiz", callback_data="cmd_quiz"),
            InlineKeyboardButton("📅 Schedule", callback_data="cmd_schedule"),
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="cmd_help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command — onboarding + user registration."""
    user = update.effective_user
    
    if not user:
        return

    log.info(f"/start from {user.id} (@{user.username})")

    # Register/update user in database
    try:
        create_or_update_user(
            telegram_id=user.id,
            username=user.username or user.first_name or ""
        )
    except Exception as e:
        log.error(f"Failed to register user {user.id}: {e}")

    await safe_reply(update, WELCOME_MESSAGE,
        parse_mode="Markdown", reply_markup=get_start_keyboard())
