from datetime import datetime

def log_decision(user_id, score, risk_band):
    return {
        "user_id": user_id,
        "score": score,
        "risk_band": risk_band,
        "timestamp": datetime.utcnow().isoformat()
    }
