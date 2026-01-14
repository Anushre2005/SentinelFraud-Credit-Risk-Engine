def to_ml_features(req):
    """
    Convert request to ML feature vector.
    
    IMPORTANT: Feature order must match train_model.py FEATURES exactly:
    [age, monthly_income, transaction_count_30d, avg_transaction_amount,
     location_risk_score, device_change_frequency, previous_fraud_flag,
     account_age_months, chargeback_count]
    """
    return [
        int(req.age),
        float(req.monthly_income),
        int(req.transaction_count_30d),
        float(req.avg_transaction_amount),
        float(req.location_risk_score),
        int(req.device_change_frequency),
        int(req.previous_fraud_flag),
        int(req.account_age_months),
        int(req.chargeback_count),
    ]
