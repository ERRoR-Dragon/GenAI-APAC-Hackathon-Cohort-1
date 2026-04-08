"""Environment analysis tools — Weather, Air Quality, Solar, Elevation, Geocoding.

These wrap Google Maps Platform Environment APIs to assess climate, air quality,
solar potential, terrain elevation, and address-to-coordinate conversion for
any location in India.
"""

import requests
from reloscope.config import MAPS_API_KEY, WEATHER_API_URL, AIR_QUALITY_API_URL, SOLAR_API_URL, ELEVATION_API_URL, GEOCODING_API_URL


def get_weather_forecast(latitude: float, longitude: float) -> dict:
    """Get a multi-day weather forecast for a specific location.

    Retrieves temperature, humidity, precipitation probability, wind speed,
    and weather conditions for the next several days. Useful for comparing
    climate between cities.

    Args:
        latitude: GPS latitude of the location (e.g., 12.9716 for Bangalore).
        longitude: GPS longitude of the location (e.g., 77.5946 for Bangalore).

    Returns:
        A dictionary containing daily weather forecasts with temperature ranges,
        humidity, precipitation probability, wind conditions, and overall
        weather description. Returns an error message if the API call fails.
    """
    try:
        response = requests.post(
            WEATHER_API_URL,
            params={"key": MAPS_API_KEY},
            json={
                "location": {"latitude": latitude, "longitude": longitude},
                "days": 10,
                "languageCode": "en"
            },
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            forecasts = []
            for day in data.get("forecastDays", [])[:10]:
                day_info = day.get("daytimeForecast", {})
                night_info = day.get("nighttimeForecast", {})
                temp = day.get("temperature", {})
                forecasts.append({
                    "date": day.get("displayDate", ""),
                    "max_temp_celsius": temp.get("maxTemperature", {}).get("degrees"),
                    "min_temp_celsius": temp.get("minTemperature", {}).get("degrees"),
                    "humidity_pct": day.get("maxRelativeHumidity"),
                    "precipitation_prob_pct": day_info.get("precipitationProbability"),
                    "weather_condition": day_info.get("weatherCondition", ""),
                    "wind_speed_kmh": day_info.get("wind", {}).get("speed", {}).get("value"),
                })
            return {
                "location": {"latitude": latitude, "longitude": longitude},
                "forecast_days": forecasts,
                "status": "success"
            }
        else:
            return {"status": "error", "message": f"Weather API returned {response.status_code}: {response.text[:300]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_air_quality(latitude: float, longitude: float) -> dict:
    """Get current air quality conditions for a specific location.

    Returns the Air Quality Index (AQI), dominant pollutant, individual
    pollutant concentrations (PM2.5, PM10, O3, NO2, SO2, CO), and
    health recommendations. Resolution is 500x500 meters in India.

    Args:
        latitude: GPS latitude of the location.
        longitude: GPS longitude of the location.

    Returns:
        A dictionary with the overall AQI score, AQI category (Good/Moderate/
        Unhealthy etc.), dominant pollutant, individual pollutant levels,
        and health recommendations for general and sensitive populations.
    """
    try:
        response = requests.post(
            AIR_QUALITY_API_URL,
            params={"key": MAPS_API_KEY},
            json={
                "location": {"latitude": latitude, "longitude": longitude},
                "extraComputations": [
                    "HEALTH_RECOMMENDATIONS",
                    "DOMINANT_POLLUTANT_CONCENTRATION",
                    "POLLUTANT_CONCENTRATION",
                    "LOCAL_AQI",
                    "POLLUTANT_ADDITIONAL_INFO"
                ],
                "languageCode": "en"
            },
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            indexes = data.get("indexes", [])
            # Prefer local AQI (India uses its own AQI standard)
            aqi_data = {}
            for idx in indexes:
                aqi_data[idx.get("code", "unknown")] = {
                    "aqi": idx.get("aqi"),
                    "category": idx.get("category", ""),
                    "dominant_pollutant": idx.get("dominantPollutant", ""),
                    "color": idx.get("color", {})
                }

            pollutants = {}
            for p in data.get("pollutants", []):
                pollutants[p.get("code", "")] = {
                    "display_name": p.get("displayName", ""),
                    "concentration_ugm3": p.get("concentration", {}).get("value"),
                    "concentration_units": p.get("concentration", {}).get("units", ""),
                }

            return {
                "location": {"latitude": latitude, "longitude": longitude},
                "air_quality_indexes": aqi_data,
                "pollutants": pollutants,
                "health_recommendations": data.get("healthRecommendations", {}),
                "date_time": data.get("dateTime", ""),
                "status": "success"
            }
        else:
            return {"status": "error", "message": f"Air Quality API returned {response.status_code}: {response.text[:300]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_solar_potential(latitude: float, longitude: float) -> dict:
    """Get rooftop solar energy potential for buildings at a location.

    Analyzes satellite imagery to estimate solar panel area, annual energy
    production in kWh, and potential financial savings. Available in India.

    Args:
        latitude: GPS latitude of the location.
        longitude: GPS longitude of the location.

    Returns:
        A dictionary with solar panel area in sq meters, estimated annual
        energy production in kWh, number of panels that fit, carbon offset,
        and data quality tier. Returns error if no building data available.
    """
    try:
        response = requests.get(
            SOLAR_API_URL,
            params={
                "key": MAPS_API_KEY,
                "location.latitude": latitude,
                "location.longitude": longitude,
                "experiments": "EXPANDED_COVERAGE"
            },
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            solar_potential = data.get("solarPotential", {})
            best_config = {}
            configs = solar_potential.get("solarPanelConfigs", [])
            if configs:
                best = configs[-1]  # Last config typically has most panels
                best_config = {
                    "panels_count": best.get("panelsCount"),
                    "yearly_energy_kwh": best.get("yearlyEnergyDcKwh"),
                }

            return {
                "location": {"latitude": latitude, "longitude": longitude},
                "max_sunshine_hours_per_year": solar_potential.get("maxSunshineHoursPerYear"),
                "max_array_area_m2": solar_potential.get("maxArrayAreaMeters2"),
                "carbon_offset_kg_per_mwh": solar_potential.get("carbonOffsetFactorKgPerMwh"),
                "best_panel_config": best_config,
                "imagery_quality": data.get("imageryQuality", ""),
                "imagery_date": data.get("imageryDate", {}),
                "status": "success"
            }
        else:
            return {"status": "error", "message": f"Solar API returned {response.status_code}: {response.text[:300]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_elevation(latitude: float, longitude: float) -> dict:
    """Get elevation in meters for a location — useful for flood risk assessment.

    Low elevation in flat terrain near rivers indicates higher flood risk.
    High elevation with steep gradients may indicate landslide risk.

    Args:
        latitude: GPS latitude of the location.
        longitude: GPS longitude of the location.

    Returns:
        A dictionary with elevation in meters above sea level and the
        data resolution in meters.
    """
    try:
        response = requests.get(
            ELEVATION_API_URL,
            params={
                "key": MAPS_API_KEY,
                "locations": f"{latitude},{longitude}"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                return {
                    "location": {"latitude": latitude, "longitude": longitude},
                    "elevation_meters": results[0].get("elevation"),
                    "resolution_meters": results[0].get("resolution"),
                    "status": "success"
                }
            return {"status": "error", "message": "No elevation data returned"}
        else:
            return {"status": "error", "message": f"Elevation API returned {response.status_code}: {response.text[:300]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def geocode_address(address: str) -> dict:
    """Convert a text address or place name to GPS coordinates.

    Essential for converting user-provided city/neighborhood names
    (like 'Koramangala, Bangalore') into latitude/longitude for other API calls.

    Args:
        address: A human-readable address or place name
                 (e.g., 'Koramangala, Bangalore, India').

    Returns:
        A dictionary with latitude, longitude, formatted address,
        and place_id. Returns error if the address cannot be geocoded.
    """
    try:
        response = requests.get(
            GEOCODING_API_URL,
            params={
                "key": MAPS_API_KEY,
                "address": address,
                "region": "in"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                loc = results[0].get("geometry", {}).get("location", {})
                return {
                    "latitude": loc.get("lat"),
                    "longitude": loc.get("lng"),
                    "formatted_address": results[0].get("formatted_address", ""),
                    "place_id": results[0].get("place_id", ""),
                    "address_components": [
                        {
                            "name": c.get("long_name"),
                            "types": c.get("types", [])
                        }
                        for c in results[0].get("address_components", [])
                    ],
                    "status": "success"
                }
            return {"status": "error", "message": f"Could not geocode address: {address}"}
        else:
            return {"status": "error", "message": f"Geocoding API returned {response.status_code}: {response.text[:300]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
