from __future__ import annotations

from typing import Any

from textual.widgets import Static

from klima.formatting import format_iso_time_short, wind_arrow_and_cardinal
from klima.units_conv import UnitsKind, format_precip_mm, format_temperature, format_wind_kmh
from klima.weather_codes import get_weather_description, get_weather_emoji


class CurrentWeather(Static):
    """Current conditions panel with color from weather code."""

    def __init__(
        self,
        data: dict[str, Any] | None = None,
        *,
        units: UnitsKind = "metric",
        show_emoji: bool = True,
        **kwargs: Any,
    ) -> None:
        self._data = data or {}
        self._units = units
        self._show_emoji = show_emoji
        content = self._format_content() if self._data else ""
        super().__init__(content, **kwargs)

    def set_data(
        self,
        data: dict[str, Any],
        *,
        units: UnitsKind | None = None,
        show_emoji: bool | None = None,
    ) -> None:
        self._data = data
        if units is not None:
            self._units = units
        if show_emoji is not None:
            self._show_emoji = show_emoji
        self.update(self._format_content())

    def _format_content(self) -> str:
        cur = self._data.get("current", {})
        daily = self._data.get("daily", {})
        code = cur.get("weather_code", 0)
        code_i = int(code) if isinstance(code, int | float) else 0
        desc = get_weather_description(code_i)
        em = f"{get_weather_emoji(code_i)} " if self._show_emoji else ""
        temp = cur.get("temperature_2m")
        tc = float(temp) if isinstance(temp, int | float) else None
        feels = cur.get("apparent_temperature")
        fc = float(feels) if isinstance(feels, int | float) else None
        humidity = cur.get("relative_humidity_2m")
        wind = cur.get("wind_speed_10m")
        wkmh = float(wind) if isinstance(wind, int | float) else None
        wdir = cur.get("wind_direction_10m")
        wdeg = float(wdir) if isinstance(wdir, int | float) else None
        precip = cur.get("precipitation")
        fl = float(precip) if isinstance(precip, int | float) else None
        cloud = cur.get("cloud_cover")
        cl = float(cloud) if isinstance(cloud, int | float) else None

        temp_s = format_temperature(tc, units=self._units) if tc is not None else "—"
        feels_s = (
            f"Feels like: {format_temperature(fc, units=self._units)}" if fc is not None else ""
        )
        humidity_s = f"{humidity:.0f}%" if isinstance(humidity, int | float) else ""
        wind_base = format_wind_kmh(wkmh, units=self._units)
        arr, card = wind_arrow_and_cardinal(wdeg)
        wind_s = f"{wind_base} {arr} {card}".strip() if wkmh is not None else ""
        precip_s = format_precip_mm(fl, units=self._units) if fl is not None else ""
        cloud_s = f"{cl:.0f}%" if cl is not None else ""

        sunrise = (daily.get("sunrise") or [None])[0]
        sunset = (daily.get("sunset") or [None])[0]
        sr = format_iso_time_short(str(sunrise) if sunrise else None)
        ss = format_iso_time_short(str(sunset) if sunset else None)

        lines: list[str] = [
            f"Temperature: [b]{em}{temp_s}[/b]",
            f"Condition: {desc}",
        ]
        if feels_s:
            lines.append(feels_s)
        if sr:
            lines.append(f"Sunrise: ☀️  {sr}")
        if ss:
            lines.append(f"Sunset: 🌅  {ss}")
        if humidity_s:
            lines.append(f"Humidity: {humidity_s}")
        if wind_s:
            lines.append(f"Wind: {wind_s}")
        if precip_s:
            lines.append(f"Precipitation: {precip_s}")
        if cloud_s:
            lines.append(f"Cloud cover: {cloud_s}")
        return "\n".join(lines)
