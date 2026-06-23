import os
import joblib
import pandas as pd
import numpy as np
import traceback


# ==================================================
# PATHS
# ==================================================

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")


# ==================================================
# MODEL LOADER
# ==================================================

def load_model(filename):
    path = os.path.join(MODEL_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing model file: {path}")
    return joblib.load(path)


# ==================================================
# LOAD MODELS
# ==================================================

try:
    duration_model  = load_model("duration_model.pkl")
    closure_model   = load_model("closure_model.pkl")
    tii_model       = load_model("tii_model.pkl")
    feature_columns = load_model("feature_columns.pkl")
    risk_scaler     = load_model("risk_scaler.pkl")

except FileNotFoundError as e:
    print(f"\n❌ STARTUP ERROR: {e}")
    print("Run gridlock3.ipynb to generate all .pkl files.")
    raise SystemExit(1)


print("\n==========================")
print("TrafficSense Models Loaded")
print("==========================")
print(f"Features Loaded: {len(feature_columns)}")


# ==================================================
# RISK COLUMNS — must match notebook exactly
# ==================================================

RISK_COLS = [
    "event_frequency_score",
    "closure_risk",
    "duration_risk",
    "junction_count",
    "junction_duration",
    "corridor_count",
    "corridor_duration",
    "historical_impact"
]


# ==================================================
# FEATURE PREPARATION
# ==================================================

def prepare_features(payload):
    row = {col: payload.get(col, 0) for col in feature_columns}
    X   = pd.DataFrame([row])

    cols_to_scale = [c for c in RISK_COLS if c in X.columns]
    if cols_to_scale:
        X[cols_to_scale] = risk_scaler.transform(X[cols_to_scale])

    return X


# ==================================================
# DURATION MODEL
# ==================================================

def predict_duration(payload):
    try:
        X          = prepare_features(payload)
        prediction = duration_model.predict(X)
        duration   = float(prediction[0])
        return round(max(1, min(duration, 1440)), 2)
    except Exception:
        print("\n===== DURATION ERROR =====")
        traceback.print_exc()
        raise


# ==================================================
# ROAD CLOSURE MODEL
# ==================================================

def predict_closure(payload):
    try:
        X           = prepare_features(payload)
        probability = closure_model.predict_proba(X)[0][1]
        return round(float(max(0, min(probability, 1))), 4)
    except Exception:
        print("\n===== CLOSURE ERROR =====")
        traceback.print_exc()
        raise


# ==================================================
# TRAFFIC IMPACT INDEX
# ==================================================

def predict_tii(payload):
    try:
        X          = prepare_features(payload)
        prediction = tii_model.predict(X)
        value      = float(prediction[0])
        return round(max(0, min(value, 100)), 2)
    except Exception:
        print("\n===== TII ERROR =====")
        traceback.print_exc()
        raise


# ==================================================
# SHAP EXPLAINABILITY
# Replaces the old rule-based generate_explanation().
# Falls back to rule-based if shap is not installed.
# ==================================================

def generate_explanation(payload):
    """
    Return a list of (feature_name, shap_value, display_label) tuples
    for the top drivers of the TII prediction.
    Falls back gracefully if shap is unavailable.
    """
    try:
        import shap

        X = prepare_features(payload)

        # Use the final estimator inside the pipeline
        estimator = tii_model.named_steps.get(
            "model",
            list(tii_model.named_steps.values())[-1]
        )

        # ColumnTransformer transforms X before reaching estimator;
        # apply the prep step first if it exists
        if "prep" in tii_model.named_steps:
            X_transformed = tii_model.named_steps["prep"].transform(X)
        else:
            X_transformed = X.values

        explainer    = shap.TreeExplainer(estimator)
        shap_values  = explainer.shap_values(X_transformed)

        if isinstance(shap_values, list):
            sv = shap_values[0]
        else:
            sv = shap_values

        sv_flat = sv[0] if sv.ndim > 1 else sv

        # Map back to original feature names (best effort)
        try:
            feature_names = (
                tii_model.named_steps["prep"].get_feature_names_out()
                if "prep" in tii_model.named_steps
                else feature_columns
            )
        except Exception:
            feature_names = [f"f{i}" for i in range(len(sv_flat))]

        pairs = sorted(
            zip(feature_names, sv_flat),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]

        labels = []
        for fname, sval in pairs:
            direction = "↑ increases" if sval > 0 else "↓ decreases"
            clean     = fname.replace("remainder__", "").replace("cat__", "").replace("_", " ").title()
            labels.append(f"{clean} {direction} impact (SHAP {sval:+.2f})")

        return labels

    except Exception:
        # Rule-based fallback
        reasons = []
        if payload.get("peak_hour", 0) == 1:
            reasons.append("Peak Hour Traffic")
        if payload.get("closure_risk", 0) >= 70:
            reasons.append("High Closure Risk")
        if payload.get("historical_impact", 0) >= 70:
            reasons.append("Historically Congested Area")
        if payload.get("event_frequency_score", 0) > 10:
            reasons.append("Large Expected Crowd")
        if not reasons:
            reasons.append("Normal Traffic Conditions")
        return reasons


# ==================================================
# COMBINED PREDICTION
# ==================================================

def predict_all(payload):
    duration            = predict_duration(payload)
    closure_probability = predict_closure(payload)
    tii                 = predict_tii(payload)
    explanation         = generate_explanation(payload)

    return {
        "predicted_duration_minutes":  duration,
        "road_closure_probability":    closure_probability,
        "traffic_impact_index":        tii,
        "explanation":                 explanation
    }


# ==================================================
# LOCAL TEST
# ==================================================

if __name__ == "__main__":
    sample = {
        "event_type": "planned", "event_cause": "accident",
        "veh_type": "car", "corridor": "Mysore Road",
        "zone": "South Zone 1", "junction": "Kengeri",
        "latitude": 12.9141, "longitude": 77.4820,
        "hour": 18, "weekday": 1, "month": 6,
        "weekend": 0, "peak_hour": 1,
        "event_frequency_score": 5,
        "closure_risk": 70, "duration_risk": 50,
        "junction_count": 10, "junction_duration": 30,
        "corridor_count": 20, "corridor_duration": 45,
        "historical_impact": 40
    }
    print(predict_all(sample))
