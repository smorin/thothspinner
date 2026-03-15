"""State management for ThothSpinner components."""

from dataclasses import dataclass


@dataclass
class StateConfig:
    """Configuration for a component state."""

    animating: bool = True
    color: str | None = None
    text: str | None = None
    icon: str | None = None
    visible: bool = True
