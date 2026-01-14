from fastapi import APIRouter, Query
from app.models import CreditRequest
from app.scoring.rule_engine import rule_score, enhanced_rule_score
from app.scoring.feature_mapper import to_ml_features
from app.scoring.ml_model import ml_score, MODEL_AUC
from app.scoring.reason_codes import generate_reason_codes
from app.scoring.explanation_agent import CreditDecision, generate_explanation
from datetime import datetime

router = APIRouter()


@router.post("/credit/assess")
def assess(req: CreditRequest, include_explanation: bool = Query(False)):
    """
    Assess credit risk for a user.
    
    Returns analyst-ready structured response with:
    - Applicant overview
    - Rule and ML scores
    - Network trust summary (CTC)
    - Address stability summary
    - Final credit decision
    - Compliance note
    """
    # Get enhanced rule score with CTC and address adjustments
    enhanced_result = enhanced_rule_score(req)
    r_score = enhanced_result["adjusted_score"]
    base_rule_score = enhanced_result["base_score"]

    # ML scoring (unchanged - no new features added)
    features = to_ml_features(req)
    prob, m_score = ml_score(features)

    # Final score fusion (60% ML + 40% enhanced rule score)
    final_score = int(0.6 * m_score + 0.4 * r_score)

    # Risk band tiers
    if final_score >= 700:
        band = "High"
    elif final_score >= 350:
        band = "Moderate"
    else:
        band = "Low"
    
    reason_codes = generate_reason_codes(req)

    # Build analyst-ready response
    response = {
        "assessment_id": f"CR-{req.user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        
        # Applicant Overview
        "applicant": {
            "user_id": req.user_id,
            "age": req.age,
            "occupation": req.occupation,
            "account_age_months": req.account_age_months
        },
        
        # Rule Score Breakdown
        "rule_scoring": {
            "base_score": base_rule_score,
            "ctc_adjustment": enhanced_result["ctc_adjustment"],
            "address_adjustment": enhanced_result["address_adjustment"],
            "total_adjustment": enhanced_result["total_adjustment"],
            "final_rule_score": r_score
        },
        
        # ML Scoring
        "ml_scoring": {
            "high_risk_probability": round(prob, 4),
            "ml_score": m_score,
            "model_auc": round(MODEL_AUC, 3) if MODEL_AUC is not None else None
        },
        
        # Network Trust Summary (CTC)
        "network_trust": {
            "available": enhanced_result["ctc_details"]["available"],
            "ctc_score": enhanced_result["ctc_details"]["score"],
            "components": enhanced_result["ctc_details"]["components"],
            "impact": "Positive" if enhanced_result["ctc_adjustment"] < 0 else 
                      "Negative" if enhanced_result["ctc_adjustment"] > 0 else "Neutral"
        },
        
        # Address Stability Summary
        "address_stability": {
            "available": enhanced_result["address_details"]["available"],
            "stability_score": enhanced_result["address_details"]["score"],
            "tenure_category": enhanced_result["address_details"]["tenure_category"],
            "impact": "Positive" if enhanced_result["address_adjustment"] < 0 else 
                      "Negative" if enhanced_result["address_adjustment"] > 0 else "Neutral"
        },
        
        # Final Decision
        "decision": {
            "final_credit_score": final_score,
            "risk_band": band,
            "reason_codes": reason_codes
        },
        
        # Compliance Note
        "compliance": {
            "note": "Score generated using explainable hybrid model. CTC and address signals applied as post-ML adjustments with capped impact.",
            "ctc_max_impact": "±10% (±100 points)",
            "address_max_impact": "±5% (±50 points)"
        }
    }
    
    # Optionally include customer-facing explanation
    if include_explanation:
        decision = CreditDecision(
            user_id=req.user_id,
            user_name=req.user_id,
            final_score=final_score,
            risk_band=band,
            monthly_income=req.monthly_income,
            transaction_count_30d=req.transaction_count_30d,
            avg_transaction_amount=req.avg_transaction_amount,
            location_risk_score=req.location_risk_score,
            device_change_frequency=req.device_change_frequency,
            previous_fraud_flag=req.previous_fraud_flag,
            account_age_months=req.account_age_months,
            chargeback_count=req.chargeback_count,
            rule_score=r_score,
            ml_probability=prob,
            reason_codes=reason_codes
        )
        explanation = generate_explanation(decision)
        response["customer_explanation"] = explanation
    
    return response


@router.post("/credit/explain")
def explain(req: CreditRequest):
    """
    Generate customer-friendly explanation for a credit decision.
    Returns both email and SMS formats.
    """
    # First, calculate the score
    r_score = rule_score(req)
    features = to_ml_features(req)
    prob, m_score = ml_score(features)
    final_score = int(0.6 * m_score + 0.4 * r_score)
    
    if final_score >= 700:
        band = "High"
    elif final_score >= 350:
        band = "Moderate"
    else:
        band = "Low"
    
    # Build decision object
    decision = CreditDecision(
        user_id=req.user_id,
        user_name=req.user_id,
        final_score=final_score,
        risk_band=band,
        monthly_income=req.monthly_income,
        transaction_count_30d=req.transaction_count_30d,
        avg_transaction_amount=req.avg_transaction_amount,
        location_risk_score=req.location_risk_score,
        device_change_frequency=req.device_change_frequency,
        previous_fraud_flag=req.previous_fraud_flag,
        account_age_months=req.account_age_months,
        chargeback_count=req.chargeback_count,
        rule_score=r_score,
        ml_probability=prob,
        reason_codes=generate_reason_codes(req)
    )
    
    explanation = generate_explanation(decision)
    
    return {
        "user_id": req.user_id,
        "risk_band": band,
        "email": explanation["email"],
        "sms": explanation["sms"]
    }


@router.post("/credit/assess/full")
def assess_full(req: CreditRequest):
    """
    Full credit assessment with all advanced behavioral and network signals.
    
    Integrates:
    - Community Trust Coefficient (CTC)
    - Address Stability
    - Income Rhythm Stability
    - Savings Cadence
    - Device Persistence
    - Expense Elasticity
    - Utility Stability
    - Merchant Loyalty
    - Repayment Velocity
    - Geo-Resilience
    
    Returns analyst-grade response with:
    - Complete scoring breakdown
    - Signal-by-signal explainability
    - Uncertainty band (PD ± confidence)
    - Compliance documentation
    """
    from app.scoring.rule_engine import fully_enhanced_rule_score
    
    # Get fully enhanced rule score with all signals
    full_result = fully_enhanced_rule_score(req)
    r_score = full_result["final_enhanced_score"]
    
    # ML scoring (unchanged)
    features = to_ml_features(req)
    prob, m_score = ml_score(features)
    
    # Final score fusion
    final_score = int(0.6 * m_score + 0.4 * r_score)
    
    # Risk band
    if final_score >= 700:
        band = "High"
    elif final_score >= 350:
        band = "Moderate"
    else:
        band = "Low"
    
    # Calculate uncertainty band based on available signals
    available_signals = full_result["stability_composite"]["signals_available"]
    # More signals = lower uncertainty
    uncertainty_pct = max(5, 25 - (available_signals * 2.5))
    uncertainty_points = int(final_score * uncertainty_pct / 100)
    
    pd_estimate = round(prob * 100, 2)
    pd_lower = max(0, round(pd_estimate - uncertainty_pct/2, 2))
    pd_upper = min(100, round(pd_estimate + uncertainty_pct/2, 2))
    
    reason_codes = generate_reason_codes(req)
    
    return {
        "assessment_id": f"CR-FULL-{req.user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        
        # Applicant Overview
        "applicant": {
            "user_id": req.user_id,
            "age": req.age,
            "occupation": req.occupation,
            "account_age_months": req.account_age_months,
            "monthly_income": req.monthly_income
        },
        
        # Final Decision with Uncertainty
        "decision": {
            "final_credit_score": final_score,
            "score_range": {
                "lower": max(0, final_score - uncertainty_points),
                "upper": min(1000, final_score + uncertainty_points)
            },
            "risk_band": band,
            "probability_of_default": {
                "estimate": pd_estimate,
                "lower_bound": pd_lower,
                "upper_bound": pd_upper,
                "uncertainty_pct": round(uncertainty_pct, 1)
            },
            "reason_codes": reason_codes
        },
        
        # Score Fusion Breakdown
        "scoring_breakdown": {
            "base_rule_score": full_result["base_rule_score"],
            "network_adjusted_score": full_result["network_adjusted_score"],
            "fully_enhanced_rule_score": r_score,
            "ml_score": m_score,
            "fusion_weights": {"ml": 0.6, "rule": 0.4}
        },
        
        # Network & Community Trust
        "network_trust": full_result["network_community"],
        
        # Stability Composite
        "stability": {
            "composite_score": full_result["stability_composite"]["composite_score"],
            "signals_available": full_result["stability_composite"]["signals_available"],
            "adjustment": full_result["stability_composite"]["total_adjustment"],
            "max_impact": "±15% (±150 points)"
        },
        
        # Individual Signal Breakdown
        "behavioral_signals": full_result["signal_breakdown"],
        
        # ML Model Info
        "ml_model": {
            "high_risk_probability": round(prob, 4),
            "model_auc": round(MODEL_AUC, 3) if MODEL_AUC is not None else None,
            "features_used": 9,
            "training_samples": 1000
        },
        
        # Compliance & Explainability
        "compliance": {
            "scoring_method": "Hybrid: ML + Rule-based + Behavioral Signals",
            "explainability": "Full signal-level breakdown provided",
            "privacy_note": "No PII stored. Network signals are aggregated and anonymized.",
            "caps_applied": {
                "ctc_max_impact": "±10%",
                "address_max_impact": "±5%",
                "stability_composite_max_impact": "±15%",
                "total_adjustment_cap": "±25%"
            },
            "ml_model_not_retrained": True,
            "signals_are_post_ml_adjustments": True
        },
        
        # Key Contributing Factors (Top 3)
        "key_factors": _extract_key_factors(full_result, reason_codes, prob)
    }


def _extract_key_factors(full_result: dict, reason_codes: list, ml_prob: float) -> list:
    """Extract top 3 contributing factors for the decision."""
    factors = []
    
    # Check reason codes first
    for code in reason_codes[:2]:
        factors.append({"factor": code, "direction": "negative"})
    
    # Check network trust
    if full_result["network_community"]["ctc_available"]:
        ctc_score = full_result["network_community"]["ctc_score"]
        if ctc_score >= 0.7:
            factors.append({"factor": "Strong network trust (CTC)", "direction": "positive"})
        elif ctc_score <= 0.3:
            factors.append({"factor": "Weak network trust (CTC)", "direction": "negative"})
    
    # Check stability signals
    for signal_name, signal_data in full_result["signal_breakdown"].items():
        if signal_data["available"] and len(factors) < 5:
            if signal_data["score"] >= 0.7:
                factors.append({
                    "factor": f"Good {signal_name.replace('_', ' ')}",
                    "direction": "positive"
                })
            elif signal_data["score"] <= 0.3:
                factors.append({
                    "factor": f"Weak {signal_name.replace('_', ' ')}",
                    "direction": "negative"
                })
    
    # ML probability contribution
    if ml_prob >= 0.5:
        factors.append({"factor": "ML model indicates elevated risk", "direction": "negative"})
    elif ml_prob <= 0.2:
        factors.append({"factor": "ML model indicates low risk", "direction": "positive"})
    
    return factors[:5]  # Return top 5
