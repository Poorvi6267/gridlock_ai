# ==================================================
# TRAFFICSENSE DIVERSION ENGINE
# ==================================================

DIVERSION_MAP = {

    "Mysore Road": [
        "Kanakapura Road",
        "NICE Road",
        "ORR South"
    ],

    "Old Madras Road": [
        "ORR East 1",
        "ORR East 2",
        "Bellary Road 1"
    ],

    "Tumkur Road": [
        "ORR North 2",
        "Bellary Road 1"
    ],

    "Bellary Road 1": [
        "ORR North 2",
        "Airport New South Road"
    ],

    "ORR East 2": [
        "ORR East 1",
        "Old Madras Road"
    ],

    "Bannerghata Road": [
        "Kanakapura Road",
        "ORR South"
    ]
}


# ==================================================
# DIVERSION LEVEL
# ==================================================

def get_diversion_level(tii):

    if tii >= 90:
        return "FULL DIVERSION"

    elif tii >= 80:
        return "MAJOR DIVERSION"

    elif tii >= 70:
        return "PARTIAL DIVERSION"

    elif tii >= 50:
        return "PREPARE DIVERSION"

    return "MONITOR ONLY"


# ==================================================
# CONGESTION REDUCTION ESTIMATE
# ==================================================

def estimate_reduction(tii):

    if tii >= 90:
        return "35% - 45%"

    elif tii >= 80:
        return "25% - 35%"

    elif tii >= 70:
        return "15% - 25%"

    elif tii >= 50:
        return "5% - 15%"

    return "Minimal Impact"


# ==================================================
# ETA IMPROVEMENT
# ==================================================

def estimate_time_saving(tii):

    if tii >= 90:
        return "45 - 60 Minutes"

    elif tii >= 80:
        return "30 - 45 Minutes"

    elif tii >= 70:
        return "15 - 30 Minutes"

    elif tii >= 50:
        return "5 - 15 Minutes"

    return "Negligible"


# ==================================================
# STRATEGY GENERATOR
# ==================================================

def get_strategy(level):

    strategies = {

        "FULL DIVERSION":
            "Immediately redirect traffic to alternate corridors and deploy maximum field resources.",

        "MAJOR DIVERSION":
            "Activate primary diversion corridors and restrict traffic flow in affected zone.",

        "PARTIAL DIVERSION":
            "Divert heavy traffic while maintaining controlled access.",

        "PREPARE DIVERSION":
            "Keep diversion routes ready and monitor traffic escalation.",

        "MONITOR ONLY":
            "No diversion required. Continue monitoring traffic conditions."
    }

    return strategies.get(
        level,
        "Continue monitoring."
    )


# ==================================================
# DIVERSION RECOMMENDATION ENGINE
# ==================================================

def recommend_diversion(
    corridor,
    tii
):

    routes = DIVERSION_MAP.get(
        corridor,
        [
            "Nearest Parallel Corridor",
            "Secondary Urban Route"
        ]
    )

    level = get_diversion_level(
        tii
    )

    reduction = estimate_reduction(
        tii
    )

    time_saving = estimate_time_saving(
        tii
    )

    strategy = get_strategy(
        level
    )

    activate = tii >= 60

    if not activate:

        return {

            "activate": False,

            "level": level,

            "routes": [],

            "recommended_route": None,

            "expected_congestion_reduction":
                reduction,

            "expected_time_saving":
                time_saving,

            "strategy":
                strategy,

            "message":
                "Traffic conditions do not currently require diversion."
        }

    return {

        "activate": True,

        "level": level,

        "routes": routes,

        "recommended_route":
            routes[0],

        "backup_route":
            routes[1] if len(routes) > 1 else None,

        "expected_congestion_reduction":
            reduction,

        "expected_time_saving":
            time_saving,

        "strategy":
            strategy,

        "message":
            f"Activate diversion plan for {corridor}."
    }


# ==================================================
# LOCAL TEST
# ==================================================

if __name__ == "__main__":

    result = recommend_diversion(
        "Mysore Road",
        88
    )

    print("\n===== DIVERSION PLAN =====\n")

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )