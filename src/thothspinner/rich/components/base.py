"""Base component classes for ThothSpinner Rich components."""

from abc import ABC, abstractmethod

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.style import Style
from rich.text import Text


class BaseComponent(ABC):
    """Base class for all ThothSpinner components."""

    def __init__(self, color: str | None = None):
        self.color = color
        self._style: Style | None = None
        if color:
            self._validate_hex_color(color)
            self._style = Style(color=color)

    @staticmethod
    def _validate_hex_color(color: str) -> None:
        """Validate hex color format #RRGGBB."""
        if not color.startswith("#") or len(color) != 7:
            raise ValueError(f"Invalid hex color: {color}")
        try:
            int(color[1:], 16)
        except ValueError as err:
            raise ValueError(f"Invalid hex color: {color}") from err

    @abstractmethod
    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Render the component."""
        pass

    def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement:
        """Measure the component width."""
        return Measurement(1, options.max_width)

    def __rich__(self) -> Text:
        """Rich protocol support for direct printing."""
        # Default implementation for simple text rendering
        return Text("")
