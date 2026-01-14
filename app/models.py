
from pydantic import BaseModel
from typing import Optional


class CreditRequest(BaseModel):
    """Credit assessment request model.
    
    Core fields are required. All behavioral, network, and stability
    fields are optional with defaults for backward compatibility.
    """
    # =========================================================================
    # CORE USER FIELDS (Required)
    # =========================================================================
    user_id: str
    age: int
    occupation: str
    monthly_income: float
    transaction_count_30d: int
    avg_transaction_amount: float
    location_risk_score: float
    device_change_frequency: int
    previous_fraud_flag: int
    account_age_months: int
    chargeback_count: int
    
    # =========================================================================
    # COMMUNITY TRUST COEFFICIENT (CTC) - Network Signals (Optional)
    # =========================================================================
    avg_contact_credit_score: Optional[float] = None  # 300-900 range
    low_risk_contact_ratio: Optional[float] = None    # 0-1 ratio
    high_risk_contact_ratio: Optional[float] = None   # 0-1 ratio
    network_stability_ratio: Optional[float] = None   # 0-1 ratio
    
    # =========================================================================
    # ADDRESS STABILITY (Optional)
    # =========================================================================
    address_change_count_12m: Optional[int] = None
    current_address_tenure_months: Optional[int] = None
    
    # =========================================================================
    # INCOME RHYTHM STABILITY (Optional) - Signal 1
    # =========================================================================
    income_coefficient_of_variation: Optional[float] = None  # CV of monthly income
    seasonal_adjustment_factor: Optional[float] = None       # 0-1
    income_frequency_months: Optional[int] = None            # Months with income in last 12
    
    # =========================================================================
    # SAVINGS CADENCE & MICRO-ESCROWS (Optional) - Signal 2
    # =========================================================================
    micro_saves_per_month: Optional[float] = None
    savings_persistence_months: Optional[int] = None
    has_escrow_commitment: Optional[bool] = None
    
    # =========================================================================
    # DEVICE PERSISTENCE & AUTHENTICITY (Optional) - Signal 4
    # =========================================================================
    device_tenure_months: Optional[int] = None
    os_change_count_12m: Optional[int] = None
    app_reinstall_count: Optional[int] = None
    
    # =========================================================================
    # EXPENSE-TO-INCOME ELASTICITY (Optional) - Signal 5
    # =========================================================================
    expense_income_correlation: Optional[float] = None  # -1 to 1
    expense_volatility: Optional[float] = None          # 0-1
    
    # =========================================================================
    # UTILITY STABILITY (Optional) - Signal 6
    # =========================================================================
    utility_payment_ontime_ratio: Optional[float] = None  # 0-1
    utility_payment_variance: Optional[float] = None      # 0-1
    utility_months_active: Optional[int] = None
    
    # =========================================================================
    # MERCHANT LOYALTY & REFUND BEHAVIOR (Optional) - Signal 8
    # =========================================================================
    repeat_merchant_ratio: Optional[float] = None   # 0-1
    refund_ratio: Optional[float] = None            # 0-1
    dispute_frequency: Optional[float] = None       # 0-1
    
    # =========================================================================
    # EMPLOYER PAYROLL FINGERPRINT (Optional) - Signal 9
    # =========================================================================
    payroll_regularity_score: Optional[float] = None  # 0-1
    employer_size_proxy: Optional[str] = None         # small/medium/large/unknown
    
    # =========================================================================
    # REPAYMENT VELOCITY (Optional) - Signal 14
    # =========================================================================
    early_payment_ratio: Optional[float] = None   # 0-1
    ontime_payment_ratio: Optional[float] = None  # 0-1
    late_payment_ratio: Optional[float] = None    # 0-1
    
    # =========================================================================
    # GEO-RESILIENCE / LOCAL ECONOMIC SHOCK (Optional) - Signal 15
    # =========================================================================
    local_economic_index: Optional[float] = None        # 0-1
    income_local_correlation: Optional[float] = None    # -1 to 1
    employment_diversity_score: Optional[float] = None  # 0-1
    
    # =========================================================================
    # PEER ATTESTATION (Optional) - Signal 12
    # =========================================================================
    has_peer_attestation: Optional[bool] = None
    attestation_freshness_days: Optional[int] = None
    
    class Config:
        extra = "ignore"  # Forward compatibility

