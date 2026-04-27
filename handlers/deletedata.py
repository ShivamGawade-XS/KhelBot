"""
KhelBot /deletedata Handler — GDPR-style data deletion.
Removes all user data from the database.
"""

from telegram import Update
from telegram.ext import ContextTypes

from database.users import delete_user_data
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

log = setup_logger("handler.deletedata")


async def deletedata_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /deletedata command — delete all user data."""
    user = update.effective_user

    log.info(f"/deletedata from {user.id} (@{user.username})")

    try:
        success = delete_user_data(telegram_id=user.id)

        if success:
            await safe_reply(update, "✅ **Data Delete Ho Gaya!**\n\n"
                "Tumhara saara data (profile + reminders) delete ho gaya hai. 🗑️\n\n"
                "Predictions mein tumhara koi personal data nahi tha, "
                "toh woh safe hai.\n\n"
                "Agar dobara use karna ho, toh `/start` bhej dena. "
                "Hum wapas dost ban jayenge! 🤝\n\n"
                "_KhelBot respects your privacy. Always._",
                parse_mode="Markdown"
            )
        else:
            await safe_reply(update, "😕 Data delete karne mein problem aayi.\n"
                "Shayad pehle se koi data nahi tha. "
                "Agar problem ho toh dobara try karo!"
            )

    except Exception as e:
        log.error(f"Delete data error for {user.id}: {e}")
        await safe_reply(update, 
            "❌ Kuch gadbad ho gayi data delete karte waqt.\n"
            "Thodi der mein phir se try karo!"
        )
