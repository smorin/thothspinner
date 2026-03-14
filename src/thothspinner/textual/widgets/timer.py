"""Textual Timer Widget for displaying elapsed time in Textual apps."""

from __future__ import annotations

from time import monotonic
from typing import Any, ClassVar, Literal

from rich.text import Text
from textual.reactive import reactive
from textual.timer import Timer as TextualTimer
from textual.widgets import Static

from ...core.states import ComponentState

TimerFormat = Literal[
    "seconds",
    "seconds_decimal",
    "seconds_precise",
    "milliseconds",
    "mm:ss",
    "hh:mm:ss",
    "compact",
    "full_ms",
    "auto",
    "auto_ms",
]


class TimerWidget(Static):
    """An elapsed time timer widget for Textual apps.

    Displays elapsed time in various formats with start/stop/pause/resume
    controls. Supports state transitions and customizable colors.

    Example:
        >>> from thothspinner.textual.widgets import TimerWidget
        >>> timer = TimerWidget(format_style="auto", color="#FFFF55")
    """

    DEFAULT_CSS: ClassVar[str] = """
    TimerWidget {
        width: auto;
        height: 1;
        padding: 0;
        background: transparent;
    }

    TimerWidget.hidden {
        display: none;
    }

    TimerWidget.success {
        color: $success;
    }

    TimerWidget.error {
        color: $error;
    }
    """

    # Reactive properties
    color = reactive("#FFFF55")
    _state = reactive(ComponentState.IN_PROGRESS)

    def __init__(
        self,
        format_style: TimerFormat = "auto",
        *,
        precision: int = 1,
        color: str = "#FFFF55",
        success_text: str | None = None,
        error_text: str | None = None,
        visible: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the TimerWidget.

        Args:
            format_style: Time display format style.
            precision: Decimal places for decimal formats.
            color: Hex color code (#RRGGBB format).
            success_text: Optional text shown in success state.
            error_text: Optional text shown in error state.
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
        self._format_style: TimerFormat = format_style
        self._precision = precision
        self._success_text = success_text
        self._error_text = error_text
        self.color = self._validate_hex_color(color)

        # Timer tracking state
        self._timer_active = False
        self._paused = False
        self._elapsed: float = 0.0
        self._start_time: float | None = None
        self._display_timer: TextualTimer | None = None

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
    def format_style(self) -> TimerFormat:
        """Get the current format style."""
        return self._format_style

    @property
    def precision(self) -> int:
        """Get the current precision setting."""
        return self._precision

    @property
    def running(self) -> bool:
        """Whether the timer is currently running."""
        return self._timer_active

    # Override Widget.is_running to avoid conflict
    def is_running(self) -> bool:  # type: ignore[override]
        """Check if the timer is currently running."""
        return self._timer_active

    @property
    def paused(self) -> bool:
        """Whether the timer is currently paused."""
        return self._paused

    # --- Time formatting (ported from Rich TimerComponent) ---

    def _format_time(self, elapsed: float) -> str:
        """Format elapsed time based on style."""
        if self._format_style == "seconds":
            return f"{int(elapsed)}s"
        elif self._format_style == "seconds_decimal":
            return f"{elapsed:.{self._precision}f}s"
        elif self._format_style == "seconds_precise":
            return f"{elapsed:.3f}s"
        elif self._format_style == "milliseconds":
            return f"{int(elapsed * 1000)}ms"
        elif self._format_style in ("mm:ss", "hh:mm:ss", "compact"):
            return self._format_duration(elapsed)
        elif self._format_style == "full_ms":
            return self._format_duration_with_ms(elapsed)
        elif self._format_style in ("auto", "auto_ms"):
            return self._format_auto(elapsed)
        return ""

    def _format_duration(self, elapsed: float) -> str:
        """Format as duration (mm:ss or hh:mm:ss)."""
        total_seconds = int(elapsed)
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if self._format_style == "compact":
            if hours:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            return f"{minutes}:{seconds:02d}"
        elif self._format_style == "mm:ss":
            total_minutes = total_seconds // 60
            secs = total_seconds % 60
            return f"{total_minutes:02d}:{secs:02d}"
        elif self._format_style == "hh:mm:ss":
            if hours == 0:
                return f"{minutes:02d}:{seconds:02d}"
            else:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{hours}:{minutes:02d}:{seconds:02d}"

    def _format_duration_with_ms(self, elapsed: float) -> str:
        """Format duration with milliseconds (mm:ss.mmm)."""
        milliseconds = int((elapsed % 1) * 1000)
        mins, secs = divmod(int(elapsed), 60)
        if mins > 0:
            return f"{mins}:{secs:02d}.{milliseconds:03d}"
        return f"{secs}.{milliseconds:03d}"

    def _format_auto(self, elapsed: float) -> str:
        """Auto format based on duration."""
        if elapsed < 10 and self._format_style == "auto_ms":
            return f"{elapsed:.1f}s"
        elif elapsed < 60:
            return f"{int(elapsed)}s"
        elif elapsed < 3600:
            mins, secs = divmod(int(elapsed), 60)
            return f"{mins}:{secs:02d}"
        else:
            return self._format_duration(elapsed)

    # --- Display timer management ---

    def on_unmount(self) -> None:
        """Stop display timer when widget is unmounted."""
        self._stop_display_timer()

    def _start_display_timer(self) -> None:
        """Start the display refresh timer."""
        self._stop_display_timer()
        if self._timer_active and not self._paused:
            self._display_timer = self.set_interval(0.1, self._tick)

    def _stop_display_timer(self) -> None:
        """Stop the display refresh timer."""
        if self._display_timer is not None:
            self._display_timer.stop()
            self._display_timer = None

    def _tick(self) -> None:
        """Refresh display on timer tick."""
        self.refresh()

    # --- Timer control methods ---

    def start(self) -> None:
        """Start the timer."""
        if not self._timer_active:
            self._start_time = monotonic()
            self._timer_active = True
            self._paused = False
            if self.is_mounted:
                self._start_display_timer()

    def stop(self) -> None:
        """Stop the timer and accumulate elapsed time."""
        if self._timer_active and self._start_time is not None:
            self._elapsed += monotonic() - self._start_time
            self._timer_active = False
            self._paused = False
            self._start_time = None
            self._stop_display_timer()

    def resume(self) -> None:
        """Resume the timer after stopping."""
        if not self._timer_active:
            self._start_time = monotonic()
            self._timer_active = True
            self._paused = False
            if self.is_mounted:
                self._start_display_timer()

    def pause(self) -> None:
        """Toggle pause/resume of the timer."""
        if self._state != ComponentState.IN_PROGRESS:
            return
        if not self._timer_active:
            return
        if not self._paused:
            # Pause: accumulate elapsed, stop display
            if self._start_time is not None:
                self._elapsed += monotonic() - self._start_time
                self._start_time = None
            self._paused = True
            self._stop_display_timer()
        else:
            # Unpause: restart timing
            self._start_time = monotonic()
            self._paused = False
            if self.is_mounted:
                self._start_display_timer()
        self.refresh()

    def reset(self) -> None:
        """Reset the timer to zero."""
        self._elapsed = 0.0
        self._start_time = monotonic() if self._timer_active else None
        self._paused = False
        self._state = ComponentState.IN_PROGRESS
        if self._timer_active and self.is_mounted:
            self._start_display_timer()
        self.refresh()

    def get_elapsed(self) -> float:
        """Get total elapsed time in seconds."""
        if self._timer_active and not self._paused and self._start_time is not None:
            return self._elapsed + (monotonic() - self._start_time)
        return self._elapsed

    # --- Rendering ---

    def render(self) -> Text:
        """Render the timer widget."""
        if self._state == ComponentState.SUCCESS:
            display = self._success_text or self._format_time(self._elapsed)
            return Text(display, style="#00FF00")
        elif self._state == ComponentState.ERROR:
            display = self._error_text or self._format_time(self._elapsed)
            return Text(display, style="#FF0000")
        else:
            return Text(self._format_time(self.get_elapsed()), style=self.color)

    # --- Reactive watchers ---

    def validate_color(self, color: str) -> str:
        """Validate color before setting."""
        return self._validate_hex_color(color)

    def watch_color(self) -> None:
        """React to color changes."""
        self.refresh()

    def watch__state(self, new_state: ComponentState) -> None:
        """React to state changes."""
        if new_state == ComponentState.IN_PROGRESS:
            self.remove_class("success", "error")
        elif new_state == ComponentState.SUCCESS:
            self._stop_display_timer()
            self.remove_class("error")
            self.add_class("success")
        elif new_state == ComponentState.ERROR:
            self._stop_display_timer()
            self.remove_class("success")
            self.add_class("error")
        self.refresh()

    # --- State management ---

    def success(self, text: str | None = None) -> None:
        """Transition to success state.

        Args:
            text: Optional custom success text.
        """
        if not self._state.can_transition_to(ComponentState.SUCCESS):
            return
        self.stop()
        if text is not None:
            self._success_text = text
        self._state = ComponentState.SUCCESS

    def error(self, text: str | None = None) -> None:
        """Transition to error state.

        Args:
            text: Optional custom error text.
        """
        if not self._state.can_transition_to(ComponentState.ERROR):
            return
        self.stop()
        if text is not None:
            self._error_text = text
        self._state = ComponentState.ERROR

    # --- Visibility methods ---

    def show(self) -> None:
        """Show the timer widget."""
        self.remove_class("hidden")

    def hide(self) -> None:
        """Hide the timer widget."""
        self.add_class("hidden")

    def toggle(self) -> None:
        """Toggle visibility state."""
        self.toggle_class("hidden")

    def set_visible(self, visible: bool) -> None:
        """Set visibility.

        Args:
            visible: Whether the widget should be visible.
        """
        self.set_class(not visible, "hidden")

    # --- Factory ---

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> TimerWidget:
        """Create from configuration dictionary.

        Args:
            config: Configuration dictionary with optional keys:
                - format_style: Time display format style
                - precision: Decimal places for decimal formats
                - color: Hex color code
                - success_text: Success state text
                - error_text: Error state text
                - visible: Whether visible

        Returns:
            A new TimerWidget instance.
        """
        return cls(
            format_style=config.get("format_style", "auto"),
            precision=config.get("precision", 1),
            color=config.get("color", "#FFFF55"),
            success_text=config.get("success_text"),
            error_text=config.get("error_text"),
            visible=config.get("visible", True),
        )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"TimerWidget(format={self._format_style}, "
            f"state={self._state.name}, elapsed={self._elapsed:.1f})"
        )
