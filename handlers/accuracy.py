"""
KhelBot /accuracy Handler — Show prediction accuracy stats.
Auto-resolves pending predictions against completed CricAPI fixtures.
"""

from telegram import Update
from telegram.ext import ContextTypes

from database.predictions import async_get_accuracy, resolve_predictions_from_matches
from database.users import async_update_user_query_count
from services.cricapi import get_all_matches
from utils.rate_limiter import rate_limiter
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.accuracy")


async def accuracy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /accuracy command — show prediction stats."""
    user = update.effective_user
    if not user:
        return

    allowed, block_msg = rate_limiter.check(user.id)
    if not allowed:
        await safe_reply(update, block_msg)
        return

    log.info(f"/accuracy from {user.id}")
    await async_update_user_query_count(user.id)

    await safe_reply(update, "📈 Prediction accuracy calculate kar raha hoon... ⏳")

    try:
        # Sync latest match results to resolve any pending predictions
        matches = await get_all_matches()
        if matches:
            resolve_predictions_from_matches(matches)

        stats = await async_get_accuracy()

        if not stats or stats.get("total", 0) == 0:
            await safe_reply(update,
                "📈 **KhelBot Prediction Stats**\n\n"
                "Abhi tak koi verified prediction match complete nahi hua hai.\n"
                "Jaise hi scheduled matches khatam honge, unka accuracy result yahan update hoga!\n\n"
                "Prediction karo: `/predict csk vs mi`",
                parse_mode="Markdown")
            return

        total = stats.get("total", 0)
        correct = stats.get("correct", 0)
        accuracy = stats.get("accuracy", 0.0)

        # Rating based on accuracy
        if accuracy >= 70:
            rating = "🔥 ELITE Predictor!"
        elif accuracy >= 50:
            rating = "💪 Solid Predictor"
        elif accuracy >= 30:
            rating = "🎯 Learning..."
        else:
            rating = "😅 Better luck next time!"

        response = (
            f"📈 **KhelBot Prediction Stats**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Total Verified: {total}\n"
            f"✅ Correct: {correct}\n"
            f"❌ Wrong: {total - correct}\n"
            f"📊 Accuracy: {accuracy:.1f}%\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🏆 Rating: {rating}\n\n"
            f"Aur predictions karo! `/predict csk vs mi`"
        )

        await safe_reply(update, response, parse_mode="Markdown")

    except Exception as e:
        log.error(f"Accuracy error: {e}")
        await safe_reply(update, "😕 Stats load nahi ho paye. Thodi der mein try karo!")
