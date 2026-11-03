"""
KhelBot /deletedata Handler — GDPR & DPDP Act compliance data deletion.
Asynchronously purges all user profile information, reminders, and preferences.
"""

from telegram import Update
from telegram.ext import ContextTypes

from database.users import async_delete_user_data
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.deletedata")


async def deletedata_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /deletedata command — delete all user data."""
    user = update.effective_user
    if not user:
        return

    log.info(f"/deletedata from {user.id}")

    try:
        success = await async_delete_user_data(telegram_id=user.id)

        if success:
            await safe_reply(update, "✅ **Data Delete Ho Gaya!**\n\n"
                "Tumhara saara personal data (profile, preferences aur reminders) delete kar diya gaya hai. 🗑️\n\n"
                "KhelBot tumhari privacy aur rights ka poora samman karta hai.\n"
                "Dobara connect karne ke liye `/start` bhej dena bhai! 🤝\n\n"
                "_KhelBot — 100% Privacy Respect._",
                parse_mode="Markdown"
            )
        else:
            await safe_reply(update, "ℹ️ Tumhara koi active profile ya data database mein store nahi tha.")

    except Exception as e:
        log.error(f"Delete data error for {user.id}: {e}")
        await safe_reply(update, 
            "❌ Kuch gadbad ho gayi data delete karte waqt.\n"
            "Thodi der mein phir se try karo!"
        )
