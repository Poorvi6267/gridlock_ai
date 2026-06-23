from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel

from maps_engine import (
    geocode_location,
    get_route
)

from resource_engine import recommend_resources
from diversion import recommend_diversion

from ml_engine import (
    predict_duration,
    predict_closure,
    predict_tii,
    predict_all
)

app = FastAPI(
    title="TrafficSense",
    version="2.0.0",
    description="AI Powered Traffic Operations Center"
)

# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/")
def home():

    return {
        "message": "TrafficSense Running",
        "status": "online"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ==================================================
# REQUEST MODELS
# ==================================================

class ResourceRequest(BaseModel):

    event_type: str
    corridor: str
    junction: str
    tii: float


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


class RouteRequest(BaseModel):

    start_location: str
    end_location: str


# ==================================================
# RESOURCE RECOMMENDATION
# ==================================================

@app.post("/recommend")
def recommend(request: ResourceRequest):

    try:

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

            "strategy":
                resource_result["strategy"],

            "estimated_clearance":
                resource_result["estimated_clearance"],

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

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==================================================
# COMBINED ML PREDICTION
# ==================================================

@app.post("/predict")
def predict(request: PredictionRequest):

    try:

        payload = request.model_dump()

        result = predict_all(payload)

        return result

    except Exception as e:

        print("\n===== PREDICT ERROR =====")
        print(e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==================================================
# DURATION PREDICTION
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
        
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==================================================
# ROAD CLOSURE PREDICTION
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

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==================================================
# TRAFFIC IMPACT INDEX
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

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==================================================
# ROUTE PLANNING
# ==================================================

@app.post("/route")
def route(
    request: RouteRequest
):

    try:

        start = geocode_location(
            request.start_location
        )

        end = geocode_location(
            request.end_location
        )

        if start is None:

            raise HTTPException(
                status_code=404,
                detail=f"Location not found: {request.start_location}"
            )

        if end is None:

            raise HTTPException(
                status_code=404,
                detail=f"Location not found: {request.end_location}"
            )

        coordinates = get_route(
            start[0],
            start[1],
            end[0],
            end[1]
        )

        return {

            "start": start,
            "end": end,
            "coordinates": coordinates
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


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