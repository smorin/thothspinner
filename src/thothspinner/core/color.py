"""Shared color validation utilities for ThothSpinner widgets."""

from __future__ import annotations


def validate_hex_color(color: str) -> str:
    """Validate hex color format (#RRGGBB).

    Args:
        color: Color string to validate.

    Returns:
        The validated color string.

    Raises:
        ValueError: If color format is invalid.
    """
    if not isinstance(color, str):
        raise ValueError(f"Color must be a string, got {type(color)}")
    if not color.startswith("#"):
        raise ValueError(f"Color must start with #, got {color}")
    if len(color) != 7:
        raise ValueError(f"Color must be #RRGGBB format, got {color}")
    try:
        int(color[1:], 16)
    except ValueError as err:
        raise ValueError(f"Invalid hex color: {color}") from err
    return color
