"""
Tests for KhelBot formatters — validates output formatting for various API response shapes.
"""

import pytest
from utils.formatters import format_score, format_news_list, format_player_stats, format_match_list


class TestFormatScore:
    """Tests for format_score()."""

    def test_empty_data(self):
        assert "unavailable" in format_score({}).lower() or "unavailable" in format_score(None).lower()

    def test_basic_match(self):
        match = {
            "name": "CSK vs MI, 30th Match",
            "status": "CSK won by 5 wickets",
            "venue": "MA Chidambaram Stadium, Chennai",
            "matchType": "t20",
            "date": "2026-04-27",
        }
        result = format_score(match)
        assert "CSK vs MI" in result
        assert "Chennai" in result
        assert "T20" in result
        assert "CSK won" in result

    def test_match_with_scores(self):
        match = {
            "name": "RCB vs KKR",
            "status": "RCB need 45 runs in 30 balls",
            "venue": "M Chinnaswamy Stadium",
            "score": [
                {"inning": "KKR Inning 1", "r": 185, "w": 6, "o": 20},
                {"inning": "RCB Inning 1", "r": 141, "w": 3, "o": 15},
            ],
        }
        result = format_score(match)
        assert "185/6" in result
        assert "141/3" in result
        assert "Scorecard" in result

    def test_match_without_venue(self):
        match = {"name": "Test Match", "status": "In Progress"}
        result = format_score(match)
        assert "Test Match" in result
        assert "In Progress" in result


class TestFormatNewsList:
    """Tests for format_news_list()."""

    def test_empty_articles(self):
        result = format_news_list([])
        assert "nahi mili" in result.lower() or "try karo" in result.lower()

    def test_single_article(self):
        articles = [{
            "title": "IPL 2026: CSK beats MI in thriller",
            "source": {"name": "ESPN Cricinfo"},
            "url": "https://example.com/article1",
        }]
        result = format_news_list(articles)
        assert "CSK beats MI" in result
        assert "ESPN Cricinfo" in result
        assert "example.com" in result

    def test_multiple_articles(self):
        articles = [
            {"title": f"Headline {i}", "source": {"name": f"Source {i}"}, "url": f"https://example.com/{i}"}
            for i in range(3)
        ]
        result = format_news_list(articles)
        assert "1." in result
        assert "2." in result
        assert "3." in result

    def test_article_without_url(self):
        articles = [{"title": "No URL Article", "source": {"name": "Test"}}]
        result = format_news_list(articles)
        assert "No URL Article" in result


class TestFormatPlayerStats:
    """Tests for format_player_stats()."""

    def test_empty_data(self):
        assert "unavailable" in format_player_stats({}).lower() or "unavailable" in format_player_stats(None).lower()

    def test_basic_player(self):
        player = {
            "name": "Virat Kohli",
            "country": "India",
            "role": "Batsman",
            "battingStyle": "Right Hand Bat",
            "bowlingStyle": "Right Arm Medium",
            "dateOfBirth": "Nov 05, 1988",
            "placeOfBirth": "Delhi",
        }
        result = format_player_stats(player)
        assert "Virat Kohli" in result
        assert "India" in result
        assert "Batsman" in result
        assert "Right Hand Bat" in result

    def test_player_with_stats(self):
        player = {
            "name": "Jasprit Bumrah",
            "country": "India",
            "role": "Bowler",
            "battingStyle": "Right Hand Bat",
            "bowlingStyle": "Right Arm Fast",
            "stats": [
                {"matchtype": "T20I", "mat": "70", "wkts": "85", "avg": "18.2"},
                {"matchtype": "ODI", "mat": "80", "runs": "30", "wkts": "130"},
            ],
        }
        result = format_player_stats(player)
        assert "Bumrah" in result
        assert "T20I" in result
        assert "85" in result  # wickets


class TestFormatMatchList:
    """Tests for format_match_list()."""

    def test_empty_list(self):
        result = format_match_list([])
        assert "nahi chal raha" in result.lower()

    def test_multiple_matches(self):
        matches = [
            {"name": "CSK vs MI", "status": "Live"},
            {"name": "RCB vs KKR", "status": "Upcoming"},
        ]
        result = format_match_list(matches)
        assert "CSK vs MI" in result
        assert "RCB vs KKR" in result
        assert "1." in result
        assert "2." in result
