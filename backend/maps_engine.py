import requests
from geopy.geocoders import Nominatim


def geocode_location(location_name):

    geolocator = Nominatim(
        user_agent="trafficsense"
    )

    try:

        location = geolocator.geocode(
            location_name,
            timeout=5
        )

    except Exception:

        return None

    if location is None:
        return None

    return (
        location.latitude,
        location.longitude
    )


def get_route(
    start_lat,
    start_lon,
    end_lat,
    end_lon
):

    url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{start_lon},{start_lat};"
        f"{end_lon},{end_lat}"
        "?overview=full&geometries=geojson"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

    except Exception:

        return []

    if ("routes" not in data or len(data["routes"]) == 0):
        return []

    coords = data["routes"][0]["geometry"]["coordinates"]

    return [
        [lat, lon]
        for lon, lat in coords
    ]