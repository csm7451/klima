"""Temperature, wind speed, and precipitation conversions for metric vs imperial."""

from __future__ import annotations

from typing import Literal

UnitsKind = Literal["metric", "imperial"]


def format_temperature(celsius: float | None, *, units: UnitsKind, precision: int = 0) -> str:
    if celsius is None:
        return "—"
    if units == "imperial":
        f_deg = celsius * 9 / 5 + 32
        return f"{f_deg:.{precision}f}°F"
    return f"{celsius:.{precision}f}°C"


def celsius_to_chart_value(celsius: float, units: UnitsKind) -> float:
    """Numeric value for plotting in the user's chosen units."""
    if units == "imperial":
        return celsius * 9 / 5 + 32
    return celsius


def format_wind_kmh(kmh: float | None, *, units: UnitsKind, precision: int = 0) -> str:
    if kmh is None:
        return "—"
    if units == "imperial":
        mph = kmh * 0.621371
        return f"{mph:.{precision}f} mph"
    return f"{kmh:.{precision}f} km/h"


def format_precip_mm(mm: float | None, *, units: UnitsKind) -> str:
    if mm is None:
        return "—"
    if units == "imperial":
        inch = mm / 25.4
        return f"{inch:.2f} in"
    return f"{mm:.1f} mm"


def temp_axis_label(units: UnitsKind) -> str:
    return "°F" if units == "imperial" else "°C"


def precip_axis_title(units: UnitsKind) -> str:
    return "Precipitation (in)" if units == "imperial" else "Precipitation (mm)"
