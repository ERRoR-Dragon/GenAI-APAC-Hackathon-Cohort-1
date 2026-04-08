"""Livability analysis tools — Places API (New) for amenity discovery.

Wraps the Google Places API (New) to search for and count nearby amenities
like schools, hospitals, parks, gyms, grocery stores, restaurants, and more.
Uses the newer Places API endpoint with field masks for efficiency.
"""

import requests
from reloscope.config import MAPS_API_KEY


def search_nearby_places(latitude: float, longitude: float, place_type: str, radius_m: int = 5000, max_results: int = 20) -> dict:
    """Search for places of a specific type near a location.

    Uses the Google Places API (New) to find nearby amenities. Returns
    place names, ratings, user rating counts, and addresses.

    Args:
        latitude: GPS latitude of the center point.
        longitude: GPS longitude of the center point.
        place_type: The type of place to search for. Valid types include:
            'school', 'hospital', 'park', 'gym', 'supermarket',
            'restaurant', 'cafe', 'pharmacy', 'bank', 'atm',
            'shopping_mall', 'movie_theater', 'library', 'police',
            'fire_station', 'post_office', 'train_station',
            'bus_station', 'airport', 'gas_station', 'ev_charging_station',
            'hindu_temple', 'mosque', 'church', 'doctor', 'dentist',
            'veterinary_care', 'laundry', 'pet_store'.
        radius_m: Search radius in meters (default 5000 = 5km).
        max_results: Maximum number of results to return (default 20, max 20).

    Returns:
        A dictionary with list of places found, each containing name, rating,
        user_ratings_total, address, types, and place_id. Also includes
        the total count of places found.
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": MAPS_API_KEY,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.types,places.id,places.location,places.primaryType"
        }
        body = {
            "includedTypes": [place_type],
            "maxResultCount": min(max_results, 20),
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": latitude, "longitude": longitude},
                    "radius": float(radius_m)
                }
            },
            "rankPreference": "DISTANCE"
        }
        response = requests.post(
            "https://places.googleapis.com/v1/places:searchNearby",
            headers=headers,
            json=body,
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            places = []
            for p in data.get("places", []):
                places.append({
                    "name": p.get("displayName", {}).get("text", ""),
                    "address": p.get("formattedAddress", ""),
                    "rating": p.get("rating"),
                    "user_ratings_total": p.get("userRatingCount"),
                    "primary_type": p.get("primaryType", ""),
                    "types": p.get("types", []),
                    "place_id": p.get("id", ""),
                    "latitude": p.get("location", {}).get("latitude"),
                    "longitude": p.get("location", {}).get("longitude"),
                })
            return {
                "search_type": place_type,
                "search_center": {"latitude": latitude, "longitude": longitude},
                "search_radius_m": radius_m,
                "total_found": len(places),
                "places": places,
                "status": "success"
            }
        else:
            return {"status": "error", "message": f"Places API returned {response.status_code}: {response.text[:300]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def count_amenities_by_type(latitude: float, longitude: float, radius_m: int = 5000) -> dict:
    """Count amenities across multiple categories near a location.

    Performs batch searches for essential amenity types and returns
    counts for each category. This gives a livability density score.

    Args:
        latitude: GPS latitude of the center point.
        longitude: GPS longitude of the center point.
        radius_m: Search radius in meters (default 5000 = 5km).

    Returns:
        A dictionary with counts for each amenity type: schools, hospitals,
        parks, gyms, supermarkets, restaurants, cafes, pharmacies, banks,
        libraries, police stations, train stations, and more.
        Also includes an overall amenity_density_score from 0 to 100.
    """
    amenity_types = [
        "school", "hospital", "park", "gym", "supermarket",
        "restaurant", "cafe", "pharmacy", "bank", "library",
        "police", "train_station", "shopping_mall", "movie_theater"
    ]

    counts = {}
    total = 0
    for atype in amenity_types:
        result = search_nearby_places(latitude, longitude, atype, radius_m, max_results=20)
        if result.get("status") == "success":
            count = result.get("total_found", 0)
            counts[atype] = count
            total += count
        else:
            counts[atype] = 0

    # Simple density score: normalized against reasonable urban expectations
    # A well-serviced urban area in India typically has 100+ amenities within 5km
    density_score = min(100, int((total / 120) * 100))

    return {
        "location": {"latitude": latitude, "longitude": longitude},
        "radius_m": radius_m,
        "amenity_counts": counts,
        "total_amenities": total,
        "amenity_density_score": density_score,
        "status": "success"
    }
