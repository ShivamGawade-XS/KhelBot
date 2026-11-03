"""
KhelBot /start Handler — Onboarding and welcome message with inline keyboards.
Non-blocking user registration and safe message delivery.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.users import async_create_or_update_user
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.start")

WELCOME_MESSAGE = """🏏 **Namaste! Main hoon KhelBot V4 — India ka apna LIVE cricket buddy!**

Mere paas ab **Real-Time Web Search** aur Llama 3.3 Intelligence ki shakti hai! 🔥
Direct internet se live scores, stats, squads aur analysis nikaal ke answers deta hoon!

🎯 **Live & Matches:**
/today — 📺 Aaj ke matches aur timings
/live `<team>` — Live score + AI commentary
/playing11 `<team>` — 📋 Playing 11 & Lineups
/pitch `<match>` — 🏟️ Pitch & Weather report
/remind `<team>` — Match reminder

🔮 **AI Analysis & Fantasy:**
/predict `<team1> vs <team2>` — Win prediction
/dream11 `<team1> vs <team2>` — Fantasy team
/h2h `<team1> vs <team2>` — Head-to-head records
/compare `<p1> vs <p2>` — Player comparison
/stats `<player>` — Career statistics

🏆 **IPL Specials:**
/points — 🏅 Points table
/orangecap — 🧡 Orange Cap race
/purplecap — 💜 Purple Cap race
/schedule `[team]` — Upcoming fixtures

💬 **Banter & Chat:**
/ask `<question>` — Cricket ka koi bhi sawaal
/roast `<team>` — Savage Hinglish roast 🔥
/quiz — Trivia quiz (Inline buttons)
/trending — Trending cricket topics
/news — Top cricket headlines

❓ /help — Sabhi commands ki list

━━━━━━━━━━━━━━━━━━━━━━
📍 **Teams:** CSK, MI, RCB, KKR, DC, RR, SRH, PBKS, GT, LSG
   Short names bhi chalenge — `csk`, `mumbai`, `kohli`, etc.

_Bolo bhai, aaj cricket mein kya chal raha hai?_ 🏏🔥"""


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

    # Non-blocking user registration
    await async_create_or_update_user(
        telegram_id=user.id,
        username=user.username or user.first_name or ""
    )

    await safe_reply(update, WELCOME_MESSAGE,
        parse_mode="Markdown", reply_markup=get_start_keyboard())
