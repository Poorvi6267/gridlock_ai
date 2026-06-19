import json


with open("data/corridor_risk.json") as f:
    corridor_risk = json.load(f)

with open("data/junction_risk.json") as f:
    junction_risk = json.load(f)

with open("data/event_severity.json") as f:
    event_severity = json.load(f)


def get_priority(tii):

    if tii >= 85:
        return "Critical"

    elif tii >= 70:
        return "High"

    elif tii >= 50:
        return "Medium"

    return "Low"


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
        0.5 * tii
        +
        0.2 * corridor_score
        +
        0.2 * junction_score
        +
        0.1 * severity_score
    )

    priority = get_priority(tii)

    traffic_police = int(
        max(
            2,
            risk_score / 10
        )
    )

    barricades = int(
        max(
            5,
            risk_score / 4
        )
    )

    tow_trucks = int(
        max(
            1,
            risk_score / 50
        )
    )

    ambulances = int(
        max(
            1,
            risk_score / 75
        )
    )

    return {

        "priority": priority,

        "traffic_police":
            traffic_police,

        "barricades":
            barricades,

        "tow_trucks":
            tow_trucks,

        "ambulances":
            ambulances,

        "risk_score":
            round(
                risk_score,
                2
            )
    }