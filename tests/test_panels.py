from __future__ import annotations

from klima.widgets.air_quality_panel import format_air_quality_panel
from klima.widgets.city_info import format_city_info


def test_format_air_quality_panel_empty() -> None:
    out = format_air_quality_panel(None)
    assert "No live AQI" in out
    assert "No current UV" in out


def test_format_air_quality_panel_us_aqi_and_uv() -> None:
    aq = {"current": {"us_aqi": 42, "uv_index": 4.2}}
    out = format_air_quality_panel(aq)
    assert "US AQI" in out
    assert "42" in out
    assert "Good" in out
    assert "4.2" in out
    assert "Moderate" in out  # UV band for 4.2


def test_format_air_quality_panel_prefers_us_over_eu() -> None:
    aq = {"current": {"us_aqi": 10, "european_aqi": 99, "uv_index": 1.0}}
    out = format_air_quality_panel(aq)
    assert "US AQI" in out
    assert "EU AQI" not in out


def test_format_air_quality_panel_eu_when_no_us() -> None:
    aq = {"current": {"european_aqi": 25, "uv_index": 0.0}}
    out = format_air_quality_panel(aq)
    assert "EU AQI" in out
    assert "25" in out


def test_format_city_info_empty() -> None:
    assert format_city_info(None) == "—"
    assert format_city_info({}) == "—"


def test_format_city_info_one_line_per_field() -> None:
    data = {
        "name": "Berlin",
        "country": "Germany",
        "admin1": "Berlin",
        "timezone": "Europe/Berlin",
        "latitude": 52.52,
        "longitude": 13.41,
        "elevation": 74.0,
        "population": 3_426_354,
    }
    out = format_city_info(data)
    lines = out.splitlines()
    assert lines[0] == "[b]Berlin[/b]"
    assert lines[1] == "Country: Germany"
    assert lines[2] == "Region: Berlin"
    assert lines[3] == "Timezone: Europe/Berlin"
    assert lines[4].startswith("Coordinates:")
    assert "52.52" in lines[4] and "N" in lines[4]
    assert lines[5] == "Elevation: 74 m"
    assert lines[6] == "Population: 3,426,354"


def test_format_city_info_skips_bad_coords_but_shows_placeholder() -> None:
    out = format_city_info({"name": "X", "latitude": "nope", "longitude": 0.0})
    assert "Coordinates: —" in out


def test_format_city_info_population_as_float() -> None:
    out = format_city_info({"name": "Tiny", "population": 1000.0})
    assert "Population: 1,000" in out
