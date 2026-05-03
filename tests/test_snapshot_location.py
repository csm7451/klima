from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from klima.widgets.location_input import LocationInputScreen

# Stable data for SVG snapshots: real history path varies by machine and CI has none.
_SNAPSHOT_HISTORY: list[dict[str, Any]] = [
    {
        "label": "Berlin, Germany (DE)",
        "latitude": 52.52,
        "longitude": 13.405,
        "timezone": "Europe/Berlin",
        "name": "Berlin",
        "country": "Germany",
        "admin1": "State of Berlin",
    },
    {
        "label": "De, Burkina Faso (BF)",
        "latitude": 11.8,
        "longitude": -1.75,
        "timezone": "Africa/Ouagadougou",
        "name": "De",
        "country": "Burkina Faso",
        "admin1": "Centre-Ouest",
    },
    {
        "label": "London, United Kingdom (GB)",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "timezone": "Europe/London",
        "name": "London",
        "country": "United Kingdom",
        "admin1": "England",
    },
]


class _LocationSnapshotApp(App[None]):
    TITLE = "klima-snap"
    CSS_PATH = Path(__file__).resolve().parents[1] / "src" / "klima" / "klima.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield LocationInputScreen()
        yield Footer()


@pytest.fixture
def _snapshot_location_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Match CI / default snapshot: no NO_COLOR (avoids nocolor pseudo-class SVG drift)."""
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setattr(
        "klima.widgets.location_input.load_history",
        lambda: [dict(row) for row in _SNAPSHOT_HISTORY],
    )


def test_location_input_svg(snap_compare, _snapshot_location_env: None) -> None:
    assert snap_compare(_LocationSnapshotApp(), terminal_size=(88, 28))
