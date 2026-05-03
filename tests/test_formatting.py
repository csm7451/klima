from __future__ import annotations

from klima.formatting import (
    format_day,
    format_day_cells,
    hourly_xticks,
    nearest_hour_slot_index,
    wind_arrow_and_cardinal,
)


def test_wind_arrow_north() -> None:
    arr, card = wind_arrow_and_cardinal(0.0)
    assert card == "N"
    assert arr == "↑"


def test_wind_arrow_southwest() -> None:
    arr, card = wind_arrow_and_cardinal(225.0)
    assert card == "SW"
    assert arr == "↙"


def test_wind_missing() -> None:
    assert wind_arrow_and_cardinal(None) == ("", "")


def test_format_day_today_tomorrow() -> None:
    assert format_day("2026-05-01", 0) == "Today"
    assert format_day("2026-05-02", 1) == "Tomorrow"


def test_hourly_xticks_short() -> None:
    x, lbl = hourly_xticks(4)
    assert len(x) >= 1
    assert len(lbl) == len(x)


def test_nearest_hour_slot_needs_data() -> None:
    assert nearest_hour_slot_index([], 5) is None


def test_format_day_cells_includes_precip_prob() -> None:
    data = {
        "daily": {
            "time": ["2026-05-01", "2026-05-02"],
            "weather_code": [0, 61],
            "temperature_2m_max": [20.0, 18.0],
            "temperature_2m_min": [10.0, 9.0],
            "precipitation_sum": [0.0, 3.0],
            "precipitation_probability_max": [5, 80],
        },
    }
    cells = format_day_cells(data, units="metric", emoji=False)
    assert "chance" in cells[0]
    assert "20" in cells[0] or "°C" in cells[0]
