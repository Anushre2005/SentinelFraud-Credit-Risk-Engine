"""
Post-Decision Credit Explanation Agent

Generates customer-safe, empathetic explanations for credit decisions.
Outputs both email and SMS/WhatsApp formats.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CreditDecision:
    """Input from upstream scoring system."""
    user_id: str
    user_name: str
    final_score: int
    risk_band: str  # Low / Moderate / High
    
    # Feature values
    monthly_income: float
    transaction_count_30d: int
    avg_transaction_amount: float
    location_risk_score: float
    device_change_frequency: int
    previous_fraud_flag: int
    account_age_months: int
    chargeback_count: int
    
    # Optional intermediate signals
    rule_score: Optional[int] = None
    ml_probability: Optional[float] = None
    reason_codes: Optional[list] = None


def _get_risk_label(band: str) -> str:
    """Customer-friendly risk descriptions."""
    labels = {
        "Low": "Excellent Standing",
        "Moderate": "Good Standing with Room for Growth",
        "High": "Needs Attention"
    }
    return labels.get(band, "Under Review")


def _analyze_negative_factors(decision: CreditDecision) -> list:
    """Identify factors that may have lowered the score."""
    factors = []
    
    if decision.previous_fraud_flag:
        factors.append({
            "title": "Account Security History",
            "explanation": "There was a previous security concern on your account that we're monitoring.",
            "impact": "High",
            "temporary": True,
            "tip": "Continue using secure practices, and this factor will naturally improve over time."
        })
    
    if decision.chargeback_count >= 2:
        factors.append({
            "title": "Transaction Disputes",
            "explanation": "Your account has had some transaction disputes in the past.",
            "impact": "Medium",
            "temporary": True,
            "tip": "Keeping transactions dispute-free for the next few months will help improve your standing."
        })
    elif decision.chargeback_count == 1:
        factors.append({
            "title": "Past Dispute",
            "explanation": "We noticed one past transaction dispute on your account.",
            "impact": "Low",
            "temporary": True,
            "tip": "This is minor and will improve naturally with continued good activity."
        })
    
    if decision.location_risk_score >= 0.7:
        factors.append({
            "title": "Geographic Activity",
            "explanation": "Some of your recent activity originated from locations we're unfamiliar with.",
            "impact": "Medium",
            "temporary": True,
            "tip": "Consistent activity from your usual locations will help build confidence."
        })
    
    if decision.device_change_frequency >= 5:
        factors.append({
            "title": "Device Patterns",
            "explanation": "We noticed you've accessed your account from several different devices recently.",
            "impact": "Medium",
            "temporary": True,
            "tip": "Using your primary devices regularly will help establish a trusted pattern."
        })
    
    if decision.account_age_months < 6:
        factors.append({
            "title": "Account History",
            "explanation": "Your account is still relatively new with us.",
            "impact": "Low",
            "temporary": True,
            "tip": "Time is on your side—building history with us will naturally strengthen your profile."
        })
    
    if decision.transaction_count_30d >= 100 and decision.avg_transaction_amount < 50:
        factors.append({
            "title": "Transaction Patterns",
            "explanation": "We noticed unusually high transaction activity with smaller amounts.",
            "impact": "Low",
            "temporary": True,
            "tip": "Maintaining steady, consistent transaction patterns helps build trust."
        })
    
    return factors


def _analyze_positive_factors(decision: CreditDecision) -> list:
    """Identify factors that helped the score."""
    positives = []
    
    if decision.monthly_income >= 3000:
        positives.append("Strong income stability")
    
    if decision.account_age_months >= 12:
        positives.append("Established account history")
    elif decision.account_age_months >= 6:
        positives.append("Growing account relationship")
    
    if decision.chargeback_count == 0:
        positives.append("Clean transaction history with no disputes")
    
    if not decision.previous_fraud_flag:
        positives.append("No security concerns on your account")
    
    if decision.device_change_frequency <= 2:
        positives.append("Consistent device usage patterns")
    
    if decision.location_risk_score < 0.3:
        positives.append("Trusted geographic activity")
    
    if 10 <= decision.transaction_count_30d <= 50:
        positives.append("Healthy transaction activity")
    
    return positives if positives else ["You're building a positive profile with us"]


def _generate_action_plan(decision: CreditDecision) -> dict:
    """Generate timeline-based improvement suggestions."""
    plan = {
        "short_term": [],   # 30-60 days
        "mid_term": [],     # 3-6 months
        "long_term": []     # 6-12 months
    }
    
    # Short-term actions
    if decision.device_change_frequency >= 4:
        plan["short_term"].append({
            "action": "Use your primary device for most transactions",
            "impact": "Medium"
        })
    
    if decision.transaction_count_30d >= 100:
        plan["short_term"].append({
            "action": "Maintain steady, predictable transaction patterns",
            "impact": "Low"
        })
    
    plan["short_term"].append({
        "action": "Keep your contact information and profile up to date",
        "impact": "Low"
    })
    
    # Mid-term actions
    if decision.chargeback_count >= 1:
        plan["mid_term"].append({
            "action": "Review transactions carefully before completing them to avoid disputes",
            "impact": "High"
        })
    
    if decision.location_risk_score >= 0.5:
        plan["mid_term"].append({
            "action": "Maintain consistent activity from your usual locations",
            "impact": "Medium"
        })
    
    plan["mid_term"].append({
        "action": "Keep your account active with regular, consistent usage",
        "impact": "Medium"
    })
    
    # Long-term actions
    if decision.account_age_months < 12:
        plan["long_term"].append({
            "action": "Continue building your history with us over time",
            "impact": "High"
        })
    
    if decision.previous_fraud_flag:
        plan["long_term"].append({
            "action": "Maintain strong security practices—previous concerns fade with time",
            "impact": "High"
        })
    
    plan["long_term"].append({
        "action": "Establish a consistent financial pattern that reflects your regular habits",
        "impact": "Medium"
    })
    
    return plan


def generate_email_explanation(decision: CreditDecision) -> str:
    """Generate full email explanation."""
    
    risk_label = _get_risk_label(decision.risk_band)
    negatives = _analyze_negative_factors(decision)
    positives = _analyze_positive_factors(decision)
    action_plan = _generate_action_plan(decision)
    
    # Build email
    lines = []
    
    # Subject line (returned separately)
    subject = f"Your Credit Profile Update — {risk_label}"
    
    # Greeting
    name = decision.user_name.split()[0] if decision.user_name else "Valued Customer"
    lines.append(f"Dear {name},")
    lines.append("")
    
    # Section 1: Summary
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("📊 YOUR CREDIT PROFILE SUMMARY")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    
    if decision.risk_band == "Low":
        lines.append(f"Great news! Based on your recent financial activity, your profile is in {risk_label}.")
        lines.append("You're doing an excellent job managing your account.")
    elif decision.risk_band == "Moderate":
        lines.append(f"Based on your recent financial activity, your profile is currently in {risk_label}.")
        lines.append("There are some areas where you're doing well, and a few where small improvements can help.")
    else:
        lines.append(f"We've reviewed your recent activity, and your profile currently {risk_label.lower()}.")
        lines.append("Don't worry—we're here to help you understand what's happening and how to improve.")
    
    lines.append("")
    
    # Section 2: Negative factors (if any)
    if negatives and decision.risk_band != "Low":
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("📋 FACTORS AFFECTING YOUR PROFILE")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        
        for factor in negatives[:3]:  # Limit to top 3
            lines.append(f"• {factor['title']}")
            lines.append(f"  {factor['explanation']}")
            if factor.get('temporary'):
                lines.append("  ✓ This is temporary and can improve over time.")
            lines.append("")
    
    # Section 3: Positive factors
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("✅ WHAT YOU'RE DOING WELL")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    
    for positive in positives[:4]:  # Limit to 4
        lines.append(f"• {positive}")
    lines.append("")
    
    # Section 4: Action Plan
    if decision.risk_band != "Low":
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("🎯 YOUR IMPROVEMENT ROADMAP")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        
        if action_plan["short_term"]:
            lines.append("📅 Next 30–60 Days:")
            for item in action_plan["short_term"][:2]:
                impact_icon = "🔹" if item["impact"] == "Low" else "🔸" if item["impact"] == "Medium" else "🔺"
                lines.append(f"   {impact_icon} {item['action']}")
            lines.append("")
        
        if action_plan["mid_term"]:
            lines.append("📅 Over the Next 3–6 Months:")
            for item in action_plan["mid_term"][:2]:
                impact_icon = "🔹" if item["impact"] == "Low" else "🔸" if item["impact"] == "Medium" else "🔺"
                lines.append(f"   {impact_icon} {item['action']}")
            lines.append("")
        
        if action_plan["long_term"]:
            lines.append("📅 Long-Term (6–12 Months):")
            for item in action_plan["long_term"][:2]:
                impact_icon = "🔹" if item["impact"] == "Low" else "🔸" if item["impact"] == "Medium" else "🔺"
                lines.append(f"   {impact_icon} {item['action']}")
            lines.append("")
        
        lines.append("Impact Guide: 🔺 High  🔸 Medium  🔹 Low")
        lines.append("")
    
    # Closing
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("Remember: Your profile is always evolving. Small, consistent actions")
    lines.append("today can lead to meaningful improvements over time.")
    lines.append("")
    lines.append("If you have any questions, our support team is here to help.")
    lines.append("")
    lines.append("Best regards,")
    lines.append("The SentinelFraud Team")
    lines.append("")
    lines.append("---")
    lines.append("This message is for informational purposes only and does not constitute")
    lines.append("financial advice. Your credit profile may change based on your activity.")
    
    return {
        "subject": subject,
        "body": "\n".join(lines)
    }


def generate_sms_explanation(decision: CreditDecision) -> str:
    """Generate short SMS/WhatsApp message (≤6 lines)."""
    
    name = decision.user_name.split()[0] if decision.user_name else ""
    greeting = f"Hi {name}! " if name else ""
    
    if decision.risk_band == "Low":
        return (
            f"{greeting}Great news! 🎉\n"
            f"Your credit profile is in excellent standing.\n"
            f"Keep up the great work!\n"
            f"Questions? Reply HELP."
        )
    
    elif decision.risk_band == "Moderate":
        # Pick top improvement tip
        tip = "Keep your account active with consistent usage."
        if decision.previous_fraud_flag:
            tip = "Continue secure practices—your profile will strengthen over time."
        elif decision.chargeback_count >= 1:
            tip = "Avoiding disputes will help improve your standing."
        
        return (
            f"{greeting}Your credit profile update 📊\n"
            f"Status: Good standing with room to grow\n"
            f"Tip: {tip}\n"
            f"Check your email for details.\n"
            f"Questions? Reply HELP."
        )
    
    else:  # High
        return (
            f"{greeting}Your credit profile needs attention 📋\n"
            f"We've sent you an email with details and\n"
            f"personalized steps to help improve it.\n"
            f"We're here to help—reply HELP anytime."
        )


def generate_explanation(decision: CreditDecision) -> dict:
    """
    Main entry point: Generate both email and SMS explanations.
    
    Args:
        decision: CreditDecision object with all relevant data
        
    Returns:
        dict with 'email' and 'sms' keys
    """
    email = generate_email_explanation(decision)
    sms = generate_sms_explanation(decision)
    
    return {
        "email": email,
        "sms": sms
    }


# Example usage
if __name__ == "__main__":
    # Sample decision from upstream system
    sample_decision = CreditDecision(
        user_id="U_0042",
        user_name="Priya Sharma",
        final_score=420,
        risk_band="Moderate",
        monthly_income=4500.00,
        transaction_count_30d=35,
        avg_transaction_amount=120.50,
        location_risk_score=0.45,
        device_change_frequency=3,
        previous_fraud_flag=0,
        account_age_months=8,
        chargeback_count=1,
        rule_score=380,
        ml_probability=0.22,
        reason_codes=["R11"]
    )
    
    result = generate_explanation(sample_decision)
    
    print("=" * 60)
    print("EMAIL VERSION")
    print("=" * 60)
    print(f"Subject: {result['email']['subject']}")
    print("-" * 60)
    print(result['email']['body'])
    print()
    print("=" * 60)
    print("SMS VERSION")
    print("=" * 60)
    print(result['sms'])
