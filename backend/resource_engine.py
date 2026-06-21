import os
import json


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)


# --------------------------------------------------
# LOAD RISK TABLES
# --------------------------------------------------

with open(
    os.path.join(DATA_DIR, "corridor_risk.json"),
    "r",
    encoding="utf-8"
) as f:
    corridor_risk = json.load(f)

with open(
    os.path.join(DATA_DIR, "junction_risk.json"),
    "r",
    encoding="utf-8"
) as f:
    junction_risk = json.load(f)

with open(
    os.path.join(DATA_DIR, "event_severity.json"),
    "r",
    encoding="utf-8"
) as f:
    event_severity = json.load(f)


# --------------------------------------------------
# PRIORITY LOGIC
# --------------------------------------------------

def get_priority(tii):

    if tii >= 85:
        return "Critical"

    elif tii >= 70:
        return "High"

    elif tii >= 50:
        return "Medium"

    return "Low"


# --------------------------------------------------
# RESOURCE RECOMMENDATION ENGINE
# --------------------------------------------------

def recommend_resources(
    event_type,
    corridor,
    junction,
    tii
):

    corridor_score = corridor_risk.get(
        corridor,
        50
    )

    junction_score = junction_risk.get(
        junction,
        10
    )

    severity_score = event_severity.get(
        event_type,
        50
    )

    risk_score = (
        0.5 * float(tii)
        + 0.2 * float(corridor_score)
        + 0.2 * float(junction_score)
        + 0.1 * float(severity_score)
    )

    priority = get_priority(tii)

    traffic_police = int(
        max(
            2,
            round(risk_score / 10)
        )
    )

    barricades = int(
        max(
            5,
            round(risk_score / 4)
        )
    )

    tow_trucks = int(
        max(
            1,
            round(risk_score / 50)
        )
    )

    ambulances = int(
        max(
            1,
            round(risk_score / 75)
        )
    )

    return {

        "priority": priority,

        "risk_score": round(
            risk_score,
            2
        ),

        "traffic_police": traffic_police,

        "barricades": barricades,

        "tow_trucks": tow_trucks,

        "ambulances": ambulances
    }


# --------------------------------------------------
# LOCAL TEST
# --------------------------------------------------

if __name__ == "__main__":

    result = recommend_resources(
        event_type="planned",
        corridor="Mysore Road",
        junction="Nayandahalli",
        tii=82
    )

    print(result)