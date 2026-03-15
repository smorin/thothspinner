"""Hint component for Rich console output.

Implements minimal hex color validation and Rich rendering.
Based on Rich patterns for deterministic testing and performance.
"""

from __future__ import annotations

from typing import Any

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.style import Style
from rich.text import Text

from ...core.color import COLOR_HINT, validate_hex_color

# Hint component defaults
DEFAULT_HINT_TEXT = "(esc to interrupt)"


class HintComponent:
    """Static hint text component for Rich console.

    A simple component that displays helper text with customizable
    color and visibility. Typically used to show keyboard shortcuts
    or status information.

    Attributes:
        text: The hint text to display
        color: Hex color code for the text (e.g., "#888888")
        visible: Whether the component should be rendered

    Example:
        >>> from rich.console import Console
        >>> console = Console()
        >>> hint = HintComponent("Press ESC to cancel", color="#FF5555")
        >>> console.print(hint)
    """

    def __init__(
        self,
        text: str = DEFAULT_HINT_TEXT,
        color: str = COLOR_HINT,
        visible: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize the HintComponent.

        Args:
            text: The hint text to display. Defaults to "(esc to interrupt)".
            color: Hex color code for the text. Defaults to "#888888" (gray).
                   Must be valid #RRGGBB format or ValueError is raised.
            visible: Whether the component should be rendered. Defaults to True.
            **kwargs: Additional keyword arguments (reserved for future use).

        Raises:
            ValueError: If color is not valid #RRGGBB format
        """
        self._text = text
        self._visible = bool(visible)
        # Validate color
        validate_hex_color(color)
        self._color = color
        # Cache for performance optimization (based on Rich patterns)
        self._cached_renderable: Text | None = None
        self._last_text: str | None = None
        self._last_color: str | None = None

    @property
    def text(self) -> str:
        """Get the hint text."""
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        """Set the hint text."""
        self._text = value
        self._cached_renderable = None  # Invalidate cache

    @property
    def color(self) -> str:
        """Get the color hex code."""
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        """Set the color hex code."""
        validate_hex_color(value)
        self._color = value
        self._cached_renderable = None  # Invalidate cache

    @property
    def visible(self) -> bool:
        """Get the visibility state."""
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        """Set the visibility state."""
        self._visible = bool(value)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> HintComponent:
        """Create a HintComponent from a configuration dictionary.

        Args:
            config: Configuration dictionary with keys:
                - text (str): The hint text
                - color (str): Hex color code
                - visible (bool): Visibility state

        Returns:
            A new HintComponent instance configured from the dictionary.

        Example:
            >>> config = {"text": "Loading...", "color": "#00FF00", "visible": True}
            >>> hint = HintComponent.from_config(config)
        """
        return cls(
            text=config.get("text", DEFAULT_HINT_TEXT),
            color=config.get("color", COLOR_HINT),
            visible=config.get("visible", True),
        )

    def configure(
        self,
        text: str | None = None,
        color: str | None = None,
        visible: bool | None = None,
    ) -> None:
        """Configure component properties.

        Args:
            text: New text to display
            color: New color hex code
            visible: New visibility state
        """
        if text is not None:
            self.text = text
        if color is not None:
            self.color = color
        if visible is not None:
            self.visible = visible

    # Backward-compatible alias
    update = configure

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Render the hint component for Rich console.

        This method is called by Rich when rendering the component.
        Uses caching for performance optimization.

        Args:
            console: The Rich console instance
            options: Console rendering options

        Yields:
            Rich Text object with styled hint text if visible
        """
        if self._visible:
            # Performance optimization: cache rendered text if unchanged
            if self._last_text == self._text and self._last_color == self._color:
                if self._cached_renderable is not None:
                    yield self._cached_renderable
                    return

            style = Style(color=self._color)
            rendered = Text(self._text, style=style)
            # Update cache
            self._cached_renderable = rendered
            self._last_text = self._text
            self._last_color = self._color
            yield rendered

    def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement:
        """Measure the hint text width.

        Based on Rich patterns for proper layout support.

        Args:
            console: The Rich console instance
            options: Console rendering options

        Returns:
            Measurement of the component's width
        """
        if not self._visible:
            return Measurement(0, 0)
        text = Text(self._text)
        return Measurement.get(console, options, text)

    def __repr__(self) -> str:
        """Return string representation of the component."""
        return f"HintComponent(text={self._text!r}, color={self._color!r}, visible={self._visible})"
