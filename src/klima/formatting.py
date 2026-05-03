"""Formatting helpers for dates, day cells, wind, and chart axes."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any

from klima.units_conv import UnitsKind, format_precip_mm, format_temperature


def wind_arrow_and_cardinal(degrees: float | None) -> tuple[str, str]:
    """Meteorological degrees (0=N, clockwise) → unicode arrow + compass label."""
    if degrees is None:
        return "", ""
    d = float(degrees) % 360.0
    labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    arrows = ["↑", "↗", "→", "↘", "↓", "↙", "←", "↖"]
    idx = int((d + 22.5) % 360 // 45) % 8
    return arrows[idx], labels[idx]


def format_iso_time_short(iso: str | None) -> str | None:
    """Show local clock time HH:MM from Open-Meteo ISO string."""
    if not iso or not isinstance(iso, str):
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except (ValueError, TypeError):
        return None


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


def format_day_cells(
    data: dict[str, Any],
    *,
    units: UnitsKind = "metric",
    emoji: bool = True,
) -> list[str]:
    """Return 7 strings, one per day, for left-to-right layout."""
    from klima.weather_codes import get_weather_description, get_weather_emoji

    daily = data.get("daily", {})
    times = daily.get("time", [])[:7]
    codes = daily.get("weather_code", [])
    max_t = daily.get("temperature_2m_max", [])
    min_t = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])
    prob = daily.get("precipitation_probability_max", [])
    cells = []
    for i in range(7):
        if i >= len(times):
            cells.append("[b]—[/b]\n—\n— / —\n—\n—")
            continue
        day = format_day(times[i], i)
        code = codes[i] if i < len(codes) else 0
        desc = get_weather_description(code)
        em = f"{get_weather_emoji(code)} " if emoji else ""
        hi_c = max_t[i] if i < len(max_t) else None
        lo_c = min_t[i] if i < len(min_t) else None
        hi_s = format_temperature(hi_c, units=units) if hi_c is not None else "—"
        lo_s = format_temperature(lo_c, units=units) if lo_c is not None else "—"
        p_s = format_precip_mm(precip[i] if i < len(precip) else None, units=units)
        if i < len(prob) and prob[i] is not None and isinstance(prob[i], int | float):
            pr_s = f"{float(prob[i]):.0f}% chance"
        else:
            pr_s = "—"
        cells.append(
            f"[b]{day}[/b]\n{em}{desc}\n{lo_s} / {hi_s}\n{p_s}\n{pr_s}",
        )
    return cells


def hourly_table_rows(
    data: dict[str, Any],
    *,
    units: UnitsKind = "metric",
    max_hours: int = 48,
) -> list[tuple[str, str, str, str]]:
    """Build rows for the hourly modal: (time_label, temp, prob, summary)."""
    from klima.weather_codes import get_weather_description

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])[:max_hours]
    temps = hourly.get("temperature_2m", [])
    probs = hourly.get("precipitation_probability", [])
    codes = hourly.get("weather_code", [])
    rows = []
    for i, iso in enumerate(times):
        lbl = "??:??"
        try:
            dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
            lbl = dt.strftime("%a %H:%M")
        except (ValueError, TypeError):
            pass
        t = temps[i] if i < len(temps) else None
        tc = float(t) if t is not None and isinstance(t, int | float) else None
        temp_s = format_temperature(tc, units=units) if tc is not None else "—"
        if i < len(probs) and probs[i] is not None:
            rp = probs[i]
            pr_s = f"{float(rp):.0f}%" if isinstance(rp, int | float) else "—"
        else:
            pr_s = "—"
        code = codes[i] if i < len(codes) else 0
        code_int = int(code) if isinstance(code, int | float) else 0
        summary = get_weather_description(code_int)
        rows.append((lbl, temp_s, pr_s, summary))
    return rows


def night_mode_from_daily(forecast: dict[str, Any]) -> bool:
    """Dark UI when local time is outside sunrise–sunset for forecast day index 0."""
    daily = forecast.get("daily") or {}
    sr_l = daily.get("sunrise") or []
    ss_l = daily.get("sunset") or []
    t0 = daily.get("time") or []
    if not sr_l or not ss_l or not t0:
        return False
    try:
        day = datetime.fromisoformat(str(t0[0])).date()
        if datetime.now().date() != day:
            return False
        sunrise = datetime.fromisoformat(str(sr_l[0]).replace("Z", "+00:00"))
        sunset = datetime.fromisoformat(str(ss_l[0]).replace("Z", "+00:00"))
        now_local = datetime.now().astimezone()
        sunrise_cmp = sunrise
        sunset_cmp = sunset
        if sunrise.tzinfo is None:
            sunrise_cmp = sunrise.replace(tzinfo=now_local.tzinfo)
            sunset_cmp = sunset.replace(tzinfo=now_local.tzinfo)
        else:
            now_local = now_local.astimezone(sunrise.tzinfo)
        return not (sunrise_cmp <= now_local <= sunset_cmp)
    except (ValueError, TypeError, IndexError):
        return False


def coords_label(lat: float, lon: float) -> str:
    """Format signed coordinates with N/S/E/W."""
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    return f"{abs(lat):.2f}°{ns}, {abs(lon):.2f}°{ew}"


def hourly_xticks(n: int) -> tuple[list[float], list[str]]:
    """~7 ticks across n hourly points."""
    if n <= 0:
        return [], []
    hours = list(range(n))
    pos = sorted(
        {
            max(0, min(n - 1, p))
            for p in (0, n // 6, 2 * n // 6, 3 * n // 6, 4 * n // 6, 5 * n // 6, n - 1)
        },
    )
    return [float(p) for p in pos], [str(hours[i]) for i in pos]


def nearest_hour_slot_index(times: Sequence[str], cap: int) -> float | None:
    """Plot x-index (0 … cap-1) of the hourly row closest to current local time."""
    if cap <= 0:
        return None
    bounded = min(cap, len(times))
    if bounded == 0:
        return None
    try:
        now = datetime.now().astimezone()
        best_gap: float | None = None
        best_i = 0.0
        for i in range(bounded):
            raw = datetime.fromisoformat(str(times[i]).replace("Z", "+00:00"))
            cand = raw
            if raw.tzinfo is None:
                cand = raw.replace(tzinfo=now.tzinfo)
            gap = abs((cand - now).total_seconds())
            if best_gap is None or gap < best_gap:
                best_gap = gap
                best_i = float(i)
        return best_i
    except (ValueError, TypeError, OSError):
        return None


def sun_event_hour_index(times: Sequence[str], event_iso: str | None, cap: int) -> float | None:
    """Index of hourly slot nearest sunrise/sunset (for vertical guide lines)."""
    if not event_iso or cap <= 0:
        return None
    try:
        ev = datetime.fromisoformat(str(event_iso).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    best_gap: float | None = None
    best_i: float | None = None
    for i in range(min(cap, len(times))):
        try:
            ht = datetime.fromisoformat(str(times[i]).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue
        htz, etz = ht, ev
        if ht.tzinfo is None and ev.tzinfo is not None:
            htz = ht.replace(tzinfo=ev.tzinfo)
        elif ev.tzinfo is None and ht.tzinfo is not None:
            etz = ev.replace(tzinfo=ht.tzinfo)
        gap = abs((htz - etz).total_seconds())
        if best_gap is None or gap < best_gap:
            best_gap = gap
            best_i = float(i)
    return best_i


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
