"""
KhelBot CricAPI Service — Live scores, match info, player stats, and standings.
All calls go through the TTL cache to respect the 500 calls/day free tier limit.
"""

import hashlib
import httpx
from typing import Any, Optional

from config.settings import CRICAPI_KEY, CRICAPI_BASE_URL, CACHE_TTL_LIVE_SCORES, CACHE_TTL_PLAYER_STATS
from services.cache import cache
from utils.logger import setup_logger

log = setup_logger("cricapi")

_client = httpx.AsyncClient(timeout=10.0)


def _cache_key(endpoint: str, params: dict = None) -> str:
    param_str = str(sorted((params or {}).items()))
    hash_suffix = hashlib.md5(param_str.encode()).hexdigest()[:8]
    return f"cricapi:{endpoint}:{hash_suffix}"


async def _cached_get(endpoint: str, params: dict = None, ttl: int = CACHE_TTL_LIVE_SCORES) -> Optional[dict]:
    key = _cache_key(endpoint, params)
    cached = cache.get(key)
    if cached is not None:
        return cached

    url = f"{CRICAPI_BASE_URL}/{endpoint}"
    request_params = {"apikey": CRICAPI_KEY}
    if params:
        request_params.update(params)

    try:
        log.info(f"API call: GET {endpoint} | params: {params}")
        response = await _client.get(url, params=request_params)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "success":
            return None
        cache.set(key, data, ttl)
        return data
    except httpx.TimeoutException:
        log.error(f"CricAPI timeout on {endpoint}")
        return None
    except httpx.HTTPStatusError as e:
        log.error(f"CricAPI HTTP error: {e.response.status_code}")
        return None
    except Exception as e:
        log.error(f"CricAPI error: {e}")
        return None


async def get_live_matches() -> list[dict]:
    data = await _cached_get("currentMatches")
    if not data:
        return []
    return [m for m in data.get("data", []) if m.get("matchStarted", False)]


async def get_match_by_team(team_name: str) -> Optional[dict]:
    matches = await get_live_matches()
    if not matches:
        return None
    team_lower = team_name.lower()
    for match in matches:
        for team in match.get("teams", []):
            if team_lower in team.lower() or team.lower() in team_lower:
                return match
        for info in match.get("teamInfo", []):
            t_name = info.get("name", "").lower()
            t_short = info.get("shortname", "").lower()
            if team_lower in t_name or t_name in team_lower:
                return match
            if t_short and (team_lower in t_short or t_short in team_lower):
                return match
        if team_lower in match.get("name", "").lower():
            return match
    return None


async def get_player_stats(player_name: str) -> Optional[dict]:
    search_data = await _cached_get("players", params={"search": player_name}, ttl=CACHE_TTL_PLAYER_STATS)
    if not search_data:
        return None
    players = search_data.get("data", [])
    if not players:
        return None
    player = players[0]
    player_id = player.get("id")
    if not player_id:
        return player
    detail_data = await _cached_get("players_info", params={"id": player_id}, ttl=CACHE_TTL_PLAYER_STATS)
    if detail_data and detail_data.get("data"):
        return detail_data["data"]
    return player


async def get_all_matches() -> list[dict]:
    data = await _cached_get("currentMatches")
    if not data:
        return []
    return data.get("data", [])


async def get_points_table() -> Optional[list]:
    """Fetch IPL points table from series data or build from match results."""
    series_data = await _cached_get("series", ttl=3600)
    if series_data:
        for series in series_data.get("data", []):
            name = series.get("name", "").lower()
            if "indian premier league" in name or "ipl" in name:
                sid = series.get("id")
                if sid:
                    info = await _cached_get("series_info", params={"id": sid}, ttl=1800)
                    if info and info.get("data", {}).get("info", {}).get("standings"):
                        return info["data"]["info"]["standings"]

    # Fallback: build from match results
    matches = await get_all_matches()
    if not matches:
        return None
    teams = {}
    for m in matches:
        status = m.get("status", "")
        match_teams = m.get("teams", [])
        if not match_teams:
            continue
        for t in match_teams:
            if t not in teams:
                teams[t] = {"name": t, "played": 0, "won": 0, "lost": 0, "nr": 0, "points": 0}
        if "won" in status.lower():
            for t in match_teams:
                teams[t]["played"] += 1
                if t.lower() in status.lower():
                    teams[t]["won"] += 1
                    teams[t]["points"] += 2
                else:
                    teams[t]["lost"] += 1
        elif "no result" in status.lower():
            for t in match_teams:
                teams[t]["played"] += 1
                teams[t]["nr"] += 1
                teams[t]["points"] += 1
    if not teams:
        return None
    return sorted(teams.values(), key=lambda x: (x["points"], x["won"]), reverse=True)
