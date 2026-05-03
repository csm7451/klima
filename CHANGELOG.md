# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] — 2026-05-03

First stable release: full TUI feature set, packaging metadata, contributor docs, and security policy.

### Added

- Help overlay (`?`), refresh (`r`), units toggle (`u`), theme cycle (`t`), hourly modal (`h`).
- Location disambiguation when geocoding returns multiple matches.
- Recent locations cache under `~/.config/klima/history.json`.
- Optional `~/.config/klima/config.toml` for theme, units, refresh interval, and default compare locations.
- Auto-refresh on a configurable interval.
- Air quality + UV summary panel (Open-Meteo Air Quality API, current values).
- Multi-city compare for two or three CLI locations.
- Wind direction arrows, sunrise/sunset line, precipitation probability on 7-day cells.
- Correct N/S/E/W coordinate labels.
- Horizontal overflow and tightened min-widths for smaller terminals.
- Public package metadata (PyPI-oriented classifiers, project URLs), semantic versioning from `klima.__version__`, and contributor documentation (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`).

### Removed

- Unused `DailyForecast` widget module.

### Changed

- CLI switched to `argparse` (`--version`, `--theme`, `--units`, `--refresh-minutes`, `--config`, `--debug`).
- Summary row (`ItemGrid`): more horizontal space for current weather and the AQI/UV column than for the location panel (`grid-columns: auto 2fr 1fr`); all three summary cells use `heavy` borders (current weather border color still follows the condition code).
- AQI/UV strip shows **current** readings from the air-quality endpoint only (daily forecast UV max is not mixed in).
- Location panel lists each geocode field on its own labeled line (name, country, region, timezone, coordinates, elevation, population).

[Unreleased]: https://github.com/YOUR_GITHUB_USER/klima/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/YOUR_GITHUB_USER/klima/releases/tag/v1.0.0
