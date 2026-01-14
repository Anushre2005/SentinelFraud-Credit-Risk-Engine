import json
import sys

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def run_test():
    with open("sample_request.json", "r") as f:
        payload = json.load(f)

    resp = client.post("/credit/assess", json=payload)
    assert resp.status_code == 200, f"Unexpected status: {resp.status_code} - {resp.text}"

    data = resp.json()

    # Basic checks
    assert data.get("user_id") == payload.get("user_id"), "User ID mismatch"
    assert "rule_score" in data and isinstance(data["rule_score"], int), "Missing or invalid rule_score"
    assert "ml_high_risk_probability" in data and isinstance(data["ml_high_risk_probability"], float), "Missing or invalid ml_high_risk_probability"
    assert "final_risk_score" in data and isinstance(data["final_risk_score"], int), "Missing or invalid final_risk_score"
    assert "risk_band" in data and data["risk_band"] in ("Low", "Moderate", "High"), "Unexpected risk_band"
    assert "model_accuracy_auc" in data, "model_accuracy_auc missing"
    assert "reason_codes" in data and isinstance(data["reason_codes"], list), "Missing reason_codes"

    print("Integration test passed. Response:")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    try:
        run_test()
    except AssertionError as e:
        print("TEST FAILED:", e)
        sys.exit(2)
    except Exception as e:
        print("ERROR running test:", e)
        sys.exit(3)
    else:
        sys.exit(0)
