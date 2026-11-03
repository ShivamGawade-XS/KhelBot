"""
KhelBot /predict Handler — AI-powered match win predictions with live context.
Extracts true predicted winner and confidence, and logs non-blockingly to database.
Always includes a mandatory responsible gaming disclaimer.
"""

import re
from telegram import Update
from telegram.ext import ContextTypes

from services.cricapi import get_match_by_team
from services.gemini import generate_prediction
from database.users import async_update_user_query_count
from database.predictions import async_log_prediction
from utils.validators import extract_two_teams, extract_team_from_args
from utils.rate_limiter import rate_limiter
from utils.reply import safe_reply
from utils.logger import setup_logger

log = setup_logger("handler.predict")

DISCLAIMER = (
    "\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚠️ **Disclaimer:** Yeh prediction sirf entertainment ke liye hai. "
    "Betting ya gambling mat karo! Cricket enjoy karo, responsibly! 🏏"
)


def _parse_winner_and_confidence(prediction_text: str, team1: str, team2: str) -> tuple[str, float]:
    """
    Parse the predicted winner and confidence percentage from the LLM text.
    Returns (predicted_winner, confidence_pct).
    """
    pct1, pct2 = 50.0, 50.0
    
    # Try finding lines like: "TeamName: 65%" or "65% - TeamName"
    lines = prediction_text.splitlines()
    for line in lines:
        line_clean = line.strip().lower()
        if team1.lower() in line_clean:
            match = re.search(r'(\d{1,3})\s*%', line_clean)
            if match:
                try:
                    pct1 = float(match.group(1))
                except ValueError:
                    pass
        if team2.lower() in line_clean:
            match = re.search(r'(\d{1,3})\s*%', line_clean)
            if match:
                try:
                    pct2 = float(match.group(1))
                except ValueError:
                    pass

    if pct1 != pct2:
        if pct1 > pct2:
            return team1, pct1
        else:
            return team2, pct2

    # Fallback: check Final Verdict section for team name mentions
    verdict_section = ""
    if "verdict" in prediction_text.lower():
        verdict_section = prediction_text.lower().split("verdict")[-1]

    t1_in_verdict = team1.lower() in verdict_section
    t2_in_verdict = team2.lower() in verdict_section

    if t2_in_verdict and not t1_in_verdict:
        return team2, 55.0
    if t1_in_verdict and not t2_in_verdict:
        return team1, 55.0

    return team1, 50.0


async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /predict command — generate win prediction."""
    user = update.effective_user
    args = context.args

    if not user:
        return

    # Check rate limiter
    allowed, block_msg = rate_limiter.check(user.id)
    if not allowed:
        await safe_reply(update, block_msg)
        return

    log.info(f"/predict from {user.id} | args: {args}")
    await async_update_user_query_count(user.id)

    if not args:
        await safe_reply(update, "🔮 Kaunsi teams ka prediction chahiye?\n\n"
            "Usage: `/predict <team1> vs <team2>`\n"
            "Example: `/predict csk vs mi`",
            parse_mode="Markdown")
        return

    team1, team2 = extract_two_teams(args)

    if not team1 or not team2:
        single_team = extract_team_from_args(args)
        if single_team:
            await safe_reply(update, 
                f"🤔 {single_team} ka prediction chahiye, but dusri team bhi batao!\n\n"
                f"Usage: `/predict {single_team} vs <team2>`",
                parse_mode="Markdown"
            )
        else:
            await safe_reply(update, 
                "🤔 Teams samajh nahi aaye bhai!\n\n"
                "Usage: `/predict csk vs mi`\n"
                "Teams: CSK, MI, RCB, KKR, DC, RR, SRH, PBKS, GT, LSG",
                parse_mode="Markdown"
            )
        return

    await safe_reply(update, f"🔮 {team1} vs {team2} ka prediction generate kar raha hoon... 🔍🧠")

    # Search the web for latest form, injuries, pitch reports
    from services.web_search import search_match_info
    live_context = await search_match_info(team1, team2)

    match_data = await get_match_by_team(team1)
    if not match_data:
        match_data = await get_match_by_team(team2)

    prediction = await generate_prediction(team1, team2, match_data, live_context=live_context)

    # Extract true winner and confidence percentage
    winner, confidence = _parse_winner_and_confidence(prediction, team1, team2)

    match_id = match_data.get("id", f"{team1}_vs_{team2}") if match_data else f"{team1}_vs_{team2}"
    await async_log_prediction(
        match_id=str(match_id),
        match_name=f"{team1} vs {team2}",
        predicted_winner=winner,
        confidence_pct=confidence,
    )

    response = f"{prediction}{DISCLAIMER}"
    await safe_reply(update, response, parse_mode="Markdown")
