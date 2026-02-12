from textual.containers import Container
from textual.widgets import Input, Label

from textual.app import ComposeResult


class LocationInputScreen(Container):
    """Screen to enter city name when not provided via CLI."""

    def compose(self) -> ComposeResult:
        yield Label("Enter a city or location:", id="prompt-label")
        yield Input(
            placeholder="e.g. Berlin, London, New York",
            id="location-input",
        )
        yield Label("(Press Enter to search)", id="hint-label")
