<p align="center">
  <img src="https://github.com/user-attachments/assets/d5c865be-0ef6-4411-a9f5-eb9a1bd5ee14" alt="A cloud with sun peeking behind" width="320">
</p>

<h1 align="center">klima</h1>
<p align="center">
  <strong>Terminal weather at a glance</strong> — minimal TUI built with Python and Textual.
</p>
<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick start</a> •
  <a href="#tech-stack">Tech stack</a> •
  <a href="#project-structure">Structure</a>
</p>

---

**klima** is a lightweight weather app that runs entirely in the terminal. It uses the [Open-Meteo](https://open-meteo.com/) API (no signup or API keys), and focuses on a simple layout and fast workflow.

## Features

| Area | What you get |
|------|----------------|
| **Location** | Search by city or place name; coordinates resolved via Open-Meteo Geocoding. |
| **Current conditions** | Temperature, feels-like, humidity, wind, precipitation, clouds.  |
| **Next 24h** | In-terminal plotext charts for temperature and precipitation. |
| **7-day forecast** | Today / Tomorrow labels, then weekday; daily highs/lows, conditions, and precipitation. |
| **Zero config** | No API keys or config files required to run. |

## Quick start

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/) (or pip).

```bash
git clone https://github.com/yourusername/klima.git && cd klima
uv sync
```

**Run with a city (recommended):**

```bash
uv run klima Berlin
# or: uv run klima "New York"
```

**Run without arguments:** the app opens and prompts you to type a location and press Enter.

| Key | Action |
|-----|--------|
| **q** | Quit |
| **n** | New location |

## Tech stack

- **Python 3.12+** - App and CLI logic, type hints throughout.
- **[Textual](https://github.com/textualize/textual/)** - TUI framework (layout, widgets, bindings).
- **[textual-plotext](https://github.com/Textualize/textual-plotext)** - In-terminal charts for 24h temperature and precipitation.
- **requests** - HTTP for Open-Meteo Geocoding and Weather APIs.
- **[Open-Meteo](https://open-meteo.com)** - Weather and geocoding (no API key, free tier).

## Project structure

```
src/klima/
├── main.py           # CLI entrypoint
├── app.py            # KlimaApp: screens, bindings, async fetch
├── api.py            # Open-Meteo geocoding + forecast client
├── formatting.py     # Date/day labels, day cells, chart axis helpers
├── weather_codes.py  # WMO code → description + border color
└── widgets/          # UI components
    ├── current_weather.py
    ├── city_info.py
    ├── daily_forecast.py
    ├── location_input.py
    └── dashboard.py  # Main dashboard + 24h charts
```

## Contributing

Contributions are welcome. Open an issue or PR; for larger changes, an issue first is appreciated.

## License

GNU GPLv3 — see [LICENSE](LICENSE).
