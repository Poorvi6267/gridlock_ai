import os
import json


# ==================================================
# PATHS
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)


# ==================================================
# LOAD JSON FILES
# ==================================================

def load_json(filename):

    path = os.path.join(
        DATA_DIR,
        filename
    )

    if not os.path.exists(path):

        print(
            f"WARNING: Missing {filename}"
        )

        return {}

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


corridor_risk = load_json(
    "corridor_risk.json"
)

junction_risk = load_json(
    "junction_risk.json"
)

event_severity = load_json(
    "event_severity.json"
)


# ==================================================
# PRIORITY ENGINE
# ==================================================

def get_priority(tii):

    if tii >= 90:
        return "CRITICAL"

    if tii >= 75:
        return "HIGH"

    if tii >= 50:
        return "MEDIUM"

    return "LOW"


# ==================================================
# RESPONSE STRATEGY
# ==================================================

def get_strategy(priority):

    strategies = {

        "CRITICAL":
            "Activate emergency diversion and deploy maximum resources.",

        "HIGH":
            "Deploy traffic control units and prepare diversion routes.",

        "MEDIUM":
            "Monitor congestion and deploy moderate resources.",

        "LOW":
            "Routine monitoring sufficient."
    }

    return strategies.get(
        priority,
        "Routine monitoring sufficient."
    )


# ==================================================
# ESTIMATED CLEARANCE
# ==================================================

def estimate_clearance_time(
    risk_score
):

    if risk_score >= 100:
        return "3 - 5 Hours"

    if risk_score >= 75:
        return "2 - 3 Hours"

    if risk_score >= 50:
        return "1 - 2 Hours"

    return "< 1 Hour"


# ==================================================
# RESOURCE ENGINE
# ==================================================

def recommend_resources(
    event_type,
    corridor,
    junction,
    tii
):

    corridor_score = float(
        corridor_risk.get(
            corridor,
            50
        )
    )

    junction_score = float(
        junction_risk.get(
            junction,
            20
        )
    )

    severity_score = float(
        event_severity.get(
            event_type,
            50
        )
    )

    risk_score = (

        0.50 * float(tii)

        + 0.20 * corridor_score

        + 0.20 * junction_score

        + 0.10 * severity_score
    )

    priority = get_priority(
        tii
    )

    traffic_police = int(
        max(
            2,
            round(
                risk_score / 8
            )
        )
    )

    barricades = int(
        max(
            5,
            round(
                risk_score / 3
            )
        )
    )

    tow_trucks = int(
        max(
            1,
            round(
                risk_score / 40
            )
        )
    )

    ambulances = int(
        max(
            1,
            round(
                risk_score / 60
            )
        )
    )

    strategy = get_strategy(
        priority
    )

    clearance_time = (
        estimate_clearance_time(
            risk_score
        )
    )

    return {

        "priority":
            priority,

        "risk_score":
            round(
                risk_score,
                2
            ),

        "traffic_police":
            traffic_police,

        "barricades":
            barricades,

        "tow_trucks":
            tow_trucks,

        "ambulances":
            ambulances,

        "strategy":
            strategy,

        "estimated_clearance":
            clearance_time
    }


# ==================================================
# LOCAL TEST
# ==================================================

if __name__ == "__main__":

    result = recommend_resources(

        event_type="planned",

        corridor="Mysore Road",

        junction="Nayandahalli",

        tii=82
    )

    print(
        "\n===== RESOURCE PLAN ====="
    )

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )