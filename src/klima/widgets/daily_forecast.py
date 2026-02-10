"""7-day forecast row (text block)."""

from __future__ import annotations

from typing import Any

from textual.widgets import Static

from klima.formatting import format_day
from klima.weather_codes import get_weather_description


class DailyForecast(Static):
    """7-day forecast row."""

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        self._data = data or {}
        content = self._format_content() if self._data else ""
        super().__init__(content, **kwargs)

    def set_data(self, data: dict[str, Any]) -> None:
        self._data = data
        self.update(self._format_content())

    def _format_content(self) -> str:
        daily = self._data.get("daily", {})
        times = daily.get("time", [])[:7]
        codes = daily.get("weather_code", [])
        max_t = daily.get("temperature_2m_max", [])
        min_t = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        prob = daily.get("precipitation_probability_max", [])

        lines = []
        for i in range(min(7, len(times))):
            day = format_day(times[i], i)
            code = codes[i] if i < len(codes) else 0
            desc = get_weather_description(code)
            hi = max_t[i] if i < len(max_t) else None
            lo = min_t[i] if i < len(min_t) else None
            p = precip[i] if i < len(precip) else None
            pr = prob[i] if i < len(prob) else None
            hi_s = f"{hi:.0f}°" if hi is not None else "—"
            lo_s = f"{lo:.0f}°" if lo is not None else "—"
            p_s = f"{p:.1f}mm" if p is not None and p > 0 else "—"
            pr_s = f"{pr:.0f}%" if pr is not None else ""
            lines.append(
                f"[b]{day}[/b]\n{desc}\n{lo_s} / {hi_s}\n{p_s}  {pr_s}"
            )
        return "\n\n".join(lines)
