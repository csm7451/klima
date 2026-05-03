"""Persist recent locations under ~/.config/klima/history.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_HISTORY_DIR = Path.home() / ".config" / "klima"
HISTORY_PATH = _HISTORY_DIR / "history.json"
_MAX = 20


def _coerce(entries: Any) -> list[dict[str, Any]]:
    if not isinstance(entries, list):
        return []
    out: list[dict[str, Any]] = []
    for e in entries:
        if isinstance(e, dict) and isinstance(e.get("label"), str):
            lat, lon = e.get("latitude"), e.get("longitude")
            if isinstance(lat, int | float) and isinstance(lon, int | float):
                tz = e.get("timezone", "auto")
                tz = tz if isinstance(tz, str) else "auto"
                out.append(
                    {
                        "label": str(e["label"]),
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "timezone": tz,
                        "name": e.get("name", e["label"]),
                        "country": e.get("country", ""),
                        "admin1": e.get("admin1", ""),
                    }
                )
    return out


def load_history() -> list[dict[str, Any]]:
    if not HISTORY_PATH.exists():
        return []
    try:
        raw = json.loads(HISTORY_PATH.read_text())
        return _coerce(raw)
    except (json.JSONDecodeError, OSError):
        return []


def save_history(entries: list[dict[str, Any]]) -> None:
    _HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(entries[:_MAX], indent=2))


def push_recent(location_info: dict[str, Any], display_label: str) -> None:
    """Record a resolved place after successful forecast fetch."""
    lat = location_info.get("latitude")
    lon = location_info.get("longitude")
    if not isinstance(lat, int | float) or not isinstance(lon, int | float):
        return
    tz = location_info.get("timezone", "auto")
    tz = tz if isinstance(tz, str) else "auto"
    item = {
        "label": display_label,
        "latitude": float(lat),
        "longitude": float(lon),
        "timezone": tz,
        "name": location_info.get("name", display_label),
        "country": location_info.get("country", ""),
        "admin1": location_info.get("admin1", ""),
    }
    cur = load_history()
    filtered = [
        e
        for e in cur
        if abs(e["latitude"] - item["latitude"]) > 1e-5
        or abs(e["longitude"] - item["longitude"]) > 1e-5
    ]
    filtered.insert(0, item)
    save_history(filtered)
