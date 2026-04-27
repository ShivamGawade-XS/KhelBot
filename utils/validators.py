"""
KhelBot Validators — Team alias resolution and input sanitization.
Maps 40+ aliases (short names, nicknames, player names) → official IPL team names.
"""

import re
from typing import Optional


# ── Team Alias Map ────────────────────────────────────────
# Maps every known alias → canonical team name
TEAM_ALIASES: dict[str, str] = {
    # Chennai Super Kings
    "csk":          "Chennai Super Kings",
    "chennai":      "Chennai Super Kings",
    "super kings":  "Chennai Super Kings",
    "dhoni":        "Chennai Super Kings",
    "yellove":      "Chennai Super Kings",
    "mahi":         "Chennai Super Kings",
    "whistle podu": "Chennai Super Kings",
    
    # Mumbai Indians
    "mi":           "Mumbai Indians",
    "mumbai":       "Mumbai Indians",
    "rohit":        "Mumbai Indians",
    "paltan":       "Mumbai Indians",
    "mumbai indians": "Mumbai Indians",
    
    # Royal Challengers Bengaluru
    "rcb":          "Royal Challengers Bengaluru",
    "bengaluru":    "Royal Challengers Bengaluru",
    "bangalore":    "Royal Challengers Bengaluru",
    "kohli":        "Royal Challengers Bengaluru",
    "royal challengers": "Royal Challengers Bengaluru",
    "ee sala":      "Royal Challengers Bengaluru",
    
    # Kolkata Knight Riders
    "kkr":          "Kolkata Knight Riders",
    "kolkata":      "Kolkata Knight Riders",
    "knight riders": "Kolkata Knight Riders",
    "korbo lorbo":  "Kolkata Knight Riders",
    
    # Delhi Capitals
    "dc":           "Delhi Capitals",
    "delhi":        "Delhi Capitals",
    "capitals":     "Delhi Capitals",
    "delhi capitals": "Delhi Capitals",
    
    # Rajasthan Royals
    "rr":           "Rajasthan Royals",
    "rajasthan":    "Rajasthan Royals",
    "royals":       "Rajasthan Royals",
    "halla bol":    "Rajasthan Royals",
    
    # Sunrisers Hyderabad
    "srh":          "Sunrisers Hyderabad",
    "hyderabad":    "Sunrisers Hyderabad",
    "sunrisers":    "Sunrisers Hyderabad",
    "orange army":  "Sunrisers Hyderabad",
    
    # Punjab Kings
    "pbks":         "Punjab Kings",
    "punjab":       "Punjab Kings",
    "punjab kings": "Punjab Kings",
    "sadda punjab": "Punjab Kings",
    
    # Gujarat Titans
    "gt":           "Gujarat Titans",
    "gujarat":      "Gujarat Titans",
    "titans":       "Gujarat Titans",
    "aava de":      "Gujarat Titans",
    
    # Lucknow Super Giants
    "lsg":          "Lucknow Super Giants",
    "lucknow":      "Lucknow Super Giants",
    "super giants": "Lucknow Super Giants",
}


def extract_team_from_args(args: tuple | list) -> Optional[str]:
    """
    Parse user input and resolve team alias to official name.
    
    Args:
        args: Tuple/list of words from user command (e.g., ('rcb',) or ('mumbai', 'indians'))
    
    Returns:
        Official team name if found, None otherwise
    
    Examples:
        >>> extract_team_from_args(('rcb',))
        'Royal Challengers Bengaluru'
        >>> extract_team_from_args(('mumbai', 'indians'))
        'Mumbai Indians'
        >>> extract_team_from_args(('xyz',))
        None
    """
    if not args:
        return None
    
    # Join all args into one string, lowercase
    raw_input = " ".join(args).strip().lower()
    
    if not raw_input:
        return None
    
    # Direct alias lookup
    if raw_input in TEAM_ALIASES:
        return TEAM_ALIASES[raw_input]
    
    # Try matching with individual words (e.g., user sends just "csk")
    for word in raw_input.split():
        if word in TEAM_ALIASES:
            return TEAM_ALIASES[word]
    
    # Fuzzy substring match — check if any alias is contained in input
    for alias, team in TEAM_ALIASES.items():
        if alias in raw_input or raw_input in alias:
            return team
    
    return None


def extract_two_teams(args: tuple | list) -> tuple[Optional[str], Optional[str]]:
    """
    Parse user input for two teams separated by 'vs', 'v', or 'and'.
    
    Args:
        args: Tuple/list of words (e.g., ('csk', 'vs', 'mi'))
    
    Returns:
        Tuple of (team1, team2) — either can be None if not found
    
    Examples:
        >>> extract_two_teams(('csk', 'vs', 'mi'))
        ('Chennai Super Kings', 'Mumbai Indians')
    """
    if not args:
        return None, None
    
    raw_input = " ".join(args).strip().lower()
    
    # Split on common separators
    for separator in [" vs ", " v ", " and ", " versus "]:
        if separator in raw_input:
            parts = raw_input.split(separator, 1)
            team1 = extract_team_from_args(parts[0].strip().split())
            team2 = extract_team_from_args(parts[1].strip().split())
            return team1, team2
    
    return None, None


def sanitize_input(text: str, max_length: int = 200) -> str:
    """
    Sanitize user input — strip dangerous characters and limit length.
    
    Args:
        text: Raw user input
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potential injection characters
    sanitized = re.sub(r'[<>{}[\]\\`]', '', text)
    
    # Limit length
    sanitized = sanitized[:max_length].strip()
    
    return sanitized


def get_all_team_names() -> list[str]:
    """Return a sorted list of all unique official team names."""
    return sorted(set(TEAM_ALIASES.values()))


def get_aliases_for_team(team_name: str) -> list[str]:
    """Return all aliases for a given official team name."""
    return [alias for alias, name in TEAM_ALIASES.items() if name == team_name]
