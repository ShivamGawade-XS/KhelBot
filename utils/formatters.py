"""
KhelBot Formatters — Transform raw API data into clean, readable text.
"""

from typing import Any


def format_score(match_data: dict) -> str:
    """
    Format CricAPI match data into a clean scorecard.
    
    Args:
        match_data: Raw match data from CricAPI
    
    Returns:
        Formatted scorecard string
    """
    if not match_data:
        return "❌ Match data unavailable."

    name = match_data.get("name", "Unknown Match")
    status = match_data.get("status", "Status unknown")
    match_type = match_data.get("matchType", "")
    venue = match_data.get("venue", "Unknown Venue")
    date = match_data.get("date", "")

    lines = [
        f"🏏 **{name}**",
        f"📍 {venue}",
    ]

    if date:
        lines.append(f"📅 {date}")

    if match_type:
        lines.append(f"🏷️ {match_type.upper()}")

    # Score lines
    scores = match_data.get("score", [])
    if scores:
        lines.append("")
        lines.append("📊 **Scorecard:**")
        for inning in scores:
            inning_name = inning.get("inning", "")
            runs = inning.get("r", 0)
            wickets = inning.get("w", 0)
            overs = inning.get("o", 0)
            lines.append(f"  • {inning_name}: **{runs}/{wickets}** ({overs} ov)")

    lines.append("")
    lines.append(f"📌 {status}")

    return "\n".join(lines)


def format_news_list(articles: list[dict]) -> str:
    """
    Format NewsAPI articles into a numbered headline list.
    Only shows headline + source + URL — never full article body.
    
    Args:
        articles: List of article dicts from NewsAPI
    
    Returns:
        Formatted news string
    """
    if not articles:
        return "📰 Abhi koi cricket news nahi mili. Thodi der mein try karo!"

    lines = ["📰 **Top Cricket Headlines:**", ""]

    for i, article in enumerate(articles[:5], 1):
        title = article.get("title", "No title")
        source = article.get("source", {}).get("name", "Unknown")
        url = article.get("url", "")

        lines.append(f"**{i}.** {title}")
        lines.append(f"   📡 _{source}_")
        if url:
            lines.append(f"   🔗 [Read more]({url})")
        lines.append("")

    return "\n".join(lines)


def format_player_stats(player_data: dict) -> str:
    """
    Format CricAPI player data into a readable stats card.
    
    Args:
        player_data: Raw player data from CricAPI
    
    Returns:
        Formatted player stats string
    """
    if not player_data:
        return "❌ Player data unavailable."

    name = player_data.get("name", "Unknown Player")
    country = player_data.get("country", "Unknown")
    role = player_data.get("role", "Unknown")
    batting_style = player_data.get("battingStyle", "N/A")
    bowling_style = player_data.get("bowlingStyle", "N/A")
    dob = player_data.get("dateOfBirth", "N/A")
    place_of_birth = player_data.get("placeOfBirth", "N/A")

    lines = [
        f"🏏 **{name}**",
        f"🇮🇳 {country} | {role}",
        "",
        f"🏏 Batting: {batting_style}",
        f"🎳 Bowling: {bowling_style}",
        f"🎂 Born: {dob}",
        f"📍 {place_of_birth}",
    ]

    # Stats sections if available
    stats = player_data.get("stats", [])
    if stats:
        lines.append("")
        lines.append("📊 **Career Stats:**")
        for stat in stats:
            fn = stat.get("fn", "")  # format name (e.g., "test", "odi", "t20i")
            matchtype = stat.get("matchtype", "")
            stat_lines = []
            
            if stat.get("mat"):
                stat_lines.append(f"Matches: {stat['mat']}")
            if stat.get("runs"):
                stat_lines.append(f"Runs: {stat['runs']}")
            if stat.get("wkts"):
                stat_lines.append(f"Wickets: {stat['wkts']}")
            if stat.get("avg"):
                stat_lines.append(f"Avg: {stat['avg']}")
            if stat.get("sr"):
                stat_lines.append(f"SR: {stat['sr']}")
            
            if stat_lines:
                label = matchtype or fn or "Overall"
                lines.append(f"\n  📋 **{label.upper()}**")
                for sl in stat_lines:
                    lines.append(f"    • {sl}")

    return "\n".join(lines)


def format_match_list(matches: list[dict]) -> str:
    """
    Format a list of matches into a simple overview.
    
    Args:
        matches: List of match dicts from CricAPI
    
    Returns:
        Formatted match list string
    """
    if not matches:
        return "🏏 Abhi koi live match nahi chal raha!"

    lines = ["🏏 **Live Matches:**", ""]

    for i, match in enumerate(matches[:10], 1):
        name = match.get("name", "Unknown")
        status = match.get("status", "")
        lines.append(f"**{i}.** {name}")
        if status:
            lines.append(f"   📌 {status}")
        lines.append("")

    return "\n".join(lines)
