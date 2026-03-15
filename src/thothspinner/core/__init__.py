"""Core utilities and state management for ThothSpinner."""

from __future__ import annotations

from .color import validate_hex_color
from .states import ComponentState

__all__ = ["ComponentState", "validate_hex_color"]
