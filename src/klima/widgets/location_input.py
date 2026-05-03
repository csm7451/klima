from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer, Vertical
from textual.message import Message
from textual.widgets import Button, Input, Label

from klima.history import load_history


class PickRecent(Message):
    """User chose a pinned recent location (bubble to app)."""

    def __init__(self, entry: dict[str, Any]) -> None:
        super().__init__()
        self.entry = entry


class LocationInputScreen(Container):
    """City name prompt plus recent-location shortcuts."""

    def compose(self) -> ComposeResult:
        hist = load_history()
        self._hist_list = hist[:18]
        yield Label("Enter a city or location:", id="prompt-label")
        yield Input(
            placeholder='e.g. Berlin, London, "Portland Maine"',
            id="location-input",
        )
        yield Label("(Enter to search)  •  Buttons below reuse saved picks", id="hint-label")
        if self._hist_list:
            yield Label("[dim]Recent[/]", id="recent-label")
            with ScrollableContainer(id="recent-scroll", classes="recent-scroll"):
                with Vertical(classes="recent-col"):
                    for i, row in enumerate(self._hist_list):
                        short = row.get("label", "?")
                        yield Button(
                            short,
                            variant="success",
                            classes="recent-button",
                            id=f"recent-{i}",
                        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        wid = getattr(event.control, "id", "") or ""
        if not isinstance(wid, str) or not wid.startswith("recent-"):
            return
        suffix = wid.removeprefix("recent-")
        try:
            idx = int(suffix)
        except ValueError:
            return
        if 0 <= idx < len(self._hist_list):
            self.post_message(PickRecent(dict(self._hist_list[idx])))
