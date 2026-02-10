"""Panel showing selected city/location details from geocoding."""

from __future__ import annotations

from typing import Any

from textual.widgets import Static


class CityInfo(Static):
    """Panel showing selected city/location details from geocoding."""

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        self._data = data or {}
        content = self._format_content()
        super().__init__(content, **kwargs)

    def _format_content(self) -> str:
        if not self._data:
            return "—"
        lines = []
        name = self._data.get("name", "")
        country = self._data.get("country", "")
        admin1 = self._data.get("admin1", "")
        tz = self._data.get("timezone", "")
        lat = self._data.get("latitude")
        lon = self._data.get("longitude")
        elev = self._data.get("elevation")
        pop = self._data.get("population")

        if country and name:
            lines.append(f"[b]{name}[/b], {country}")
        elif name:
            lines.append(f"[b]{name}[/b]")
        if admin1:
            lines.append(f"Region: {admin1}")
        if tz:
            lines.append(f"Timezone: {tz}")
        if lat is not None and lon is not None:
            lines.append(f"Coordinates: {lat:.2f}°N, {lon:.2f}°E")
        if elev is not None:
            lines.append(f"Elevation: {elev:.0f} m")
        if pop is not None and pop > 0:
            lines.append(f"Population: {pop:,}")
        return "\n".join(lines) if lines else "—"
