"""Package version is defined and semver-shaped for releases."""

from __future__ import annotations

import re

from klima import __version__


def test_version_is_semver_release() -> None:
    assert re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", __version__), __version__
