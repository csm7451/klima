"""Klima — terminal weather app. Entrypoint and CLI."""

from __future__ import annotations

import sys

from klima.app import KlimaApp


def main() -> None:
    """Run the app, optionally with an initial location from argv."""
    location = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else None
    app = KlimaApp(initial_location=location)
    app.run()


if __name__ == "__main__":
    main()
