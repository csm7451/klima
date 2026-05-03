from __future__ import annotations

from typing import Any

from textual.widgets import Static

from klima.formatting import coords_label


def format_city_info(data: dict[str, Any] | None) -> str:
    """One labeled line per geocode field (Open-Meteo search / resolve payload)."""
    if not data:
        return "—"
    lines: list[str] = []
    name = data.get("name", "")
    country = data.get("country", "")
    admin1 = data.get("admin1", "")
    tz = data.get("timezone", "")
    lat = data.get("latitude")
    lon = data.get("longitude")
    elev = data.get("elevation")
    pop = data.get("population")

    if name:
        lines.append(f"[b]{name}[/b]")
    if country:
        lines.append(f"Country: {country}")
    if admin1:
        lines.append(f"Region: {admin1}")
    if tz:
        lines.append(f"Timezone: {tz}")
    if lat is not None and lon is not None:
        try:
            lines.append(f"Coordinates: {coords_label(float(lat), float(lon))}")
        except (ValueError, TypeError):
            lines.append("Coordinates: —")
    if elev is not None:
        try:
            lines.append(f"Elevation: {float(elev):.0f} m")
        except (ValueError, TypeError):
            lines.append("Elevation: —")
    if pop is not None:
        try:
            n = int(float(pop))
        except (ValueError, TypeError):
            n = 0
        if n > 0:
            lines.append(f"Population: {n:,}")
    return "\n".join(lines) if lines else "—"


class CityInfo(Static):
    """Location metadata from geocoding (name through population)."""

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        self._data = data or {}
        super().__init__(format_city_info(self._data), **kwargs)
