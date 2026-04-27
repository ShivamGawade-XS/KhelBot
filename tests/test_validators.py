"""
Tests for KhelBot validators — team alias resolution and input sanitization.
"""

import pytest
from utils.validators import (
    extract_team_from_args,
    extract_two_teams,
    sanitize_input,
    get_all_team_names,
    get_aliases_for_team,
    TEAM_ALIASES,
)


class TestExtractTeamFromArgs:
    """Tests for extract_team_from_args()."""

    def test_empty_args(self):
        assert extract_team_from_args(()) is None
        assert extract_team_from_args([]) is None

    def test_short_names(self):
        assert extract_team_from_args(("csk",)) == "Chennai Super Kings"
        assert extract_team_from_args(("mi",)) == "Mumbai Indians"
        assert extract_team_from_args(("rcb",)) == "Royal Challengers Bengaluru"
        assert extract_team_from_args(("kkr",)) == "Kolkata Knight Riders"
        assert extract_team_from_args(("dc",)) == "Delhi Capitals"
        assert extract_team_from_args(("rr",)) == "Rajasthan Royals"
        assert extract_team_from_args(("srh",)) == "Sunrisers Hyderabad"
        assert extract_team_from_args(("pbks",)) == "Punjab Kings"
        assert extract_team_from_args(("gt",)) == "Gujarat Titans"
        assert extract_team_from_args(("lsg",)) == "Lucknow Super Giants"

    def test_city_names(self):
        assert extract_team_from_args(("chennai",)) == "Chennai Super Kings"
        assert extract_team_from_args(("mumbai",)) == "Mumbai Indians"
        assert extract_team_from_args(("kolkata",)) == "Kolkata Knight Riders"
        assert extract_team_from_args(("delhi",)) == "Delhi Capitals"
        assert extract_team_from_args(("hyderabad",)) == "Sunrisers Hyderabad"
        assert extract_team_from_args(("punjab",)) == "Punjab Kings"
        assert extract_team_from_args(("gujarat",)) == "Gujarat Titans"
        assert extract_team_from_args(("lucknow",)) == "Lucknow Super Giants"

    def test_player_nicknames(self):
        assert extract_team_from_args(("dhoni",)) == "Chennai Super Kings"
        assert extract_team_from_args(("kohli",)) == "Royal Challengers Bengaluru"
        assert extract_team_from_args(("rohit",)) == "Mumbai Indians"

    def test_multi_word_aliases(self):
        assert extract_team_from_args(("mumbai", "indians")) == "Mumbai Indians"
        assert extract_team_from_args(("knight", "riders")) == "Kolkata Knight Riders"
        assert extract_team_from_args(("super", "kings")) == "Chennai Super Kings"

    def test_case_insensitive(self):
        assert extract_team_from_args(("CSK",)) == "Chennai Super Kings"
        assert extract_team_from_args(("Mi",)) == "Mumbai Indians"
        assert extract_team_from_args(("RCB",)) == "Royal Challengers Bengaluru"

    def test_unknown_team(self):
        assert extract_team_from_args(("xyz",)) is None
        assert extract_team_from_args(("random", "team")) is None


class TestExtractTwoTeams:
    """Tests for extract_two_teams()."""

    def test_empty_args(self):
        assert extract_two_teams(()) == (None, None)

    def test_vs_separator(self):
        t1, t2 = extract_two_teams(("csk", "vs", "mi"))
        assert t1 == "Chennai Super Kings"
        assert t2 == "Mumbai Indians"

    def test_v_separator(self):
        t1, t2 = extract_two_teams(("rcb", "v", "kkr"))
        assert t1 == "Royal Challengers Bengaluru"
        assert t2 == "Kolkata Knight Riders"

    def test_and_separator(self):
        t1, t2 = extract_two_teams(("dc", "and", "rr"))
        assert t1 == "Delhi Capitals"
        assert t2 == "Rajasthan Royals"

    def test_no_separator(self):
        t1, t2 = extract_two_teams(("csk", "mi"))
        assert t1 is None
        assert t2 is None

    def test_one_unknown_team(self):
        t1, t2 = extract_two_teams(("csk", "vs", "xyz"))
        assert t1 == "Chennai Super Kings"
        assert t2 is None


class TestSanitizeInput:
    """Tests for sanitize_input()."""

    def test_clean_input(self):
        assert sanitize_input("virat kohli") == "virat kohli"

    def test_special_chars(self):
        result = sanitize_input("<script>alert('xss')</script>")
        assert "<" not in result
        assert ">" not in result

    def test_max_length(self):
        long_input = "a" * 500
        result = sanitize_input(long_input, max_length=200)
        assert len(result) == 200

    def test_empty_input(self):
        assert sanitize_input("") == ""
        assert sanitize_input(None) == ""


class TestHelpers:
    """Tests for helper functions."""

    def test_all_10_teams_exist(self):
        teams = get_all_team_names()
        assert len(teams) == 10
        assert "Chennai Super Kings" in teams
        assert "Mumbai Indians" in teams
        assert "Royal Challengers Bengaluru" in teams

    def test_get_aliases(self):
        aliases = get_aliases_for_team("Chennai Super Kings")
        assert "csk" in aliases
        assert "chennai" in aliases
        assert "dhoni" in aliases

    def test_alias_count(self):
        """Ensure we have 40+ aliases total."""
        assert len(TEAM_ALIASES) >= 40
