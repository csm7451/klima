"""Regression: App key bindings must map to `action_<name>` methods."""

from __future__ import annotations

import asyncio

from klima.app import KlimaApp
from klima.config import CliConfig


def test_toggle_units_binding_runs_when_main_container_focused() -> None:
    """Key `u` must dispatch to `action_toggle_units` (binding action name: `toggle_units`)."""

    async def run() -> None:
        async with KlimaApp(locations_on_launch=[], cli=CliConfig()).run_test() as pilot:
            pilot.app.query_one("#main-container").focus()
            await pilot.pause(0.05)
            assert pilot.app._units == "metric"
            await pilot.press("u")
            await pilot.pause(0.05)
            assert pilot.app._units == "imperial"

    asyncio.run(run())
