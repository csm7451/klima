"""Formatting helpers for dates, day cells, and chart axes."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Sequence


def format_day(iso_date: str, day_index: int | None = None) -> str:
    """Format ISO date as short day name; use 'Today' / 'Tomorrow' for first two days."""
    if day_index == 0:
        return "Today"
    if day_index == 1:
        return "Tomorrow"
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        return dt.strftime("%a")
    except (ValueError, TypeError):
        return "?"


def format_day_cells(data: dict[str, Any]) -> list[str]:
    """Return 7 strings, one per day, for left-to-right layout."""
    from klima.weather_codes import get_weather_description

    daily = data.get("daily", {})
    times = daily.get("time", [])[:7]
    codes = daily.get("weather_code", [])
    max_t = daily.get("temperature_2m_max", [])
    min_t = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])
    cells = []
    for i in range(7):
        if i >= len(times):
            cells.append("[b]—[/b]\n—\n— / —\n—")
            continue
        day = format_day(times[i], i)
        desc = get_weather_description(codes[i]) if i < len(codes) else "?"
        hi = f"{max_t[i]:.0f}°" if i < len(max_t) else "—"
        lo = f"{min_t[i]:.0f}°" if i < len(min_t) else "—"
        p = f"{precip[i]:.0f} mm" if i < len(precip) and precip[i] else "—"
        cells.append(f"[b]{day}[/b]\n{desc}\n{lo} / {hi}\n{p}")
    return cells


def y_ticks_from_data(
    values: Sequence[float],
    *,
    num_ticks: int = 5,
    fmt: str = "{:.1f}",
) -> tuple[list[float], list[str]]:
    """Return (tick positions, tick labels) for plotext y-axis from data range."""
    if not values:
        return [0], ["0"]
    lo, hi = min(values), max(values)
    if lo == hi:
        return [lo], [fmt.format(lo)]
    step = (hi - lo) / max(1, num_ticks - 1)
    positions = [lo + step * i for i in range(num_ticks)]
    labels = [fmt.format(p) for p in positions]
    return positions, labels
