"""
KhelBot Predictions Database — Log and track prediction accuracy.
"""

from datetime import datetime
from typing import Optional
from database.client import get_client
from utils.logger import setup_logger

log = setup_logger("db.predictions")


def log_prediction(
    match_id: str,
    match_name: str,
    predicted_winner: str,
    confidence_pct: float,
    match_date: datetime = None
) -> bool:
    """
    Log a prediction for accuracy tracking.
    
    Args:
        match_id: Unique match identifier
        match_name: Human-readable match name
        predicted_winner: Predicted winning team
        confidence_pct: Confidence percentage (0-100)
        match_date: When the match is scheduled
    
    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_client()
        data = {
            "match_id": match_id,
            "match_name": match_name,
            "predicted_winner": predicted_winner,
            "confidence_pct": confidence_pct,
            "match_date": match_date.isoformat() if match_date else None,
        }
        
        client.table("predictions").insert(data).execute()
        log.info(f"Prediction logged: {match_name} → {predicted_winner} ({confidence_pct}%)")
        return True
        
    except Exception as e:
        log.error(f"Failed to log prediction: {e}")
        return False


def get_accuracy() -> Optional[dict]:
    """
    Get overall prediction accuracy stats via DB function.
    
    Returns:
        Dict with {total, correct, accuracy} or None
    """
    try:
        client = get_client()
        result = client.rpc("get_prediction_accuracy").execute()
        
        if result.data:
            return result.data[0] if isinstance(result.data, list) else result.data
        return None
        
    except Exception as e:
        log.error(f"Failed to get prediction accuracy: {e}")
        return None


def update_actual_result(match_id: str, actual_winner: str) -> bool:
    """
    Update a prediction with the actual match result.
    Also sets is_correct based on comparison.
    
    Args:
        match_id: Match identifier
        actual_winner: The team that actually won
    
    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_client()
        
        # First fetch the prediction to check correctness
        result = client.table("predictions").select("predicted_winner").eq(
            "match_id", match_id
        ).execute()
        
        if not result.data:
            log.warning(f"No prediction found for match_id: {match_id}")
            return False
        
        predicted = result.data[0]["predicted_winner"]
        is_correct = predicted.lower().strip() == actual_winner.lower().strip()
        
        # Update with actual result
        client.table("predictions").update({
            "actual_winner": actual_winner,
            "is_correct": is_correct,
        }).eq("match_id", match_id).execute()
        
        log.info(f"Prediction updated: {match_id} → actual={actual_winner}, correct={is_correct}")
        return True
        
    except Exception as e:
        log.error(f"Failed to update prediction result for {match_id}: {e}")
        return False
