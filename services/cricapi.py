"""
KhelBot CricAPI Service — Live scores, match info, and player stats.
All calls go through the TTL cache to respect the 500 calls/day free tier limit.
"""

import hashlib
import httpx
from typing import Any, Optional

from config.settings import CRICAPI_KEY, CRICAPI_BASE_URL, CACHE_TTL_LIVE_SCORES, CACHE_TTL_PLAYER_STATS
from services.cache import cache
from utils.logger import setup_logger

log = setup_logger("cricapi")

# HTTP client with timeout
_client = httpx.AsyncClient(timeout=10.0)


def _cache_key(endpoint: str, params: dict = None) -> str:
    """Generate a cache key from endpoint + params."""
    param_str = str(sorted((params or {}).items()))
    hash_suffix = hashlib.md5(param_str.encode()).hexdigest()[:8]
    return f"cricapi:{endpoint}:{hash_suffix}"


async def _cached_get(endpoint: str, params: dict = None, ttl: int = CACHE_TTL_LIVE_SCORES) -> Optional[dict]:
    """
    Make a cached GET request to CricAPI.
    Returns parsed JSON data or None on failure.
    """
    key = _cache_key(endpoint, params)
    
    # Check cache first
    cached = cache.get(key)
    if cached is not None:
        log.debug(f"Cache HIT: {key}")
        return cached

    # Build request
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
            log.warning(f"CricAPI returned non-success: {data.get('status')}")
            return None

        # Cache the successful response
        cache.set(key, data, ttl)
        log.debug(f"Cache SET: {key} (TTL={ttl}s)")
        
        return data

    except httpx.TimeoutException:
        log.error(f"CricAPI timeout on {endpoint}")
        return None
    except httpx.HTTPStatusError as e:
        log.error(f"CricAPI HTTP error: {e.response.status_code} on {endpoint}")
        return None
    except Exception as e:
        log.error(f"CricAPI unexpected error: {e}")
        return None


async def get_live_matches() -> list[dict]:
    """
    Fetch all currently live cricket matches.
    
    Returns:
        List of match dicts, or empty list on failure
    """
    data = await _cached_get("currentMatches")
    if not data:
        return []
    
    matches = data.get("data", [])
    
    # Filter to only matches that are actually live or recently completed
    live = [m for m in matches if m.get("matchStarted", False)]
    
    return live


async def get_match_by_team(team_name: str) -> Optional[dict]:
    """
    Find a live match for a specific team.
    Uses fuzzy matching on team names in match data.
    
    Args:
        team_name: Official team name (e.g., 'Chennai Super Kings')
    
    Returns:
        Match dict if found, None otherwise
    """
    matches = await get_live_matches()
    
    if not matches:
        return None

    team_lower = team_name.lower()
    
    for match in matches:
        # Check team names in match data
        teams = match.get("teams", [])
        team_info = match.get("teamInfo", [])
        name = match.get("name", "").lower()
        
        # Check in teams list
        for team in teams:
            if team_lower in team.lower() or team.lower() in team_lower:
                return match
        
        # Check in team info
        for info in team_info:
            t_name = info.get("name", "").lower()
            t_short = info.get("shortname", "").lower()
            if team_lower in t_name or t_name in team_lower:
                return match
            if t_short and (team_lower in t_short or t_short in team_lower):
                return match
        
        # Check in match name
        if team_lower in name:
            return match

    return None


async def get_player_stats(player_name: str) -> Optional[dict]:
    """
    Search for a player and return their stats.
    
    Args:
        player_name: Player name to search for
    
    Returns:
        Player data dict if found, None otherwise
    """
    # First, search for the player
    search_data = await _cached_get(
        "players", 
        params={"search": player_name},
        ttl=CACHE_TTL_PLAYER_STATS
    )
    
    if not search_data:
        return None

    players = search_data.get("data", [])
    if not players:
        log.info(f"No player found for: {player_name}")
        return None

    # Get the first matching player's ID
    player = players[0]
    player_id = player.get("id")
    
    if not player_id:
        return player  # Return basic info if no ID

    # Fetch detailed player info
    detail_data = await _cached_get(
        "players_info",
        params={"id": player_id},
        ttl=CACHE_TTL_PLAYER_STATS
    )
    
    if detail_data and detail_data.get("data"):
        return detail_data["data"]
    
    return player  # Fallback to basic search result


async def get_all_matches() -> list[dict]:
    """
    Fetch all current matches (live + upcoming + completed).
    
    Returns:
        List of all match dicts
    """
    data = await _cached_get("currentMatches")
    if not data:
        return []
    return data.get("data", [])
