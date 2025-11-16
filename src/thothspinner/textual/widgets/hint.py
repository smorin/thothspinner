"""Textual Hint Widget for displaying helper text in Textual apps."""

from __future__ import annotations

from typing import ClassVar

from rich.text import Text
from textual.reactive import reactive
from textual.widgets import Static


class HintWidget(Static):
    """A hint widget for displaying helper text in Textual apps."""

    DEFAULT_CSS: ClassVar[str] = """
    HintWidget {
        width: auto;
        height: 1;
        padding: 0;
        background: transparent;
    }

    HintWidget.hidden {
        display: none;
    }

    HintWidget.error {
        color: $error;
    }

    HintWidget.warning {
        color: $warning;
    }

    HintWidget.success {
        color: $success;
    }
    """

    # Reactive properties
    text = reactive("")
    color = reactive("#888888")
    icon = reactive("")

    def __init__(
        self,
        text: str = "",
        *,
        color: str = "#888888",
        visible: bool = True,
        icon: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the HintWidget.

        Args:
            text: The text to display
            color: Hex color code for the text (#RRGGBB format)
            visible: Whether the widget is initially visible
            icon: Optional icon/emoji to display before the text
            name: Optional name for the widget
            id: Optional ID for the widget
            classes: Optional CSS classes
        """
        super().__init__(
            "",  # Empty initial content for Static
            name=name,
            id=id,
            classes=classes,
        )
        self.text = text
        self.color = self._validate_hex_color(color)
        self.icon = icon
        if not visible:
            self.add_class("hidden")

    @staticmethod
    def _validate_hex_color(color: str) -> str:
        """Validate hex color format (#RRGGBB).

        Args:
            color: Color string to validate

        Returns:
            The validated color string

        Raises:
            ValueError: If color format is invalid
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

    def render(self) -> Text:
        """Render the hint text.

        Note: Visibility is handled by CSS classes, not in render.
        """
        content = self._build_content()
        return Text(content, style=self.color)

    def _build_content(self) -> str:
        """Build the content string with optional icon."""
        if self.icon and self.text:
            return f"{self.icon} {self.text}"
        return self.text or self.icon or ""

    def validate_color(self, color: str) -> str:
        """Validate color before setting."""
        return self._validate_hex_color(color)

    def watch_text(self) -> None:
        """React to text changes."""
        self.refresh()

    def watch_color(self) -> None:
        """React to color changes."""
        self.refresh()

    def watch_icon(self) -> None:
        """React to icon changes."""
        self.refresh()

    def set_icon(self, icon: str) -> None:
        """Set an optional icon/symbol prefix.

        Args:
            icon: Unicode icon/emoji to display
        """
        self.icon = icon

    def clear_icon(self) -> None:
        """Remove the icon."""
        self.icon = ""

    def show(self) -> None:
        """Show the hint widget using CSS classes."""
        self.remove_class("hidden")

    def hide(self) -> None:
        """Hide the hint widget using CSS classes."""
        self.add_class("hidden")

    def toggle(self) -> None:
        """Toggle visibility state using CSS classes."""
        self.toggle_class("hidden")

    def set_visible(self, visible: bool) -> None:
        """Set visibility using Textual's set_class method.

        Args:
            visible: Whether the widget should be visible
        """
        self.set_class(not visible, "hidden")

    @classmethod
    def from_config(cls, config: dict) -> HintWidget:
        """Create from configuration dictionary.

        Args:
            config: Configuration dictionary with optional keys:
                - text: Text to display
                - color: Hex color code
                - visible: Whether visible
                - icon: Optional icon

        Returns:
            A new HintWidget instance
        """
        return cls(
            text=config.get("text", ""),
            color=config.get("color", "#888888"),
            visible=config.get("visible", True),
            icon=config.get("icon", ""),
        )

    def update(self, **kwargs) -> None:
        """Batch update properties.

        Args:
            **kwargs: Properties to update (text, color, icon, etc.)
        """
        for key, value in kwargs.items():
            if key == "color":
                value = self._validate_hex_color(value)
            if hasattr(self, key):
                setattr(self, key, value)

    def fade_in(self, duration: float = 0.3) -> None:
        """Animate widget appearance using Textual's style animation.

        Args:
            duration: Animation duration in seconds
        """
        self.remove_class("hidden")
        self.styles.opacity = 0
        self.styles.animate("opacity", value=1.0, duration=duration)

    def fade_out(self, duration: float = 0.3) -> None:
        """Animate widget disappearance using Textual's style animation.

        Args:
            duration: Animation duration in seconds
        """

        def hide_after_fade() -> None:
            self.add_class("hidden")

        self.styles.animate("opacity", value=0.0, duration=duration, on_complete=hide_after_fade)

    def animate_color_change(self, new_color: str, duration: float = 0.5) -> None:
        """Animate color transition.

        Args:
            new_color: Target hex color
            duration: Animation duration in seconds
        """
        self.color = self._validate_hex_color(new_color)
        # Color animation handled by CSS transitions
