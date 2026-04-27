"""
KhelBot /predict Handler — AI-powered match win predictions.
Always includes a mandatory disclaimer.
"""

from telegram import Update
from telegram.ext import ContextTypes

from services.cricapi import get_match_by_team
from services.gemini import generate_prediction
from database.users import update_user_query_count
from database.predictions import log_prediction
from utils.validators import extract_two_teams, extract_team_from_args
from utils.logger import setup_logger

log = setup_logger("handler.predict")

DISCLAIMER = (
    "\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚠️ **Disclaimer:** Yeh prediction sirf entertainment ke liye hai. "
    "Betting ya gambling mat karo! Cricket enjoy karo, responsibly! 🏏"
)


async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /predict command — generate win prediction."""
    user = update.effective_user
    args = context.args

    log.info(f"/predict from {user.id} | args: {args}")

    # Track query
    try:
        update_user_query_count(user.id)
    except Exception:
        pass

    if not args:
        await update.message.reply_text(
            "🔮 Kaunsi teams ka prediction chahiye?\n\n"
            "Usage: `/predict <team1> vs <team2>`\n"
            "Example: `/predict csk vs mi`",
            parse_mode="Markdown"
        )
        return

    # Parse two teams
    team1, team2 = extract_two_teams(args)

    if not team1 or not team2:
        # Maybe user gave just one team
        single_team = extract_team_from_args(args)
        if single_team:
            await update.message.reply_text(
                f"🤔 {single_team} ka prediction chahiye, but dusri team bhi batao!\n\n"
                f"Usage: `/predict {single_team} vs <team2>`",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "🤔 Teams samajh nahi aaye bhai!\n\n"
                "Usage: `/predict csk vs mi`\n"
                "Teams: CSK, MI, RCB, KKR, DC, RR, SRH, PBKS, GT, LSG",
                parse_mode="Markdown"
            )
        return

    # Send loading message
    await update.message.reply_text(
        f"🔮 {team1} vs {team2} ka prediction generate kar raha hoon... ⏳"
    )

    # Try to get live match data for context
    match_data = await get_match_by_team(team1)
    if not match_data:
        match_data = await get_match_by_team(team2)

    # Generate prediction
    prediction = await generate_prediction(team1, team2, match_data)

    # Log prediction to database
    try:
        match_id = match_data.get("id", f"{team1}_vs_{team2}") if match_data else f"{team1}_vs_{team2}"
        match_name = f"{team1} vs {team2}"
        
        # Try to extract confidence from the AI response
        confidence = 50.0  # Default
        log_prediction(
            match_id=str(match_id),
            match_name=match_name,
            predicted_winner=team1,  # AI's pick (simplified)
            confidence_pct=confidence,
        )
    except Exception as e:
        log.error(f"Failed to log prediction: {e}")

    # Send with disclaimer
    response = f"{prediction}{DISCLAIMER}"

    if len(response) > 4000:
        await update.message.reply_text(prediction, parse_mode="Markdown")
        await update.message.reply_text(DISCLAIMER, parse_mode="Markdown")
    else:
        await update.message.reply_text(response, parse_mode="Markdown")
