"""
KhelBot /start Handler — Onboarding and welcome message with inline keyboards.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.users import create_or_update_user
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.start")

WELCOME_MESSAGE = """🏏 **Namaste! Main hoon KhelBot V3 — India ka apna LIVE cricket buddy!**

Mere paas ab **Real-Time Web Search** ki shakti hai! 🔥
Main direct internet se live data, stats, aur news nikaal ke answers deta hoon!

🎯 **Naye Commands:**
/today — 📺 Aaj ke matches aur timings
/orangecap — 🧡 Orange Cap race stats
/purplecap — 💜 Purple Cap race stats

🏆 **Match Action:**
/live `<team>` — Live score + AI context
/predict `<team1> vs <team2>` — Win prediction (Live form data)
/dream11 `<team1> vs <team2>` — Fantasy team (Real squads)
/remind `<team>` — Match reminder

📊 **AI Analysis:**
/stats `<player>` — Player stats + AI summary
/h2h `<team1> vs <team2>` — Head-to-head analysis
/compare `<p1> vs <p2>` — Player comparison
/schedule `[team]` — Upcoming matches

💬 **Chat & Fun:**
/ask `<question>` — Ask anything (Web Search Enabled!)
/news `[team]` — Cricket headlines
/trending — Trending cricket topics
/quiz — Cricket trivia quiz

❓ /help — Quick command list

━━━━━━━━━━━━━━━━━━━━━━
📍 **Teams:** CSK, MI, RCB, KKR, DC, RR, SRH, PBKS, GT, LSG
   Short names bhi chalega — `csk`, `mumbai`, `kohli`, etc.

_Ab bolo, aaj kya chal raha hai cricket ki duniya mein?_ 🏏🔥"""


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
