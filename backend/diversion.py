# diversion_engine.py

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


def recommend_diversion(corridor, tii):

    if tii < 75:
        return {
            "activate": False,
            "routes": []
        }

    routes = DIVERSION_MAP.get(
        corridor,
        ["Nearest Parallel Corridor"]
    )

    return {
        "activate": True,
        "routes": routes
    }