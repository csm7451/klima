from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, ItemGrid, Vertical
from textual.widgets import Label, Static
from textual_plotext import PlotextPlot

from klima.formatting import (
    format_day_cells,
    hourly_xticks,
    nearest_hour_slot_index,
    night_mode_from_daily,
    sun_event_hour_index,
    y_ticks_from_data,
)
from klima.units_conv import (
    UnitsKind,
    celsius_to_chart_value,
    precip_axis_title,
    temp_axis_label,
)
from klima.weather_codes import get_weather_color, get_weather_emoji
from klima.widgets.air_quality_panel import AirQualityPanel
from klima.widgets.city_info import CityInfo
from klima.widgets.current_weather import CurrentWeather


class WeatherDashboard(Container):
    """Main weather view: current, charts, daily."""

    def __init__(
        self,
        location_name: str,
        forecast_data: dict[str, Any] | None = None,
        location_info: dict[str, Any] | None = None,
        *,
        units: UnitsKind = "metric",
        air_quality: dict[str, Any] | None = None,
        night_mode: bool | None = None,
        show_emoji: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._location_name = location_name
        self._forecast_data = forecast_data or {}
        self._location_info = location_info or {}
        self._units = units
        self._aq = air_quality
        self._show_emoji = show_emoji
        if night_mode is None:
            self._night = night_mode_from_daily(self._forecast_data)
        else:
            self._night = night_mode

    def compose(self) -> ComposeResult:
        cur = self._forecast_data.get("current", {})
        code_raw = cur.get("weather_code", 0)
        code = int(code_raw) if isinstance(code_raw, int | float) else 0
        hex_color = get_weather_color(code)
        em = get_weather_emoji(code) if self._show_emoji else ""
        title_prefix = f"{em} " if em else ""
        dash_cls = "dash-root"
        if self._night:
            dash_cls += " theme-night"

        with Vertical(classes=dash_cls, id="dashboard-vertical"):
            yield Label(
                f"[b]{title_prefix}📍 {self._location_name}[/b]",
                id="location-label",
            )
            # Current weather | AQI/UV | geocode details — widths from klima.tcss (2fr middle).
            with ItemGrid(id="summary-block", regular=True):
                section = Container(
                    CurrentWeather(
                        self._forecast_data,
                        units=self._units,
                        show_emoji=self._show_emoji,
                        id="current-static",
                    ),
                    id="current-section",
                )
                section.styles.border = ("heavy", hex_color)
                section.styles.padding = (1, 2)
                yield section
                yield AirQualityPanel(id="aq-strip")
                yield CityInfo(self._location_info, id="city-info")

            yield Label("[b]Next 24h[/b]", classes="section-label")
            with Horizontal(id="charts-row"):
                with Vertical(classes="chart-column"):
                    yield PlotextPlot(id="temp-plot")
                with Vertical(classes="chart-column"):
                    yield PlotextPlot(id="precip-plot")

            yield Label("[b]7-day forecast[/b]", classes="section-label")
            with Horizontal(id="daily-row"):
                for cell in format_day_cells(
                    self._forecast_data,
                    units=self._units,
                    emoji=self._show_emoji,
                ):
                    yield Static(cell, classes="day-cell")

    def on_mount(self) -> None:
        aq = self.query_one("#aq-strip", AirQualityPanel)
        aq.set_payload(self._aq)
        self._build_charts()

    def _precip_chart_values(self, raw_mm: list[float]) -> list[float]:
        if self._units == "imperial":
            return [round(m / 25.4, 3) for m in raw_mm]
        return [round(p, 1) for p in raw_mm]

    def _build_charts(self) -> None:
        """Build or refresh the temperature and precipitation plots."""
        hourly = self._forecast_data.get("hourly", {})
        daily = self._forecast_data.get("daily", {})
        raw_temps = hourly.get("temperature_2m", [])[:24] or [0.0]
        raw_precipts = hourly.get("precipitation", [])[:24] or [0.0]
        times = hourly.get("time", [])
        sr0 = None
        ss0 = None
        sunrise = daily.get("sunrise") or []
        sunset = daily.get("sunset") or []
        if sunrise:
            sr0 = sunrise[0]
        if sunset:
            ss0 = sunset[0]
        temps = [round(celsius_to_chart_value(float(t), self._units), 1) for t in raw_temps]
        precipts = self._precip_chart_values([float(p) for p in raw_precipts])
        hours = list(range(len(temps)))
        n = len(hours)
        x_pos_float, x_lbl = hourly_xticks(n)

        now_ix = nearest_hour_slot_index(times, n)
        sun_ix = sun_event_hour_index(times, sr0, n)
        set_ix = sun_event_hour_index(times, ss0, n)

        def draw_vlines(plt_d: PlotextPlot) -> None:
            plt = plt_d.plt
            candidates = [(now_ix, 226), (sun_ix, 51), (set_ix, 208)]
            for coord, clr in candidates:
                if coord is None:
                    continue
                plt.vline(coord, color=clr)

        try:
            temp_plot = self.query_one("#temp-plot", PlotextPlot)
            plt_t = temp_plot.plt
            plt_t.clear_data()
            plt_t.ylabel(temp_axis_label(self._units))
            plt_t.xlabel("Time")
            plt_t.plot(hours, temps)
            plt_t.xticks(x_pos_float, x_lbl)
            y_pos, y_lbl = y_ticks_from_data(temps, fmt="{:.1f}")
            plt_t.yticks(y_pos, y_lbl)
            plt_t.title(f"Temperature ({temp_axis_label(self._units)})")
            draw_vlines(temp_plot)
            temp_plot.refresh()
        except Exception:
            pass

        try:
            precip_plot = self.query_one("#precip-plot", PlotextPlot)
            plt_p = precip_plot.plt
            plt_p.clear_data()
            yaxis = "in" if self._units == "imperial" else "mm"
            plt_p.ylabel(yaxis)
            plt_p.xlabel("Time")
            plt_p.ylim(lower=0)
            plt_p.bar(hours, precipts, reset_ticks=False)
            plt_p.xticks(x_pos_float, x_lbl)
            y_pos, y_lbl = y_ticks_from_data([0] + list(precipts), fmt="{:.2f}")
            plt_p.yticks(y_pos, y_lbl)
            plt_p.title(precip_axis_title(self._units))
            draw_vlines(precip_plot)
            precip_plot.refresh()
        except Exception:
            pass

    def set_forecast(self, data: dict[str, Any], *, aq: dict[str, Any] | None = None) -> None:
        self._forecast_data = data
        if aq is not None:
            self._aq = aq
        current = self.query_one("#current-static", CurrentWeather)
        current.set_data(data, units=self._units, show_emoji=self._show_emoji)
        self._night = night_mode_from_daily(data)
        dq = self.query_one("#dashboard-vertical", Vertical)
        dq.set_class(self._night, "theme-night")
        cells = format_day_cells(
            data,
            units=self._units,
            emoji=self._show_emoji,
        )
        for static, content in zip(
            self.query("#daily-row .day-cell"),
            cells,
            strict=True,
        ):
            if isinstance(static, Static):
                static.update(content)
        aq_strip = self.query_one("#aq-strip", AirQualityPanel)
        aq_strip.set_payload(self._aq)
        self._build_charts()

    def apply_preferences(
        self,
        *,
        units: UnitsKind | None = None,
        show_emoji: bool | None = None,
    ) -> None:
        if units is not None:
            self._units = units
        if show_emoji is not None:
            self._show_emoji = show_emoji
        self._night = night_mode_from_daily(self._forecast_data)
        dq = self.query_one("#dashboard-vertical", Vertical)
        dq.set_class(self._night, "theme-night")
        current = self.query_one("#current-static", CurrentWeather)
        current.set_data(
            self._forecast_data,
            units=self._units,
            show_emoji=self._show_emoji,
        )
        cells = format_day_cells(
            self._forecast_data,
            units=self._units,
            emoji=self._show_emoji,
        )
        for static, content in zip(
            self.query("#daily-row .day-cell"),
            cells,
            strict=True,
        ):
            if isinstance(static, Static):
                static.update(content)
        self._build_charts()
