"""
Comprehensive End-to-End (E2E) Test Suite for KhelBot V4.
Tests all 27 bot commands, inline mode, voice notes, chat, callbacks,
error handling, and keep-alive health endpoints.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message, User, Chat, CallbackQuery, InlineQuery

from handlers.start import start_command
from handlers.help import help_command
from handlers.today import today_command
from handlers.live import live_command
from handlers.playing11 import playing11_command
from handlers.pitch import pitch_command
from handlers.predict import predict_command
from handlers.dream11 import dream11_command
from handlers.stats import stats_command
from handlers.h2h import h2h_command
from handlers.compare import compare_command
from handlers.schedule import schedule_command
from handlers.points import points_command
from handlers.caps import orangecap_command, purplecap_command
from handlers.ask import ask_command
from handlers.quiz import quiz_command
from handlers.roast import roast_command
from handlers.recap import recap_command
from handlers.trending import trending_command
from handlers.funfact import funfact_command
from handlers.poll import poll_command
from handlers.accuracy import accuracy_command
from handlers.remind import remind_command
from handlers.news import news_command
from handlers.favteam import favteam_command
from handlers.deletedata import deletedata_command
from handlers.callbacks import button_callback
from handlers.chat import chat_handler
from handlers.voice import voice_handler
from handlers.inline import inline_query_handler
from main import error_handler
from utils.keep_alive import app as flask_app
from services.cache import cache

# Global sequence for unique IDs per test
_user_seq = 300000

def _get_next_user_id() -> int:
    global _user_seq
    _user_seq += 1
    return _user_seq


def make_mock_update(text: str = "/test", args: list = None, is_callback: bool = False, callback_data: str = None) -> tuple[Update, MagicMock]:
    user_id = _get_next_user_id()
    update = MagicMock(spec=Update)

    user = MagicMock(spec=User)
    user.id = user_id
    user.first_name = "KhelFan"
    user.last_name = "India"
    user.username = f"khelfan_{user_id}"

    chat = MagicMock(spec=Chat)
    chat.id = user_id
    chat.type = "private"

    message = MagicMock(spec=Message)
    message.text = text
    message.reply_text = AsyncMock()
    message.reply_poll = AsyncMock()
    message.reply_photo = AsyncMock()
    message.from_user = user
    message.chat = chat

    update.effective_user = user
    update.effective_chat = chat
    update.effective_message = message
    update.message = message

    if is_callback:
        query = MagicMock(spec=CallbackQuery)
        query.data = callback_data
        query.from_user = user
        query.answer = AsyncMock()
        query.message = message
        update.callback_query = query
        update.message = None
    else:
        update.callback_query = None

    context = MagicMock()
    context.args = args or []
    context.user_data = {}
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()

    return update, context


# ── 1. /start & /help ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_e2e_start_command():
    update, context = make_mock_update("/start")
    with patch("handlers.start.async_create_or_update_user", AsyncMock(return_value={"id": update.effective_user.id})):
        await start_command(update, context)
        assert update.effective_message.reply_text.called
        sent_text = update.effective_message.reply_text.call_args[0][0]
        assert "KhelBot" in sent_text


@pytest.mark.asyncio
async def test_e2e_help_command():
    update, context = make_mock_update("/help")
    with patch("handlers.help.async_update_user_query_count", AsyncMock()):
        await help_command(update, context)
        assert update.effective_message.reply_text.called
        sent_text = update.effective_message.reply_text.call_args[0][0]
        assert "/live" in sent_text
        assert "/predict" in sent_text


# ── 2. /today & /live ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_e2e_today_command_with_matches():
    update, context = make_mock_update("/today")
    with patch("handlers.today.search_web", AsyncMock(return_value="CSK vs MI at Wankhede Stadium 7:30 PM")), \
         patch("handlers.today.generate_freeform_answer", AsyncMock(return_value="📺 Aaj ka Match:\nCSK vs MI (7:30 PM IST)")), \
         patch("handlers.today.async_update_user_query_count", AsyncMock()):
        await today_command(update, context)
        assert update.effective_message.reply_text.called
        assert any("CSK vs MI" in call[0][0] for call in update.effective_message.reply_text.call_args_list)


@pytest.mark.asyncio
async def test_e2e_live_command():
    update, context = make_mock_update("/live")
    fake_matches = [
        {
            "id": "m1",
            "name": "India vs Australia",
            "status": "India 180/3 (32.4 ov)",
            "matchStarted": True,
            "score": [{"inning": "India", "r": 180, "w": 3, "o": 32.4}]
        }
    ]
    with patch("handlers.live.get_live_matches", AsyncMock(return_value=fake_matches)), \
         patch("handlers.live.generate_live_context", AsyncMock(return_value="Virat Kohli is batting solid.")), \
         patch("handlers.live.async_update_user_query_count", AsyncMock()):
        await live_command(update, context)
        assert update.effective_message.reply_text.called


# ── 3. /playing11 & /pitch ─────────────────────────────────────

@pytest.mark.asyncio
async def test_e2e_playing11_command():
    update, context = make_mock_update("/playing11", args=["csk"])
    with patch("handlers.playing11.search_web", AsyncMock(return_value="Ruturaj Gaikwad (c), MS Dhoni (wk)")), \
         patch("handlers.playing11.generate_freeform_answer", AsyncMock(return_value="CSK Lineup: Ruturaj, Conway, Dube, Dhoni")), \
         patch("handlers.playing11.async_update_user_query_count", AsyncMock()):
        await playing11_command(update, context)
        assert update.effective_message.reply_text.called
        assert any("CSK Lineup" in call[0][0] for call in update.effective_message.reply_text.call_args_list)


@pytest.mark.asyncio
async def test_e2e_pitch_command():
    update, context = make_mock_update("/pitch", args=["wankhede"])
    with patch("handlers.pitch.search_web", AsyncMock(return_value="Red soil pitch, batting paradise")), \
         patch("handlers.pitch.generate_freeform_answer", AsyncMock(return_value="🏟️ Wankhede: True bounce, dew expected in 2nd innings")), \
         patch("handlers.pitch.async_update_user_query_count", AsyncMock()):
        await pitch_command(update, context)
        assert update.effective_message.reply_text.called
        assert any("Wankhede" in call[0][0] for call in update.effective_message.reply_text.call_args_list)


# ── 4. /predict & /dream11 ─────────────────────────────────────

@pytest.mark.asyncio
async def test_e2e_predict_command():
    update, context = make_mock_update("/predict", args=["csk", "vs", "mi"])
    prediction_ai_text = (
        "🔮 Win Probability:\n"
        "  Chennai Super Kings: 58%\n"
        "  Mumbai Indians: 42%\n\n"
        "📊 Key Factors:\n• Strong spin bowling at Chepauk\n\n"
        "🏏 Final Verdict: Mera prediction hai CSK jeetegi!"
    )
    with patch("handlers.predict.get_match_by_team", AsyncMock(return_value={"id": "m100"})), \
         patch("services.web_search.search_match_info", AsyncMock(return_value="CSK in great form")), \
         patch("handlers.predict.generate_prediction", AsyncMock(return_value=prediction_ai_text)), \
         patch("handlers.predict.async_log_prediction", AsyncMock()) as mock_log, \
         patch("handlers.predict.async_update_user_query_count", AsyncMock()):
        await predict_command(update, context)
        assert update.effective_message.reply_text.called
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert kwargs["predicted_winner"] == "Chennai Super Kings"
        assert kwargs["confidence_pct"] == 58.0


@pytest.mark.asyncio
async def test_e2e_dream11_command():
    update, context = make_mock_update("/dream11", args=["rcb", "vs", "kkr"])
    dream11_ai_text = "🏆 Dream11 Team:\n👑 Captain: Virat Kohli\n🥈 Vice-Captain: Andre Russell"
    with patch("handlers.dream11.get_match_by_team", AsyncMock(return_value=None)), \
         patch("services.web_search.search_web", AsyncMock(return_value="")), \
         patch("handlers.dream11.generate_dream11", AsyncMock(return_value=dream11_ai_text)), \
         patch("handlers.dream11.async_update_user_query_count", AsyncMock()):
        await dream11_command(update, context)
        assert update.effective_message.reply_text.called
        assert any("Virat Kohli" in call[0][0] for call in update.effective_message.reply_text.call_args_list)


# ── 5. /stats, /h2h & /compare ─────────────────────────────────

@pytest.mark.asyncio
async def test_e2e_stats_command():
    update, context = make_mock_update("/stats", args=["virat", "kohli"])
    fake_player = {
        "name": "Virat Kohli",
        "role": "Top-order batter",
        "country": "India"
    }
    with patch("handlers.stats.get_player_stats", AsyncMock(return_value=fake_player)), \
         patch("services.web_search.search_player_info", AsyncMock(return_value="")), \
         patch("handlers.stats.generate_player_summary", AsyncMock(return_value="Run machine King Kohli!")), \
         patch("handlers.stats.async_update_user_query_count", AsyncMock()):
        await stats_command(update, context)
        assert update.effective_message.reply_text.called
        assert any("Virat Kohli" in call[0][0] for call in update.effective_message.reply_text.call_args_list)


@pytest.mark.asyncio
async def test_e2e_h2h_command():
    update, context = make_mock_update("/h2h", args=["csk", "vs", "mi"])
    with patch("services.web_search.search_match_info", AsyncMock(return_value="CSK vs MI rivalry")), \
         patch("handlers.h2h.generate_h2h_analysis", AsyncMock(return_value="CSK vs MI: El Clasico of IPL! MI leads 20-17.")), \
         patch("handlers.h2h.async_update_user_query_count", AsyncMock()):
        await h2h_command(update, context)
        assert update.effective_message.reply_text.called


@pytest.mark.asyncio
async def test_e2e_compare_command():
    update, context = make_mock_update("/compare", args=["rohit", "vs", "kohli"])
    with patch("services.web_search.search_web", AsyncMock(return_value="Comparison data")), \
         patch("handlers.compare.get_player_stats", AsyncMock(side_effect=[{"name": "Rohit Sharma"}, {"name": "Virat Kohli"}])), \
         patch("handlers.compare.generate_player_comparison", AsyncMock(return_value="Rohit has 5 IPL trophies, Virat has most runs.")), \
         patch("handlers.compare.async_update_user_query_count", AsyncMock()):
        await compare_command(update, context)
        assert update.effective_message.reply_text.called


# ── 6. /schedule, /points, /caps ───────────────────────────────

@pytest.mark.asyncio
async def test_e2e_schedule_command():
    update, context = make_mock_update("/schedule")
    fake_matches = [
        {"name": "Match 1: CSK vs RCB", "status": "Upcoming", "matchEnded": False}
    ]
    with patch("handlers.schedule.get_all_matches", AsyncMock(return_value=fake_matches)), \
         patch("handlers.schedule.async_update_user_query_count", AsyncMock()):
        await schedule_command(update, context)
        assert update.effective_message.reply_text.called


@pytest.mark.asyncio
async def test_e2e_points_command():
    update, context = make_mock_update("/points")
    fake_standings = [
        {"name": "Kolkata Knight Riders", "points": 20, "won": 9, "played": 14}
    ]
    with patch("handlers.points.get_points_table", AsyncMock(return_value=fake_standings)), \
         patch("handlers.points.async_update_user_query_count", AsyncMock()):
        await points_command(update, context)
        assert update.effective_message.reply_text.called


@pytest.mark.asyncio
async def test_e2e_caps_commands():
    update1, context1 = make_mock_update("/orangecap")
    with patch("handlers.caps.search_web", AsyncMock(return_value="Virat Kohli - 741 runs")), \
         patch("handlers.caps.generate_freeform_answer", AsyncMock(return_value="🧡 Orange Cap Leader: Virat Kohli")), \
         patch("handlers.caps.async_update_user_query_count", AsyncMock()):
        await orangecap_command(update1, context1)
        assert update1.effective_message.reply_text.called

    update2, context2 = make_mock_update("/purplecap")
    with patch("handlers.caps.search_web", AsyncMock(return_value="Harshal Patel - 24 wickets")), \
         patch("handlers.caps.generate_freeform_answer", AsyncMock(return_value="💜 Purple Cap Leader: Harshal Patel")), \
         patch("handlers.caps.async_update_user_query_count", AsyncMock()):
        await purplecap_command(update2, context2)
        assert update2.effective_message.reply_text.called


# ── 7. /ask, /quiz, /roast, /recap ─────────────────────────────

@pytest.mark.asyncio
async def test_e2e_ask_command():
    update, context = make_mock_update("/ask", args=["who", "has", "the", "fastest", "ipl", "fifty"])
    with patch("handlers.ask.search_web", AsyncMock(return_value="Yashasvi Jaiswal scored 50 in 13 balls.")), \
         patch("handlers.ask.generate_freeform_answer", AsyncMock(return_value="Yashasvi Jaiswal holds the record with 13 balls!")), \
         patch("handlers.ask.async_update_user_query_count", AsyncMock()):
        await ask_command(update, context)
        assert update.effective_message.reply_text.called


@pytest.mark.asyncio
async def test_e2e_quiz_command_and_callbacks():
    update, context = make_mock_update("/quiz")
    quiz_sample = {
        "question": "Fastest IPL century kiske naam hai?",
        "options": ["Chris Gayle", "Yusuf Pathan", "David Miller", "AB de Villiers"],
        "correct": 0,
        "explanation": "Chris Gayle hit 100 in 30 balls against PWI."
    }
    with patch("handlers.quiz.generate_quiz_question", AsyncMock(return_value=quiz_sample)), \
         patch("handlers.quiz.async_update_user_query_count", AsyncMock()):
        await quiz_command(update, context)
        assert update.effective_message.reply_text.called

        # Find the generated quiz ID from the cache
        keys = [k for k in cache._store.keys() if k.startswith("quiz:")]
        assert len(keys) > 0
        qid = keys[0].split(":")[1]

        # Test answering correctly
        cb_update_correct, cb_context = make_mock_update(is_callback=True, callback_data=f"q_{qid}_0")
        await button_callback(cb_update_correct, cb_context)
        cb_update_correct.effective_message.reply_text.assert_called()
        assert "Sahi Jawab" in cb_update_correct.effective_message.reply_text.call_args[0][0]

        # Test answering incorrectly
        cb_update_wrong, _ = make_mock_update(is_callback=True, callback_data=f"q_{qid}_1")
        await button_callback(cb_update_wrong, cb_context)
        assert "Galat" in cb_update_wrong.effective_message.reply_text.call_args[0][0]

        # Test expired quiz
        cb_update_expired, _ = make_mock_update(is_callback=True, callback_data="q_nonexistent_0")
        await button_callback(cb_update_expired, cb_context)
        assert "expire" in cb_update_expired.effective_message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_e2e_roast_command():
    update, context = make_mock_update("/roast", args=["rcb"])
    with patch("handlers.roast.search_web", AsyncMock(return_value="")), \
         patch("handlers.roast.generate_freeform_answer", AsyncMock(return_value="Ee sala cup namde... agle saal pakka! 😂")), \
         patch("handlers.roast.async_update_user_query_count", AsyncMock()):
        await roast_command(update, context)
        assert update.effective_message.reply_text.called


@pytest.mark.asyncio
async def test_e2e_recap_command():
    update, context = make_mock_update("/recap", args=["csk"])
    with patch("handlers.recap.get_match_by_team", AsyncMock(return_value={"id": "m1", "name": "CSK vs GT"})), \
         patch("handlers.recap.generate_match_recap", AsyncMock(return_value="CSK won in a thriller final ball! 🏆")), \
         patch("handlers.recap.async_update_user_query_count", AsyncMock()):
        await recap_command(update, context)
        assert update.effective_message.reply_text.called


# ── 8. /trending, /funfact, /poll ──────────────────────────────

@pytest.mark.asyncio
async def test_e2e_trending_command():
    update, context = make_mock_update("/trending")
    with patch("handlers.trending.get_cricket_news", AsyncMock(return_value=[{"title": "IPL Mega Auction"}]), create=True), \
         patch("handlers.trending.search_cricket_news", AsyncMock(return_value="IPL rumors")), \
         patch("handlers.trending.generate_trending", AsyncMock(return_value="🔥 Trending: Mega auction retentions buzz!")), \
         patch("handlers.trending.async_update_user_query_count", AsyncMock()):
        await trending_command(update, context)
        assert update.effective_message.reply_text.called


@pytest.mark.asyncio
async def test_e2e_funfact_command():
    update, context = make_mock_update("/funfact")
    with patch("handlers.funfact.search_web", AsyncMock(return_value="")), \
         patch("handlers.funfact.generate_funfact", AsyncMock(return_value="🤯 Fact: Sachin played for Pakistan before India in 1987!")), \
         patch("handlers.funfact.async_update_user_query_count", AsyncMock()):
        await funfact_command(update, context)
        assert update.effective_message.reply_text.called


@pytest.mark.asyncio
async def test_e2e_poll_command():
    update, context = make_mock_update("/poll", args=["csk", "vs", "mi"])
    with patch("handlers.poll.async_update_user_query_count", AsyncMock()):
        await poll_command(update, context)
        assert update.effective_message.reply_poll.called
        kwargs = update.effective_message.reply_poll.call_args[1]
        assert "Chennai Super Kings vs Mumbai Indians" in kwargs["question"]


# ── 9. /accuracy, /remind, /news ───────────────────────────────

@pytest.mark.asyncio
async def test_e2e_accuracy_command():
    update, context = make_mock_update("/accuracy")
    fake_accuracy = {"total": 10, "correct": 8, "accuracy": 80.0}
    with patch("handlers.accuracy.get_all_matches", AsyncMock(return_value=[])), \
         patch("handlers.accuracy.async_get_accuracy", AsyncMock(return_value=fake_accuracy)), \
         patch("handlers.accuracy.async_update_user_query_count", AsyncMock()):
        await accuracy_command(update, context)
        assert update.effective_message.reply_text.called
        assert any("80.0%" in call[0][0] for call in update.effective_message.reply_text.call_args_list)


@pytest.mark.asyncio
async def test_e2e_remind_command():
    update, context = make_mock_update("/remind", args=["csk"])
    fake_matches = [
        {
            "id": "csk_match_99",
            "name": "CSK vs MI",
            "status": "Upcoming",
            "teams": ["Chennai Super Kings", "Mumbai Indians"],
            "dateTimeGMT": "2026-05-15T14:00:00"
        }
    ]
    with patch("handlers.remind.get_all_matches", AsyncMock(return_value=fake_matches)), \
         patch("handlers.remind.async_create_or_update_user", AsyncMock()), \
         patch("handlers.remind.async_create_reminder", AsyncMock(return_value={"id": 1})), \
         patch("handlers.remind.async_update_user_query_count", AsyncMock()):
        await remind_command(update, context)
        assert update.effective_message.reply_text.called
        assert any("reminder set ho gaya" in call[0][0].lower() for call in update.effective_message.reply_text.call_args_list)


@pytest.mark.asyncio
async def test_e2e_news_command():
    update, context = make_mock_update("/news")
    with patch("handlers.news.get_cricket_news", AsyncMock(return_value=[{"title": "BCCI announces new tournament"}]), create=True), \
         patch("handlers.news.async_update_user_query_count", AsyncMock()):
        await news_command(update, context)
        assert update.effective_message.reply_text.called


# ── 10. /favteam & /deletedata ─────────────────────────────────

@pytest.mark.asyncio
async def test_e2e_favteam_command():
    update, context = make_mock_update("/favteam", args=["rcb"])
    with patch("handlers.favteam.async_create_or_update_user", AsyncMock()), \
         patch("handlers.favteam.async_set_favorite_team", AsyncMock(return_value=True)):
        await favteam_command(update, context)
        assert update.effective_message.reply_text.called
        assert any("Royal Challengers Bengaluru" in call[0][0] for call in update.effective_message.reply_text.call_args_list)


@pytest.mark.asyncio
async def test_e2e_deletedata_command():
    update, context = make_mock_update("/deletedata")
    with patch("handlers.deletedata.async_delete_user_data", AsyncMock(return_value=True)):
        await deletedata_command(update, context)
        assert update.effective_message.reply_text.called
        assert any("Data Delete Ho Gaya" in call[0][0] for call in update.effective_message.reply_text.call_args_list)


# ── 11. Chat & Voice Handlers ──────────────────────────────────

@pytest.mark.asyncio
async def test_e2e_chat_handler_greeting():
    update, context = make_mock_update("Namaste KhelBot!")
    with patch("handlers.chat.async_update_user_query_count", AsyncMock()):
        await chat_handler(update, context)
        assert update.effective_message.reply_text.called
        assert any("Namaste bhai" in call[0][0] for call in update.effective_message.reply_text.call_args_list)


@pytest.mark.asyncio
async def test_e2e_chat_handler_cricket_query():
    update, context = make_mock_update("Virat Kohli kitne centuries mara hai?")
    with patch("handlers.chat.search_web", AsyncMock(return_value="Virat Kohli has 80 international centuries.")), \
         patch("handlers.chat.generate_freeform_answer", AsyncMock(return_value="King Kohli has 80 centuries! 👑")), \
         patch("handlers.chat.async_update_user_query_count", AsyncMock()):
        await chat_handler(update, context)
        assert update.effective_message.reply_text.called
        assert any("King Kohli" in call[0][0] for call in update.effective_message.reply_text.call_args_list)


@pytest.mark.asyncio
async def test_e2e_voice_handler():
    update, context = make_mock_update()
    voice_mock = MagicMock()
    voice_mock.duration = 4
    voice_mock.file_id = "voice_file_123"
    update.message.voice = voice_mock
    update.message.audio = None

    tg_file_mock = MagicMock()
    tg_file_mock.download_as_bytearray = AsyncMock(return_value=bytearray(b"ogg_voice_content"))
    context.bot.get_file = AsyncMock(return_value=tg_file_mock)

    with patch("handlers.voice.transcribe_audio_file", AsyncMock(return_value="Aaj ka match kaun jeetega?")), \
         patch("handlers.voice.search_web", AsyncMock(return_value="CSK in good form")), \
         patch("handlers.voice.generate_freeform_answer", AsyncMock(return_value="CSK ke chances zyada lag rahe hain!")), \
         patch("handlers.voice.async_update_user_query_count", AsyncMock()):
        await voice_handler(update, context)
        assert update.effective_message.reply_text.call_count >= 2


# ── 12. Telegram Inline Query Mode ─────────────────────────────

@pytest.mark.asyncio
async def test_e2e_inline_query_handler():
    update = MagicMock(spec=Update)
    inline_q = MagicMock(spec=InlineQuery)
    inline_q.query = "live"
    inline_q.answer = AsyncMock()
    update.inline_query = inline_q

    fake_matches = [
        {"name": "CSK vs MI", "status": "CSK 140/2 (15 ov)", "score": [{"inning": "CSK", "r": 140, "w": 2, "o": 15}]}
    ]
    with patch("handlers.inline.get_live_matches", AsyncMock(return_value=fake_matches)):
        await inline_query_handler(update, MagicMock())
        assert inline_q.answer.called
        results = inline_q.answer.call_args[0][0]
        assert len(results) > 0
        assert "CSK vs MI" in results[0].title


# ── 13. Global Error Handler ───────────────────────────────────

@pytest.mark.asyncio
async def test_e2e_error_handler():
    update, context = make_mock_update("/crash")
    context.error = ValueError("Unexpected mock failure")

    await error_handler(update, context)
    assert update.effective_message.reply_text.called
    sent_text = update.effective_message.reply_text.call_args[0][0]
    assert "Oops! Kuch gadbad ho gayi" in sent_text


# ── 14. Keep-Alive Web Server Routes ───────────────────────────

def test_e2e_keep_alive_routes():
    client = flask_app.test_client()
    res_home = client.get("/")
    assert res_home.status_code == 200
    assert "KhelBot V4 is alive" in res_home.get_data(as_text=True)

    res_health = client.get("/health")
    assert res_health.status_code == 200
    json_data = res_health.get_json()
    assert json_data["status"] == "healthy"
    assert json_data["service"] == "khelbot"
