"""ReloScope configuration — loads environment variables and provides constants."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Google Cloud ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "project-cohort-one")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "asia-south1")
MODEL_NAME = os.getenv("MODEL", "gemini-2.5-flash")

# --- Google Maps Platform ---
MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# --- API Base URLs ---
WEATHER_API_URL = "https://weather.googleapis.com/v1/forecast/days:lookup"
AIR_QUALITY_API_URL = "https://airquality.googleapis.com/v1/currentConditions:lookup"
SOLAR_API_URL = "https://solar.googleapis.com/v1/buildingInsights:findClosest"
ELEVATION_API_URL = "https://maps.googleapis.com/maps/api/elevation/json"
GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"
PLACES_API_URL = "https://places.googleapis.com/v1/places:searchNearby"
ROUTES_API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
TRANSLATE_API_URL = "https://translation.googleapis.com/language/translate/v2"

# --- Default parameters ---
DEFAULT_RADIUS_M = 5000  # 5 km radius for place searches
DEFAULT_REGION = "IN"
