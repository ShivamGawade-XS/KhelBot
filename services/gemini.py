"""
KhelBot Gemini Service — AI-powered Hinglish cricket commentary.
Uses Google Gemini 2.5 Flash for speed and generous free tier.
"""

import json
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
9. IMPORTANT: Do NOT use markdown special characters like * or _ in your responses. Use plain text with emojis for formatting.
"""

# ── Hinglish Error Fallbacks ──────────────────────────────
FALLBACK_ERROR = "Arre yaar, AI buddy abhi thoda busy hai 😅 Thodi der mein try karo!"
FALLBACK_NO_DATA = "Bhai, data nahi mil raha abhi 🤷‍♂️ API wale chai break pe hain lagta hai!"


async def _generate(prompt: str) -> str:
    """Generate a response from Gemini with error handling."""
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
    """Generate Hinglish commentary for a live match."""
    if not match_data:
        return FALLBACK_NO_DATA

    prompt = f"""Analyze this LIVE cricket match and give exciting Hinglish commentary:

MATCH DATA:
{_format_match_for_prompt(match_data)}

YOUR TASK:
1. Summarize the current match situation in 2-3 lines
2. Analyze the momentum — kaun haavi hai? (who's dominating?)
3. Highlight key moments or turning points
4. Give your take — kya lagta hai aage kya hoga?

Remember: Be enthusiastic, use Hinglish, and keep it under 250 words!"""

    return await _generate(prompt)


async def generate_prediction(team1: str, team2: str, match_data: dict = None) -> str:
    """Generate win probability prediction."""
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
    """Generate Dream11 fantasy team suggestion."""
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
5. RISK/DIFFERENTIAL PICK — one underrated player

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
    """Generate an entertaining player summary in Hinglish."""
    stats_context = ""
    if stats_data:
        stats_context = f"\nPLAYER DATA:\n{str(stats_data)}"

    prompt = f"""Give an entertaining Hinglish summary of this cricket player:

PLAYER: {player_name}
{stats_context}

YOUR TASK:
1. Quick intro — kaun hai yeh banda?
2. Key stats highlights — runs, wickets, best performances
3. Playing style — kaise khelte hain?
4. Current form — abhi ka form kaisa hai?
5. Fun fact or iconic moment
6. Your verdict — "Mera take hai..."

Keep it under 200 words, entertaining, and in Hinglish!"""

    return await _generate(prompt)


async def generate_h2h_analysis(team1: str, team2: str, match_data: dict = None) -> str:
    """Generate head-to-head analysis between two teams."""
    match_context = ""
    if match_data:
        match_context = f"\nCURRENT MATCH DATA:\n{_format_match_for_prompt(match_data)}"

    prompt = f"""Give a detailed HEAD-TO-HEAD analysis for:

⚔️ {team1} vs {team2}
{match_context}

YOUR TASK:
1. Historical H2H record — kitne matches, kaun kitne jeeta?
2. Recent form — last 5 matches mein kaun better?
3. Key player battles — konse players ka matchup exciting hai?
4. Venue factor — agar venue pata hai toh
5. X-factor — kaun sa player match winner ban sakta hai?
6. Your verdict — "Mera take: is baar ____"

FORMAT:
⚔️ {team1} vs {team2} — Head to Head

📊 Overall Record: [summary]
🔥 Recent Form: [analysis]
🎯 Key Battles: [matchups]
🏟️ Venue Factor: [if applicable]
⚡ X-Factor: [game changer]
🏏 Verdict: [your take]

Keep it under 300 words, exciting Hinglish!"""

    return await _generate(prompt)


async def generate_player_comparison(player1: str, player2: str, stats1: dict = None, stats2: dict = None) -> str:
    """Generate side-by-side player comparison."""
    context1 = f"\n{player1} DATA:\n{str(stats1)}" if stats1 else ""
    context2 = f"\n{player2} DATA:\n{str(stats2)}" if stats2 else ""

    prompt = f"""Compare these two cricket players side-by-side:

🔄 {player1.title()} vs {player2.title()}
{context1}
{context2}

YOUR TASK:
1. Quick intro of both players
2. Stats comparison — batting avg, SR, runs, wickets (whatever applies)
3. Playing style comparison — kaise different hain dono?
4. Big match performance — pressure mein kaun better?
5. Current form — abhi kaun zyada on fire?
6. Fun fact about their rivalry/friendship
7. VERDICT — "Winner hai..." (pick one with reasoning)

FORMAT:
🔄 {player1.title()} vs {player2.title()}

👤 Player 1: [quick intro]
👤 Player 2: [quick intro]

📊 Stats Face-Off:
  [comparison table/list]

🎯 Style: [comparison]
💪 Pressure: [who's better]
🔥 Current Form: [who's hotter]
🏆 Verdict: [pick winner]

Keep it under 300 words, Hinglish, and be bold with your verdict!"""

    return await _generate(prompt)


async def generate_freeform_answer(question: str) -> str:
    """Generate a free-form answer to any cricket question."""
    prompt = f"""A cricket fan is asking you a question. Answer it like a knowledgeable Hinglish cricket buddy:

QUESTION: {question}

YOUR TASK:
1. Answer the question accurately with cricket knowledge
2. Add interesting facts or context if relevant
3. If it's about records/stats, try to be as accurate as possible
4. If you're not sure about exact numbers, say so honestly
5. Keep the Hinglish tone — fun, casual, but informative
6. If the question is NOT about cricket/sports, politely redirect: "Bhai main cricket expert hoon, cricket ke baare mein poocho!"

Keep it under 250 words!"""

    return await _generate(prompt)


async def generate_quiz_question() -> Optional[dict]:
    """Generate a cricket trivia question with 4 options."""
    prompt = """Generate a cricket trivia question for an Indian cricket fan.

REQUIREMENTS:
1. Question should be about IPL, Indian cricket, or international cricket
2. 4 options (A, B, C, D)
3. Only ONE correct answer
4. Mix of easy and medium difficulty
5. Include a brief explanation for the correct answer

RESPOND IN EXACTLY THIS JSON FORMAT (no markdown, no extra text):
{"question": "your question here?", "options": ["Option A", "Option B", "Option C", "Option D"], "correct": 0, "explanation": "Brief explanation in Hinglish"}

Where "correct" is the index (0-3) of the correct option.
IMPORTANT: Respond ONLY with the JSON, nothing else!"""

    try:
        full_prompt = f"{SYSTEM_PERSONALITY}\n\n{prompt}"
        response = await _model.generate_content_async(full_prompt)
        
        if response and response.text:
            text = response.text.strip()
            # Clean up potential markdown formatting
            text = text.replace("```json", "").replace("```", "").strip()
            
            quiz_data = json.loads(text)
            
            # Validate structure
            if all(k in quiz_data for k in ["question", "options", "correct", "explanation"]):
                if isinstance(quiz_data["options"], list) and len(quiz_data["options"]) >= 4:
                    return quiz_data
            
            log.warning(f"Quiz data invalid structure: {quiz_data}")
            return None

    except json.JSONDecodeError as e:
        log.error(f"Quiz JSON parse error: {e}")
        return None
    except Exception as e:
        log.error(f"Quiz generation error: {e}")
        return None


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
