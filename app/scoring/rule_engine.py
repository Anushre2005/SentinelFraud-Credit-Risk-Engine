from typing import Optional
from .network_score import compute_network_adjustments


def rule_score(req):
    """Produce a rule-based risk score (higher value => higher risk) 0-1000 scale.
    
    This function is UNCHANGED for backward compatibility.
    """
    score = 0

    # Transaction volume risk
    if req.transaction_count_30d >= 100:
        score += 300
    elif req.transaction_count_30d >= 50:
        score += 200
    elif req.transaction_count_30d >= 20:
        score += 120
    else:
        score += 40

    # Avg transaction amount
    if req.avg_transaction_amount >= 1000:
        score += 250
    elif req.avg_transaction_amount >= 200:
        score += 150
    else:
        score += 60

    # Location risk
    score += int(req.location_risk_score * 200)

    # Device churn
    score += min(req.device_change_frequency * 40, 200)

    # Previous indicators
    if req.previous_fraud_flag:
        score += 200
    score += min(req.chargeback_count * 50, 200)

    # Normalize to 0-1000 cap
    return min(score, 1000)


def enhanced_rule_score(req) -> dict:
    """
    Enhanced rule scoring with CTC and address stability adjustments.
    
    Returns:
        dict with base_score, adjustments breakdown, and final adjusted score
    """
    # Get base score (original logic)
    base_score = rule_score(req)
    
    # Extract optional network/address fields with None defaults
    network_result = compute_network_adjustments(
        avg_contact_credit_score=getattr(req, 'avg_contact_credit_score', None),
        low_risk_contact_ratio=getattr(req, 'low_risk_contact_ratio', None),
        high_risk_contact_ratio=getattr(req, 'high_risk_contact_ratio', None),
        network_stability_ratio=getattr(req, 'network_stability_ratio', None),
        address_change_count_12m=getattr(req, 'address_change_count_12m', None),
        current_address_tenure_months=getattr(req, 'current_address_tenure_months', None)
    )
    
    ctc = network_result["ctc"]
    address = network_result["address_stability"]
    
    # Apply adjustments (note: higher CTC/stability = lower risk, so we subtract)
    # CTC is a trust score, so high CTC should reduce risk score
    # We invert the adjustment for risk scoring (negative adjustment = lower risk)
    adjusted_score = base_score - network_result["total_adjustment"]
    
    # Keep within 0-1000 bounds
    adjusted_score = max(0, min(1000, adjusted_score))
    
    return {
        "base_score": base_score,
        "ctc_adjustment": -ctc.impact_adjustment if ctc.available else 0,
        "address_adjustment": -address.impact_adjustment if address.available else 0,
        "total_adjustment": -network_result["total_adjustment"],
        "adjusted_score": adjusted_score,
        "ctc_details": {
            "score": ctc.score,
            "available": ctc.available,
            "components": ctc.components if ctc.available else {}
        },
        "address_details": {
            "score": address.score,
            "available": address.available,
            "tenure_category": address.tenure_category
        }
    }


def fully_enhanced_rule_score(req) -> dict:
    """
    Fully enhanced rule scoring with all behavioral and network signals.
    
    Score Fusion Logic:
        Final = Base Rule Score 
              + Network & Community Composite (≤15%)
              + Stability Composite (≤15%)
              + Behavioral Enhancers (≤10%)
    
    All adjustments have hard caps.
    
    Returns:
        dict with complete breakdown for explainability
    """
    from .stability_scores import (
        compute_income_rhythm,
        compute_savings_cadence,
        compute_device_persistence,
        compute_expense_elasticity,
        compute_utility_stability,
        compute_merchant_loyalty,
        compute_repayment_velocity,
        compute_geo_resilience,
        compute_stability_composite
    )
    
    # Get base enhanced score (includes CTC and address)
    enhanced = enhanced_rule_score(req)
    base_with_network = enhanced["adjusted_score"]
    
    # Compute all stability signals
    income_rhythm = compute_income_rhythm(
        income_coefficient_of_variation=getattr(req, 'income_coefficient_of_variation', None),
        seasonal_adjustment_factor=getattr(req, 'seasonal_adjustment_factor', None),
        income_frequency_months=getattr(req, 'income_frequency_months', None)
    )
    
    savings_cadence = compute_savings_cadence(
        micro_saves_per_month=getattr(req, 'micro_saves_per_month', None),
        savings_persistence_months=getattr(req, 'savings_persistence_months', None),
        has_escrow_commitment=getattr(req, 'has_escrow_commitment', None)
    )
    
    device_persistence = compute_device_persistence(
        device_tenure_months=getattr(req, 'device_tenure_months', None),
        os_change_count_12m=getattr(req, 'os_change_count_12m', None),
        app_reinstall_count=getattr(req, 'app_reinstall_count', None)
    )
    
    expense_elasticity = compute_expense_elasticity(
        expense_income_correlation=getattr(req, 'expense_income_correlation', None),
        expense_volatility=getattr(req, 'expense_volatility', None)
    )
    
    utility_stability = compute_utility_stability(
        utility_payment_ontime_ratio=getattr(req, 'utility_payment_ontime_ratio', None),
        utility_payment_variance=getattr(req, 'utility_payment_variance', None),
        utility_months_active=getattr(req, 'utility_months_active', None)
    )
    
    merchant_loyalty = compute_merchant_loyalty(
        repeat_merchant_ratio=getattr(req, 'repeat_merchant_ratio', None),
        refund_ratio=getattr(req, 'refund_ratio', None),
        dispute_frequency=getattr(req, 'dispute_frequency', None)
    )
    
    repayment_velocity = compute_repayment_velocity(
        early_payment_ratio=getattr(req, 'early_payment_ratio', None),
        ontime_payment_ratio=getattr(req, 'ontime_payment_ratio', None),
        late_payment_ratio=getattr(req, 'late_payment_ratio', None)
    )
    
    geo_resilience = compute_geo_resilience(
        local_economic_index=getattr(req, 'local_economic_index', None),
        income_local_correlation=getattr(req, 'income_local_correlation', None),
        employment_diversity_score=getattr(req, 'employment_diversity_score', None)
    )
    
    # Compute stability composite
    stability_composite = compute_stability_composite(
        income_rhythm=income_rhythm,
        savings_cadence=savings_cadence,
        device_persistence=device_persistence,
        expense_elasticity=expense_elasticity,
        utility_stability=utility_stability,
        merchant_loyalty=merchant_loyalty,
        repayment_velocity=repayment_velocity,
        geo_resilience=geo_resilience
    )
    
    # Apply stability adjustment (higher stability = lower risk, so subtract)
    stability_adjustment = -stability_composite["total_adjustment"]
    
    # Final score with all adjustments
    final_score = base_with_network + stability_adjustment
    final_score = max(0, min(1000, int(final_score)))
    
    return {
        # Base scores
        "base_rule_score": enhanced["base_score"],
        "network_adjusted_score": base_with_network,
        "final_enhanced_score": final_score,
        
        # Network adjustments (from enhanced_rule_score)
        "network_community": {
            "ctc_score": enhanced["ctc_details"]["score"],
            "ctc_available": enhanced["ctc_details"]["available"],
            "ctc_adjustment": enhanced["ctc_adjustment"],
            "address_score": enhanced["address_details"]["score"],
            "address_available": enhanced["address_details"]["available"],
            "address_adjustment": enhanced["address_adjustment"],
            "total_network_adjustment": enhanced["total_adjustment"]
        },
        
        # Stability composite
        "stability_composite": {
            "composite_score": stability_composite["composite_score"],
            "signals_available": stability_composite["available_count"],
            "total_adjustment": stability_adjustment,
            "signal_details": stability_composite["signal_details"]
        },
        
        # Individual signal results for explainability
        "signal_breakdown": {
            "income_rhythm": {
                "score": income_rhythm.score,
                "available": income_rhythm.available,
                "category": income_rhythm.rhythm_category
            },
            "savings_cadence": {
                "score": savings_cadence.score,
                "available": savings_cadence.available,
                "category": savings_cadence.cadence_category
            },
            "device_persistence": {
                "score": device_persistence.score,
                "available": device_persistence.available,
                "trust_level": device_persistence.trust_level
            },
            "expense_elasticity": {
                "score": expense_elasticity.score,
                "available": expense_elasticity.available,
                "type": expense_elasticity.elasticity_type
            },
            "utility_stability": {
                "score": utility_stability.score,
                "available": utility_stability.available,
                "pattern": utility_stability.payment_pattern
            },
            "merchant_loyalty": {
                "score": merchant_loyalty.score,
                "available": merchant_loyalty.available,
                "tier": merchant_loyalty.loyalty_tier
            },
            "repayment_velocity": {
                "score": repayment_velocity.score,
                "available": repayment_velocity.available,
                "category": repayment_velocity.velocity_category
            },
            "geo_resilience": {
                "score": geo_resilience.score,
                "available": geo_resilience.available,
                "level": geo_resilience.resilience_level
            }
        }
    }
