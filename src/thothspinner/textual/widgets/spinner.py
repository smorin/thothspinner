"""Textual Spinner Widget for animated spinners in Textual apps."""

from __future__ import annotations

from typing import Any, ClassVar

from rich.text import Text
from textual.reactive import reactive
from textual.timer import Timer
from textual.widgets import Static

from ...core.states import ComponentState
from ...rich.spinners.frames import SPINNER_FRAMES, validate_frames


class SpinnerWidget(Static):
    """An animated spinner widget for Textual apps.

    Displays an animated spinner that cycles through frames to indicate
    activity. Supports multiple built-in styles, state transitions,
    and customizable colors.

    Example:
        >>> from thothspinner.textual.widgets import SpinnerWidget
        >>> spinner = SpinnerWidget(style="npm_dots", color="#D97706")
    """

    DEFAULT_CSS: ClassVar[str] = """
    SpinnerWidget {
        width: auto;
        height: 1;
        padding: 0;
        background: transparent;
    }

    SpinnerWidget.hidden {
        display: none;
    }

    SpinnerWidget.success {
        color: $success;
    }

    SpinnerWidget.error {
        color: $error;
    }
    """

    # Reactive properties
    color = reactive("#D97706")
    _frame_index = reactive(0)
    _state = reactive(ComponentState.IN_PROGRESS)

    def __init__(
        self,
        style: str = "npm_dots",
        *,
        frames: list[str] | None = None,
        interval: float | None = None,
        color: str = "#D97706",
        success_icon: str = "✓",
        error_icon: str = "✗",
        speed: float = 1.0,
        visible: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the SpinnerWidget.

        Args:
            style: Built-in spinner style name. Defaults to "npm_dots".
            frames: Custom frame sequence. Overrides style if provided.
            interval: Custom interval in seconds. Overrides style default.
            color: Hex color code for the spinner (#RRGGBB format).
            success_icon: Icon to display in success state.
            error_icon: Icon to display in error state.
            speed: Animation speed multiplier. Defaults to 1.0.
            visible: Whether the widget is initially visible.
            name: Optional name for the widget.
            id: Optional ID for the widget.
            classes: Optional CSS classes.
        """
        super().__init__(
            "",
            name=name,
            id=id,
            classes=classes,
        )

        if frames is not None:
            if not validate_frames(frames):
                raise ValueError("frames must be a non-empty list of non-empty strings")
            self._frames = list(frames)
            self._interval = interval if interval is not None else 0.08
        else:
            spinner_def = SPINNER_FRAMES.get(style, SPINNER_FRAMES["npm_dots"])
            self._frames = spinner_def["frames"]
            self._interval = spinner_def["interval"]

        self._style_name = style
        self.color = self._validate_hex_color(color)
        self._success_icon = success_icon
        self._error_icon = error_icon
        self._speed = speed
        self._paused = False
        self._timer: Timer | None = None

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

    @property
    def state(self) -> ComponentState:
        """Get the current component state."""
        return self._state

    @property
    def frames(self) -> list[str]:
        """Get the current frame list."""
        return list(self._frames)

    @property
    def interval(self) -> float:
        """Get the base animation interval."""
        return self._interval

    @property
    def speed(self) -> float:
        """Get the current speed multiplier."""
        return self._speed

    @property
    def paused(self) -> bool:
        """Whether the spinner animation is paused."""
        return self._paused

    def on_mount(self) -> None:
        """Start animation timer when widget is mounted."""
        self._start_timer()

    def on_unmount(self) -> None:
        """Stop animation timer when widget is unmounted."""
        self._stop_timer()

    def _start_timer(self) -> None:
        """Start or restart the animation timer."""
        self._stop_timer()
        if self._state == ComponentState.IN_PROGRESS and not self._paused:
            effective_interval = self._interval / self._speed
            self._timer = self.set_interval(effective_interval, self._advance_frame)

    def _stop_timer(self) -> None:
        """Stop the animation timer if running."""
        if self._timer is not None:
            self._timer.stop()
            self._timer = None

    def _advance_frame(self) -> None:
        """Advance to the next animation frame."""
        self._frame_index = (self._frame_index + 1) % len(self._frames)

    def render(self) -> Text:
        """Render the spinner widget."""
        if self._state == ComponentState.SUCCESS:
            return Text(self._success_icon, style="#00FF00")
        elif self._state == ComponentState.ERROR:
            return Text(self._error_icon, style="#FF0000")
        else:
            frame = self._frames[self._frame_index]
            return Text(frame, style=self.color)

    def validate_color(self, color: str) -> str:
        """Validate color before setting."""
        return self._validate_hex_color(color)

    def watch_color(self) -> None:
        """React to color changes."""
        self.refresh()

    def watch__frame_index(self) -> None:
        """React to frame index changes."""
        self.refresh()

    def watch__state(self, new_state: ComponentState) -> None:
        """React to state changes."""
        if new_state == ComponentState.IN_PROGRESS:
            self.remove_class("success", "error")
            if self.is_mounted:
                self._start_timer()
        elif new_state == ComponentState.SUCCESS:
            self._stop_timer()
            self.remove_class("error")
            self.add_class("success")
        elif new_state == ComponentState.ERROR:
            self._stop_timer()
            self.remove_class("success")
            self.add_class("error")
        self.refresh()

    def success(self, message: str | None = None) -> None:
        """Transition to success state.

        Args:
            message: Optional message (reserved for future use)
        """
        if not self._state.can_transition_to(ComponentState.SUCCESS):
            return
        self._state = ComponentState.SUCCESS

    def error(self, message: str | None = None) -> None:
        """Transition to error state.

        Args:
            message: Optional message (reserved for future use)
        """
        if not self._state.can_transition_to(ComponentState.ERROR):
            return
        self._state = ComponentState.ERROR

    def start(self) -> None:
        """Start or restart spinner animation."""
        self._paused = False
        self._frame_index = 0
        self._state = ComponentState.IN_PROGRESS

    def reset(self) -> None:
        """Reset to in_progress state."""
        self.start()

    def stop(self) -> None:
        """Stop the animation without changing state.

        Freezes the spinner on the current frame.
        """
        self._stop_timer()

    def pause(self) -> None:
        """Toggle pause/resume of the animation."""
        if self._state != ComponentState.IN_PROGRESS:
            return
        self._paused = not self._paused
        if self._paused:
            self._stop_timer()
        else:
            if self.is_mounted:
                self._start_timer()

    def set_speed(self, speed: float) -> None:
        """Set the animation speed multiplier.

        Args:
            speed: Speed multiplier (e.g., 2.0 for double speed)
        """
        if speed <= 0:
            raise ValueError(f"Speed must be positive, got {speed}")
        self._speed = speed
        if self._state == ComponentState.IN_PROGRESS and not self._paused and self.is_mounted:
            self._start_timer()

    def show(self) -> None:
        """Show the spinner widget."""
        self.remove_class("hidden")

    def hide(self) -> None:
        """Hide the spinner widget."""
        self.add_class("hidden")

    def toggle(self) -> None:
        """Toggle visibility state."""
        self.toggle_class("hidden")

    def set_visible(self, visible: bool) -> None:
        """Set visibility.

        Args:
            visible: Whether the widget should be visible
        """
        self.set_class(not visible, "hidden")

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> SpinnerWidget:
        """Create from configuration dictionary.

        Args:
            config: Configuration dictionary with optional keys:
                - style: Built-in spinner style name
                - frames: Custom frame sequence
                - interval: Time between frames in seconds
                - color: Hex color code
                - success_icon: Success state icon
                - error_icon: Error state icon
                - speed: Animation speed multiplier
                - visible: Whether visible

        Returns:
            A new SpinnerWidget instance
        """
        return cls(
            style=config.get("style", "npm_dots"),
            frames=config.get("frames"),
            interval=config.get("interval"),
            color=config.get("color", "#D97706"),
            success_icon=config.get("success_icon", "✓"),
            error_icon=config.get("error_icon", "✗"),
            speed=config.get("speed", 1.0),
            visible=config.get("visible", True),
        )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"SpinnerWidget(style={len(self._frames)} frames, "
            f"state={self._state.name}, speed={self._speed})"
        )
