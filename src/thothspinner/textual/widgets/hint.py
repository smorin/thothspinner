"""Textual Hint Widget for displaying helper text in Textual apps."""

from __future__ import annotations

from typing import ClassVar

from rich.text import Text
from textual.reactive import reactive
from textual.widgets import Static

from ...core.color import validate_hex_color
from ...core.states import ComponentState


class HintWidget(Static):
    """A hint widget for displaying helper text in Textual apps."""

    DEFAULT_CSS: ClassVar[str] = """
    HintWidget {
        width: auto;
        height: 1;
        padding: 0;
        background: transparent;
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
    _state = reactive(ComponentState.IN_PROGRESS)

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
        self.color = validate_hex_color(color)
        self.icon = icon
        if not visible:
            self.display = False

    @property
    def state(self) -> ComponentState:
        """Read-only access to the current component state."""
        return self._state

    def render(self) -> Text:
        """Render the hint text.

        Note: Visibility is handled by the display property.
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
        return validate_hex_color(color)

    def watch_text(self) -> None:
        """React to text changes."""
        self.refresh()

    def watch_color(self) -> None:
        """React to color changes."""
        self.refresh()

    def watch_icon(self) -> None:
        """React to icon changes."""
        self.refresh()

    def watch__state(self, new_state: ComponentState) -> None:
        """React to state changes."""
        if new_state == ComponentState.IN_PROGRESS:
            self.remove_class("success", "error")
        elif new_state == ComponentState.SUCCESS:
            self.remove_class("error")
            self.add_class("success")
        elif new_state == ComponentState.ERROR:
            self.remove_class("success")
            self.add_class("error")
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
        """Show the hint widget."""
        self.display = True

    def hide(self) -> None:
        """Hide the hint widget."""
        self.display = False

    def toggle(self) -> None:
        """Toggle visibility state."""
        self.display = not self.display

    def set_visible(self, visible: bool) -> None:
        """Set visibility.

        Args:
            visible: Whether the widget should be visible
        """
        self.display = visible

    def success(self, text: str | None = None) -> None:
        """Transition to success state.

        Args:
            text: Optional custom success text.
        """
        if not self._state.can_transition_to(ComponentState.SUCCESS):
            return
        if text is not None:
            self.text = text
        self._state = ComponentState.SUCCESS
        self.display = False

    def error(self, text: str | None = None) -> None:
        """Transition to error state.

        Args:
            text: Optional custom error text.
        """
        if not self._state.can_transition_to(ComponentState.ERROR):
            return
        if text is not None:
            self.text = text
        self._state = ComponentState.ERROR
        self.display = False

    def reset(self) -> None:
        """Reset to in_progress state and show the widget."""
        self.display = True
        self._state = ComponentState.IN_PROGRESS

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

    def configure(self, **kwargs) -> None:
        """Batch update properties.

        Args:
            **kwargs: Properties to update (text, color, icon, etc.)
        """
        for key, value in kwargs.items():
            if key == "color":
                value = validate_hex_color(value)
            if hasattr(self, key):
                setattr(self, key, value)

    def fade_in(self, duration: float = 0.3) -> None:
        """Animate widget appearance using Textual's style animation.

        Args:
            duration: Animation duration in seconds
        """
        self.display = True
        self.styles.opacity = 0
        self.styles.animate("opacity", value=1.0, duration=duration)

    def fade_out(self, duration: float = 0.3) -> None:
        """Animate widget disappearance using Textual's style animation.

        Args:
            duration: Animation duration in seconds
        """

        def hide_after_fade() -> None:
            self.display = False

        self.styles.animate("opacity", value=0.0, duration=duration, on_complete=hide_after_fade)

    def animate_color_change(self, new_color: str, duration: float = 0.5) -> None:
        """Animate color transition.

        Args:
            new_color: Target hex color
            duration: Animation duration in seconds
        """
        self.color = validate_hex_color(new_color)
        # Color animation handled by CSS transitions
