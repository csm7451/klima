"""Side-by-side weather for multiple resolved locations."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Label, Static

from klima.formatting import format_day_cells, night_mode_from_daily
from klima.units_conv import UnitsKind
from klima.widgets.air_quality_panel import AirQualityPanel
from klima.widgets.city_info import CityInfo
from klima.widgets.current_weather import CurrentWeather


class CompareDashboard(Container):
    """Horizontal layout comparing 2–3 cities."""

    def __init__(
        self,
        *,
        bundles: list[tuple[str, dict[str, Any], dict[str, Any], dict[str, Any] | None]],
        units: UnitsKind,
        night_mode: bool | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._bundles = bundles
        self._units = units
        if night_mode is None and bundles:
            self._night = night_mode_from_daily(bundles[0][1])
        else:
            self._night = bool(night_mode)

    def compose(self) -> ComposeResult:
        root_cls = "compare-root"
        if self._night:
            root_cls += " theme-night"
        with Vertical(classes=root_cls):
            yield Label("[b]Multi-city compare[/b]", id="compare-title")
            with Horizontal(id="compare-row"):
                for i, (label, fc, meta, _aq) in enumerate(self._bundles):
                    col_cls = "compare-column"
                    with Vertical(classes=col_cls):
                        yield Label(f"[b]{label}[/b]", classes="compare-heading")
                        yield CurrentWeather(
                            fc,
                            units=self._units,
                            id=f"cw-{i}",
                            classes="compare-current",
                        )
                        yield CityInfo(meta, id=f"ci-{i}", classes="compare-city")
                        yield AirQualityPanel(id=f"aq-{i}")
                        cells = format_day_cells(fc, units=self._units, emoji=True)
                        with Horizontal(classes="daily-row-compare"):
                            for cell in cells:
                                yield Static(cell, classes="day-cell")

    def on_mount(self) -> None:
        for i, (_label, _fc, _meta, aq) in enumerate(self._bundles):
            strip = self.query_one(f"#aq-{i}", AirQualityPanel)
            strip.set_payload(aq)
