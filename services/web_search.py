"""
KhelBot Web Search Service — Real-time internet search for live cricket data.
Uses DuckDuckGo Search (ddgs) with multi-level TTL caching and error resilience.
"""

import hashlib
import asyncio
from typing import Optional, List
from services.cache import cache
from utils.logger import setup_logger

log = setup_logger("web_search")

SEARCH_CACHE_TTL = 900  # 15 minutes cache for web queries


def _cache_key(query: str) -> str:
    hash_str = hashlib.md5(query.strip().lower().encode()).hexdigest()[:10]
    return f"search:{hash_str}"


async def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web for a cricket query with TTL caching.
    Runs synchronous search in a thread to keep the asyncio event loop responsive.
    """
    clean_query = query.strip()
    if not clean_query:
        return ""

    key = _cache_key(clean_query)
    cached = cache.get(key)
    if cached is not None:
        log.debug(f"Search cache HIT for: '{clean_query[:35]}...'")
        return cached

    try:
        loop = asyncio.get_running_loop()
        results = await asyncio.wait_for(
            loop.run_in_executor(None, _sync_search, clean_query, max_results),
            timeout=8.0
        )

        if not results:
            log.warning(f"No web results returned for: '{clean_query[:35]}...'")
            return ""

        context_parts = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "").strip()
            body = r.get("body", "").strip()
            href = r.get("href", "")
            if title and body:
                context_parts.append(f"{i}. {title}\n   {body}\n   Source: {href}")

        context = "\n\n".join(context_parts)
        if context:
            cache.set(key, context, ttl=SEARCH_CACHE_TTL)
            log.info(f"Web search for '{clean_query[:35]}...' returned {len(context_parts)} results (cached)")

        return context
    except asyncio.TimeoutError:
        log.warning(f"Web search timed out for: '{clean_query[:35]}...'")
        return ""
    except Exception as e:
        log.error(f"Web search unexpected error: {e}")
        return ""


def _sync_search(query: str, max_results: int) -> list:
    """Synchronous wrapper for ddgs search with fallback."""
    try:
        from ddgs import DDGS
        # Append 'cricket' keyword if not present to ensure sports relevance
        search_term = query if "cricket" in query.lower() or "ipl" in query.lower() else f"{query} cricket"
        results = DDGS().text(
            query=search_term,
            max_results=max_results
        )
        return list(results) if results else []
    except Exception as e:
        log.warning(f"DDGS search execution failed: {e}")
        return []


async def search_cricket_news(topic: str = "cricket", max_results: int = 5) -> str:
    """Search for latest cricket news headlines."""
    return await search_web(f"{topic} latest news today 2026", max_results=max_results)


async def search_ipl_info(query: str) -> str:
    """Search specifically for IPL-related information."""
    return await search_web(f"IPL 2026 {query}", max_results=5)


async def search_player_info(player_name: str) -> str:
    """Search for latest info about a specific cricket player."""
    return await search_web(f"{player_name} cricket 2026 latest news form", max_results=4)


async def search_match_info(team1: str, team2: str = "") -> str:
    """Search for latest match info between teams."""
    if team2:
        return await search_web(f"{team1} vs {team2} cricket match 2026", max_results=4)
    return await search_web(f"{team1} cricket match latest 2026", max_results=4)
