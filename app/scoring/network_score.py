"""
Network Score Module

Computes Community Trust Coefficient (CTC) and Address Stability Score (ASS).
Both scores are normalized 0-1 and capped to prevent dominance in final scoring.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CTCResult:
    """Community Trust Coefficient computation result."""
    score: float           # 0-1 normalized
    available: bool        # Whether CTC data was provided
    components: dict       # Breakdown for explainability
    impact_adjustment: int # Capped adjustment to final score (±10% of 1000 = ±100)


@dataclass
class AddressStabilityResult:
    """Address Stability Score computation result."""
    score: float           # 0-1 normalized
    available: bool        # Whether address data was provided
    tenure_category: str   # High / Medium / Low / Unknown
    impact_adjustment: int # Capped adjustment to final score (±5% of 1000 = ±50)


def compute_ctc(
    avg_contact_credit_score: Optional[float],
    low_risk_contact_ratio: Optional[float],
    high_risk_contact_ratio: Optional[float],
    network_stability_ratio: Optional[float]
) -> CTCResult:
    """
    Compute Community Trust Coefficient (CTC).
    
    Formula:
        CTC = 0.4 × normalized_avg_contact_credit_score +
              0.3 × low_risk_contact_ratio +
              0.2 × network_stability_ratio +
              0.1 × (1 − high_risk_contact_ratio)
    
    Args:
        avg_contact_credit_score: Average credit score of contacts (300-900)
        low_risk_contact_ratio: Ratio of low-risk contacts (0-1)
        high_risk_contact_ratio: Ratio of high-risk contacts (0-1)
        network_stability_ratio: Network relationship stability (0-1)
    
    Returns:
        CTCResult with score, availability flag, and impact adjustment
    """
    # Check if any CTC data is available
    if all(v is None for v in [avg_contact_credit_score, low_risk_contact_ratio, 
                                high_risk_contact_ratio, network_stability_ratio]):
        return CTCResult(
            score=0.5,  # Neutral default
            available=False,
            components={},
            impact_adjustment=0
        )
    
    # Apply defaults for missing values (neutral defaults)
    avg_credit = avg_contact_credit_score if avg_contact_credit_score is not None else 600
    low_risk = low_risk_contact_ratio if low_risk_contact_ratio is not None else 0.5
    high_risk = high_risk_contact_ratio if high_risk_contact_ratio is not None else 0.2
    stability = network_stability_ratio if network_stability_ratio is not None else 0.5
    
    # Normalize avg_contact_credit_score from 300-900 to 0-1
    # Clamp to valid range first
    avg_credit = max(300, min(900, avg_credit))
    normalized_credit = (avg_credit - 300) / 600  # 0-1
    
    # Clamp ratios to 0-1
    low_risk = max(0, min(1, low_risk))
    high_risk = max(0, min(1, high_risk))
    stability = max(0, min(1, stability))
    
    # Compute CTC using formula
    ctc_score = (
        0.4 * normalized_credit +
        0.3 * low_risk +
        0.2 * stability +
        0.1 * (1 - high_risk)
    )
    
    # Clamp final score to 0-1
    ctc_score = max(0, min(1, ctc_score))
    
    # Calculate impact adjustment (±10% of 1000 = ±100 max)
    # CTC of 0.5 = neutral (0 adjustment)
    # CTC of 1.0 = +100, CTC of 0.0 = -100
    MAX_IMPACT = 100
    impact = int((ctc_score - 0.5) * 2 * MAX_IMPACT)
    impact = max(-MAX_IMPACT, min(MAX_IMPACT, impact))
    
    return CTCResult(
        score=round(ctc_score, 3),
        available=True,
        components={
            "normalized_credit_score": round(normalized_credit, 3),
            "low_risk_contact_ratio": round(low_risk, 3),
            "high_risk_contact_ratio": round(high_risk, 3),
            "network_stability_ratio": round(stability, 3)
        },
        impact_adjustment=impact
    )


def compute_address_stability(
    address_change_count_12m: Optional[int],
    current_address_tenure_months: Optional[int]
) -> AddressStabilityResult:
    """
    Compute Address Stability Score (ASS).
    
    Scoring logic:
        - High stability: tenure >= 18 months AND changes <= 1/year
        - Medium stability: tenure >= 6 months OR changes <= 2/year
        - Low stability: tenure < 6 months AND changes >= 3/year
    
    Args:
        address_change_count_12m: Number of address changes in last 12 months
        current_address_tenure_months: Months at current address
    
    Returns:
        AddressStabilityResult with score, category, and impact adjustment
    """
    # Check if any address data is available
    if address_change_count_12m is None and current_address_tenure_months is None:
        return AddressStabilityResult(
            score=0.5,  # Neutral default
            available=False,
            tenure_category="Unknown",
            impact_adjustment=0
        )
    
    # Apply defaults for partial data
    changes = address_change_count_12m if address_change_count_12m is not None else 1
    tenure = current_address_tenure_months if current_address_tenure_months is not None else 12
    
    # Clamp to reasonable ranges
    changes = max(0, min(10, changes))
    tenure = max(0, min(240, tenure))  # Max 20 years
    
    # Compute score components
    # Tenure score: 0-1 (higher tenure = higher score)
    tenure_score = min(1, tenure / 24)  # Max at 24 months
    
    # Change penalty: 0-1 (more changes = lower score)
    change_penalty = min(1, changes / 4)  # Max penalty at 4+ changes
    change_score = 1 - change_penalty
    
    # Combined score (weighted)
    ass_score = 0.6 * tenure_score + 0.4 * change_score
    ass_score = max(0, min(1, ass_score))
    
    # Determine category
    if tenure >= 18 and changes <= 1:
        category = "High"
    elif tenure >= 6 or changes <= 2:
        category = "Medium"
    else:
        category = "Low"
    
    # Calculate impact adjustment (±5% of 1000 = ±50 max)
    # Score of 0.5 = neutral (0 adjustment)
    MAX_IMPACT = 50
    impact = int((ass_score - 0.5) * 2 * MAX_IMPACT)
    impact = max(-MAX_IMPACT, min(MAX_IMPACT, impact))
    
    return AddressStabilityResult(
        score=round(ass_score, 3),
        available=True,
        tenure_category=category,
        impact_adjustment=impact
    )


def compute_network_adjustments(
    avg_contact_credit_score: Optional[float] = None,
    low_risk_contact_ratio: Optional[float] = None,
    high_risk_contact_ratio: Optional[float] = None,
    network_stability_ratio: Optional[float] = None,
    address_change_count_12m: Optional[int] = None,
    current_address_tenure_months: Optional[int] = None
) -> dict:
    """
    Compute all network-aware adjustments.
    
    Returns dict with CTC result, address stability result,
    and total capped adjustment.
    """
    ctc = compute_ctc(
        avg_contact_credit_score,
        low_risk_contact_ratio,
        high_risk_contact_ratio,
        network_stability_ratio
    )
    
    address = compute_address_stability(
        address_change_count_12m,
        current_address_tenure_months
    )
    
    # Total adjustment is sum of both, but still capped
    # CTC: ±100, Address: ±50, Total max: ±150 but we cap at ±120
    total_adjustment = ctc.impact_adjustment + address.impact_adjustment
    total_adjustment = max(-120, min(120, total_adjustment))
    
    return {
        "ctc": ctc,
        "address_stability": address,
        "total_adjustment": total_adjustment
    }
