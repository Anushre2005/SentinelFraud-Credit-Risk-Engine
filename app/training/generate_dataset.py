import random
import pandas as pd
import numpy as np

# Reproducible
random.seed(42)
np.random.seed(42)

OCCUPATIONS = [
    "student",
    "salaried",
    "freelancer",
    "business_owner",
    "retiree",
    "contractor",
    "gig_worker",
    "self_employed",
    "unemployed",
    "executive",
]

# Helper to create realistic profiles per occupation
def base_profile(occupation):
    if occupation == "student":
        return {
            "age": random.randint(18, 25),
            "monthly_income": round(random.uniform(200, 800), 2),
            "transaction_count_30d": np.random.poisson(10),
            "avg_transaction_amount": round(random.uniform(5, 50), 2),
            "location_risk_score": round(np.random.beta(2, 8), 2),
            "device_change_frequency": random.randint(0, 1),
            "previous_fraud_flag": 0,
            "account_age_months": random.randint(1, 36),
            "chargeback_count": 0,
        }
    if occupation == "salaried":
        return {
            "age": random.randint(22, 60),
            "monthly_income": round(random.uniform(1500, 8000), 2),
            "transaction_count_30d": np.random.poisson(30),
            "avg_transaction_amount": round(random.uniform(20, 300), 2),
            "location_risk_score": round(np.random.beta(1.5, 6), 2),
            "device_change_frequency": random.randint(0, 2),
            "previous_fraud_flag": 0,
            "account_age_months": random.randint(6, 120),
            "chargeback_count": 0,
        }
    if occupation == "freelancer":
        return {
            "age": random.randint(25, 50),
            "monthly_income": round(random.uniform(800, 5000), 2),
            "transaction_count_30d": np.random.poisson(40),
            "avg_transaction_amount": round(random.uniform(30, 500), 2),
            "location_risk_score": round(np.random.beta(2, 4), 2),
            "device_change_frequency": random.randint(0, 3),
            "previous_fraud_flag": 0,
            "account_age_months": random.randint(3, 84),
            "chargeback_count": random.randint(0, 1),
        }
    if occupation == "business_owner":
        return {
            "age": random.randint(30, 65),
            "monthly_income": round(random.uniform(3000, 20000), 2),
            "transaction_count_30d": np.random.poisson(120),
            "avg_transaction_amount": round(random.uniform(50, 2000), 2),
            "location_risk_score": round(np.random.beta(2, 3), 2),
            "device_change_frequency": random.randint(0, 5),
            "previous_fraud_flag": 0,
            "account_age_months": random.randint(12, 180),
            "chargeback_count": random.randint(0, 3),
        }
    if occupation == "retiree":
        return {
            "age": random.randint(60, 85),
            "monthly_income": round(random.uniform(800, 3000), 2),
            "transaction_count_30d": np.random.poisson(8),
            "avg_transaction_amount": round(random.uniform(10, 200), 2),
            "location_risk_score": round(np.random.beta(1, 4), 2),
            "device_change_frequency": random.randint(0, 1),
            "previous_fraud_flag": 0,
            "account_age_months": random.randint(24, 240),
            "chargeback_count": 0,
        }
    if occupation == "contractor":
        return {
            "age": random.randint(25, 55),
            "monthly_income": round(random.uniform(1000, 7000), 2),
            "transaction_count_30d": np.random.poisson(25),
            "avg_transaction_amount": round(random.uniform(20, 400), 2),
            "location_risk_score": round(np.random.beta(2, 5), 2),
            "device_change_frequency": random.randint(0, 3),
            "previous_fraud_flag": 0,
            "account_age_months": random.randint(3, 96),
            "chargeback_count": random.randint(0, 2),
        }
    if occupation == "gig_worker":
        return {
            "age": random.randint(20, 50),
            "monthly_income": round(random.uniform(400, 4000), 2),
            "transaction_count_30d": np.random.poisson(60),
            "avg_transaction_amount": round(random.uniform(10, 150), 2),
            "location_risk_score": round(np.random.beta(3, 4), 2),
            "device_change_frequency": random.randint(0, 4),
            "previous_fraud_flag": 0,
            "account_age_months": random.randint(1, 72),
            "chargeback_count": random.randint(0, 2),
        }
    if occupation == "self_employed":
        return {
            "age": random.randint(28, 60),
            "monthly_income": round(random.uniform(1500, 15000), 2),
            "transaction_count_30d": np.random.poisson(80),
            "avg_transaction_amount": round(random.uniform(30, 1200), 2),
            "location_risk_score": round(np.random.beta(2, 3), 2),
            "device_change_frequency": random.randint(0, 5),
            "previous_fraud_flag": 0,
            "account_age_months": random.randint(6, 240),
            "chargeback_count": random.randint(0, 4),
        }
    if occupation == "unemployed":
        return {
            "age": random.randint(18, 65),
            "monthly_income": round(random.uniform(0, 1500), 2),
            "transaction_count_30d": np.random.poisson(12),
            "avg_transaction_amount": round(random.uniform(5, 200), 2),
            "location_risk_score": round(np.random.beta(2, 5), 2),
            "device_change_frequency": random.randint(0, 3),
            "previous_fraud_flag": 0,
            "account_age_months": random.randint(1, 60),
            "chargeback_count": random.randint(0, 2),
        }
    if occupation == "executive":
        return {
            "age": random.randint(30, 65),
            "monthly_income": round(random.uniform(7000, 30000), 2),
            "transaction_count_30d": np.random.poisson(40),
            "avg_transaction_amount": round(random.uniform(100, 5000), 2),
            "location_risk_score": round(np.random.beta(1, 3), 2),
            "device_change_frequency": random.randint(0, 2),
            "previous_fraud_flag": 0,
            "account_age_months": random.randint(12, 360),
            "chargeback_count": random.randint(0, 1),
        }
    return {}


def network_profile(occupation):
    """
    Generate synthetic Community Trust Coefficient (CTC) network data.
    Based on occupation type for realism.
    
    Returns:
        dict with network-related fields
    """
    if occupation in ["executive", "salaried"]:
        # High-quality stable networks
        return {
            "avg_contact_credit_score": round(random.uniform(680, 850), 0),
            "low_risk_contact_ratio": round(np.random.beta(7, 2), 2),
            "high_risk_contact_ratio": round(np.random.beta(1, 8), 2),
            "network_stability_ratio": round(np.random.beta(7, 2), 2),
        }
    elif occupation in ["business_owner", "self_employed"]:
        # Good but variable networks
        return {
            "avg_contact_credit_score": round(random.uniform(600, 780), 0),
            "low_risk_contact_ratio": round(np.random.beta(5, 3), 2),
            "high_risk_contact_ratio": round(np.random.beta(2, 6), 2),
            "network_stability_ratio": round(np.random.beta(5, 3), 2),
        }
    elif occupation in ["freelancer", "contractor"]:
        # Mixed quality networks
        return {
            "avg_contact_credit_score": round(random.uniform(550, 720), 0),
            "low_risk_contact_ratio": round(np.random.beta(4, 4), 2),
            "high_risk_contact_ratio": round(np.random.beta(3, 5), 2),
            "network_stability_ratio": round(np.random.beta(4, 4), 2),
        }
    elif occupation in ["student", "gig_worker"]:
        # Younger, less established networks
        return {
            "avg_contact_credit_score": round(random.uniform(450, 650), 0),
            "low_risk_contact_ratio": round(np.random.beta(3, 4), 2),
            "high_risk_contact_ratio": round(np.random.beta(3, 4), 2),
            "network_stability_ratio": round(np.random.beta(2, 5), 2),
        }
    elif occupation == "retiree":
        # Stable but smaller networks
        return {
            "avg_contact_credit_score": round(random.uniform(620, 750), 0),
            "low_risk_contact_ratio": round(np.random.beta(6, 3), 2),
            "high_risk_contact_ratio": round(np.random.beta(1, 7), 2),
            "network_stability_ratio": round(np.random.beta(8, 2), 2),
        }
    else:  # unemployed and others
        # Less stable, lower quality networks
        return {
            "avg_contact_credit_score": round(random.uniform(400, 600), 0),
            "low_risk_contact_ratio": round(np.random.beta(2, 5), 2),
            "high_risk_contact_ratio": round(np.random.beta(4, 4), 2),
            "network_stability_ratio": round(np.random.beta(2, 5), 2),
        }


def address_profile(occupation):
    """
    Generate synthetic address stability data.
    Based on occupation type for realism.
    
    Returns:
        dict with address-related fields
    """
    if occupation in ["executive", "retiree"]:
        # Very stable addresses
        return {
            "address_change_count_12m": random.choices([0, 0, 0, 1], weights=[70, 20, 5, 5])[0],
            "current_address_tenure_months": random.randint(24, 120),
        }
    elif occupation in ["salaried", "business_owner"]:
        # Stable addresses
        return {
            "address_change_count_12m": random.choices([0, 1, 1, 2], weights=[50, 30, 15, 5])[0],
            "current_address_tenure_months": random.randint(12, 72),
        }
    elif occupation in ["self_employed", "contractor"]:
        # Moderate stability
        return {
            "address_change_count_12m": random.choices([0, 1, 2, 2], weights=[30, 40, 20, 10])[0],
            "current_address_tenure_months": random.randint(6, 48),
        }
    elif occupation in ["freelancer", "gig_worker"]:
        # More mobile
        return {
            "address_change_count_12m": random.choices([0, 1, 2, 3], weights=[20, 35, 30, 15])[0],
            "current_address_tenure_months": random.randint(3, 36),
        }
    elif occupation == "student":
        # High mobility (dorms, rentals)
        return {
            "address_change_count_12m": random.choices([0, 1, 2, 3], weights=[15, 25, 40, 20])[0],
            "current_address_tenure_months": random.randint(1, 24),
        }
    else:  # unemployed
        # Variable, sometimes unstable
        return {
            "address_change_count_12m": random.choices([0, 1, 2, 3, 4], weights=[20, 25, 25, 20, 10])[0],
            "current_address_tenure_months": random.randint(1, 36),
        }


def compute_risk_category(rec):
    # Normalize components
    tx_count_norm = min(rec["transaction_count_30d"] / 200, 1.0)
    avg_tx_norm = min(rec["avg_transaction_amount"] / 2000, 1.0)
    device_norm = min(rec["device_change_frequency"] / 10, 1.0)
    chargeback_norm = min(rec["chargeback_count"] / 5, 1.0)

    # Weighted risk score (higher -> higher risk)
    score = (
        0.35 * tx_count_norm +
        0.25 * rec["location_risk_score"] +
        0.15 * device_norm +
        0.15 * chargeback_norm +
        0.10 * rec["previous_fraud_flag"]
    )

    if score < 0.25:
        return "Low"
    if score < 0.50:
        return "Moderate"
    return "High"


def inject_noise(records, noise_rate=0.10):
    """Inject controlled realistic noise into the dataset.
    
    Types of noise:
    - Feature inconsistencies (low income + high transaction volume)
    - Borderline values between risk categories
    - Contradictory signals (good profile + fraud flag)
    """
    n = len(records)
    k = max(1, int(round(n * noise_rate)))
    noisy_indices = random.sample(range(n), k)

    noise_types = ["high_income_fraud", "low_income_high_volume", "high_location_risk", 
                   "device_anomaly", "borderline_moderate"]

    for i in noisy_indices:
        rec = records[i]
        noise_type = random.choice(noise_types)
        
        if noise_type == "high_income_fraud":
            # High income but previous fraud flag (contradictory)
            rec["previous_fraud_flag"] = 1
            rec["chargeback_count"] = max(rec["chargeback_count"], random.randint(2, 4))
            rec["location_risk_score"] = min(1.0, rec["location_risk_score"] + 0.3)
        elif noise_type == "low_income_high_volume":
            # Low income but sudden high transaction volume
            rec["transaction_count_30d"] = max(rec["transaction_count_30d"] * 4, 150)
            rec["avg_transaction_amount"] = round(rec["avg_transaction_amount"] * 0.5, 2)
            rec["device_change_frequency"] = max(rec["device_change_frequency"], 5)
        elif noise_type == "high_location_risk":
            # Elevated location risk with normal behavior
            rec["location_risk_score"] = round(random.uniform(0.7, 0.95), 2)
            rec["device_change_frequency"] = max(rec["device_change_frequency"], 4)
        elif noise_type == "device_anomaly":
            # Device changes suggesting account takeover attempt
            rec["device_change_frequency"] = random.randint(6, 10)
            rec["previous_fraud_flag"] = 1
        else:  # borderline_moderate
            # Slight adjustments to push towards borderline
            rec["location_risk_score"] = round(random.uniform(0.4, 0.6), 2)
            rec["chargeback_count"] = random.randint(1, 2)

        # Recompute risk category after noise
        rec["risk_category"] = compute_risk_category(rec)

    return records


def generate_dataset(num_rows=1000):
    """
    Generate synthetic fraud/risk classification dataset.
    
    Args:
        num_rows: Number of rows to generate (default 1000)
    
    Returns:
        pandas DataFrame with synthetic user data
    """
    records = []
    num_occupations = len(OCCUPATIONS)
    rows_per_occupation = num_rows // num_occupations  # 100 per occupation for 1000 rows
    extra_rows = num_rows % num_occupations  # Handle remainder
    
    user_counter = 1
    
    for occ_idx, occ in enumerate(OCCUPATIONS):
        # Determine how many rows for this occupation
        rows_for_this_occ = rows_per_occupation
        if occ_idx < extra_rows:
            rows_for_this_occ += 1
        
        for _ in range(rows_for_this_occ):
            base = base_profile(occ)
            network = network_profile(occ)
            address = address_profile(occ)
            rec = {
                "user_id": f"U_{user_counter:04d}",
                "occupation": occ,
                **base,
                **network,
                **address,
            }
            rec["risk_category"] = compute_risk_category(rec)
            records.append(rec)
            user_counter += 1

    # Inject ~10% realistic noise (controlled)
    records = inject_noise(records, noise_rate=0.10)

    df = pd.DataFrame(records)

    # Ensure exactly num_rows distinct rows
    assert len(df) == num_rows, f"Expected {num_rows} rows, got {len(df)}"
    assert df["user_id"].is_unique, "Duplicate user IDs detected"
    
    # Verify all risk categories are represented
    categories = df["risk_category"].unique()
    assert "Low" in categories, "Low risk category missing"
    assert "Moderate" in categories, "Moderate risk category missing"
    assert "High" in categories, "High risk category missing"

    # Save dataset used by training (in same directory as this script)
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "credit_training_data.csv")
    df.to_csv(csv_path, index=False)

    return df


if __name__ == "__main__":
    df = generate_dataset()


