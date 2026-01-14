import joblib

bundle = joblib.load("app/artifacts/credit_model.joblib")
model = bundle["model"]
MODEL_AUC = bundle.get("auc", None)


def ml_score(features):
    # features: a list of values in the same order used in training
    probs = model.predict_proba([features])[0]
    # Find index for 'High' class (2);
    if 2 in list(model.classes_):
        high_idx = list(model.classes_).index(2)
        prob_high = float(probs[high_idx])
    else:
        # fallback to max probability if classes aren't labeled as 2
        prob_high = float(max(probs))

    score = int(prob_high * 1000)
    return prob_high, score

