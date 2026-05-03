from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from klima.widgets.location_input import LocationInputScreen


class _LocationSnapshotApp(App[None]):
    TITLE = "klima-snap"
    CSS_PATH = Path(__file__).resolve().parents[1] / "src" / "klima" / "klima.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield LocationInputScreen()
        yield Footer()


def test_location_input_svg(snap_compare) -> None:
    assert snap_compare(_LocationSnapshotApp(), terminal_size=(88, 28))
