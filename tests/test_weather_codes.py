from __future__ import annotations

from klima.weather_codes import get_weather_color, get_weather_description, get_weather_emoji


def test_known_code() -> None:
    assert get_weather_description(0) == "Clear sky"
    assert get_weather_emoji(0) == "☀️"
    assert get_weather_color(0).startswith("#")


def test_unknown_code() -> None:
    assert "Unknown" in get_weather_description(9999)
    assert get_weather_emoji(9999) == "🌥️"
