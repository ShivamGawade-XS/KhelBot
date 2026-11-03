"""
KhelBot Voice Handler — Voice note transcription & intelligence.
Accepts Hindi / Hinglish voice notes, transcribes them using Groq Whisper Large V3,
and generates real-time cricket intelligence answers.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.gemini import transcribe_audio_file, generate_freeform_answer
from services.web_search import search_web
from database.users import async_update_user_query_count
from utils.rate_limiter import rate_limiter
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.voice")


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming voice notes and audio clips from users."""
    if not update.message:
        return

    user = update.effective_user
    if not user:
        return

    allowed, block_msg = rate_limiter.check(user.id)
    if not allowed:
        await safe_reply(update, block_msg)
        return

    voice = update.message.voice or update.message.audio
    if not voice:
        return

    log.info(f"Voice message received from {user.id} ({voice.duration}s)")
    await async_update_user_query_count(user.id)

    # Inform user that audio is being processed
    await safe_reply(update, "🎧 **Aapka voice note sun raha hoon...** ⏳")

    try:
        # Download audio file from Telegram
        tg_file = await context.bot.get_file(voice.file_id)
        audio_bytearray = await tg_file.download_as_bytearray()
        audio_bytes = bytes(audio_bytearray)

        # Transcribe with Whisper
        transcript = await transcribe_audio_file(audio_bytes, filename="voice.ogg")

        if not transcript or len(transcript.strip()) < 2:
            await safe_reply(update, 
                "🤔 Awaz thodi saaf nahi aayi bhai! Thoda paas aake dobara voice note bhejo ya text type karo.",
                parse_mode="Markdown"
            )
            return

        log.info(f"Voice transcription for {user.id}: {transcript[:60]}...")

        # Acknowledge transcription to user
        await safe_reply(update, f"🎙️ **Maine suna:** *\"{transcript}\"*\n\n_Answer nikaal raha hoon..._ 🔍🧠", parse_mode="Markdown")

        # Ground answer with real-time web search
        live_context = await search_web(transcript)
        answer = await generate_freeform_answer(transcript, live_context=live_context)

        await safe_reply(update, answer, parse_mode="Markdown")

    except Exception as e:
        log.error(f"Failed to process voice note from {user.id}: {e}")
        await safe_reply(update, "😅 Voice note process karne mein thodi dikkat aayi. Text type karke poocho bhai!")

