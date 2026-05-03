from __future__ import annotations

from typing import Any

from textual.widgets import Static

_TIP_MAX_AQI = 58
_TIP_MAX_UV = 48


def _us_aqi_band(value: float) -> tuple[str, str]:
    """EPA AQI category + short dim reference."""
    v = int(round(value))
    if v <= 50:
        return "Good", "EPA 0–50: healthy for almost everyone."
    if v <= 100:
        return "Moderate", "EPA 51–100: sensitive groups may notice."
    if v <= 150:
        return "Unhealthy for sensitive", "EPA 101–150: limit long exertion if at risk."
    if v <= 200:
        return "Unhealthy", "EPA 151–200: cut prolonged outdoor exertion."
    if v <= 300:
        return "Very unhealthy", "EPA 201–300: avoid extended outdoor activity."
    return "Hazardous", "EPA 301+: emergency-level pollution."


def _eu_aqi_band(value: float) -> tuple[str, str]:
    """European AQI category + short dim reference."""
    v = int(round(value))
    if v <= 20:
        return "Good", "EAQI 0–20: minimal health concern."
    if v <= 40:
        return "Fair", "EAQI 20–40: generally fine; very sensitive may notice."
    if v <= 60:
        return "Moderate", "EAQI 40–60: shorten long outdoor effort if sensitive."
    if v <= 80:
        return "Poor", "EAQI 60–80: noticeable for most people."
    if v <= 100:
        return "Very poor", "EAQI 80–100: reduce outdoor exposure."
    return "Extremely poor", "EAQI 100+: serious risk outdoors."


def _uv_band(value: float) -> tuple[str, str]:
    """WHO-style UV label + short dim hint."""
    if value < 3:
        return "Low", "0–2: little risk."
    if value < 6:
        return "Moderate", "3–5: sunscreen & hat near midday."
    if value < 8:
        return "High", "6–7: seek shade; limit noon sun."
    if value < 11:
        return "Very high", "8–10: burns quickly; minimize 10am–4pm."
    return "Extreme", "11+: avoid midday sun."


def _ellipsize(s: str, max_len: int) -> str:
    t = " ".join(s.split())
    if len(t) <= max_len:
        return t
    if max_len <= 1:
        return "…"
    return t[: max_len - 1].rstrip() + "…"


def _parse_aq_current(
    aq_json: dict[str, Any] | None,
) -> tuple[float | None, float | None, float | None]:
    """Read US AQI, EU AQI, and UV from an Open-Meteo air-quality `current` object."""
    if not aq_json or not isinstance(aq_json.get("current"), dict):
        return None, None, None
    cur = aq_json["current"]
    usa: float | None = None
    eu: float | None = None
    uv: float | None = None
    u = cur.get("us_aqi")
    if isinstance(u, int | float):
        usa = float(u)
    e = cur.get("european_aqi")
    if isinstance(e, int | float):
        eu = float(e)
    uxc = cur.get("uv_index")
    if isinstance(uxc, int | float):
        uv = float(uxc)
    return usa, eu, uv


def _append_aqi_lines(
    lines: list[str],
    usa: float | None,
    eu: float | None,
) -> None:
    if usa is not None:
        band, tip = _us_aqi_band(usa)
        lines.append("[b]US AQI[/]")
        lines.append(f"[bold yellow]{usa:.0f}[/]")
        lines.append(f"[b]{band}[/]   [dim]{_ellipsize(tip, _TIP_MAX_AQI)}[/]")
        return
    if eu is not None:
        band, tip = _eu_aqi_band(eu)
        lines.append("[b]EU AQI[/]")
        lines.append(f"[bold yellow]{eu:.0f}[/]")
        lines.append(f"[b]{band}[/]   [dim]{_ellipsize(tip, _TIP_MAX_AQI)}[/]")
        return
    lines.append("[dim]No live AQI for this cell.[/]")


def _append_uv_lines(lines: list[str], cur_uv: float | None) -> None:
    lines.append("[b]UV index[/]")
    if cur_uv is None:
        lines.append("[dim]No current UV value.[/]")
        return
    band, tip = _uv_band(cur_uv)
    lines.append(f"[bold yellow]{cur_uv:.1f}[/]")
    lines.append(f"[b]{band}[/]   [dim]{_ellipsize(tip, _TIP_MAX_UV)}[/]")


def format_air_quality_panel(aq_json: dict[str, Any] | None) -> str:
    """Rich markup: current US/EU AQI and UV from the Open-Meteo Air Quality API."""
    usa, eu, cur_uv = _parse_aq_current(aq_json)
    lines: list[str] = [
        "[b]Air quality & UV[/]",
        "[dim]Current readings (Open-Meteo Air Quality).[/]",
        "",
    ]
    _append_aqi_lines(lines, usa, eu)
    lines.append("")
    _append_uv_lines(lines, cur_uv)
    return "\n".join(lines)


class AirQualityPanel(Static):
    """Air quality + UV strip for the dashboard summary row."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__("", **kwargs)

    def set_payload(self, aq: dict[str, Any] | None) -> None:
        self.update(format_air_quality_panel(aq))
