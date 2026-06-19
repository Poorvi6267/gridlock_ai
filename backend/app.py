from fastapi import FastAPI
from pydantic import BaseModel

from resource_engine import recommend_resources
from diversion import recommend_diversion

app = FastAPI(
    title="Gridlock AI"
)


class ResourceRequest(BaseModel):

    event_type: str
    corridor: str
    junction: str
    tii: float


@app.get("/")
def home():

    return {
        "message": "Gridlock AI Running"
    }


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