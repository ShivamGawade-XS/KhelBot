"""
Unit & Integration Tests for KhelBot Services:
- CricAPI service
- Gemini / Groq AI service (with multi-model fallback & Whisper)
- Web search service (with TTL caching)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.cricapi import (
    get_live_matches, get_match_by_team, get_player_stats, get_all_matches, get_points_table
)
from services.gemini import (
    _generate, transcribe_audio_file, generate_live_context,
    generate_prediction, generate_dream11, generate_quiz_question,
    generate_freeform_answer
)
from services.web_search import search_web
from services.cache import cache


@pytest.mark.asyncio
async def test_cricapi_get_live_matches():
    mock_data = {
        "status": "success",
        "data": [
            {"id": "m1", "name": "CSK vs MI", "matchStarted": True, "status": "CSK 150/4 (18 ov)"},
            {"id": "m2", "name": "RCB vs KKR", "matchStarted": False, "status": "Upcoming"}
        ]
    }
    with patch("services.cricapi._cached_get", AsyncMock(return_value=mock_data)):
        matches = await get_live_matches()
        assert len(matches) == 1
        assert matches[0]["id"] == "m1"
        assert matches[0]["name"] == "CSK vs MI"


@pytest.mark.asyncio
async def test_cricapi_get_match_by_team():
    live_matches = [
        {
            "id": "m1",
            "name": "Chennai Super Kings vs Mumbai Indians",
            "teams": ["Chennai Super Kings", "Mumbai Indians"],
            "teamInfo": [
                {"name": "Chennai Super Kings", "shortname": "CSK"},
                {"name": "Mumbai Indians", "shortname": "MI"}
            ]
        },
        {
            "id": "m2",
            "name": "Royal Challengers vs Kolkata Knight Riders",
            "teams": ["RCB", "KKR"],
            "teamInfo": [
                {"name": "Royal Challengers", "shortname": "RCB"},
                {"name": "Kolkata Knight Riders", "shortname": "KKR"}
            ]
        }
    ]
    with patch("services.cricapi.get_live_matches", AsyncMock(return_value=live_matches)):
        m_csk = await get_match_by_team("csk")
        assert m_csk is not None
        assert m_csk["id"] == "m1"

        m_rcb = await get_match_by_team("rcb")
        assert m_rcb is not None
        assert m_rcb["id"] == "m2"

        m_none = await get_match_by_team("australia")
        assert m_none is None


@pytest.mark.asyncio
async def test_cricapi_get_player_stats():
    search_resp = {
        "status": "success",
        "data": [{"id": "p1", "name": "Virat Kohli", "country": "India"}]
    }
    detail_resp = {
        "status": "success",
        "data": {"id": "p1", "name": "Virat Kohli", "role": "Top-order batter", "country": "India"}
    }
    with patch("services.cricapi._cached_get", AsyncMock(side_effect=[search_resp, detail_resp])):
        player = await get_player_stats("kohli")
        assert player is not None
        assert player["name"] == "Virat Kohli"
        assert player["role"] == "Top-order batter"


@pytest.mark.asyncio
async def test_cricapi_get_points_table_fallback():
    mock_matches = [
        {"teams": ["CSK", "MI"], "status": "CSK won by 20 runs"},
        {"teams": ["CSK", "RCB"], "status": "CSK won by 6 wickets"},
        {"teams": ["MI", "RCB"], "status": "RCB won by 4 wickets"}
    ]
    with patch("services.cricapi._cached_get", AsyncMock(return_value=None)), \
         patch("services.cricapi.get_all_matches", AsyncMock(return_value=mock_matches)):
        table = await get_points_table()
        assert table is not None
        assert len(table) == 3
        # CSK won 2 -> 4 points
        assert table[0]["name"] == "CSK"
        assert table[0]["points"] == 4


@pytest.mark.asyncio
async def test_gemini_generate_primary_model_success():
    mock_choice = MagicMock()
    mock_choice.message.content = "Bhai CSK ka match zabardast hone wala hai!"
    mock_resp = MagicMock(choices=[mock_choice])

    with patch("services.gemini._client.chat.completions.create", AsyncMock(return_value=mock_resp)):
        ans = await _generate("Tell me about CSK")
        assert "CSK" in ans
        assert "zabardast" in ans


@pytest.mark.asyncio
async def test_gemini_generate_fallback_chain_on_error():
    """Verify fallback to second model when primary model throws an exception (e.g. rate limit)."""
    mock_choice = MagicMock()
    mock_choice.message.content = "Fallback 8B response: RCB jeet sakti hai!"
    mock_resp = MagicMock(choices=[mock_choice])

    # First call fails (primary model), second call succeeds (fallback model)
    with patch("services.gemini._client.chat.completions.create", AsyncMock(side_effect=[Exception("Rate limit 429"), mock_resp])):
        ans = await _generate("Who will win?")
        assert "Fallback 8B" in ans


@pytest.mark.asyncio
async def test_gemini_transcribe_audio():
    mock_transcription = "Bhai aaj ka live score kya chal raha hai?"
    with patch("services.gemini._client.audio.transcriptions.create", AsyncMock(return_value=mock_transcription)):
        text = await transcribe_audio_file(b"fake_audio_bytes")
        assert text == "Bhai aaj ka live score kya chal raha hai?"


@pytest.mark.asyncio
async def test_gemini_generate_quiz_question():
    mock_json = """{
        "question": "IPL 2024 kisne jeeta?",
        "options": ["KKR", "SRH", "RR", "RCB"],
        "correct": 0,
        "explanation": "KKR defeated SRH in the final."
    }"""
    mock_choice = MagicMock()
    mock_choice.message.content = mock_json
    mock_resp = MagicMock(choices=[mock_choice])

    with patch("services.gemini._client.chat.completions.create", AsyncMock(return_value=mock_resp)):
        quiz = await generate_quiz_question()
        assert quiz is not None
        assert quiz["question"] == "IPL 2024 kisne jeeta?"
        assert quiz["correct"] == 0
        assert len(quiz["options"]) == 4


@pytest.mark.asyncio
async def test_web_search_cached_and_live():
    cache.clear()
    fake_results = [
        {"title": "IND vs AUS Live Score", "body": "India 240/3 after 40 overs", "href": "https://cricket.com/ind-aus"}
    ]

    with patch("services.web_search._sync_search", return_value=fake_results):
        # 1. Live call
        res1 = await search_web("ind vs aus score")
        assert "IND vs AUS" in res1
        assert "240/3" in res1

        # 2. Subsequent call should hit cache without calling _sync_search
        with patch("services.web_search._sync_search", side_effect=Exception("Should not be called")):
            res2 = await search_web("ind vs aus score")
            assert res2 == res1
