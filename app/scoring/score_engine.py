import json
import os
from .feature_mapper import map_features

ROOT = os.path.dirname(__file__)
WEIGHTS_PATH = os.path.join(ROOT, "weights.json")
with open(WEIGHTS_PATH, "r", encoding="utf-8") as f:
    WEIGHTS = json.load(f)

def calculate_credit_score(req):
    features = map_features(req)
    weighted_sum = 0

    for feature, data in features.items():
        weighted_sum += data["score"] * WEIGHTS[feature]

    final_score = round(weighted_sum * 10)

    risk_band = (
        "Low" if final_score >= 750 else
        "Medium" if final_score >= 600 else
        "High"
    )

    return final_score, risk_band, features
