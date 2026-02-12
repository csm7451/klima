from __future__ import annotations

from typing import Any

from textual.widgets import Static

from klima.weather_codes import get_weather_description


class CurrentWeather(Static):
    """Current conditions panel with color from weather code."""

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        self._data = data or {}
        content = self._format_content() if self._data else ""
        super().__init__(content, **kwargs)

    def set_data(self, data: dict[str, Any]) -> None:
        self._data = data
        self.update(self._format_content())

    def _format_content(self) -> str:
        cur = self._data.get("current", {})
        code = cur.get("weather_code", 0)
        desc = get_weather_description(code)
        temp = cur.get("temperature_2m")
        feels = cur.get("apparent_temperature")
        humidity = cur.get("relative_humidity_2m")
        wind = cur.get("wind_speed_10m")
        precip = cur.get("precipitation")
        cloud = cur.get("cloud_cover")

        temp_s = f"{temp:.0f}°C" if temp is not None else "—"
        feels_s = f"Feels like {feels:.0f}°C" if feels is not None else ""
        humidity_s = f"{humidity:.0f}%" if humidity is not None else ""
        wind_s = f"{wind:.0f} km/h" if wind is not None else ""
        precip_s = f"{precip:.1f} mm" if precip is not None else ""
        cloud_s = f"{cloud:.0f}%" if cloud is not None else ""

        lines = [
            f"[b]{temp_s}[/b]",
            desc,
            feels_s,
            "",
            f"Humidity: {humidity_s}  Wind: {wind_s}",
            f"Precip: {precip_s}  Clouds: {cloud_s}",
        ]
        return "\n".join(l for l in lines if l)
