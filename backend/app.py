from fastapi import FastAPI
from pydantic import BaseModel

from resource_engine import recommend_resources
from diversion import recommend_diversion

from ml_engine import (
    predict_duration,
    predict_closure,
    predict_tii,
    predict_all
)

app = FastAPI(
    title="Gridlock AI",
    version="1.0.0",
    description="Traffic Impact Intelligence Platform"
)


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/")
def home():

    return {
        "message": "Gridlock AI Running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ==================================================
# RESOURCE REQUEST
# ==================================================

class ResourceRequest(BaseModel):

    event_type: str
    corridor: str
    junction: str
    tii: float


# ==================================================
# ML PREDICTION REQUEST
# ==================================================

class PredictionRequest(BaseModel):

    event_type: str
    event_cause: str
    veh_type: str

    corridor: str
    zone: str
    junction: str

    latitude: float
    longitude: float

    hour: int
    weekday: int
    month: int

    weekend: int
    peak_hour: int

    event_frequency_score: float

    closure_risk: float
    duration_risk: float

    junction_count: int
    junction_duration: float

    corridor_count: int
    corridor_duration: float

    historical_impact: float


# ==================================================
# RESOURCE RECOMMENDATION
# ==================================================

@app.post("/recommend")
def recommend(
    request: ResourceRequest
):

    resource_result = recommend_resources(
        request.event_type,
        request.corridor,
        request.junction,
        request.tii
    )

    diversion_result = recommend_diversion(
        request.corridor,
        request.tii
    )

    return {

        "priority":
            resource_result["priority"],

        "risk_score":
            resource_result["risk_score"],

        "resources": {

            "traffic_police":
                resource_result["traffic_police"],

            "barricades":
                resource_result["barricades"],

            "tow_trucks":
                resource_result["tow_trucks"],

            "ambulances":
                resource_result["ambulances"]
        },

        "diversion":
            diversion_result
    }


# ==================================================
# ML PREDICTION
# ==================================================

@app.post("/predict")
def predict(
    request: PredictionRequest
):

    try:

        payload = request.model_dump()

        result = predict_all(payload)

        return result

    except Exception as e:

        print("\n===== PREDICT ERROR =====")
        print(e)

        return {
            "error": str(e)
        }


# ==================================================
# DURATION ONLY
# ==================================================

@app.post("/predict-duration")
def predict_duration_api(
    request: PredictionRequest
):

    try:

        payload = request.model_dump()

        duration = predict_duration(payload)

        return {
            "predicted_duration_minutes":
                round(duration, 2)
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# ==================================================
# CLOSURE ONLY
# ==================================================

@app.post("/predict-closure")
def predict_closure_api(
    request: PredictionRequest
):

    try:

        payload = request.model_dump()

        closure = predict_closure(payload)

        return {
            "closure_probability":
                round(closure, 4)
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# ==================================================
# TII ONLY
# ==================================================

@app.post("/predict-tii")
def predict_tii_api(
    request: PredictionRequest
):

    try:

        payload = request.model_dump()

        tii = predict_tii(payload)

        return {
            "traffic_impact_index":
                round(tii, 2)
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# ==================================================
# LOCAL RUN
# ==================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
    
