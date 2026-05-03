"""Load and persist ~/.config/klima/config.toml (optional)."""

from __future__ import annotations

import logging
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "klima" / "config.toml"


@dataclass
class CliConfig:
    """Startup settings merged from defaults, optional TOML, then argparse."""

    theme: str = "nord"
    units: Literal["metric", "imperial"] = "metric"
    refresh_minutes: int = 30
    debug: bool = False
    config_path: Path = field(default_factory=lambda: DEFAULT_CONFIG_PATH)
    file_locations: list[str] = field(default_factory=list)


def load_cli_config(config_path: Path | None = None) -> CliConfig:
    cfg = CliConfig()
    path = config_path if config_path is not None else DEFAULT_CONFIG_PATH
    cfg.config_path = path
    if not path.exists():
        return cfg
    try:
        data = tomllib.loads(path.read_text())
    except (OSError, tomllib.TOMLDecodeError) as e:
        logging.warning("Could not load config %s: %s", path, e)
        return cfg
    if isinstance(data.get("theme"), str):
        cfg.theme = data["theme"]
    if isinstance(data.get("units"), str):
        u = data["units"].strip().lower()
        if u == "metric" or u == "imperial":
            cfg.units = u
    r = data.get("refresh_minutes")
    if isinstance(r, int):
        cfg.refresh_minutes = max(1, min(720, r))
    locs = data.get("locations")
    if isinstance(locs, list):
        cfg.file_locations = [str(x).strip() for x in locs if isinstance(x, str) and str(x).strip()]
    return cfg


def persist_live_settings(path: Path, *, theme: str, units: str, refresh_minutes: int) -> None:
    """Write theme, units, and refresh_interval (best-effort, overwrites minimal keys)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing_file_locs: list[str] = []
    if path.exists():
        try:
            parsed = tomllib.loads(path.read_text())
            raw = parsed.get("locations")
            if isinstance(raw, list):
                existing_file_locs = [
                    str(x).strip() for x in raw if isinstance(x, str) and str(x).strip()
                ]
        except (OSError, tomllib.TOMLDecodeError):
            existing_file_locs = []
    lines = [
        f'theme = "{_escape(theme)}"',
        f'units = "{_escape(units)}"',
        f"refresh_minutes = {int(refresh_minutes)}",
    ]
    if existing_file_locs:
        inner = ", ".join(f'"{_escape(loc)}"' for loc in existing_file_locs)
        lines.append(f"locations = [{inner}]")
    path.write_text("\n".join(lines) + "\n")


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def toggle_units(current: Literal["metric", "imperial"]) -> Literal["metric", "imperial"]:
    return "imperial" if current == "metric" else "metric"
