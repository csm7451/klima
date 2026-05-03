"""Klima TUI app: dashboards, overlays, threaded Open-Meteo fetches."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer, Vertical
from textual.widgets import Footer, Header, Input, LoadingIndicator, Static
from textual.worker import get_current_worker

from klima.api import get_air_quality, get_forecast, search_location
from klima.config import CliConfig, persist_live_settings, toggle_units
from klima.history import push_recent
from klima.screens import HelpScreen, HourlyScreen, LocationPickScreen
from klima.units_conv import UnitsKind
from klima.widgets import CompareDashboard, LocationInputScreen, WeatherDashboard
from klima.widgets.location_input import PickRecent

THEME_SEQUENCE = (
    "nord",
    "catppuccin-mocha",
    "gruvbox",
    "solarized-dark",
    "tokyo-night",
    "textual-dark",
    "rose-pine",
)


def _format_place_label(hit: dict[str, Any]) -> str:
    name = hit.get("name", "?")
    country = hit.get("country", "")
    cc = str(hit.get("country_code") or "").strip().upper()
    if country and cc:
        return f"{name}, {country} ({cc})"
    if country:
        return f"{name}, {country}"
    return str(name)


def _setup_logging(debug: bool, log_dir: Path) -> None:
    if not debug:
        return
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "klima.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        filename=log_file,
        encoding="utf-8",
        force=True,
    )
    logging.debug("Debug logging initialized at %s", log_file)


class KlimaApp(App[None]):
    """Terminal weather app using Open-Meteo."""

    TITLE = "Klima — Weather"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("n", "new_location", "Location"),
        # Action strings are the suffix after `action_` (not the full method name).
        Binding("?", "help", "Help"),
        Binding("r", "refresh", "Refresh"),
        Binding("u", "toggle_units", "Units"),
        Binding("h", "hourly", "Hourly"),
        Binding("t", "cycle_theme", "Theme"),
    ]

    CSS_PATH = Path(__file__).parent / "klima.tcss"

    def __init__(
        self,
        *,
        locations_on_launch: list[str],
        cli: CliConfig,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.theme = cli.theme
        self._launch_locs = [x.strip() for x in locations_on_launch if x.strip()]
        self._cli = cli
        cache_dir = Path.home() / ".cache" / "klima"
        _setup_logging(cli.debug, cache_dir)
        self._compare_mode = len(self._launch_locs) >= 2
        self._units: UnitsKind = cli.units
        self._refresh_minutes = cli.refresh_minutes
        self._config_save_path = cli.config_path
        self._forecast: dict[str, Any] | None = None
        self._air_quality: dict[str, Any] | None = None
        self._location_meta: dict[str, Any] = {}
        self._display_label = ""
        self._coords_known = False
        self._bundles_compare: (
            list[tuple[str, dict[str, Any], dict[str, Any], dict[str, Any] | None]] | None
        ) = None
        self._auto_refresh_timer: Any | None = None

    # ---------------------------------------------------------------- lifecycle
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        if self._launch_locs:
            yield ScrollableContainer(
                Vertical(LoadingIndicator(), id="loading-inner"),
                id="main-container",
                classes="main-splash",
            )
        else:
            yield ScrollableContainer(
                LocationInputScreen(id="input-screen"),
                id="main-container",
                classes="main-splash",
            )
        yield Footer()

    def on_mount(self) -> None:
        self._sync_auto_refresh()
        if len(self._launch_locs) == 1:
            q = self._launch_locs[0]
            self.run_worker(lambda: self._geo_thread(q), thread=True)
        elif self._compare_mode:
            qs = self._launch_locs[:3]
            self.run_worker(lambda: self._compare_thread(qs), thread=True)

    def _sync_auto_refresh(self) -> None:
        if self._auto_refresh_timer is not None:
            try:
                self._auto_refresh_timer.stop()
            except Exception:
                pass
            self._auto_refresh_timer = None
        secs = max(60, int(self._refresh_minutes) * 60)
        self._auto_refresh_timer = self.set_interval(secs, self._auto_refresh_tick)

    def _auto_refresh_tick(self) -> None:
        if not self._coords_known:
            return
        try:
            self._do_refresh(show_loading=False)
        except Exception:
            logging.exception("auto-refresh")

    # ---------------------------------------------------------------- mount helpers
    def _replace_main(self, widget: Any) -> None:
        """Swap `#main-container` content (`remove_children()` must be awaited in Textual)."""

        async def _swap() -> None:
            container = self.query_one("#main-container", ScrollableContainer)
            await container.remove_children()
            await container.mount(widget)
            # Center compact splash UIs; full dashboards stay top-aligned and scroll.
            wid = getattr(widget, "id", None)
            splash = isinstance(widget, LocationInputScreen) or wid in (
                "loading-inner",
                "error-box-wrap",
            )
            container.set_class(splash, "main-splash")

        self.run_worker(_swap, exclusive=True, thread=False, name="swap-main-pane")  # type: ignore[arg-type]

    def _show_loading_main(self) -> None:
        self._replace_main(Vertical(LoadingIndicator(), id="loading-inner"))

    # ---------------------------------------------------------------- geocode flow
    def _geo_thread(self, query: str) -> None:
        worker = get_current_worker()
        try:
            hits = search_location(query, count=5)
            if not hits:
                self.call_from_thread(
                    self._show_error,
                    f"No results for «{query}». Try another wording.",
                )
                return
            if worker and worker.is_cancelled:
                return
            self.call_from_thread(self._finish_geocode, hits)
        except Exception as e:
            if not (worker and worker.is_cancelled):
                self.call_from_thread(self._show_error, str(e))

    def _finish_geocode(self, hits: list[dict[str, Any]]) -> None:
        if len(hits) == 1:
            self._show_loading_main()
            self.run_worker(lambda: self._forecast_thread_for_pick(dict(hits[0])), thread=True)
            return
        self.push_screen(LocationPickScreen(hits), callback=self._after_pick)

    def _after_pick(self, picked: dict[str, Any] | None) -> None:
        if picked is None:
            self._restore_input_clean()
            return
        self._show_loading_main()
        self.run_worker(lambda: self._forecast_thread_for_pick(dict(picked)), thread=True)

    def _forecast_thread_for_pick(self, place: dict[str, Any]) -> None:
        worker = get_current_worker()
        try:
            lat = float(place["latitude"])
            lon = float(place["longitude"])
            tz = str(place.get("timezone", "auto"))
            fc = get_forecast(lat, lon, timezone=tz)
            aq = get_air_quality(lat, lon, timezone=tz)
            label = _format_place_label(place)
            if worker and worker.is_cancelled:
                return
            self.call_from_thread(self._finalize_single, fc, aq, dict(place), label)
        except Exception as e:
            if not (worker and worker.is_cancelled):
                self.call_from_thread(self._show_error, str(e))

    def _finalize_single(
        self,
        fc: dict[str, Any],
        aq: dict[str, Any] | None,
        meta: dict[str, Any],
        label: str,
    ) -> None:
        self._forecast = fc
        self._air_quality = aq
        self._location_meta = meta
        self._display_label = label
        self._coords_known = True
        self._compare_mode = False
        self._bundles_compare = None
        push_recent(meta, label)
        self._replace_main(
            WeatherDashboard(
                label,
                fc,
                location_info=meta,
                units=self._units,
                air_quality=aq,
                show_emoji=True,
            ),
        )

    # ---------------------------------------------------------------- compare flow
    def _compare_thread(self, queries: list[str]) -> None:
        worker = get_current_worker()
        bundles: list[tuple[str, dict[str, Any], dict[str, Any], dict[str, Any] | None]] = []
        try:
            for raw_q in queries:
                hits = search_location(raw_q.strip(), count=1)
                if not hits:
                    raise RuntimeError(f"No geocode match for «{raw_q}».")
                meta = dict(hits[0])
                lat = float(meta["latitude"])
                lon = float(meta["longitude"])
                tz = str(meta.get("timezone", "auto"))
                fc = get_forecast(lat, lon, timezone=tz)
                aq = get_air_quality(lat, lon, timezone=tz)
                label = _format_place_label(meta)
                push_recent(meta, label)
                bundles.append((label, fc, meta, aq))
            if worker and worker.is_cancelled:
                return
            self.call_from_thread(self._finalize_compare, bundles)
        except Exception as e:
            if not (worker and worker.is_cancelled):
                self.call_from_thread(self._show_error, str(e))

    def _finalize_compare(
        self,
        bundles: list[tuple[str, dict[str, Any], dict[str, Any], dict[str, Any] | None]],
    ) -> None:
        self._bundles_compare = bundles
        self._coords_known = True
        self._compare_mode = True
        self._forecast = None
        self._air_quality = None
        self._location_meta = {}
        self._display_label = ""
        self._replace_main(
            CompareDashboard(units=self._units, bundles=bundles),
        )

    # ---------------------------------------------------------------- refresh
    def _forecast_from_coords_thread(self, meta: dict[str, Any]) -> None:
        worker = get_current_worker()
        try:
            lat = float(meta["latitude"])
            lon = float(meta["longitude"])
            tz = str(meta.get("timezone", "auto"))
            fc = get_forecast(lat, lon, timezone=tz)
            aq = get_air_quality(lat, lon, timezone=tz)
            label = _format_place_label(meta)
            if worker and worker.is_cancelled:
                return
            self.call_from_thread(self._apply_single_refresh, fc, aq, meta, label)
        except Exception as e:
            if not (worker and worker.is_cancelled):
                self.call_from_thread(self._show_error, str(e))

    def _apply_single_refresh(
        self,
        fc: dict[str, Any],
        aq: dict[str, Any] | None,
        meta: dict[str, Any],
        label: str,
    ) -> None:
        self._forecast = fc
        self._air_quality = aq
        self._location_meta = meta
        self._display_label = label
        self._replace_main(
            WeatherDashboard(
                label,
                fc,
                location_info=meta,
                units=self._units,
                air_quality=aq,
                show_emoji=True,
            ),
        )

    def _compare_reload_worker(self) -> None:
        worker = get_current_worker()
        if not self._bundles_compare:
            return
        new_bundles: list[tuple[str, dict[str, Any], dict[str, Any], dict[str, Any] | None]] = []
        try:
            for _, _fc_old, meta_old, __ in self._bundles_compare:
                lat = float(meta_old["latitude"])
                lon = float(meta_old["longitude"])
                tz = str(meta_old.get("timezone", "auto"))
                fc = get_forecast(lat, lon, timezone=tz)
                aq = get_air_quality(lat, lon, timezone=tz)
                label = _format_place_label(meta_old)
                new_bundles.append((label, fc, meta_old, aq))
            if worker and worker.is_cancelled:
                return
            self.call_from_thread(self._finalize_compare, new_bundles)
        except Exception as e:
            if not (worker and worker.is_cancelled):
                self.call_from_thread(self._show_error, str(e))

    def _do_refresh(self, *, show_loading: bool) -> None:
        if self._compare_mode and self._bundles_compare:
            if show_loading:
                self._show_loading_main()
            self.run_worker(lambda: self._compare_reload_worker(), thread=True)
            return
        if not self._location_meta:
            return
        if show_loading:
            self._show_loading_main()
        self.run_worker(
            lambda: self._forecast_from_coords_thread(dict(self._location_meta)),
            thread=True,
        )

    def action_refresh(self) -> None:
        if not self._coords_known:
            self.notify("Nothing to refresh yet.")
            return
        self._do_refresh(show_loading=True)

    # ---------------------------------------------------------------- actions
    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_toggle_units(self) -> None:
        self._units = toggle_units(self._units)
        self._persist_prefs()
        self.notify(f"Units: {self._units}")
        if self._bundles_compare and self._compare_mode:
            self._finalize_compare(list(self._bundles_compare))
            return
        if self._forecast is not None and self._coords_known:
            label = self._display_label or _format_place_label(self._location_meta)
            self._replace_main(
                WeatherDashboard(
                    label,
                    self._forecast,
                    location_info=dict(self._location_meta),
                    units=self._units,
                    air_quality=self._air_quality,
                    show_emoji=True,
                ),
            )

    def action_hourly(self) -> None:
        if self._compare_mode:
            if not self._bundles_compare:
                return
            self.push_screen(
                HourlyScreen(self._bundles_compare[0][1], units=self._units),
            )
            return
        if self._forecast is None:
            self.notify("Open a forecast first.")
            return
        self.push_screen(HourlyScreen(self._forecast, units=self._units))

    def action_cycle_theme(self) -> None:
        avail = sorted(self.available_themes)
        seq = [t for t in THEME_SEQUENCE if t in avail] or avail
        if not seq:
            return
        try:
            cur = str(self.theme)
            ix = seq.index(cur)
        except ValueError:
            ix = -1
        new_theme = seq[(ix + 1) % len(seq)]
        self.theme = new_theme
        self._persist_prefs()
        self.notify(f"Theme: {new_theme}")

    def action_new_location(self) -> None:
        self._restore_input_clean()

    def _persist_prefs(self) -> None:
        try:
            persist_live_settings(
                self._config_save_path,
                theme=str(self.theme),
                units=self._units,
                refresh_minutes=self._refresh_minutes,
            )
        except OSError as exc:
            self.notify(f"Could not save config: {exc}", severity="warning")

    # ---------------------------------------------------------------- misc UI
    def _show_error(self, message: str) -> None:
        self._replace_main(
            Vertical(
                Static(f"[bold red]Error[/]\n\n{message}", markup=True, id="error-text"),
                id="error-box-wrap",
                classes="center-pad",
            ),
        )

    def _restore_input_clean(self) -> None:
        self._coords_known = False
        self._forecast = None
        self._bundles_compare = None
        self._compare_mode = False
        self._location_meta = {}
        self._display_label = ""
        self._air_quality = None
        self._replace_main(LocationInputScreen(id="input-screen"))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "location-input":
            return
        value = (event.input.value or "").strip()
        if not value:
            return
        event.input.value = ""
        self._compare_mode = False
        self._bundles_compare = None
        self._show_loading_main()
        self.run_worker(lambda: self._geo_thread(value), thread=True)

    @on(PickRecent)
    def recent_from_history(self, event: PickRecent) -> None:
        meta_flat = dict(event.entry)
        lat = meta_flat.get("latitude")
        lon = meta_flat.get("longitude")
        tz = meta_flat.get("timezone", "auto")
        if lat is None or lon is None:
            self.notify("That entry lacks coordinates.")
            return
        self._compare_mode = False
        self._bundles_compare = None
        hit = {
            "name": meta_flat.get("name", "?"),
            "country": meta_flat.get("country", "") or "",
            "admin1": meta_flat.get("admin1", "") or "",
            "latitude": float(lat),
            "longitude": float(lon),
            "timezone": str(tz),
        }
        self._show_loading_main()
        self.run_worker(lambda: self._forecast_thread_for_pick(hit), thread=True)
