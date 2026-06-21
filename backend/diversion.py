# diversion.py

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


def get_diversion_level(tii):

    if tii >= 90:
        return "Full Diversion"

    elif tii >= 80:
        return "Major Diversion"

    elif tii >= 70:
        return "Partial Diversion"

    return "Monitor Only"


def recommend_diversion(
    corridor,
    tii
):

    routes = DIVERSION_MAP.get(
        corridor,
        ["Nearest Parallel Corridor"]
    )

    if tii < 70:

        return {

            "activate": False,

            "level": "Monitor Only",

            "routes": [],

            "message":
                "Traffic impact not high enough for diversion."
        }

    return {

        "activate": True,

        "level":
            get_diversion_level(tii),

        "routes":
            routes,

        "recommended_route":
            routes[0],

        "message":
            f"Activate diversion plan for {corridor}."
    }


if __name__ == "__main__":

    print(
        recommend_diversion(
            "Mysore Road",
            88
        )
    )