"""Shared color validation utilities and constants for ThothSpinner widgets."""

from __future__ import annotations

# Standard state colors
COLOR_SUCCESS = "#00FF00"
COLOR_ERROR = "#FF0000"
COLOR_DEFAULT = "#D97706"

# Component-specific colors
COLOR_SHIMMER = "#FFA500"
COLOR_HINT = "#888888"
COLOR_TIMER = "#FFFF55"


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
        raise ValueError(f"Invalid hex color: expected string, got {type(color)}")
    if not color.startswith("#") or len(color) != 7:
        raise ValueError(f"Invalid hex color: {color}")
    try:
        int(color[1:], 16)
    except ValueError as err:
        raise ValueError(f"Invalid hex color: {color}") from err
    return color
