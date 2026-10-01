"""Regression checks for the SVG snapshot extension's storage and comparison."""

from pathlib import Path

from .svg_snapshot import CompatibleSVGImageExtension


def test_svg_snapshot_lookup_and_id_normalization(tmp_path: Path):
    """Read an existing SVG and ignore only Rich's random terminal identifiers."""
    location = tmp_path / "existing.svg"
    location.write_text('<svg id="terminal-123-content">Loading</svg>')
    extension = CompatibleSVGImageExtension()

    stored = extension.read_snapshot_data_from_location(
        snapshot_location=str(location), snapshot_name="existing", session_id="test"
    )

    assert extension.file_extension == "svg"
    assert extension.is_snapshot_location(location=str(location))
    assert not extension.is_snapshot_location(location=str(tmp_path / "existing.raw"))
    assert stored == extension.serialize('<svg id="terminal-456-content">Loading</svg>')
    assert stored != extension.serialize('<svg id="terminal-456-content">Changed</svg>')


def test_missing_svg_snapshot_still_fails_lookup(tmp_path: Path):
    """An absent baseline must remain absent rather than accepting current output."""
    extension = CompatibleSVGImageExtension()
    assert (
        extension.read_snapshot_data_from_location(
            snapshot_location=str(tmp_path / "missing.svg"),
            snapshot_name="missing",
            session_id="test",
        )
        is None
    )
