"""
KhelBot AI Service — AI-powered Hinglish cricket commentary.
Uses Meta Llama 3 via Groq for blazing speed and free tier.
"""

import json
from groq import AsyncGroq
from typing import Optional

from config.settings import GROQ_API_KEY, GROQ_MODEL
from utils.logger import setup_logger

log = setup_logger("ai_service")

# Configure Groq
_client = AsyncGroq(api_key=GROQ_API_KEY)

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
10. When LIVE WEB SEARCH RESULTS are provided, ALWAYS use them as your primary source of truth. Base your answer on the search results, not your training data. Cite specific facts from the search results.
11. Today's date is provided in the prompt. Use it to understand what is "current" and "recent".
"""

# ── Hinglish Error Fallbacks ──────────────────────────────
FALLBACK_ERROR = "Arre yaar, AI buddy abhi thoda busy hai 😅 Thodi der mein try karo!"
FALLBACK_NO_DATA = "Bhai, data nahi mil raha abhi 🤷‍♂️ API wale chai break pe hain lagta hai!"


async def _generate(prompt: str) -> str:
    """Generate a response from Groq with error handling."""
    try:
        response = await _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PERSONALITY},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=700,
            top_p=0.95
        )
        
        if response and response.choices:
            return response.choices[0].message.content.strip()
        
        log.warning("Groq returned empty response")
        return FALLBACK_ERROR

    except Exception as e:
        log.error(f"Groq generation error: {e}")
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


async def generate_prediction(team1: str, team2: str, match_data: dict = None, live_context: str = "") -> str:
    """Generate win probability prediction with live web data."""
    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")
    
    match_context = ""
    if match_data:
        match_context = f"\nCURRENT MATCH DATA:\n{_format_match_for_prompt(match_data)}"
    
    web_section = ""
    if live_context:
        web_section = f"""\n\n--- LIVE WEB SEARCH (recent form, injuries, pitch reports) ---
{live_context}
--- END ---\n"""

    prompt = f"""Predict the winner of this cricket match:

TODAY'S DATE: {today}
{team1} vs {team2}
{match_context}
{web_section}
YOUR TASK:
1. Give a WIN PROBABILITY percentage for each team (must add up to 100%)
2. List 3-4 KEY FACTORS — use REAL recent form data from search results
3. Mention any injuries, pitch conditions, weather from search results
4. Name the PLAYER TO WATCH from each team based on CURRENT form
5. Give your FINAL VERDICT — "Mera prediction hai..."

FORMAT:
🔮 Win Probability:
  {team1}: X%
  {team2}: Y%

📊 Key Factors: (3-4 bullet points with real data)
🚑 Team News: (injuries/changes if found)
⭐ Players to Watch: (1 from each team)
🏏 Final Verdict: (Your confident Hinglish take)

Remember: This is ENTERTAINMENT ONLY, not betting advice!"""

    return await _generate(prompt)


async def generate_dream11(team1: str, team2: str, match_data: dict = None, live_context: str = "") -> str:
    """Generate Dream11 fantasy team suggestion with live web data."""
    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")
    
    match_context = ""
    if match_data:
        match_context = f"\nMATCH DATA:\n{_format_match_for_prompt(match_data)}"
    
    web_section = ""
    if live_context:
        web_section = f"""\n\n--- LIVE WEB SEARCH (squads, form, injuries, pitch) ---
{live_context}
--- END ---\n"""

    prompt = f"""Suggest a Dream11 fantasy cricket team for:

TODAY'S DATE: {today}
{team1} vs {team2}
{match_context}
{web_section}
YOUR TASK — Create an 11-player Dream11 team using REAL current squad data:

1. Pick exactly 11 players from the ACTUAL current squads (use search results!):
   - 1-2 Wicketkeepers (WK)
   - 3-5 Batsmen (BAT)
   - 1-3 All-rounders (AR)
   - 3-5 Bowlers (BOWL)

2. For each player, mention:
   - Name + Role (WK/BAT/AR/BOWL)
   - Which team they play for
   - Current form (runs/wickets in recent matches from search results)

3. CAPTAIN (C) — explain WHY with recent stats (2x points wala banda)
4. VICE-CAPTAIN (VC) — explain WHY with recent stats (1.5x points)
5. RISK/DIFFERENTIAL PICK — one underrated player who is in form

6. Give PROJECTED FANTASY POINTS RANGE for the team
7. 🏟️ PITCH REPORT — if available from search results

FORMAT:
🏆 Dream11 Team: {team1} vs {team2}

🏟️ Pitch: [conditions if known]

WK: [names + recent form]
BAT: [names + recent form]
AR: [names + recent form]
BOWL: [names + recent form]

👑 Captain: [name] — [reason with stats]
🥈 Vice-Captain: [name] — [reason with stats]
🎲 Risk Pick: [name] — [why this pick]

📊 Projected Points: XX-XX

Remember: Hinglish mein bolo, use REAL data, and be confident!"""

    return await _generate(prompt)


async def generate_player_summary(player_name: str, stats_data: dict = None, live_context: str = "") -> str:
    """Generate an entertaining player summary with live web data."""
    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")
    
    stats_context = ""
    if stats_data:
        stats_context = f"\nPLAYER DATA:\n{str(stats_data)}"
    
    web_section = ""
    if live_context:
        web_section = f"""\n\n--- LIVE WEB SEARCH (latest news, recent performances) ---
{live_context}
--- END ---\n"""

    prompt = f"""Give an entertaining Hinglish summary of this cricket player:

TODAY'S DATE: {today}
PLAYER: {player_name}
{stats_context}
{web_section}
YOUR TASK:
1. Quick intro — kaun hai yeh banda?
2. Key stats highlights — runs, wickets, best performances (use search data!)
3. Playing style — kaise khelte hain?
4. CURRENT FORM — abhi ka form kaisa hai? Use RECENT match data from search!
5. Latest news — any injuries, milestones, controversies?
6. Fun fact or iconic moment
7. Your verdict — "Mera take hai..."

Keep it under 250 words, entertaining, and in Hinglish!"""

    return await _generate(prompt)


async def generate_h2h_analysis(team1: str, team2: str, match_data: dict = None, live_context: str = "") -> str:
    """Generate head-to-head analysis with live web data."""
    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")
    
    match_context = ""
    if match_data:
        match_context = f"\nCURRENT MATCH DATA:\n{_format_match_for_prompt(match_data)}"
    
    web_section = ""
    if live_context:
        web_section = f"""\n\n--- LIVE WEB SEARCH (recent results, H2H stats, form) ---
{live_context}
--- END ---\n"""

    prompt = f"""Give a detailed HEAD-TO-HEAD analysis for:

TODAY'S DATE: {today}
⚔️ {team1} vs {team2}
{match_context}
{web_section}
YOUR TASK:
1. Historical H2H record — kitne matches, kaun kitne jeeta? (use REAL stats from search!)
2. Recent form — IPL 2026 mein kaun better? Use ACTUAL recent results!
3. Key player battles — konse players ka matchup exciting hai?
4. Venue factor — agar venue pata hai toh
5. X-factor — kaun sa player match winner ban sakta hai?
6. Your verdict — "Mera take: is baar ____"

FORMAT:
⚔️ {team1} vs {team2} — Head to Head

📊 Overall Record: [summary with real numbers]
🔥 Recent Form: [IPL 2026 form with real results]
🎯 Key Battles: [matchups]
🏟️ Venue Factor: [if applicable]
⚡ X-Factor: [game changer]
🏏 Verdict: [your confident take]

Keep it under 300 words, exciting Hinglish!"""

    return await _generate(prompt)


async def generate_player_comparison(player1: str, player2: str, stats1: dict = None, stats2: dict = None, live_context: str = "") -> str:
    """Generate side-by-side player comparison with live web data."""
    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")
    
    context1 = f"\n{player1} DATA:\n{str(stats1)}" if stats1 else ""
    context2 = f"\n{player2} DATA:\n{str(stats2)}" if stats2 else ""
    
    web_section = ""
    if live_context:
        web_section = f"""\n\n--- LIVE WEB SEARCH (recent performances, IPL 2026 stats) ---
{live_context}
--- END ---\n"""

    prompt = f"""Compare these two cricket players side-by-side:

TODAY'S DATE: {today}
🔄 {player1.title()} vs {player2.title()}
{context1}
{context2}
{web_section}
YOUR TASK:
1. Quick intro of both players
2. Stats comparison — use REAL IPL 2026 stats from search results!
3. Playing style comparison — kaise different hain dono?
4. Big match performance — pressure mein kaun better?
5. Current form — abhi kaun zyada on fire? (use RECENT match data!)
6. Fun fact about their rivalry/friendship
7. VERDICT — "Winner hai..." (pick one with reasoning)

FORMAT:
🔄 {player1.title()} vs {player2.title()}

👤 Player 1: [quick intro]
👤 Player 2: [quick intro]

📊 Stats Face-Off (IPL 2026):
  [comparison with real numbers]

🎯 Style: [comparison]
💪 Pressure: [who's better]
🔥 Current Form: [who's hotter with real data]
🏆 Verdict: [pick winner boldly]

Keep it under 300 words, Hinglish, and be bold!"""

    return await _generate(prompt)


async def generate_freeform_answer(question: str, live_context: str = "") -> str:
    """Generate a free-form answer to any cricket question, optionally with live web context."""
    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")
    
    web_section = ""
    if live_context:
        web_section = f"""\n\n--- LIVE WEB SEARCH RESULTS (use these as PRIMARY source!) ---
{live_context}
--- END OF SEARCH RESULTS ---\n"""
    
    prompt = f"""A cricket fan is asking you a question. Answer it like a knowledgeable Hinglish cricket buddy.

TODAY'S DATE: {today}

QUESTION: {question}
{web_section}
YOUR TASK:
1. Answer the question accurately — if web search results are provided, USE THEM as your primary source
2. Include specific details, dates, names, and numbers from the search results
3. Add interesting facts or context if relevant
4. If it's about schedules/scores/news, provide the LATEST info from search results
5. Keep the Hinglish tone — fun, casual, but informative
6. If the question is NOT about cricket/sports, politely redirect: "Bhai main cricket expert hoon, cricket ke baare mein poocho!"
7. NEVER say "data nahi mila" or "schedule announce nahi hua" if search results clearly contain the answer!

Keep it under 300 words!"""

    return await _generate(prompt)


async def generate_quiz_question() -> Optional[dict]:
    """Generate a cricket trivia question with 4 options using Groq JSON mode."""
    prompt = """Generate a cricket trivia question for an Indian cricket fan.

REQUIREMENTS:
1. Question should be about IPL, Indian cricket, or international cricket
2. 4 options (A, B, C, D)
3. Only ONE correct answer
4. Mix of easy and medium difficulty
5. Include a brief explanation for the correct answer

RESPOND IN EXACTLY THIS JSON FORMAT:
{"question": "your question here?", "options": ["Option A", "Option B", "Option C", "Option D"], "correct": 0, "explanation": "Brief explanation in Hinglish"}

Where "correct" is the index (0-3) of the correct option.
IMPORTANT: Respond ONLY with valid JSON."""

    try:
        response = await _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PERSONALITY},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        if response and response.choices:
            text = response.choices[0].message.content.strip()
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


async def generate_funfact() -> str:
    """Generate a random cricket fun fact."""
    prompt = """Tell me a RANDOM, SURPRISING cricket fun fact that most fans don't know!

YOUR TASK:
1. Pick a random, lesser-known cricket fact
2. It can be about any era — old or new
3. Make it genuinely surprising ("Arre sach mein?!" type)
4. Add context — why is this interesting?
5. End with a fun one-liner

FORMAT:
🤯 Cricket Ka Fun Fact

[Your surprising fact with context]

💡 [One-liner takeaway]

Keep it under 150 words, Hinglish, and make it WOW-worthy!
IMPORTANT: Pick a DIFFERENT fact every time — don't repeat!"""

    return await _generate(prompt)


async def generate_match_recap(match_data: dict) -> str:
    """Generate an AI match recap/summary."""
    if not match_data:
        return FALLBACK_NO_DATA

    prompt = f"""Give a complete match recap in Hinglish:

MATCH DATA:
{_format_match_for_prompt(match_data)}

YOUR TASK:
1. Match summary — kya hua match mein? (2-3 lines)
2. Key performances — kaun chamka? (top 2-3 players)
3. Turning point — match kab palti?
4. Best moments — crowd ko kya pasand aaya?
5. Final verdict — "Is match ka hero hai..."

FORMAT:
📝 Match Recap

🏏 Summary: [what happened]
⭐ Key Performers: [top players]
🔄 Turning Point: [when match changed]
🎯 Best Moments: [highlights]
🏆 Hero: [match winner]

Keep it under 250 words, exciting Hinglish!"""

    return await _generate(prompt)


async def generate_trending(headlines: list = None, live_context: str = "") -> str:
    """Generate trending cricket topics analysis."""
    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")
    
    context = ""
    if headlines:
        context = "\nCURRENT HEADLINES:\n" + "\n".join(f"- {h}" for h in headlines if h)
    
    web_section = ""
    if live_context:
        web_section = f"""\n\n--- LIVE WEB SEARCH RESULTS ---
{live_context}
--- END OF SEARCH RESULTS ---\n"""

    prompt = f"""What's TRENDING in cricket right now? Analyze the current cricket scene:

TODAY'S DATE: {today}
{context}
{web_section}
YOUR TASK:
1. Top 3-5 trending topics in cricket right now based on the LIVE search results and headlines
2. For each topic — ek line summary + why it matters
3. Hot takes — tumhara opinion on each
4. One bold prediction about what will happen next

FORMAT:
🔥 Cricket Trending

1. [Topic] — [why it's hot]
   💭 KhelBot ka take: [opinion]

2. [Topic] — [why it's hot]
   💭 KhelBot ka take: [opinion]

[... more topics]

🎯 Bold Prediction: [your prediction]

Keep it under 300 words, Hinglish, entertaining!"""

    return await _generate(prompt)


def _format_match_for_prompt(match_data: dict) -> str:
    """Format match data into a clean string for AI prompts."""
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
