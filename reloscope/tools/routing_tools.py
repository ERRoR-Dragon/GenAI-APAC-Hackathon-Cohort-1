"""Routing tools — Google Routes API for commute calculation.

Wraps the Routes API to compute travel time, distance, and route details
between two locations. Supports driving, transit, walking, and cycling modes.
"""

import requests
from reloscope.config import MAPS_API_KEY


def compute_commute(origin_address: str, destination_address: str, travel_mode: str = "DRIVE", departure_time: str = "") -> dict:
    """Compute travel time and distance between two locations.

    Calculates the commute from one address to another using the specified
    travel mode. Accounts for real-time or typical traffic conditions.

    Args:
        origin_address: Starting address (e.g., 'Kondapur, Hyderabad').
        destination_address: Ending address (e.g., 'HiTech City, Hyderabad').
        travel_mode: Mode of transport. One of:
            'DRIVE' — driving by car
            'TRANSIT' — public transit (bus, metro, train)
            'WALK' — walking
            'BICYCLE' — cycling
        departure_time: Optional ISO 8601 datetime for departure
                       (e.g., '2026-04-07T09:00:00+05:30').
                       If empty, uses current time.

    Returns:
        A dictionary with distance in km, estimated duration in minutes,
        duration in traffic, route summary, and toll information if applicable.
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": MAPS_API_KEY,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.description,routes.travelAdvisory,routes.legs.duration,routes.legs.distanceMeters,routes.legs.steps.navigationInstruction"
        }
        body = {
            "origin": {"address": origin_address},
            "destination": {"address": destination_address},
            "travelMode": travel_mode.upper(),
            "routingPreference": "TRAFFIC_AWARE" if travel_mode.upper() == "DRIVE" else "ROUTING_PREFERENCE_UNSPECIFIED",
            "computeAlternativeRoutes": False,
            "languageCode": "en",
            "units": "METRIC",
            "regionCode": "IN"
        }
        if departure_time:
            body["departureTime"] = departure_time

        response = requests.post(
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            headers=headers,
            json=body,
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            routes = data.get("routes", [])
            if routes:
                route = routes[0]
                duration_str = route.get("duration", "0s")
                duration_seconds = int(duration_str.replace("s", ""))
                distance_m = route.get("distanceMeters", 0)

                return {
                    "origin": origin_address,
                    "destination": destination_address,
                    "travel_mode": travel_mode,
                    "distance_km": round(distance_m / 1000, 1),
                    "duration_minutes": round(duration_seconds / 60, 1),
                    "route_description": route.get("description", ""),
                    "status": "success"
                }
            return {"status": "error", "message": "No route found between the given locations"}
        else:
            return {"status": "error", "message": f"Routes API returned {response.status_code}: {response.text[:300]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
