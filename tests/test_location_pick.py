from __future__ import annotations

import asyncio
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Static

from klima.screens import LocationPickScreen


def test_pick_label_includes_country_code() -> None:
    screen = LocationPickScreen(
        [
            {
                "name": "London",
                "country": "United Kingdom",
                "admin1": "England",
                "country_code": "gb",
            },
        ],
    )
    text = screen._label(screen._candidates[0])
    assert "United Kingdom" in text
    assert "GB" in text


def test_pick_label_without_country_code() -> None:
    screen = LocationPickScreen(
        [{"name": "X", "country": "Y", "admin1": "Z"}],
    )
    assert screen._label(screen._candidates[0]) == "X (Z, Y)"


def test_enter_confirms_while_radio_set_focused() -> None:
    """Enter confirms the highlighted row (priority binding; index follows keyboard selection)."""
    hits = [
        {
            "name": "A",
            "country": "One",
            "admin1": "",
            "country_code": "O1",
            "latitude": 1.0,
            "longitude": 1.0,
            "timezone": "Etc/UTC",
        },
        {
            "name": "B",
            "country": "Two",
            "admin1": "",
            "country_code": "T2",
            "latitude": 2.0,
            "longitude": 2.0,
            "timezone": "Etc/UTC",
        },
    ]
    picked: list[object] = []

    class Host(App[None]):
        CSS_PATH = Path(__file__).resolve().parents[1] / "src" / "klima" / "klima.tcss"

        def compose(self) -> ComposeResult:
            yield Static("host")

        def on_mount(self) -> None:
            self.push_screen(LocationPickScreen(hits), callback=picked.append)

    async def run() -> None:
        async with Host().run_test() as pilot:
            await pilot.pause(0.15)
            await pilot.press("down")
            await pilot.pause(0.05)
            await pilot.press("enter")
            await pilot.pause(0.05)

    asyncio.run(run())
    assert picked == [hits[1]]
