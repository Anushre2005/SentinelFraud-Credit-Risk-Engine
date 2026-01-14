"""
Stability Scores Module

Computes behavioral stability signals for credit risk assessment.
All scores are normalized 0-1 with capped influence on final score.
"""

from dataclasses import dataclass
from typing import Optional
import math


# =============================================================================
# 1️⃣ INCOME RHYTHM STABILITY
# =============================================================================

@dataclass
class IncomeRhythmResult:
    """Income rhythm stability score result."""
    score: float           # 0-1 normalized
    available: bool
    rhythm_category: str   # Stable / Variable / Irregular
    impact_adjustment: int # ±7% of 1000 = ±70 max


def compute_income_rhythm(
    income_coefficient_of_variation: Optional[float] = None,
    seasonal_adjustment_factor: Optional[float] = None,
    income_frequency_months: Optional[int] = None
) -> IncomeRhythmResult:
    """
    Compute income rhythm stability score.
    
    Args:
        income_coefficient_of_variation: CV of monthly income (lower = more stable)
        seasonal_adjustment_factor: Adjustment for seasonal patterns (0-1)
        income_frequency_months: Number of income months in last 12
    
    Returns:
        IncomeRhythmResult with score and impact
    """
    if all(v is None for v in [income_coefficient_of_variation, seasonal_adjustment_factor]):
        return IncomeRhythmResult(
            score=0.5, available=False, rhythm_category="Unknown", impact_adjustment=0
        )
    
    # Defaults
    cv = income_coefficient_of_variation if income_coefficient_of_variation is not None else 0.3
    seasonal = seasonal_adjustment_factor if seasonal_adjustment_factor is not None else 1.0
    freq = income_frequency_months if income_frequency_months is not None else 12
    
    # Clamp CV (0 = perfect, 1+ = high variance)
    cv = max(0, min(2.0, cv))
    cv_score = 1 - min(1, cv / 0.5)  # Score decreases as CV increases
    
    # Frequency score (12/12 = perfect)
    freq_score = min(1, freq / 12)
    
    # Combined with seasonal adjustment
    rhythm_score = (0.6 * cv_score + 0.4 * freq_score) * seasonal
    rhythm_score = max(0, min(1, rhythm_score))
    
    # Category
    if rhythm_score >= 0.7:
        category = "Stable"
    elif rhythm_score >= 0.4:
        category = "Variable"
    else:
        category = "Irregular"
    
    # Impact: ±7% = ±70 points
    MAX_IMPACT = 70
    impact = int((rhythm_score - 0.5) * 2 * MAX_IMPACT)
    
    return IncomeRhythmResult(
        score=round(rhythm_score, 3),
        available=True,
        rhythm_category=category,
        impact_adjustment=max(-MAX_IMPACT, min(MAX_IMPACT, impact))
    )


# =============================================================================
# 2️⃣ SAVINGS CADENCE & MICRO-ESCROWS
# =============================================================================

@dataclass
class SavingsCadenceResult:
    """Savings behavior score result."""
    score: float
    available: bool
    cadence_category: str  # Strong / Moderate / Weak / None
    impact_adjustment: int # ±5% = ±50 max


def compute_savings_cadence(
    micro_saves_per_month: Optional[float] = None,
    savings_persistence_months: Optional[int] = None,
    has_escrow_commitment: Optional[bool] = None
) -> SavingsCadenceResult:
    """
    Compute savings cadence score.
    
    Args:
        micro_saves_per_month: Average micro-save count per month
        savings_persistence_months: How many months savings activity continued
        has_escrow_commitment: Whether user has locked escrow/bond
    """
    if all(v is None for v in [micro_saves_per_month, savings_persistence_months]):
        return SavingsCadenceResult(
            score=0.5, available=False, cadence_category="Unknown", impact_adjustment=0
        )
    
    saves = micro_saves_per_month if micro_saves_per_month is not None else 0
    persistence = savings_persistence_months if savings_persistence_months is not None else 0
    escrow = has_escrow_commitment if has_escrow_commitment is not None else False
    
    # Frequency score (4+ saves/month = max)
    freq_score = min(1, saves / 4)
    
    # Persistence score (12+ months = max)
    persist_score = min(1, persistence / 12)
    
    # Escrow bonus
    escrow_bonus = 0.1 if escrow else 0
    
    savings_score = 0.5 * freq_score + 0.4 * persist_score + 0.1 * (1 if escrow else 0)
    savings_score = min(1, savings_score + escrow_bonus)
    
    if savings_score >= 0.7:
        category = "Strong"
    elif savings_score >= 0.4:
        category = "Moderate"
    elif savings_score > 0.1:
        category = "Weak"
    else:
        category = "None"
    
    MAX_IMPACT = 50
    impact = int((savings_score - 0.5) * 2 * MAX_IMPACT)
    
    return SavingsCadenceResult(
        score=round(savings_score, 3),
        available=True,
        cadence_category=category,
        impact_adjustment=max(-MAX_IMPACT, min(MAX_IMPACT, impact))
    )


# =============================================================================
# 4️⃣ DEVICE PERSISTENCE & AUTHENTICITY
# =============================================================================

@dataclass
class DevicePersistenceResult:
    """Device persistence score result."""
    score: float
    available: bool
    trust_level: str  # High / Medium / Low
    impact_adjustment: int


def compute_device_persistence(
    device_tenure_months: Optional[int] = None,
    os_change_count_12m: Optional[int] = None,
    app_reinstall_count: Optional[int] = None
) -> DevicePersistenceResult:
    """
    Compute device persistence score.
    """
    if all(v is None for v in [device_tenure_months, os_change_count_12m]):
        return DevicePersistenceResult(
            score=0.5, available=False, trust_level="Unknown", impact_adjustment=0
        )
    
    tenure = device_tenure_months if device_tenure_months is not None else 6
    os_changes = os_change_count_12m if os_change_count_12m is not None else 1
    reinstalls = app_reinstall_count if app_reinstall_count is not None else 0
    
    # Tenure score (24+ months = max)
    tenure_score = min(1, tenure / 24)
    
    # Churn penalty
    churn_penalty = min(1, (os_changes + reinstalls) / 6)
    churn_score = 1 - churn_penalty
    
    device_score = 0.6 * tenure_score + 0.4 * churn_score
    
    if device_score >= 0.7:
        trust = "High"
    elif device_score >= 0.4:
        trust = "Medium"
    else:
        trust = "Low"
    
    MAX_IMPACT = 40
    impact = int((device_score - 0.5) * 2 * MAX_IMPACT)
    
    return DevicePersistenceResult(
        score=round(device_score, 3),
        available=True,
        trust_level=trust,
        impact_adjustment=max(-MAX_IMPACT, min(MAX_IMPACT, impact))
    )


# =============================================================================
# 5️⃣ EXPENSE-TO-INCOME ELASTICITY
# =============================================================================

@dataclass
class ExpenseElasticityResult:
    """Expense elasticity score result."""
    score: float
    available: bool
    elasticity_type: str  # Rigid / Flexible / Volatile
    impact_adjustment: int


def compute_expense_elasticity(
    expense_income_correlation: Optional[float] = None,
    expense_volatility: Optional[float] = None
) -> ExpenseElasticityResult:
    """
    Compute expense-to-income elasticity score.
    Lower elasticity = more controlled spending = positive signal.
    """
    if expense_income_correlation is None and expense_volatility is None:
        return ExpenseElasticityResult(
            score=0.5, available=False, elasticity_type="Unknown", impact_adjustment=0
        )
    
    # Correlation: high positive correlation means spending follows income closely
    correlation = expense_income_correlation if expense_income_correlation is not None else 0.5
    volatility = expense_volatility if expense_volatility is not None else 0.3
    
    # Lower volatility is better
    volatility_score = 1 - min(1, volatility)
    
    # Moderate correlation is best (not too rigid, not too volatile)
    # Score peaks around 0.5-0.7 correlation
    correlation_score = 1 - abs(correlation - 0.6) * 2
    correlation_score = max(0, min(1, correlation_score))
    
    elasticity_score = 0.6 * volatility_score + 0.4 * correlation_score
    
    if elasticity_score >= 0.7:
        etype = "Controlled"
    elif elasticity_score >= 0.4:
        etype = "Flexible"
    else:
        etype = "Volatile"
    
    MAX_IMPACT = 40
    impact = int((elasticity_score - 0.5) * 2 * MAX_IMPACT)
    
    return ExpenseElasticityResult(
        score=round(elasticity_score, 3),
        available=True,
        elasticity_type=etype,
        impact_adjustment=max(-MAX_IMPACT, min(MAX_IMPACT, impact))
    )


# =============================================================================
# 6️⃣ UTILITY STABILITY
# =============================================================================

@dataclass
class UtilityStabilityResult:
    """Utility payment stability score."""
    score: float
    available: bool
    payment_pattern: str  # Consistent / Variable / Irregular
    impact_adjustment: int


def compute_utility_stability(
    utility_payment_ontime_ratio: Optional[float] = None,
    utility_payment_variance: Optional[float] = None,
    utility_months_active: Optional[int] = None
) -> UtilityStabilityResult:
    """
    Compute utility payment stability score.
    """
    if all(v is None for v in [utility_payment_ontime_ratio, utility_payment_variance]):
        return UtilityStabilityResult(
            score=0.5, available=False, payment_pattern="Unknown", impact_adjustment=0
        )
    
    ontime = utility_payment_ontime_ratio if utility_payment_ontime_ratio is not None else 0.8
    variance = utility_payment_variance if utility_payment_variance is not None else 0.2
    months = utility_months_active if utility_months_active is not None else 12
    
    ontime_score = min(1, ontime)
    variance_score = 1 - min(1, variance)
    history_score = min(1, months / 24)
    
    utility_score = 0.5 * ontime_score + 0.3 * variance_score + 0.2 * history_score
    
    if utility_score >= 0.8:
        pattern = "Consistent"
    elif utility_score >= 0.5:
        pattern = "Variable"
    else:
        pattern = "Irregular"
    
    MAX_IMPACT = 35
    impact = int((utility_score - 0.5) * 2 * MAX_IMPACT)
    
    return UtilityStabilityResult(
        score=round(utility_score, 3),
        available=True,
        payment_pattern=pattern,
        impact_adjustment=max(-MAX_IMPACT, min(MAX_IMPACT, impact))
    )


# =============================================================================
# 8️⃣ MERCHANT LOYALTY & REFUND BEHAVIOR
# =============================================================================

@dataclass
class MerchantLoyaltyResult:
    """Merchant loyalty and refund behavior score."""
    score: float
    available: bool
    loyalty_tier: str  # Premium / Standard / Low
    impact_adjustment: int


def compute_merchant_loyalty(
    repeat_merchant_ratio: Optional[float] = None,
    refund_ratio: Optional[float] = None,
    dispute_frequency: Optional[float] = None
) -> MerchantLoyaltyResult:
    """
    Compute merchant loyalty score.
    High repeat purchases + low refunds = positive signal.
    """
    if all(v is None for v in [repeat_merchant_ratio, refund_ratio]):
        return MerchantLoyaltyResult(
            score=0.5, available=False, loyalty_tier="Unknown", impact_adjustment=0
        )
    
    repeat = repeat_merchant_ratio if repeat_merchant_ratio is not None else 0.5
    refunds = refund_ratio if refund_ratio is not None else 0.05
    disputes = dispute_frequency if dispute_frequency is not None else 0.01
    
    repeat_score = min(1, repeat)
    refund_score = 1 - min(1, refunds * 10)  # 10% refunds = 0 score
    dispute_score = 1 - min(1, disputes * 20)  # 5% disputes = 0 score
    
    loyalty_score = 0.4 * repeat_score + 0.35 * refund_score + 0.25 * dispute_score
    
    if loyalty_score >= 0.75:
        tier = "Premium"
    elif loyalty_score >= 0.5:
        tier = "Standard"
    else:
        tier = "Low"
    
    MAX_IMPACT = 30
    impact = int((loyalty_score - 0.5) * 2 * MAX_IMPACT)
    
    return MerchantLoyaltyResult(
        score=round(loyalty_score, 3),
        available=True,
        loyalty_tier=tier,
        impact_adjustment=max(-MAX_IMPACT, min(MAX_IMPACT, impact))
    )


# =============================================================================
# 14️⃣ REPAYMENT VELOCITY
# =============================================================================

@dataclass
class RepaymentVelocityResult:
    """Repayment velocity score."""
    score: float
    available: bool
    velocity_category: str  # Early / On-Time / Late
    impact_adjustment: int


def compute_repayment_velocity(
    early_payment_ratio: Optional[float] = None,
    ontime_payment_ratio: Optional[float] = None,
    late_payment_ratio: Optional[float] = None
) -> RepaymentVelocityResult:
    """
    Compute repayment velocity score.
    Early payments weighted higher than on-time.
    """
    if all(v is None for v in [early_payment_ratio, ontime_payment_ratio]):
        return RepaymentVelocityResult(
            score=0.5, available=False, velocity_category="Unknown", impact_adjustment=0
        )
    
    early = early_payment_ratio if early_payment_ratio is not None else 0.2
    ontime = ontime_payment_ratio if ontime_payment_ratio is not None else 0.7
    late = late_payment_ratio if late_payment_ratio is not None else 0.1
    
    # Normalize
    total = early + ontime + late
    if total > 0:
        early /= total
        ontime /= total
        late /= total
    
    # Weighted score: early=1.0, ontime=0.7, late=0.2
    velocity_score = early * 1.0 + ontime * 0.7 + late * 0.2
    
    if early >= 0.4:
        category = "Early Payer"
    elif ontime >= 0.7:
        category = "On-Time"
    else:
        category = "Late Tendency"
    
    MAX_IMPACT = 50
    impact = int((velocity_score - 0.5) * 2 * MAX_IMPACT)
    
    return RepaymentVelocityResult(
        score=round(velocity_score, 3),
        available=True,
        velocity_category=category,
        impact_adjustment=max(-MAX_IMPACT, min(MAX_IMPACT, impact))
    )


# =============================================================================
# 15️⃣ GEO-RESILIENCE (Local Economic Shock Sensitivity)
# =============================================================================

@dataclass
class GeoResilienceResult:
    """Geo-resilience score."""
    score: float
    available: bool
    resilience_level: str  # High / Medium / Low
    impact_adjustment: int


def compute_geo_resilience(
    local_economic_index: Optional[float] = None,
    income_local_correlation: Optional[float] = None,
    employment_diversity_score: Optional[float] = None
) -> GeoResilienceResult:
    """
    Compute geo-resilience score.
    Low correlation with local economic shocks = high resilience.
    """
    if all(v is None for v in [local_economic_index, income_local_correlation]):
        return GeoResilienceResult(
            score=0.5, available=False, resilience_level="Unknown", impact_adjustment=0
        )
    
    local_index = local_economic_index if local_economic_index is not None else 0.5
    correlation = income_local_correlation if income_local_correlation is not None else 0.5
    diversity = employment_diversity_score if employment_diversity_score is not None else 0.5
    
    # Lower correlation with local economy = more resilient
    correlation_score = 1 - abs(correlation)
    
    # Higher local economic index = better environment
    environment_score = local_index
    
    # Higher diversity = more resilient
    diversity_score = diversity
    
    resilience_score = 0.4 * correlation_score + 0.3 * environment_score + 0.3 * diversity_score
    
    if resilience_score >= 0.7:
        level = "High"
    elif resilience_score >= 0.4:
        level = "Medium"
    else:
        level = "Low"
    
    MAX_IMPACT = 40
    impact = int((resilience_score - 0.5) * 2 * MAX_IMPACT)
    
    return GeoResilienceResult(
        score=round(resilience_score, 3),
        available=True,
        resilience_level=level,
        impact_adjustment=max(-MAX_IMPACT, min(MAX_IMPACT, impact))
    )


# =============================================================================
# COMPOSITE STABILITY SCORE
# =============================================================================

def compute_stability_composite(
    income_rhythm: Optional[IncomeRhythmResult] = None,
    savings_cadence: Optional[SavingsCadenceResult] = None,
    device_persistence: Optional[DevicePersistenceResult] = None,
    expense_elasticity: Optional[ExpenseElasticityResult] = None,
    utility_stability: Optional[UtilityStabilityResult] = None,
    merchant_loyalty: Optional[MerchantLoyaltyResult] = None,
    repayment_velocity: Optional[RepaymentVelocityResult] = None,
    geo_resilience: Optional[GeoResilienceResult] = None
) -> dict:
    """
    Compute composite stability score from all behavioral signals.
    
    Returns:
        dict with composite score, available signals, and capped total adjustment
    """
    signals = {
        "income_rhythm": income_rhythm,
        "savings_cadence": savings_cadence,
        "device_persistence": device_persistence,
        "expense_elasticity": expense_elasticity,
        "utility_stability": utility_stability,
        "merchant_loyalty": merchant_loyalty,
        "repayment_velocity": repayment_velocity,
        "geo_resilience": geo_resilience
    }
    
    available_signals = {k: v for k, v in signals.items() if v is not None and v.available}
    
    if not available_signals:
        return {
            "composite_score": 0.5,
            "available_count": 0,
            "total_adjustment": 0,
            "signal_details": {}
        }
    
    # Weights for each signal
    weights = {
        "income_rhythm": 0.20,
        "savings_cadence": 0.10,
        "device_persistence": 0.10,
        "expense_elasticity": 0.10,
        "utility_stability": 0.10,
        "merchant_loyalty": 0.10,
        "repayment_velocity": 0.15,
        "geo_resilience": 0.15
    }
    
    # Calculate weighted average of available signals
    total_weight = sum(weights[k] for k in available_signals.keys())
    weighted_score = sum(
        weights[k] * v.score for k, v in available_signals.items()
    ) / total_weight if total_weight > 0 else 0.5
    
    # Sum adjustments but cap total
    total_adjustment = sum(v.impact_adjustment for v in available_signals.values())
    
    # Cap stability composite to ±15% of 1000 = ±150
    MAX_COMPOSITE_IMPACT = 150
    total_adjustment = max(-MAX_COMPOSITE_IMPACT, min(MAX_COMPOSITE_IMPACT, total_adjustment))
    
    return {
        "composite_score": round(weighted_score, 3),
        "available_count": len(available_signals),
        "total_adjustment": total_adjustment,
        "signal_details": {
            k: {"score": v.score, "impact": v.impact_adjustment}
            for k, v in available_signals.items()
        }
    }
