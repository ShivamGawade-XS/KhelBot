"""
KhelBot Predictions Database — Log and track prediction accuracy.
Includes automatic fallback for RPC calculations, de-duplication, and async safety.
"""

import asyncio
from datetime import datetime
from typing import Optional, List
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
    De-duplicates by updating existing prediction if match_id exists.
    """
    try:
        client = get_client()

        # Check if prediction for this match already exists
        existing = client.table("predictions").select("id").eq("match_id", str(match_id)).execute()
        
        data = {
            "match_id": str(match_id),
            "match_name": match_name,
            "predicted_winner": predicted_winner,
            "confidence_pct": float(confidence_pct),
            "match_date": match_date.isoformat() if match_date else None,
        }

        if existing.data:
            # Update existing prediction
            client.table("predictions").update(data).eq("match_id", str(match_id)).execute()
            log.info(f"Prediction updated: {match_name} → {predicted_winner} ({confidence_pct}%)")
        else:
            # Insert new prediction
            client.table("predictions").insert(data).execute()
            log.info(f"Prediction logged: {match_name} → {predicted_winner} ({confidence_pct}%)")

        return True
    except Exception as e:
        log.error(f"Failed to log prediction: {e}")
        return False


def get_accuracy() -> Optional[dict]:
    """
    Get overall prediction accuracy stats.
    Attempts RPC function first, then falls back to direct client-side calculation.
    """
    try:
        client = get_client()
        try:
            result = client.rpc("get_prediction_accuracy").execute()
            if result.data:
                return result.data[0] if isinstance(result.data, list) else result.data
        except Exception:
            pass

        # Fallback: compute accuracy directly from predictions table
        records = client.table("predictions").select("actual_winner, is_correct").execute().data or []
        verified = [r for r in records if r.get("actual_winner") is not None]
        
        if not verified:
            return None

        total = len(verified)
        correct = sum(1 for r in verified if r.get("is_correct") is True)
        accuracy = (correct / total * 100.0) if total > 0 else 0.0

        return {
            "total": total,
            "correct": correct,
            "accuracy": round(accuracy, 1)
        }
    except Exception as e:
        log.error(f"Failed to calculate prediction accuracy: {e}")
        return None


def update_actual_result(match_id: str, actual_winner: str) -> bool:
    """
    Update a prediction with the actual match result.
    Sets is_correct based on case-insensitive substring comparison.
    """
    try:
        client = get_client()
        result = client.table("predictions").select("predicted_winner").eq(
            "match_id", str(match_id)
        ).execute()
        
        if not result.data:
            log.warning(f"No prediction found for match_id: {match_id}")
            return False
        
        predicted = result.data[0].get("predicted_winner", "").lower().strip()
        actual = actual_winner.lower().strip()

        # Generous match check: e.g. "csk" in "chennai super kings"
        is_correct = (predicted in actual) or (actual in predicted)
        
        client.table("predictions").update({
            "actual_winner": actual_winner,
            "is_correct": is_correct,
        }).eq("match_id", str(match_id)).execute()
        
        log.info(f"Prediction resolved: {match_id} → actual={actual_winner}, correct={is_correct}")
        return True
    except Exception as e:
        log.error(f"Failed to update prediction result for {match_id}: {e}")
        return False


def resolve_predictions_from_matches(matches: List[dict]) -> int:
    """
    Inspect match statuses from CricAPI and resolve any matching predictions.
    Returns the count of resolved predictions.
    """
    resolved_count = 0
    try:
        for m in matches:
            match_id = str(m.get("id", ""))
            status = m.get("status", "")
            if not status or "won" not in status.lower():
                continue

            # Detect winner from status string (e.g. "Chennai Super Kings won by 5 wkts")
            teams = m.get("teams", [])
            actual_winner = None
            for t in teams:
                if t.lower() in status.lower():
                    actual_winner = t
                    break

            if actual_winner and match_id:
                if update_actual_result(match_id, actual_winner):
                    resolved_count += 1
    except Exception as e:
        log.error(f"Error resolving predictions from matches: {e}")

    return resolved_count


# ── Non-blocking Async Wrappers for Event Loop Safety ───────────────────────

async def async_log_prediction(
    match_id: str,
    match_name: str,
    predicted_winner: str,
    confidence_pct: float,
    match_date: datetime = None
) -> bool:
    """Non-blocking async log prediction with timeout."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(log_prediction, match_id, match_name, predicted_winner, confidence_pct, match_date),
            timeout=3.0
        )
    except Exception as e:
        log.error(f"Async log prediction error: {e}")
        return False


async def async_get_accuracy() -> Optional[dict]:
    """Non-blocking async get accuracy with timeout."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(get_accuracy),
            timeout=3.0
        )
    except Exception as e:
        log.error(f"Async get accuracy error: {e}")
        return None
