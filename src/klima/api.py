"""Open-Meteo API client for geocoding, forecast, and air quality."""

from __future__ import annotations

from typing import Any, cast

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def search_location(name: str, count: int = 5) -> list[dict[str, Any]]:
    """Convert a location name to coordinates using Open-Meteo Geocoding API."""
    if not name or len(name.strip()) < 2:
        return []
    params = {"name": name.strip(), "count": min(count, 100)}
    resp = requests.get(GEOCODING_URL, params=cast(Any, params), timeout=10)
    resp.raise_for_status()
    data = resp.json()
    raw = data.get("results", [])
    if isinstance(raw, list):
        return cast(list[dict[str, Any]], raw)
    return []


def get_forecast(
    latitude: float,
    longitude: float,
    timezone: str = "auto",
    forecast_days: int = 7,
) -> dict[str, Any]:
    """Fetch weather forecast for given coordinates."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "forecast_days": forecast_days,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
            "precipitation",
            "cloud_cover",
        ],
        "hourly": [
            "temperature_2m",
            "precipitation_probability",
            "precipitation",
            "weather_code",
        ],
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "sunrise",
            "sunset",
            "uv_index_max",
        ],
    }
    resp = requests.get(FORECAST_URL, params=cast(Any, params), timeout=10)
    resp.raise_for_status()
    return cast(dict[str, Any], resp.json())


def get_air_quality(
    latitude: float,
    longitude: float,
    timezone: str = "auto",
) -> dict[str, Any] | None:
    """Fetch current air quality (+ UV in current bundle). Failures → None."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "current": "us_aqi,european_aqi,uv_index",
    }
    try:
        resp = requests.get(AIR_QUALITY_URL, params=cast(Any, params), timeout=10)
        resp.raise_for_status()
        return cast(dict[str, Any], resp.json())
    except requests.RequestException:
        return None
