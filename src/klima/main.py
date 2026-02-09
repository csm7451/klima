"""Klima — terminal weather app with Textual."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Sequence

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.widgets import Footer, Header, Input, Label, Static
from textual.worker import get_current_worker
from textual_plotext import PlotextPlot

from klima.api import get_forecast, search_location
from klima.weather_codes import get_weather_color, get_weather_description


def _format_day(iso_date: str, day_index: int | None = None) -> str:
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


class CurrentWeather(Static):
    """Current conditions panel with color from weather code."""

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        self._data = data or {}
        content = self._format_content() if self._data else ""
        super().__init__(content, **kwargs)

    def set_data(self, data: dict[str, Any]) -> None:
        self._data = data
        self.update(self._format_content())

    def _format_content(self) -> str:
        cur = self._data.get("current", {})
        code = cur.get("weather_code", 0)
        desc = get_weather_description(code)
        temp = cur.get("temperature_2m")
        feels = cur.get("apparent_temperature")
        humidity = cur.get("relative_humidity_2m")
        wind = cur.get("wind_speed_10m")
        precip = cur.get("precipitation")
        cloud = cur.get("cloud_cover")

        temp_s = f"{temp:.0f}°C" if temp is not None else "—"
        feels_s = f"Feels like {feels:.0f}°C" if feels is not None else ""
        humidity_s = f"{humidity:.0f}%" if humidity is not None else ""
        wind_s = f"{wind:.0f} km/h" if wind is not None else ""
        precip_s = f"{precip:.1f} mm" if precip is not None else ""
        cloud_s = f"{cloud:.0f}%" if cloud is not None else ""

        lines = [
            f"[b]{temp_s}[/b]",
            desc,
            feels_s,
            "",
            f"Humidity: {humidity_s}  Wind: {wind_s}",
            f"Precip: {precip_s}  Clouds: {cloud_s}",
        ]
        return "\n".join(l for l in lines if l)

    def on_mount(self) -> None:
        pass


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
        # make more readable
        for i in range(min(7, len(times))):
            day = _format_day(times[i], i)
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

    def on_mount(self) -> None:
        pass


class CityInfo(Static):
    """Panel showing selected city/location details from geocoding."""

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        self._data = data or {}
        content = self._format_content()
        super().__init__(content, **kwargs)

    def _format_content(self) -> str:
        if not self._data:
            return "—"
        lines = []
        name = self._data.get("name", "")
        country = self._data.get("country", "")
        admin1 = self._data.get("admin1", "")
        tz = self._data.get("timezone", "")
        lat = self._data.get("latitude")
        lon = self._data.get("longitude")
        elev = self._data.get("elevation")
        pop = self._data.get("population")

        if country and name:
            lines.append(f"[b]{name}[/b], {country}")
        elif name:
            lines.append(f"[b]{name}[/b]")
        if admin1:
            lines.append(f"Region: {admin1}")
        if tz:
            lines.append(f"Timezone: {tz}")
        if lat is not None and lon is not None:
            lines.append(f"Coordinates: {lat:.2f}°N, {lon:.2f}°E")
        if elev is not None:
            lines.append(f"Elevation: {elev:.0f} m")
        if pop is not None and pop > 0:
            lines.append(f"Population: {pop:,}")
        return "\n".join(lines) if lines else "—"


def _format_day_cells(data: dict[str, Any]) -> list[str]:
    """Return 7 strings, one per day, for left-to-right layout."""
    daily = data.get("daily", {})
    times = daily.get("time", [])[:7]
    codes = daily.get("weather_code", [])
    max_t = daily.get("temperature_2m_max", [])
    min_t = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])
    cells = []
    for i in range(7):
        if i >= len(times):
            cells.append("[b]—[/b]\n—\n— / —\n—")
            continue
        day = _format_day(times[i], i)
        desc = get_weather_description(codes[i]) if i < len(codes) else "?"
        hi = f"{max_t[i]:.0f}°" if i < len(max_t) else "—"
        lo = f"{min_t[i]:.0f}°" if i < len(min_t) else "—"
        p = f"{precip[i]:.0f} mm" if i < len(precip) and precip[i] else "—"
        cells.append(f"[b]{day}[/b]\n{desc}\n{lo} / {hi}\n{p}")
    return cells


def _y_ticks_from_data(
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


class WeatherDashboard(Container):
    """Main weather view: current, sparklines, daily."""

    def __init__(
        self,
        location_name: str,
        forecast_data: dict[str, Any] | None = None,
        location_info: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._location_name = location_name
        self._forecast_data = forecast_data or {}
        self._location_info = location_info or {}

    def compose(self) -> ComposeResult:
        cur = self._forecast_data.get("current", {})
        code = cur.get("weather_code", 0)
        hex_color = get_weather_color(code)

        with Vertical(id="dashboard-vertical"):
            yield Label(f"[b]📍 {self._location_name}[/b]", id="location-label")
            with Horizontal(id="current-row"):
                with Container(id="current-section"):
                    current = CurrentWeather(self._forecast_data)
                    current.styles.border = ("heavy", hex_color)
                    current.styles.padding = (1, 2)
                    yield current
                yield CityInfo(self._location_info)

            yield Label("[b]Next 24h[/b]", classes="section-label")
            with Horizontal(id="charts-row"):
                with Vertical(classes="chart-column"):
                    yield PlotextPlot(id="temp-plot")
                with Vertical(classes="chart-column"):
                    yield PlotextPlot(id="precip-plot")

            yield Label("[b]7-day forecast[/b]", classes="section-label")
            with Horizontal(id="daily-row"):
                for cell in _format_day_cells(self._forecast_data):
                    yield Static(cell, classes="day-cell")

    def on_mount(self) -> None:
        self._build_charts()

    def _build_charts(self) -> None:
        """Build or refresh the temperature and precipitation plots."""
        hourly = self._forecast_data.get("hourly", {})
        raw_temps = hourly.get("temperature_2m", [])[:24] or [0.0]
        raw_precipts = hourly.get("precipitation", [])[:24] or [0.0]
        temps = [round(t, 1) for t in raw_temps]
        precipts = [round(p) for p in raw_precipts]
        hours = list(range(len(temps)))
        # X-axis: whole hours (e.g. 0, 4, 8, 12, 16, 20, 23)
        n = len(hours)
        x_pos = sorted({max(0, p) for p in (0, n // 6, 2 * n // 6, 3 * n // 6, 4 * n // 6, 5 * n // 6, n - 1)})
        x_pos_float = [float(p) for p in x_pos]
        x_lbl = [str(hours[i]) for i in x_pos]

        try:
            temp_plot = self.query_one("#temp-plot", PlotextPlot)
            plt = temp_plot.plt
            plt.clear_data()
            plt.ylabel("°C")
            plt.xlabel("Hour")
            plt.plot(hours, temps)
            plt.xticks(x_pos_float, x_lbl)
            y_pos, y_lbl = _y_ticks_from_data(temps, fmt="{:.1f}")
            plt.yticks(y_pos, y_lbl)
            if len(y_pos) > 0:
                mid_y = y_pos[len(y_pos) // 2]
                plt.hline(mid_y, color=245)
            plt.title("Temperature (°C)")
            temp_plot.refresh()
        except Exception:  # Widget may not be mounted yet
            pass

        try:
            precip_plot = self.query_one("#precip-plot", PlotextPlot)
            plt = precip_plot.plt
            plt.clear_data()
            plt.ylabel("mm")
            plt.xlabel("Hour")
            plt.ylim(lower=0)
            plt.bar(hours, precipts, reset_ticks=False)
            plt.xticks(x_pos_float, x_lbl)
            # Include 0 in y range so axis starts at 0 mm
            y_pos, y_lbl = _y_ticks_from_data([0] + list(precipts), fmt="{:.0f}")
            plt.yticks(y_pos, y_lbl)
            if len(y_pos) > 0:
                mid_y = y_pos[len(y_pos) // 2]
                plt.hline(mid_y, color=245)
            plt.title("Precipitation (mm)")
            precip_plot.refresh()
        except Exception:
            pass

    def set_forecast(self, data: dict[str, Any]) -> None:
        self._forecast_data = data
        current = self.query_one("#current-section CurrentWeather", CurrentWeather)
        current.set_data(data)
        cells = _format_day_cells(data)
        for static, content in zip(
            self.query("#daily-row .day-cell"),
            cells,
        ):
            if isinstance(static, Static):
                static.update(content)
        self._build_charts()


class LocationInputScreen(Container):
    """Screen to enter city name when not provided via CLI."""

    def compose(self) -> ComposeResult:
        yield Label("Enter a city or location:", id="prompt-label")
        yield Input(
            placeholder="e.g. Berlin, London, New York",
            id="location-input",
        )
        yield Label("(Press Enter to search)", id="hint-label")


class KlimaApp(App[None]):
    """Terminal weather app using Open-Meteo."""

    TITLE = "Klima — Weather"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("n", "new_location", "New location"),
    ]

    CSS = """
    Screen {
        align: center middle;
    }

    #dashboard-vertical {
        width: 100%;
        align: center middle;
    }

    #location-label {
        width: 100%;
        content-align: center middle;
        margin-top: 1;
        margin-bottom: 1;
        color: $primary;
    }

    #current-row {
        width: 100%;
        height: 11;
        margin: 0 1 2 1;
    }

    #current-row #current-section {
        width: auto;
        max-width: 50;
        min-width: 24;
        height: 100%;
    }

    #current-row CityInfo {
        width: 1fr;
        min-width: 20;
        height: 100%;
        padding: 1 2;
        border: heavy $surface-lighten-2;
        color: $text-muted;
    }

    .section-label {
        width: 100%;
        margin: 1 0 0 0;
        color: $secondary;
        content-align: center middle;
    }

    #charts-row {
        width: 100%;
        height: auto;
        min-height: 16;
        margin: 0 1 2 1;
        padding: 0;
        border: solid $primary 30%;
    }

    #charts-row .chart-column {
        width: 1fr;
        min-width: 20;
        height: auto;
        align: center middle;
    }

    #charts-row PlotextPlot {
        width: 100%;
        height: 14;
        min-height: 10;
    }

    #daily-row {
        width: 100%;
        margin: 0 1 1 1;
        padding: 1;
        border: solid $primary 20%;
    }

    #daily-row .day-cell {
        width: 1fr;
        min-width: 10;
        padding: 0 1;
        border-left: solid $primary 15%;
    }

    #daily-row .day-cell:first-child {
        border-left: none;
    }

    LocationInputScreen {
        width: 40;
        height: auto;
        padding: 2;
        border: solid $primary;
        align: center middle;
    }

    #prompt-label {
        width: 100%;
        margin-bottom: 1;
    }

    #location-input {
        width: 100%;
        margin-bottom: 1;
    }

    #hint-label {
        width: 100%;
        color: $text-muted;
    }

    .error-box {
        width: 100%;
        max-width: 50;
        padding: 1 2;
        border: solid $error;
        color: $error;
        margin: 1 1;
        content-align: center middle;
    }
    """

    def __init__(self, initial_location: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._initial_location = (initial_location or "").strip()
        self._forecast_data: dict[str, Any] | None = None
        self._location_name = ""
        self._location_info: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        if self._initial_location:
            yield ScrollableContainer(
                Static("Loading…", id="loading-label"),
                id="main-container",
            )
        else:
            yield ScrollableContainer(
                LocationInputScreen(id="input-screen"),
                id="main-container",
            )
        yield Footer()

    def on_mount(self) -> None:
        if self._initial_location:
            loc = self._initial_location
            self.run_worker(
                lambda: self._fetch_weather_sync(loc),
                thread=True,
            )

    def _replace_main(self, widget: Static | Container) -> None:
        container = self.query_one("#main-container", ScrollableContainer)
        container.remove_children()
        container.mount(widget)

    def _fetch_weather_sync(self, location_query: str) -> None:
        """Run in a thread worker; calls API then updates UI via call_from_thread."""
        worker = get_current_worker()
        try:
            results = search_location(location_query, count=1)
            if not results:
                self.call_from_thread(
                    self._show_error,
                    f"No results for “{location_query}”. Try another name.",
                )
                return
            first = results[0]
            self._location_info = dict(first)
            name = first.get("name", "?")
            country = first.get("country", "")
            if country:
                self._location_name = f"{name}, {country}"
            else:
                self._location_name = name
            lat = first["latitude"]
            lon = first["longitude"]
            tz = first.get("timezone", "auto")
            data = get_forecast(lat, lon, timezone=tz)
            self._forecast_data = data
            if not (worker and worker.is_cancelled):
                self.call_from_thread(self._show_dashboard)
        except Exception as e:
            if not (worker and worker.is_cancelled):
                self.call_from_thread(self._show_error, str(e))

    def _show_dashboard(self) -> None:
        if not self._forecast_data:
            return
        self._replace_main(
            WeatherDashboard(
                self._location_name,
                self._forecast_data,
                location_info=self._location_info,
            ),
        )

    def _show_error(self, message: str) -> None:
        self._replace_main(
            Static(f"Error: {message}", classes="error-box"),
        )

    def _show_input_screen(self) -> None:
        container = self.query_one("#main-container", ScrollableContainer)
        if container.children and isinstance(container.children[0], LocationInputScreen):
            return  # already on location screen
        self._replace_main(LocationInputScreen(id="input-screen"))

    def action_new_location(self) -> None:
        self._show_input_screen()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "location-input":
            return
        value = (event.input.value or "").strip()
        if not value:
            return
        event.input.value = ""
        self._replace_main(Static("Loading…", id="loading-label"))
        self.run_worker(
            lambda: self._fetch_weather_sync(value),
            thread=True,
        )


def main() -> None:
    import sys
    location = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    app = KlimaApp(initial_location=location)
    app.run()


if __name__ == "__main__":
    main()
