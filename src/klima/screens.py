"""Modal overlays: help, geocoding disambiguation, hourly table."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, RadioButton, RadioSet, RichLog, Static

from klima.formatting import hourly_table_rows
from klima.units_conv import UnitsKind

HELP_MARKDOWN = """
# Klima — keys

| Key | Action |
|-----|--------|
| **q** | Quit |
| **?** | Close this help overlay |
| **n** | New location search |
| **r** | Refresh (same coordinates) |
| **u** | Toggle °C ↔ °F and related units |
| **t** | Cycle Textual themes (saved to config when possible) |
| **h** | Hourly forecast — next ~48 steps |

↑/↓ on the location row moves through recent picks (when visible).
"""


class HelpScreen(ModalScreen[None]):
    BINDINGS = [
        Binding("escape", "dismiss_help", "Close"),
        Binding("?", "dismiss_help", "Close"),
    ]

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }
    #help-box {
        width: 76;
        max-width: 90%;
        height: auto;
        max-height: 90%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="help-box"):
            yield Static(HELP_MARKDOWN.strip(), markup=True)
            yield Static("\n[yellow]Esc or ? to close[/]")

    def action_dismiss_help(self) -> None:
        self.dismiss()


class LocationPickScreen(ModalScreen[dict[str, Any] | None]):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        # Priority: focused RadioSet also binds Enter; non-priority never reaches this screen.
        Binding("enter", "confirm", "Select", priority=True),
    ]

    DEFAULT_CSS = """
    LocationPickScreen {
        align: center middle;
    }
    #pick-shell {
        width: 76;
        max-width: 95%;
        height: auto;
        border: heavy $accent;
        background: $surface;
        padding: 1 2;
    }
    LocationPickScreen RadioSet {
        margin-top: 1;
        height: auto;
    }
    #pick-buttons {
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, candidates: list[dict[str, Any]]) -> None:
        super().__init__()
        self._candidates = candidates

    def _label(self, h: dict[str, Any]) -> str:
        name = str(h.get("name", "?"))
        cty = str(h.get("country") or "")
        a1 = str(h.get("admin1") or "")
        cc = str(h.get("country_code") or "").strip().upper()
        tail = ", ".join(p for p in (a1, cty) if p)
        if tail and cc:
            return f"{name} ({tail}) · {cc}"
        if tail:
            return f"{name} ({tail})"
        return name

    def _selected_row_index(self) -> int:
        """Map UI row → `_candidates` index (keyboard highlight vs checked state can differ)."""
        rs = self.query_one("#pick-radio", RadioSet)
        buttons = list(rs.query(RadioButton))
        if self.focused is rs:
            ks = getattr(rs, "_selected", None)
            if isinstance(ks, int) and 0 <= ks < len(self._candidates):
                return ks
        for i, btn in enumerate(buttons):
            if btn.value:
                return i
        pb = rs.pressed_button
        if pb is not None:
            try:
                return buttons.index(pb)
            except ValueError:
                pass
        idx = rs.pressed_index
        if isinstance(idx, int) and 0 <= idx < len(self._candidates):
            return idx
        return 0

    def compose(self) -> ComposeResult:
        rs_labels = tuple(self._label(h) for h in self._candidates)
        with Vertical(id="pick-shell"):
            yield Static("[b]Several matches[/] — choose with ↑↓ then Enter:")
            yield RadioSet(*rs_labels, id="pick-radio")
            with Horizontal(id="pick-buttons"):
                yield Button("Select", variant="success", id="btn-ok")
                yield Button("Cancel", variant="error", id="btn-cancel")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-ok":
            self.action_confirm()
        elif event.button.id == "btn-cancel":
            self.action_cancel()

    def action_confirm(self) -> None:
        focused = self.focused
        if focused is not None and focused.id == "btn-cancel":
            self.action_cancel()
            return
        idx = self._selected_row_index()
        idx = max(0, min(idx, len(self._candidates) - 1))
        self.dismiss(self._candidates[idx])

    def action_cancel(self) -> None:
        self.dismiss(None)


class HourlyScreen(ModalScreen[None]):
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("h", "close", "Close"),
    ]

    DEFAULT_CSS = """
    HourlyScreen {
        align: center middle;
    }
    #hour-shell {
        width: 92;
        max-width: 98%;
        height: 85%;
        border: heavy $accent;
        background: $surface;
    }
    #hour-log {
        width: 100%;
        height: 100%;
        margin: 0 1;
    }
    """

    def __init__(self, forecast: dict[str, Any], *, units: UnitsKind) -> None:
        super().__init__()
        self._forecast = forecast
        self._units = units

    def compose(self) -> ComposeResult:
        with Vertical(id="hour-shell"):
            yield Static("[b]Hourly forecast[/] — [yellow]Esc[/] or [yellow]h[/] to close\n")
            yield RichLog(id="hour-log", highlight=False, markup=True)

    def on_mount(self) -> None:
        log = self.query_one("#hour-log", RichLog)
        log.write("[b]Time[/]        │ [b]Temp[/] │ [b]Rain %[/] │ Summary")
        for row in hourly_table_rows(self._forecast, units=self._units):
            t, temp, prob, summ = row
            log.write(f"[dim]{t:14}[/] │ {temp:>7} │ {prob:>6} │ {summ}")

    def action_close(self) -> None:
        self.dismiss()
