"""
KhelBot NewsAPI Service — Curated cricket headlines.
Returns only headline + source + URL — never full article body (legal compliance).
"""

import hashlib
import httpx
from typing import Optional

from config.settings import NEWSAPI_KEY, NEWSAPI_BASE_URL, CACHE_TTL_NEWS
from services.cache import cache
from utils.logger import setup_logger

log = setup_logger("newsapi")

# HTTP client with timeout
_client = httpx.AsyncClient(timeout=10.0)


async def get_cricket_news(team_name: str = None, max_articles: int = 3) -> list[dict]:
    """
    Fetch top cricket/IPL news headlines, optionally filtered by team.
    
    Args:
        team_name: Optional team name to filter news
        max_articles: Maximum number of articles to return (default: 3)
    
    Returns:
        List of article dicts with title, source, and url
    """
    # Build search query
    query = "cricket IPL"
    if team_name:
        query = f"{team_name} cricket IPL"
    
    # Check cache
    cache_key = f"news:{hashlib.md5(query.encode()).hexdigest()[:8]}"
    cached = cache.get(cache_key)
    if cached is not None:
        log.debug(f"News cache HIT: {cache_key}")
        return cached[:max_articles]

    try:
        params = {
            "q": query,
            "apiKey": NEWSAPI_KEY,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": max_articles + 2,  # Fetch a couple extra in case of filtering
        }

        log.info(f"NewsAPI call: query='{query}'")
        response = await _client.get(f"{NEWSAPI_BASE_URL}/everything", params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "ok":
            log.warning(f"NewsAPI returned non-ok: {data.get('status')}")
            return []

        articles = data.get("articles", [])
        
        # Extract only what we need (title + source + URL — no body!)
        clean_articles = []
        for article in articles[:max_articles]:
            clean_articles.append({
                "title": article.get("title", "No title"),
                "source": article.get("source", {}),
                "url": article.get("url", ""),
                "publishedAt": article.get("publishedAt", ""),
            })

        # Cache the results
        cache.set(cache_key, clean_articles, CACHE_TTL_NEWS)
        log.debug(f"News cache SET: {cache_key} (TTL={CACHE_TTL_NEWS}s)")

        return clean_articles

    except httpx.TimeoutException:
        log.error("NewsAPI timeout")
        return []
    except httpx.HTTPStatusError as e:
        log.error(f"NewsAPI HTTP error: {e.response.status_code}")
        return []
    except Exception as e:
        log.error(f"NewsAPI unexpected error: {e}")
        return []
