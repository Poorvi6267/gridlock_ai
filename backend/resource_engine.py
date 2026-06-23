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

    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Required data file missing: {path}\n"
            f"Run gridlock3.ipynb to regenerate data files."
        )

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


corridor_risk_raw = load_json("corridor_risk.json")
junction_risk_raw = load_json("junction_risk.json")
event_severity    = load_json("event_severity.json")


# ==================================================
# NORMALIZE JSON VALUES TO 0-100
# ✅ CHANGE 1: Normalize corridor and junction scores
# ❌ OLD: Values were raw duration means (600–2000 min)
#         not risk scores. The formula produced risk_score
#         of 200+ instead of the expected 0–100 range.
#         e.g. Mysore Road = 1070, SilkBoard = 714 →
#         0.2*1070 + 0.2*714 = 357 before even adding TII.
# ==================================================

def normalize_dict(d):
    """MinMax normalize a dict of floats to 0–100."""
    vals = list(d.values())
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return {k: 50.0 for k in d}
    return {
        k: round(100.0 * (v - lo) / (hi - lo), 2)
        for k, v in d.items()
    }


corridor_risk = normalize_dict(corridor_risk_raw)
junction_risk = normalize_dict(junction_risk_raw)


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

    return strategies.get(priority, "Routine monitoring sufficient.")


# ==================================================
# ESTIMATED CLEARANCE
# ==================================================

def estimate_clearance_time(risk_score):

    if risk_score >= 80:
        return "3 - 5 Hours"
    if risk_score >= 60:
        return "2 - 3 Hours"
    if risk_score >= 40:
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

    # All values now 0-100 after normalization above
    corridor_score = float(
        corridor_risk.get(corridor, 50)
    )

    junction_score = float(
        junction_risk.get(junction, 50)
    )

    # event_severity values are already 0-100
    # (they are TII means from the notebook)
    severity_score = float(
        event_severity.get(event_type, 50)
    )

    # Weighted formula — all inputs now 0-100
    # so risk_score output is also ~0-100
    risk_score = (
        0.50 * float(tii)
        + 0.20 * corridor_score
        + 0.20 * junction_score
        + 0.10 * severity_score
    )

    priority = get_priority(tii)

    traffic_police = int(max(2, round(risk_score / 8)))
    barricades     = int(max(5, round(risk_score / 3)))
    tow_trucks     = int(max(1, round(risk_score / 40)))
    ambulances     = int(max(1, round(risk_score / 60)))

    strategy       = get_strategy(priority)
    clearance_time = estimate_clearance_time(risk_score)

    return {
        "priority":           priority,
        "risk_score":         round(risk_score, 2),
        "traffic_police":     traffic_police,
        "barricades":         barricades,
        "tow_trucks":         tow_trucks,
        "ambulances":         ambulances,
        "strategy":           strategy,
        "estimated_clearance": clearance_time
    }


# ==================================================
# LOCAL TEST
# ==================================================

if __name__ == "__main__":

    result = recommend_resources(
        event_type="planned",
        corridor="Mysore Road",
        junction="SilkBoardJunc",
        tii=51.66
    )

    print("\n===== RESOURCE PLAN =====")
    for key, value in result.items():
        print(f"{key}: {value}")
