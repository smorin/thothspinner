"""State management for ThothSpinner components."""

from dataclasses import dataclass
from enum import Enum


class ComponentState(Enum):
    """Component state enumeration."""

    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"


@dataclass
class StateConfig:
    """Configuration for a component state."""

    animating: bool = True
    color: str | None = None
    text: str | None = None
    icon: str | None = None
    visible: bool = True
