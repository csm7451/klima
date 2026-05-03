<p align="center">
  <img src="https://github.com/user-attachments/assets/d5c865be-0ef6-4411-a9f5-eb9a1bd5ee14" alt="A cloud with sun peeking behind" width="320">
</p>

<h1 align="center">klima</h1>

<p align="center">
  <a href="https://github.com/YOUR_GITHUB_USER/klima/actions/workflows/ci.yml"><img src="https://github.com/YOUR_GITHUB_USER/klima/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
  <img src="https://img.shields.io/badge/python-3.12%2B-blue?style=flat-square" alt="Python 3.12+">
  <a href="https://github.com/YOUR_GITHUB_USER/klima/releases/tag/v1.0.0"><img src="https://img.shields.io/badge/version-1.0.0-informational?style=flat-square" alt="Version 1.0.0"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPLv3-blue?style=flat-square" alt="GNU GPLv3"></a>
</p>

<p align="center">
  <strong>Terminal weather at a glance</strong> — minimal TUI built with Python and Textual.
</p>
<p align="center">
  <a href="#demo">Demo</a> •
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick start</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#releases--versioning">Releases</a>
</p>

---

## Demo

Record a README GIF locally with **[VHS](https://github.com/charmbracelet/vhs)**. The tape is **[`docs/demo.tape`](docs/demo.tape)** — from the repo root:

```bash
vhs docs/demo.tape    # writes docs/demo.gif — commit alongside the README if you want an inline preview
```


**klima** is a lightweight weather app that runs entirely in the terminal. It uses **[Open-Meteo](https://open-meteo.com/)** (forecast, geocoding, and air quality) — no signup or API keys.

## Features

| Area | What you get |
|------|----------------|
| **Location** | Typed search or recent picks on the landing screen; disambiguation when several places match |
| **Current** | Temp & emoji, sunrise/sunset, humidity, wind (speed + compass arrow), precip, clouds |
| **Charts** | Next 24h temperature + precipitation with “now” and sunrise/sunset markers |
| **7-day forecast** | High/low per day, precipitation amount, POP %, condition text + emoji |
| **Air & UV** | Current US or EU AQI and UV from the Open-Meteo Air Quality API |
| **Multi-city** | Pass 2–3 place names on the CLI for side-by-side compare |
| **Config** | Optional `~/.config/klima/config.toml` (theme, units, refresh interval, default locations) |
| **History** | Successful picks saved under `~/.config/klima/history.json` |

## Quick start

**Prerequisites:** Python 3.12+, **[uv](https://docs.astral.sh/uv/)** (recommended) or pip.

```bash
git clone https://github.com/YOUR_GITHUB_USER/klima.git && cd klima
uv sync --all-groups
```

Run with **one city**, **multiple cities** (compare), or **no args** for the interactive search screen:

```bash
uv run klima Berlin
uv run klima Paris "New York" Tokyo   # compares up to three
uv run klima                            # prompts for a query
uv run klima --theme nord --units imperial --refresh-minutes 15
uv run klima --debug                  # writes ~/.cache/klima/klima.log
```

After you publish or fork, replace `YOUR_GITHUB_USER` in this README, in [`pyproject.toml`](pyproject.toml) (`[project.urls]`), and in [`CHANGELOG.md`](CHANGELOG.md) link footers so badges and links resolve.

## Example config (`~/.config/klima/config.toml`)

```toml
theme = "nord"
units = "metric"
refresh_minutes = 30

# Optional CLI defaults when you launch with no arguments:
locations = ["Berlin", "London"]
```

## Tech stack

- **Python 3.12+** — typed where practical (`py.typed` shipped).
- **[Textual](https://textual.textualize.io/)** — layout, overlays, timers, themes.
- **[textual-plotext](https://github.com/Textualize/textual-plotext)** — hourly charts.
- **requests** — synchronous HTTP inside workers.
- **Open-Meteo** — weather, geocoding, CAMS-style air-quality endpoint.

## Engineering notes

Useful context if you are reviewing this repo or comparing it to other CLI projects:

- **CI** (GitHub Actions): Ruff format + lint, Mypy, pytest, and a release wheel build on Python 3.12 and 3.13 ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)).
- **Tests**: unit tests plus **Textual snapshot** SVG checks for stable UI output.
- **Packaging**: [Hatchling](https://hatch.pypa.io/) + **uv**; version is the `__version__` string in [`src/klima/__init__.py`](src/klima/__init__.py) (single source for `klima --version` and the built wheel).
- **No API keys** for the default weather path (public Open-Meteo endpoints over HTTPS).

## Project structure

```
src/klima/
├── main.py            # argparse CLI
├── app.py             # KlimaApp, workers, overlays, auto-refresh
├── api.py             # forecast + geocode + optional air-quality
├── config.py          # ~/.config/klima/config.toml
├── formatting.py      # day cells, wind helpers, hourly table text
├── history.py        # ~/.config/klima/history.json
├── units_conv.py     # metric / imperial
├── weather_codes.py   # WMO → text, hex color, emoji
├── screens.py         # Help, location picker, hourly modal
├── klima.tcss         # Styles (including narrow-terminal tweaks)
└── widgets/           # dashboard, compare layout, panels, …
tests/                  # pytest + textual snapshot SVG
docs/demo.tape         # VHS recipe for README GIF
```

## Contributing

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for setup, the same commands CI runs, and how to update snapshots. The **[Code of Conduct](CODE_OF_CONDUCT.md)** applies to issues and pull requests. Security disclosures: **[SECURITY.md](SECURITY.md)**.

Quick local check:

```bash
uv sync --all-groups
uv run ruff format --check . && uv run ruff check . && uv run mypy src/klima && uv run pytest tests/
```

Issue templates: [bug report](.github/ISSUE_TEMPLATE/bug_report.yml), [feature request](.github/ISSUE_TEMPLATE/feature_request.yml). Pull requests use [`.github/pull_request_template.md`](.github/pull_request_template.md).

## Releases & versioning

**Current release: [1.0.0](https://github.com/YOUR_GITHUB_USER/klima/releases/tag/v1.0.0)** — first stable line under [Semantic Versioning](https://semver.org/). Summary of changes: **[CHANGELOG.md](CHANGELOG.md)**. Installable version string: `klima --version` (from `klima.__version__`).

## License

GNU GPLv3 — see [LICENSE](LICENSE).
