from typing import Iterable

from textual.binding import Binding
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class KlimaApp(App):
    """A Textual app to provide weather updates."""
    TITLE = "Klima - Weather Forecasts"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    async def action_quit(self) -> None: # type: ignore[override]
        """Enter 'q' to quit the app."""
        self.exit()


if __name__ == "__main__":
    app = KlimaApp()
    app.run()
