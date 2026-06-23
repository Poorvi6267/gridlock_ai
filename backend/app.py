from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import json
import os
import sqlite3
from datetime import datetime

from maps_engine import (
    geocode_location,
    get_route
)

from resource_engine import (
    recommend_resources,
    corridor_risk,
    junction_risk,
)
from diversion import recommend_diversion

from ml_engine import (
    predict_duration,
    predict_closure,
    predict_tii,
    predict_all
)

app = FastAPI(
    title="TrafficSense",
    version="3.0.0",
    description="AI Powered Traffic Operations Center"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================================================
# BANGALORE BOUNDS
# ==================================================

BANGALORE_LAT_MIN = 12.70
BANGALORE_LAT_MAX = 13.20
BANGALORE_LON_MIN = 77.35
BANGALORE_LON_MAX = 77.85

# ==================================================
# SQLite PREDICTION LOG
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "predictions.db")


def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            ts               TEXT    NOT NULL,
            junction         TEXT,
            corridor         TEXT,
            event_type       TEXT,
            tii              REAL,
            closure_prob     REAL,
            duration_minutes REAL,
            risk_score       REAL
        )
    """)
    con.commit()
    con.close()


init_db()


def log_prediction(junction, corridor, event_type,
                   tii, closure_prob, duration, risk_score):
    try:
        con = sqlite3.connect(DB_PATH)
        con.execute("""
            INSERT INTO predictions
            (ts, junction, corridor, event_type,
             tii, closure_prob, duration_minutes, risk_score)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            datetime.utcnow().isoformat(),
            junction, corridor, event_type,
            tii, closure_prob, duration, risk_score
        ))
        con.commit()
        con.close()
    except Exception as e:
        print(f"DB log error: {e}")


# ==================================================
# JUNCTION -> LAT/LON LOOKUP
# ==================================================

JUNCTION_COORDS = {
    "Kengeri":              (12.9141, 77.4820),
    "Nagavara Junction":    (13.0468, 77.6195),
    "Hebbal Junction":      (13.0450, 77.5970),
    "Silk Board Junction":  (12.9177, 77.6228),
}

# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/")
def home():
    return {"message": "TrafficSense Running", "status": "online"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# ==================================================
# META ENDPOINTS
# ==================================================

@app.get("/corridors")
def get_corridors():
    """Return all valid corridor names with normalised risk scores."""
    return {
        "corridors": [
            {"name": name, "risk_score": score}
            for name, score in sorted(
                corridor_risk.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]
    }


@app.get("/junctions")
def get_junctions():
    """Return valid junction names with coordinates."""
    return {
        "junctions": [
            {
                "name": name,
                "latitude":  JUNCTION_COORDS.get(name, (12.9716, 77.5946))[0],
                "longitude": JUNCTION_COORDS.get(name, (12.9716, 77.5946))[1],
            }
            for name in JUNCTION_COORDS
        ]
    }


@app.get("/status")
def get_status():
    """Live KPIs from recent predictions in the DB."""
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()

        cur.execute("SELECT COUNT(*) FROM predictions WHERE ts >= datetime('now','-1 hour')")
        active = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM predictions
            WHERE ts >= datetime('now','-1 hour') AND tii >= 75
        """)
        critical = cur.fetchone()[0]

        cur.execute("""
            SELECT COALESCE(SUM(CAST(risk_score / 8 AS INTEGER)), 0)
            FROM predictions WHERE ts >= datetime('now','-1 hour')
        """)
        police = cur.fetchone()[0] or 0

        cur.execute("""
            SELECT COUNT(*) FROM predictions
            WHERE ts >= datetime('now','-1 hour') AND tii >= 70
        """)
        diversions = cur.fetchone()[0]

        con.close()
        return {
            "active_incidents":   max(active, 0),
            "critical_incidents": max(critical, 0),
            "police_deployed":    max(int(police), 0),
            "diversions_active":  max(diversions, 0),
        }
    except Exception as e:
        return {
            "active_incidents": 0, "critical_incidents": 0,
            "police_deployed": 0,  "diversions_active": 0,
            "note": str(e)
        }


@app.get("/history")
def get_history():
    """Average duration from all logged predictions."""
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT AVG(duration_minutes), COUNT(*) FROM predictions")
        row = cur.fetchone()
        con.close()
        avg   = round(row[0], 1) if row and row[0] is not None else None
        count = row[1] if row else 0
        return {"average_duration_minutes": avg, "total_predictions": count}
    except Exception as e:
        return {"average_duration_minutes": None, "total_predictions": 0, "error": str(e)}


# ==================================================
# REQUEST MODELS
# ==================================================

class ResourceRequest(BaseModel):
    event_type: str
    corridor: str
    junction: str
    tii: float


VALID_EVENT_TYPES  = {"planned", "unplanned"}
VALID_EVENT_CAUSES = {"accident", "construction", "event", "breakdown", "flooding", "protest"}


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

    @validator("hour")
    def hour_in_range(cls, v):
        if not (0 <= v <= 23):
            raise ValueError(f"hour must be 0-23, got {v}")
        return v

    @validator("weekday")
    def weekday_in_range(cls, v):
        if not (0 <= v <= 6):
            raise ValueError(f"weekday must be 0-6, got {v}")
        return v

    @validator("month")
    def month_in_range(cls, v):
        if not (1 <= v <= 12):
            raise ValueError(f"month must be 1-12, got {v}")
        return v

    @validator("latitude")
    def lat_in_bangalore(cls, v):
        if not (BANGALORE_LAT_MIN <= v <= BANGALORE_LAT_MAX):
            raise ValueError(
                f"latitude {v} outside Bangalore bounds "
                f"({BANGALORE_LAT_MIN}-{BANGALORE_LAT_MAX})"
            )
        return v

    @validator("longitude")
    def lon_in_bangalore(cls, v):
        if not (BANGALORE_LON_MIN <= v <= BANGALORE_LON_MAX):
            raise ValueError(
                f"longitude {v} outside Bangalore bounds "
                f"({BANGALORE_LON_MIN}-{BANGALORE_LON_MAX})"
            )
        return v

    @validator("event_type")
    def event_type_valid(cls, v):
        if v not in VALID_EVENT_TYPES:
            raise ValueError(f"event_type must be one of {VALID_EVENT_TYPES}")
        return v

    @validator("event_cause")
    def event_cause_valid(cls, v):
        if v not in VALID_EVENT_CAUSES:
            raise ValueError(f"event_cause must be one of {VALID_EVENT_CAUSES}")
        return v


class RouteRequest(BaseModel):
    start_location: str
    end_location: str


# ==================================================
# RESOURCE RECOMMENDATION
# ==================================================

@app.post("/recommend")
def recommend(request: ResourceRequest):
    try:
        resource_result  = recommend_resources(
            request.event_type, request.corridor,
            request.junction,   request.tii
        )
        diversion_result = recommend_diversion(request.corridor, request.tii)
        return {
            "priority":            resource_result["priority"],
            "risk_score":          resource_result["risk_score"],
            "strategy":            resource_result["strategy"],
            "estimated_clearance": resource_result["estimated_clearance"],
            "resources": {
                "traffic_police": resource_result["traffic_police"],
                "barricades":     resource_result["barricades"],
                "tow_trucks":     resource_result["tow_trucks"],
                "ambulances":     resource_result["ambulances"]
            },
            "diversion": diversion_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================
# COMBINED ML PREDICTION  (logs to SQLite)
# ==================================================

@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        payload = request.model_dump()
        result  = predict_all(payload)

        log_prediction(
            junction     = request.junction,
            corridor     = request.corridor,
            event_type   = request.event_type,
            tii          = result["traffic_impact_index"],
            closure_prob = result["road_closure_probability"],
            duration     = result["predicted_duration_minutes"],
            risk_score   = 0,
        )

        return result

    except Exception as e:
        print("\n===== PREDICT ERROR =====")
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================
# INDIVIDUAL PREDICTIONS
# ==================================================

@app.post("/predict-duration")
def predict_duration_api(request: PredictionRequest):
    try:
        duration = predict_duration(request.model_dump())
        return {"predicted_duration_minutes": round(duration, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict-closure")
def predict_closure_api(request: PredictionRequest):
    try:
        closure = predict_closure(request.model_dump())
        return {"closure_probability": round(closure, 4)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict-tii")
def predict_tii_api(request: PredictionRequest):
    try:
        tii = predict_tii(request.model_dump())
        return {"traffic_impact_index": round(tii, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================
# ROUTE PLANNING
# ==================================================

@app.post("/route")
def route(request: RouteRequest):
    try:
        start = geocode_location(request.start_location)
        end   = geocode_location(request.end_location)

        if start is None:
            raise HTTPException(status_code=404,
                detail=f"Location not found: {request.start_location}")
        if end is None:
            raise HTTPException(status_code=404,
                detail=f"Location not found: {request.end_location}")

        coordinates = get_route(start[0], start[1], end[0], end[1])
        return {"start": start, "end": end, "coordinates": coordinates}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================
# LOCAL RUN
# ==================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
