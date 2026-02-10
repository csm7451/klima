"""Main weather dashboard: current conditions, 24h charts, 7-day row."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Label, Static
from textual_plotext import PlotextPlot

from klima.formatting import format_day_cells, y_ticks_from_data
from klima.weather_codes import get_weather_color
from klima.widgets.current_weather import CurrentWeather
from klima.widgets.city_info import CityInfo


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
                for cell in format_day_cells(self._forecast_data):
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
            y_pos, y_lbl = y_ticks_from_data(temps, fmt="{:.1f}")
            plt.yticks(y_pos, y_lbl)
            if len(y_pos) > 0:
                mid_y = y_pos[len(y_pos) // 2]
                plt.hline(mid_y, color=245)
            plt.title("Temperature (°C)")
            temp_plot.refresh()
        except Exception:
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
            y_pos, y_lbl = y_ticks_from_data([0] + list(precipts), fmt="{:.0f}")
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
        cells = format_day_cells(data)
        for static, content in zip(
            self.query("#daily-row .day-cell"),
            cells,
        ):
            if isinstance(static, Static):
                static.update(content)
        self._build_charts()
