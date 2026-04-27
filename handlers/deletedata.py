"""
KhelBot /deletedata Handler — GDPR-style data deletion.
Removes all user data from the database.
"""

from telegram import Update
from telegram.ext import ContextTypes

from database.users import delete_user_data
from utils.logger import setup_logger

log = setup_logger("handler.deletedata")


async def deletedata_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /deletedata command — delete all user data."""
    user = update.effective_user

    log.info(f"/deletedata from {user.id} (@{user.username})")

    try:
        success = delete_user_data(telegram_id=user.id)

        if success:
            await update.message.reply_text(
                "✅ **Data Delete Ho Gaya!**\n\n"
                "Tumhara saara data (profile + reminders) delete ho gaya hai. 🗑️\n\n"
                "Predictions mein tumhara koi personal data nahi tha, "
                "toh woh safe hai.\n\n"
                "Agar dobara use karna ho, toh `/start` bhej dena. "
                "Hum wapas dost ban jayenge! 🤝\n\n"
                "_KhelBot respects your privacy. Always._",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "😕 Data delete karne mein problem aayi.\n"
                "Shayad pehle se koi data nahi tha. "
                "Agar problem ho toh dobara try karo!"
            )

    except Exception as e:
        log.error(f"Delete data error for {user.id}: {e}")
        await update.message.reply_text(
            "❌ Kuch gadbad ho gayi data delete karte waqt.\n"
            "Thodi der mein phir se try karo!"
        )
