"""Keep Textual's SVG snapshot format compatible with Syrupy 6."""

from pytest_textual_snapshot import SVGImageExtension, normalize_svg


class CompatibleSVGImageExtension(SVGImageExtension):
    """Expose the public Syrupy 6 API while retaining the older plugin API."""

    file_extension = "svg"

    def read_snapshot_data_from_location(
        self, *, snapshot_location: str, snapshot_name: str, session_id: str
    ) -> str | None:
        """Normalize stored SVG IDs exactly as the plugin normalizes actual SVGs."""
        read_data = getattr(
            super(), "read_snapshot_data_from_location", self._read_snapshot_data_from_location
        )
        data = read_data(
            snapshot_location=snapshot_location,
            snapshot_name=snapshot_name,
            session_id=session_id,
        )
        return normalize_svg(data) if data is not None else None
