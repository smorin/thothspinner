"""Base component classes for ThothSpinner Rich components."""

from abc import ABC, abstractmethod

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.style import Style
from rich.text import Text

from ...core.color import validate_hex_color


class BaseComponent(ABC):
    """Base class for all ThothSpinner components."""

    def __init__(self, color: str | None = None):
        """Initialize the base component.

        Args:
            color: Optional hex color code (e.g., "#FF0000").
                   Must be valid #RRGGBB format or ValueError is raised.
        """
        self.color = color
        self._style: Style | None = None
        if color:
            validate_hex_color(color)
            self._style = Style(color=color)

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
