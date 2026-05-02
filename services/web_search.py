"""
KhelBot Web Search Service — Real-time internet search for live cricket data.
Uses DuckDuckGo Search (ddgs) for free, unlimited web queries.
"""

import asyncio
from typing import Optional
from utils.logger import setup_logger

log = setup_logger("web_search")


async def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web for a cricket-related query and return formatted context.
    Runs the synchronous DDGS in a thread to keep the bot async.
    """
    try:
        # Run synchronous ddgs search in a thread pool
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, _sync_search, query, max_results)

        if not results:
            log.warning(f"No web results for: {query}")
            return ""

        # Format results into a clean context block
        context_parts = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "").strip()
            body = r.get("body", "").strip()
            href = r.get("href", "")
            if title and body:
                context_parts.append(f"{i}. {title}\n   {body}\n   Source: {href}")

        if not context_parts:
            return ""

        context = "\n\n".join(context_parts)
        log.info(f"Web search for '{query[:40]}...' returned {len(context_parts)} results")
        return context

    except Exception as e:
        log.error(f"Web search error: {e}")
        return ""


def _sync_search(query: str, max_results: int) -> list:
    """Synchronous wrapper for ddgs search."""
    try:
        from ddgs import DDGS
        results = DDGS().text(
            keywords=f"{query} cricket",
            max_results=max_results,
            region="in-en"
        )
        return results
    except Exception as e:
        log.error(f"DDGS search error: {e}")
        return []


async def search_cricket_news(topic: str = "cricket", max_results: int = 5) -> str:
    """Search for latest cricket news headlines."""
    return await search_web(f"{topic} latest news today 2026", max_results=max_results)


async def search_ipl_info(query: str) -> str:
    """Search specifically for IPL-related information."""
    return await search_web(f"IPL 2026 {query}", max_results=5)


async def search_player_info(player_name: str) -> str:
    """Search for latest info about a specific cricket player."""
    return await search_web(f"{player_name} cricket 2026 latest", max_results=4)


async def search_match_info(team1: str, team2: str = "") -> str:
    """Search for latest match info between teams."""
    if team2:
        return await search_web(f"{team1} vs {team2} cricket match 2026", max_results=4)
    return await search_web(f"{team1} cricket match latest 2026", max_results=4)
