"""
KhelBot /start Handler — Onboarding and welcome message.
"""

from telegram import Update
from telegram.ext import ContextTypes

from database.users import create_or_update_user
from utils.logger import setup_logger

from telegram.error import BadRequest
async def safe_reply(update, text, **kwargs):
    try:
        await update.message.reply_text(text, **kwargs)
    except BadRequest as e:
        if "parse entities" in str(e).lower():
            # Fallback without markdown
            kwargs.pop("parse_mode", None)
            await update.message.reply_text(text, **kwargs)
        else:
            raise e

log = setup_logger("handler.start")

WELCOME_MESSAGE = """🏏 **Namaste! Main hoon KhelBot — India ka apna cricket buddy!**

Mere saath cricket aur bhi mast ho jayega! 🔥

🎯 **Yeh commands use karo:**

🏏 /live `<team>` — Live score + AI match context
   _Example: /live rcb_

🔮 /predict `<team1>` vs `<team2>` — Win prediction
   _Example: /predict csk vs mi_

🏆 /dream11 `<team1>` vs `<team2>` — Fantasy team
   _Example: /dream11 kkr vs pbks_

📊 /stats `<player>` — Player stats + summary
   _Example: /stats virat kohli_

⏰ /remind `<team>` — Match reminder set karo
   _Example: /remind mi_

📰 /news `[team]` — Cricket headlines
   _Example: /news or /news rcb_

🗑️ /deletedata — Apna data delete karo (Privacy)

━━━━━━━━━━━━━━━━━━━━━━
📍 **Team names:** CSK, MI, RCB, KKR, DC, RR, SRH, PBKS, GT, LSG
   Ya short names bhi chalega — `csk`, `mumbai`, `kohli`, etc.

🔒 **Privacy:** Hum sirf tumhara Telegram ID aur username store karte hain.
   Kabhi bhi /deletedata se apna data hata sakte ho.

Ab bolo, kaunsi team ka scene dekhna hai? 🏏🔥"""


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
        # Don't block the welcome message if DB fails

    await safe_reply(update, WELCOME_MESSAGE,
        parse_mode="Markdown")
