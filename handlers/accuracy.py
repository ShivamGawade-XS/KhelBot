"""
KhelBot /accuracy Handler — Show prediction accuracy stats.
"""

from telegram import Update
from telegram.ext import ContextTypes

from database.predictions import get_accuracy
from database.users import update_user_query_count, get_user
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.accuracy")


async def accuracy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /accuracy command — show prediction stats."""
    user = update.effective_user
    log.info(f"/accuracy from {user.id}")

    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    await safe_reply(update, "📈 Prediction accuracy calculate kar raha hoon... ⏳")

    try:
        stats = get_accuracy()

        if not stats:
            await safe_reply(update,
                "📈 KhelBot Prediction Stats\n\n"
                "Abhi tak koi verified prediction nahi hai.\n"
                "Jaise matches complete honge, accuracy track hogi!\n\n"
                "Predictions karo: `/predict csk vs mi`",
                parse_mode="Markdown")
            return

        total = stats.get("total", 0)
        correct = stats.get("correct", 0)
        accuracy = stats.get("accuracy", 0)

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
            f"📈 KhelBot Prediction Stats\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Total Predictions: {total}\n"
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
