"""Compatibility fixtures for Textual SVG snapshot consumers."""

import pytest
import pytest_textual_snapshot

from .svg_snapshot import CompatibleSVGImageExtension


@pytest.fixture(autouse=True)
def svg_snapshot_compatibility(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    """Adapt only tests that use the Textual plugin's snap_compare fixture."""
    if "snap_compare" in request.fixturenames:
        monkeypatch.setattr(
            pytest_textual_snapshot, "SVGImageExtension", CompatibleSVGImageExtension
        )
