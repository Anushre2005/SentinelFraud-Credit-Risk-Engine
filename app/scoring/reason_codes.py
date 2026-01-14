def generate_reason_codes(req):
    reasons = []

    if req.previous_fraud_flag:
        reasons.append("R10: Historical fraud flag on account")

    if req.chargeback_count >= 1:
        reasons.append("R11: Chargebacks detected")

    if req.location_risk_score >= 0.7:
        reasons.append("R07: High-risk location activity")

    if req.transaction_count_30d >= 100 and req.avg_transaction_amount < 50:
        reasons.append("R12: High frequency of low-value transactions")

    return reasons
