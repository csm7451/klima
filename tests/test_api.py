from __future__ import annotations

import responses

from klima.api import get_forecast, search_location


@responses.activate
def test_search_location_parses_results() -> None:
    responses.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        json={
            "results": [{"name": "Berlin", "latitude": 52.5, "longitude": 13.4, "country": "DE"}]
        },
    )
    out = search_location("Berlin", count=3)
    assert len(out) == 1
    assert out[0]["name"] == "Berlin"


@responses.activate
def test_get_forecast_returns_json() -> None:
    responses.get(
        "https://api.open-meteo.com/v1/forecast",
        json={
            "latitude": 0.0,
            "longitude": 0.0,
            "hourly": {"time": ["2026-05-01T00:00"], "temperature_2m": [25.0]},
            "daily": {"time": ["2026-05-01"]},
        },
    )
    data = get_forecast(1.0, 2.0)
    assert data["hourly"]["temperature_2m"][0] == 25.0
