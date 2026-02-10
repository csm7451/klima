"""Klima TUI app: entry screen, dashboard, and async fetch flow."""

from __future__ import annotations

from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer
from textual.widgets import Footer, Header, Input, Static
from textual.worker import get_current_worker

from klima.api import get_forecast, search_location
from klima.widgets import LocationInputScreen, WeatherDashboard


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
                    f"No results for \"{location_query}\". Try another name.",
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
            return
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
