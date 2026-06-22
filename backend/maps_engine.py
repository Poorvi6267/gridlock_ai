import os
import joblib
import pandas as pd
import traceback


# ==================================================
# PATHS
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)


# ==================================================
# MODEL LOADER
# ==================================================

def load_model(filename):

    path = os.path.join(
        MODEL_DIR,
        filename
    )

    if not os.path.exists(path):

        raise FileNotFoundError(
            f"Missing model file: {path}"
        )

    return joblib.load(path)


# ==================================================
# LOAD MODELS
# ==================================================

duration_model = load_model(
    "duration_model.pkl"
)

closure_model = load_model(
    "closure_model.pkl"
)

tii_model = load_model(
    "tii_model.pkl"
)

feature_columns = load_model(
    "feature_columns.pkl"
)


print("\n==========================")
print("TrafficSense Models Loaded")
print("==========================")
print(
    f"Features Loaded: {len(feature_columns)}"
)


# ==================================================
# FEATURE PREPARATION
# ==================================================

def prepare_features(payload):

    row = {}

    for col in feature_columns:

        row[col] = payload.get(
            col,
            0
        )

    X = pd.DataFrame([row])

    return X


# ==================================================
# DURATION MODEL
# ==================================================

def predict_duration(payload):

    try:

        X = prepare_features(
            payload
        )

        prediction = duration_model.predict(X)

        duration = float(
            prediction[0]
        )

        # ------------------------------------------
        # SAFETY CAP FOR DEMO
        # ------------------------------------------

        duration = max(
            1,
            min(duration, 1440)
        )

        return round(
            duration,
            2
        )

    except Exception:

        print(
            "\n===== DURATION ERROR ====="
        )

        traceback.print_exc()

        raise


# ==================================================
# ROAD CLOSURE MODEL
# ==================================================

def predict_closure(payload):

    try:

        X = prepare_features(
            payload
        )

        probability = (
            closure_model
            .predict_proba(X)[0][1]
        )

        probability = max(
            0,
            min(probability, 1)
        )

        return round(
            float(probability),
            4
        )

    except Exception:

        print(
            "\n===== CLOSURE ERROR ====="
        )

        traceback.print_exc()

        raise


# ==================================================
# TRAFFIC IMPACT INDEX
# ==================================================

def predict_tii(payload):

    try:

        X = prepare_features(
            payload
        )

        prediction = tii_model.predict(X)

        value = float(
            prediction[0]
        )

        value = max(
            0,
            min(value, 100)
        )

        return round(
            value,
            2
        )

    except Exception:

        print(
            "\n===== TII ERROR ====="
        )

        traceback.print_exc()

        raise


# ==================================================
# EXPLAINABILITY
# ==================================================

def generate_explanation(payload):

    reasons = []

    if payload.get(
        "peak_hour",
        0
    ) == 1:

        reasons.append(
            "Peak Hour Traffic"
        )

    if payload.get(
        "closure_risk",
        0
    ) > 70:

        reasons.append(
            "High Closure Risk"
        )

    if payload.get(
        "historical_impact",
        0
    ) > 70:

        reasons.append(
            "Historically Congested Area"
        )

    if payload.get(
        "event_frequency_score",
        0
    ) > 10:

        reasons.append(
            "Large Expected Crowd"
        )

    if not reasons:

        reasons.append(
            "Normal Traffic Conditions"
        )

    return reasons


# ==================================================
# COMBINED PREDICTION
# ==================================================

def predict_all(payload):

    duration = predict_duration(
        payload
    )

    closure_probability = (
        predict_closure(payload)
    )

    tii = predict_tii(
        payload
    )

    explanation = (
        generate_explanation(
            payload
        )
    )

    return {

        "predicted_duration_minutes":
            duration,

        "road_closure_probability":
            closure_probability,

        "traffic_impact_index":
            tii,

        "explanation":
            explanation
    }


# ==================================================
# LOCAL TEST
# ==================================================

if __name__ == "__main__":

    sample = {

        "event_type": "planned",

        "latitude": 12.9716,

        "longitude": 77.5946,

        "event_frequency_score": 15,

        "closure_risk": 80,

        "historical_impact": 60,

        "peak_hour": 1
    }

    print(
        predict_all(sample)
    )