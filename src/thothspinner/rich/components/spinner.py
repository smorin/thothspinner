"""Spinner component for Rich console output.

Animated spinner component that cycles through frames to indicate
activity. Supports multiple built-in styles and state transitions.
"""

from __future__ import annotations

import time
from typing import Any, cast

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.style import Style
from rich.text import Text

from ...core.color import COLOR_DEFAULT, COLOR_ERROR, COLOR_SUCCESS, validate_hex_color
from ...core.states import ComponentState
from ..spinners.frames import SPINNER_FRAMES

# Spinner component defaults
DEFAULT_INTERVAL = 0.08
DEFAULT_SPEED = 1.0
DEFAULT_STYLE = "npm_dots"
DEFAULT_SUCCESS_ICON = "✓"
DEFAULT_ERROR_ICON = "✗"


class SpinnerComponent:
    """Animated spinner component for Rich console.

    A component that displays an animated spinner cycling through
    predefined frames. Supports multiple styles, state transitions,
    and customizable colors.

    Attributes:
        frames: List of characters to cycle through
        interval: Time between frame changes in seconds
        color: Hex color code for the spinner
        style: Name of built-in spinner style
        success_icon: Icon to display in success state
        error_icon: Icon to display in error state
        visible: Whether the component should be rendered
        speed: Speed multiplier for animation

    Example:
        >>> from rich.console import Console
        >>> from rich.live import Live
        >>> console = Console()
        >>> spinner = SpinnerComponent(style="npm_dots", color="#D97706")
        >>> with Live(spinner, console=console, refresh_per_second=20):
        ...     time.sleep(5)
        ...     spinner.success()
    """

    def __init__(
        self,
        frames: list[str] | None = None,
        interval: float = DEFAULT_INTERVAL,
        color: str = COLOR_DEFAULT,
        style: str = DEFAULT_STYLE,
        success_icon: str = DEFAULT_SUCCESS_ICON,
        error_icon: str = DEFAULT_ERROR_ICON,
        visible: bool = True,
        speed: float = DEFAULT_SPEED,
        **kwargs: Any,
    ) -> None:
        """Initialize the SpinnerComponent.

        Args:
            frames: Custom frame sequence. If None, uses style frames.
            interval: Time between frames in seconds. Defaults to 0.08.
            color: Hex color code for the spinner. Defaults to "#D97706".
            style: Built-in spinner style name. Defaults to "npm_dots".
            success_icon: Icon for success state. Defaults to "✓".
            error_icon: Icon for error state. Defaults to "✗".
            visible: Whether to render the component. Defaults to True.
            speed: Animation speed multiplier. Defaults to 1.0.
            **kwargs: Additional keyword arguments (reserved for future use).
        """
        if frames is None:
            if style in SPINNER_FRAMES:
                spinner_def = SPINNER_FRAMES[style]
            else:
                spinner_def = SPINNER_FRAMES["npm_dots"]
            self.frames = spinner_def["frames"]
            self.interval = spinner_def["interval"]
        else:
            self.frames = frames
            self.interval = interval

        if not self.frames:
            raise ValueError("frames must not be empty")
        if self.interval <= 0:
            raise ValueError("interval must be positive")

        validate_hex_color(color)
        self.color = color
        self.success_icon = success_icon
        self.error_icon = error_icon
        self.visible = visible
        self.speed = speed
        if self.speed <= 0:
            raise ValueError("speed must be positive")

        # Internal state management
        self._state = ComponentState.IN_PROGRESS
        self._start_time: float | None = None
        self._success_color = COLOR_SUCCESS
        self._error_color = COLOR_ERROR

    @property
    def state(self) -> ComponentState:
        """Get the current component state."""
        return self._state

    def start(self) -> None:
        """Start or restart spinner animation.

        Resets the spinner to IN_PROGRESS state and restarts
        the animation from the first frame.
        """
        self._state = ComponentState.IN_PROGRESS
        self._start_time = None  # Reset animation

    def success(self, message: str | None = None) -> None:
        """Transition to success state.

        Changes the spinner to display a success icon with
        success color (green).

        Args:
            message: Optional message (reserved for future use)
        """
        if not self._state.can_transition_to(ComponentState.SUCCESS):
            # Silently ignore invalid transitions
            return
        self._state = ComponentState.SUCCESS

    def error(self, message: str | None = None) -> None:
        """Transition to error state.

        Changes the spinner to display an error icon with
        error color (red).

        Args:
            message: Optional message (reserved for future use)
        """
        if not self._state.can_transition_to(ComponentState.ERROR):
            # Silently ignore invalid transitions
            return
        self._state = ComponentState.ERROR

    def reset(self) -> None:
        """Reset to in_progress state.

        Returns the spinner to its initial animated state,
        restarting the animation from the beginning.
        """
        self._state = ComponentState.IN_PROGRESS
        self._start_time = None

    def configure_state(
        self,
        state: ComponentState,
        *,
        icon: str | None = None,
        color: str | None = None,
    ) -> None:
        """Update terminal-state icon or color overrides."""
        if color is not None:
            validate_hex_color(color)

        if state == ComponentState.SUCCESS:
            if icon is not None:
                self.success_icon = icon
            if color is not None:
                self._success_color = color
        elif state == ComponentState.ERROR:
            if icon is not None:
                self.error_icon = icon
            if color is not None:
                self._error_color = color

    def _calculate_frame(self, current_time: float) -> int:
        """Calculate current frame index based on time.

        Uses time-based calculation for stateless rendering,
        ensuring smooth animation regardless of refresh rate.

        Args:
            current_time: Current time in seconds

        Returns:
            Index of the frame to display
        """
        if self._start_time is None:
            self._start_time = current_time
            return 0

        # Calculate frame based on elapsed time with speed multiplier
        elapsed = (current_time - self._start_time) * self.speed
        frame_no = int(elapsed / self.interval) % len(self.frames)

        return frame_no

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> SpinnerComponent:
        """Create a SpinnerComponent from a configuration dictionary.

        Args:
            config: Configuration dictionary with keys:
                - frames (list[str]): Custom frame sequence
                - interval (float): Time between frames
                - color (str): Hex color code
                - style (str): Built-in style name
                - success_icon (str): Success state icon
                - error_icon (str): Error state icon
                - visible (bool): Visibility state
                - speed (float): Animation speed multiplier

        Returns:
            A new SpinnerComponent instance configured from the dictionary.

        Example:
            >>> config = {
            ...     "style": "claude_stars",
            ...     "color": "#FFA500",
            ...     "speed": 1.5
            ... }
            >>> spinner = SpinnerComponent.from_config(config)
        """
        return cls(
            frames=config.get("frames"),
            interval=config.get("interval", DEFAULT_INTERVAL),
            color=config.get("color", COLOR_DEFAULT),
            style=config.get("style", DEFAULT_STYLE),
            success_icon=config.get("success_icon", DEFAULT_SUCCESS_ICON),
            error_icon=config.get("error_icon", DEFAULT_ERROR_ICON),
            visible=config.get("visible", True),
            speed=config.get("speed", DEFAULT_SPEED),
        )

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Render the spinner component for Rich console.

        This method is called by Rich when rendering the component.
        Displays animated frames in IN_PROGRESS state, or static
        icons in SUCCESS/ERROR states.

        Args:
            console: The Rich console instance
            options: Console rendering options

        Yields:
            Rich Text object with styled spinner frame or icon
        """
        if not self.visible:
            return

        # Get current time for frame calculation
        current_time = console.get_time() if hasattr(console, "get_time") else time.time()

        if self._state == ComponentState.SUCCESS:
            style = Style(color=self._success_color)
            yield Text(self.success_icon, style=style)
        elif self._state == ComponentState.ERROR:
            style = Style(color=self._error_color)
            yield Text(self.error_icon, style=style)
        else:
            # Animate spinner using time-based calculation
            frame_idx = self._calculate_frame(current_time)
            style = Style(color=self.color)
            yield Text(self.frames[frame_idx], style=style)

    def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement:
        """Measure the spinner width for layout.

        Args:
            console: The Rich console instance
            options: Console rendering options

        Returns:
            Measurement of the component's width
        """
        if not self.visible:
            return Measurement(0, 0)

        # Measure based on current display
        if self._state == ComponentState.SUCCESS:
            text = Text(self.success_icon)
        elif self._state == ComponentState.ERROR:
            text = Text(self.error_icon)
        else:
            # Use longest frame for measurement
            longest_frame = cast(str, max(self.frames, key=len))
            text = Text(longest_frame)

        return Measurement.get(console, options, text)

    def __repr__(self) -> str:
        """Return string representation of the component."""
        return (
            f"SpinnerComponent(style={len(self.frames)} frames, "
            f"state={self._state.name}, visible={self.visible})"
        )
