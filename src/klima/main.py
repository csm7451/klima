"""Klima — terminal weather app. Entrypoint and CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from klima import __version__
from klima.app import KlimaApp
from klima.config import DEFAULT_CONFIG_PATH, load_cli_config


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="klima",
        description=(
            "Terminal weather via Open-Meteo. Give one city, several for compare, "
            "or omit to search interactively."
        ),
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    p.add_argument(
        "--config",
        type=Path,
        default=None,
        help=f"Path to config TOML (default: {DEFAULT_CONFIG_PATH})",
    )
    p.add_argument(
        "--theme",
        default=None,
        help="Textual theme name (e.g. nord, gruvbox, textual-dark)",
    )
    p.add_argument(
        "--units",
        choices=("metric", "imperial"),
        default=None,
        help="Temperature / wind / precip units",
    )
    p.add_argument(
        "--refresh-minutes",
        type=int,
        default=None,
        metavar="N",
        help="Auto-refresh interval in minutes (minimum 1; default from config or 30)",
    )
    p.add_argument(
        "--debug",
        action="store_true",
        help=f"Write debug logs to {Path.home() / '.cache' / 'klima' / 'klima.log'}",
    )
    p.add_argument(
        "locations",
        nargs="*",
        metavar="LOCATION",
        help="City name(s). Two or three locations open multi-city compare.",
    )
    return p


def main() -> None:
    args = build_arg_parser().parse_args()
    cfg_path = args.config.expanduser() if args.config else DEFAULT_CONFIG_PATH
    cfg = load_cli_config(cfg_path)
    if args.theme:
        cfg.theme = args.theme
    if args.units is not None and args.units in ("metric", "imperial"):
        cfg.units = args.units
    if args.refresh_minutes is not None:
        cfg.refresh_minutes = max(1, min(720, int(args.refresh_minutes)))
    if args.debug:
        cfg.debug = True

    locs = [x.strip() for x in args.locations if x.strip()]
    if not locs:
        locs = list(cfg.file_locations)

    app = KlimaApp(locations_on_launch=locs, cli=cfg)
    app.run()


if __name__ == "__main__":
    main()
