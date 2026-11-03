"""
Unit tests for prediction parsing and accuracy resolution logic.
"""

import pytest
from handlers.predict import _parse_winner_and_confidence
from database.predictions import resolve_predictions_from_matches


def test_parse_winner_and_confidence_direct_pct():
    sample_text = """
🔮 Win Probability:
  Chennai Super Kings: 68%
  Mumbai Indians: 32%

📊 Key Factors:
- Good spin conditions
"""
    winner, conf = _parse_winner_and_confidence(sample_text, "Chennai Super Kings", "Mumbai Indians")
    assert winner == "Chennai Super Kings"
    assert conf == 68.0


def test_parse_winner_and_confidence_team2_higher():
    sample_text = """
🔮 Win Probability:
  Royal Challengers Bengaluru: 42%
  Kolkata Knight Riders: 58%

Final Verdict: KKR to dominate.
"""
    winner, conf = _parse_winner_and_confidence(sample_text, "Royal Challengers Bengaluru", "Kolkata Knight Riders")
    assert winner == "Kolkata Knight Riders"
    assert conf == 58.0


def test_parse_winner_fallback_to_verdict():
    sample_text = """
🔮 Win Probability is evenly balanced.

Final Verdict: Mera prediction hai Mumbai Indians is match ko nikaal legi!
"""
    winner, conf = _parse_winner_and_confidence(sample_text, "Chennai Super Kings", "Mumbai Indians")
    assert winner == "Mumbai Indians"

