"""Textual components for ThothSpinner."""

from __future__ import annotations

from .widgets import (
    HintWidget,
    MessageWidget,
    ProgressWidget,
    SpinnerWidget,
    ThothSpinnerWidget,
    TimerWidget,
)

# Public alias matching M12 deliverable
TextualThothSpinner = ThothSpinnerWidget

__all__ = [
    "HintWidget",
    "MessageWidget",
    "ProgressWidget",
    "SpinnerWidget",
    "TextualThothSpinner",
    "ThothSpinnerWidget",
    "TimerWidget",
]
