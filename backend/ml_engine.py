import os
import joblib
import pandas as pd


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)


# --------------------------------------------------
# LOAD MODELS
# --------------------------------------------------

duration_model = joblib.load(
    os.path.join(
        MODEL_DIR,
        "duration_model.pkl"
    )
)

closure_model = joblib.load(
    os.path.join(
        MODEL_DIR,
        "closure_model.pkl"
    )
)

tii_model = joblib.load(
    os.path.join(
        MODEL_DIR,
        "tii_model.pkl"
    )
)

feature_columns = joblib.load(
    os.path.join(
        MODEL_DIR,
        "feature_columns.pkl"
    )
)


# --------------------------------------------------
# FEATURE PREPARATION
# --------------------------------------------------
def prepare_features(payload):

    row = {}

    for col in feature_columns:
        row[col] = payload.get(col, 0)

    X = pd.DataFrame([row])

    print("\n===== DATAFRAME =====")
    print(X)

    print("\n===== DTYPES =====")
    print(X.dtypes)

    return X
#---------------------------------------------------
# DURATION MODEL
# --------------------------------------------------

def predict_duration(payload):

    try:

        X = prepare_features(payload)

        prediction = duration_model.predict(X)

        return float(prediction[0])

    except Exception as e:

        print("\n===== DURATION ERROR =====")

        import traceback

        traceback.print_exc()

        print("\nERROR TYPE:")
        print(type(e))

        print("\nERROR MESSAGE:")
        print(e)

        raise


# --------------------------------------------------
# ROAD CLOSURE MODEL
# --------------------------------------------------

def predict_closure(payload):

    try:

        X = prepare_features(payload)

        probability = closure_model.predict_proba(X)[0][1]

        return float(probability)

    except Exception as e:

        print("\n===== CLOSURE ERROR =====")

        import traceback

        traceback.print_exc()

        print("\nERROR TYPE:")
        print(type(e))

        print("\nERROR MESSAGE:")
        print(e)

        raise


# --------------------------------------------------
# TRAFFIC IMPACT INDEX MODEL
# --------------------------------------------------
def predict_tii(payload):

    try:

        X = prepare_features(payload)

        prediction = tii_model.predict(X)

        value = float(prediction[0])

        value = max(0, min(100, value))

        return round(value, 2)

    except Exception as e:

        print("\n===== TII ERROR =====")

        import traceback

        traceback.print_exc()

        print("\nERROR TYPE:")
        print(type(e))

        print("\nERROR MESSAGE:")
        print(e)

        raise


# --------------------------------------------------
# COMBINED PREDICTION
# --------------------------------------------------

def predict_all(payload):

    duration = predict_duration(payload)

    closure_probability = predict_closure(payload)

    tii = predict_tii(payload)

    return {

        "predicted_duration_minutes":
            round(duration, 2),

        "road_closure_probability":
            round(
                closure_probability,
                4
            ),

        "traffic_impact_index":
            round(
                tii,
                2
            )
    }


# --------------------------------------------------
# LOCAL TEST
# --------------------------------------------------

if __name__ == "__main__":

    sample = {

        "event_type": "planned",

        "latitude": 12.9716,

        "longitude": 77.5946,

        "expected_attendance": 10000,

        "is_weekend": 1,

        "start_hour": 18
    }

    print(
        predict_all(sample)
    )