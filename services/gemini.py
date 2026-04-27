"""
KhelBot Gemini Service — AI-powered Hinglish cricket commentary.
Uses Google Gemini 1.5 Flash for speed and generous free tier.
"""

import google.generativeai as genai
from typing import Optional

from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from utils.logger import setup_logger

log = setup_logger("gemini")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Model with KhelBot personality
_model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    generation_config={
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 700,
    }
)

# ── System Personality ────────────────────────────────────
SYSTEM_PERSONALITY = """You are KhelBot 🏏 — India ka apna cricket buddy!

RULES:
1. You speak in Hinglish (Hindi + English mix) naturally — like how Indian friends talk about cricket.
2. Use cricket slang, emojis, and be always enthusiastic.
3. You're opinionated but back it up with data when available.
4. You NEVER promote gambling — predictions are entertainment only.
5. Keep responses under 300 words. Be concise, fun, and insightful.
6. Use emojis liberally but tastefully — 🏏🔥💪🎯⚡🏆
7. Always respond in a way that makes the user feel like they're chatting with a knowledgeable cricket buddy.
8. When data is unavailable, be honest and say "Data nahi mila bhai" instead of making stuff up.
"""

# ── Hinglish Error Fallbacks ──────────────────────────────
FALLBACK_ERROR = "Arre yaar, AI buddy abhi thoda busy hai 😅 Thodi der mein try karo!"
FALLBACK_NO_DATA = "Bhai, data nahi mil raha abhi 🤷‍♂️ API wale chai break pe hain lagta hai!"


async def _generate(prompt: str) -> str:
    """
    Generate a response from Gemini with error handling.
    
    Args:
        prompt: Full prompt including context
    
    Returns:
        Generated text or fallback error message
    """
    try:
        full_prompt = f"{SYSTEM_PERSONALITY}\n\n{prompt}"
        response = await _model.generate_content_async(full_prompt)
        
        if response and response.text:
            return response.text.strip()
        
        log.warning("Gemini returned empty response")
        return FALLBACK_ERROR

    except Exception as e:
        log.error(f"Gemini generation error: {e}")
        return FALLBACK_ERROR


async def generate_live_context(match_data: dict) -> str:
    """
    Generate Hinglish commentary for a live match.
    Prompt 1 from spec — adds context, momentum analysis, and key moments.
    
    Args:
        match_data: Raw match data from CricAPI
    
    Returns:
        AI-generated match context in Hinglish
    """
    if not match_data:
        return FALLBACK_NO_DATA

    prompt = f"""Analyze this LIVE cricket match and give exciting Hinglish commentary:

MATCH DATA:
{_format_match_for_prompt(match_data)}

YOUR TASK:
1. Summarize the current match situation in 2-3 lines
2. Analyze the momentum — kaun haavi hai? (who's dominating?)
3. Highlight key moments or turning points
4. Give your take — kya lagta hai aage kya hoga? (what do you think will happen?)

Remember: Be enthusiastic, use Hinglish, and keep it under 250 words!"""

    return await _generate(prompt)


async def generate_prediction(team1: str, team2: str, match_data: dict = None) -> str:
    """
    Generate win probability prediction.
    Prompt 2 from spec — data-backed prediction with reasoning.
    
    Args:
        team1: First team name
        team2: Second team name  
        match_data: Optional current match data
    
    Returns:
        AI-generated prediction in Hinglish
    """
    match_context = ""
    if match_data:
        match_context = f"\nCURRENT MATCH DATA:\n{_format_match_for_prompt(match_data)}"

    prompt = f"""Predict the winner of this cricket match:

{team1} vs {team2}
{match_context}

YOUR TASK:
1. Give a WIN PROBABILITY percentage for each team (must add up to 100%)
2. List 3-4 KEY FACTORS affecting the prediction
3. Name the PLAYER TO WATCH from each team
4. Give your FINAL VERDICT — "Mera prediction hai..."

FORMAT:
🔮 Win Probability:
  {team1}: X%
  {team2}: Y%

Key Factors: (3-4 bullet points)
Players to Watch: (1 from each team)
Final Verdict: (Your confident Hinglish take)

Remember: This is ENTERTAINMENT ONLY, not betting advice!"""

    return await _generate(prompt)


async def generate_dream11(team1: str, team2: str, match_data: dict = None) -> str:
    """
    Generate Dream11 fantasy team suggestion.
    Prompt 3 from spec — full team with C/VC reasoning.
    
    Args:
        team1: First team name
        team2: Second team name
        match_data: Optional match data for context
    
    Returns:
        AI-generated Dream11 team in Hinglish
    """
    match_context = ""
    if match_data:
        match_context = f"\nMATCH DATA:\n{_format_match_for_prompt(match_data)}"

    prompt = f"""Suggest a Dream11 fantasy cricket team for:

{team1} vs {team2}
{match_context}

YOUR TASK — Create an 11-player Dream11 team:

1. Pick exactly 11 players:
   - 1-2 Wicketkeepers (WK)
   - 3-5 Batsmen (BAT)
   - 1-3 All-rounders (AR)
   - 3-5 Bowlers (BOWL)

2. For each player, mention:
   - Name + Role (WK/BAT/AR/BOWL)
   - Which team they play for

3. CAPTAIN (C) — explain WHY (2x points wala banda)
4. VICE-CAPTAIN (VC) — explain WHY (1.5x points)
5. RISK/DIFFERENTIAL PICK — one underrated player who could be a game changer

6. Give PROJECTED FANTASY POINTS RANGE for the team

FORMAT:
🏆 Dream11 Team: {team1} vs {team2}

WK: [names]
BAT: [names]
AR: [names]
BOWL: [names]

👑 Captain: [name] — [reason]
🥈 Vice-Captain: [name] — [reason]
🎲 Risk Pick: [name] — [reason]

📊 Projected Points: XX-XX

Remember: Hinglish mein bolo, and be confident in your picks!"""

    return await _generate(prompt)


async def generate_player_summary(player_name: str, stats_data: dict = None) -> str:
    """
    Generate an entertaining player summary in Hinglish.
    Prompt 4 from spec.
    
    Args:
        player_name: Player name
        stats_data: Optional player stats from CricAPI
    
    Returns:
        AI-generated player summary in Hinglish
    """
    stats_context = ""
    if stats_data:
        stats_context = f"\nPLAYER DATA:\n{str(stats_data)}"

    prompt = f"""Give an entertaining Hinglish summary of this cricket player:

PLAYER: {player_name}
{stats_context}

YOUR TASK:
1. Quick intro — kaun hai yeh banda? (who is this person?)
2. Key stats highlights — runs, wickets, best performances
3. Playing style — kaise khelte hain? (how do they play?)
4. Current form — abhi ka form kaisa hai?
5. Fun fact or iconic moment
6. Your verdict — "Mera take hai..."

Keep it under 200 words, entertaining, and in Hinglish!"""

    return await _generate(prompt)


def _format_match_for_prompt(match_data: dict) -> str:
    """Format match data into a clean string for Gemini prompts."""
    if not match_data:
        return "No match data available"

    parts = []
    
    name = match_data.get("name", "Unknown")
    parts.append(f"Match: {name}")
    
    status = match_data.get("status", "")
    if status:
        parts.append(f"Status: {status}")
    
    venue = match_data.get("venue", "")
    if venue:
        parts.append(f"Venue: {venue}")

    scores = match_data.get("score", [])
    if scores:
        parts.append("Scores:")
        for inning in scores:
            inning_name = inning.get("inning", "")
            runs = inning.get("r", 0)
            wickets = inning.get("w", 0)
            overs = inning.get("o", 0)
            parts.append(f"  {inning_name}: {runs}/{wickets} ({overs} overs)")

    teams = match_data.get("teams", [])
    if teams:
        parts.append(f"Teams: {' vs '.join(teams)}")

    return "\n".join(parts)
