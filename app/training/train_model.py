import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import joblib
import os

# Load data from the same directory as this script
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "credit_training_data.csv")
df = pd.read_csv(csv_path)

# Map risk categories to numeric
risk_map = {"Low": 0, "Moderate": 1, "High": 2}
df["risk_numeric"] = df["risk_category"].map(risk_map)

# Features we'll use for training
FEATURES = [
    "age",
    "monthly_income",
    "transaction_count_30d",
    "avg_transaction_amount",
    "location_risk_score",
    "device_change_frequency",
    "previous_fraud_flag",
    "account_age_months",
    "chargeback_count",
]

X = df[FEATURES]
y = df["risk_numeric"]

# Stratified split to maintain class distribution
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Multinomial logistic regression for 3-class risk
model = LogisticRegression(max_iter=2000, solver='lbfgs', random_state=42)
model.fit(X_train, y_train)

# AUC for 'High' class (one-vs-rest)
preds_proba = model.predict_proba(X_test)
high_index = list(model.classes_).index(2) if 2 in model.classes_ else -1
if high_index != -1:
    preds_high = preds_proba[:, high_index]
    auc = roc_auc_score((y_test == 2).astype(int), preds_high)
else:
    auc = None

joblib.dump({"model": model, "auc": auc}, "app/artifacts/credit_model.joblib")

print("Model AUC (High vs rest):", round(auc, 3) if auc is not None else None)
