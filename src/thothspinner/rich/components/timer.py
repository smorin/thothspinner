"""Timer component for ThothSpinner."""

from time import time
from typing import Any, Literal

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.text import Text

from ...core.color import COLOR_ERROR, COLOR_SUCCESS, COLOR_TIMER
from ...core.states import ComponentState
from .base import BaseComponent
from .state import StateConfig

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


class TimerComponent(BaseComponent):
    """Timer component with multiple time formats."""

    def __init__(
        self,
        format: dict[str, Any] | None = None,
        color: str | None = None,
        precision: int = 1,
        visible: bool = True,
    ):
        """Initialize the TimerComponent.

        Args:
            format: Format configuration dict with key "style" set to one of:
                "seconds", "seconds_decimal", "seconds_precise", "milliseconds",
                "mm:ss", "hh:mm:ss", "compact", "full_ms", "auto", "auto_ms".
                Defaults to {"style": "auto"}.
            color: Hex color code for display. Defaults to None (uses "#FFFF55").
            precision: Decimal places for seconds_decimal format. Defaults to 1.
            visible: Whether to render the component. Defaults to True.
        """
        super().__init__(color)
        self.visible = visible
        self.format = format or {"style": "auto"}
        self.format_style: TimerFormat = self.format.get("style", "auto")
        self.precision = self.format.get("precision", precision)
        self._start_time: float | None = None
        self._elapsed: float = 0.0
        self._running = False
        self._state = ComponentState.IN_PROGRESS
        self._state_configs = self._get_default_state_configs()

    def _get_default_state_configs(self) -> dict[ComponentState, StateConfig]:
        """Get default state configurations."""
        return {
            ComponentState.IN_PROGRESS: StateConfig(
                animating=True, color=self.color or COLOR_TIMER
            ),
            ComponentState.SUCCESS: StateConfig(animating=False, color=COLOR_SUCCESS),
            ComponentState.ERROR: StateConfig(animating=False, color=COLOR_ERROR),
        }

    def _format_time(self, elapsed: float) -> str:
        """Format elapsed time based on style."""
        if self.format_style == "seconds":
            return f"{int(elapsed)}s"
        elif self.format_style == "seconds_decimal":
            return f"{elapsed:.{self.precision}f}s"
        elif self.format_style == "seconds_precise":
            return f"{elapsed:.3f}s"
        elif self.format_style == "milliseconds":
            return f"{int(elapsed * 1000)}ms"
        elif self.format_style in ("mm:ss", "hh:mm:ss", "compact"):
            return self._format_duration(elapsed)
        elif self.format_style == "full_ms":
            return self._format_duration_with_ms(elapsed)
        elif self.format_style in ("auto", "auto_ms"):
            return self._format_auto(elapsed)
        return ""

    def _format_duration(self, elapsed: float) -> str:
        """Format as duration (mm:ss or hh:mm:ss)."""
        total_seconds = int(elapsed)
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if self.format_style == "compact":
            if hours:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            return f"{minutes}:{seconds:02d}"
        elif self.format_style == "mm:ss":
            # mm:ss format shows total minutes (can exceed 59)
            total_minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{total_minutes:02d}:{seconds:02d}"
        elif self.format_style == "hh:mm:ss":
            if hours == 0:
                return f"{minutes:02d}:{seconds:02d}"
            else:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{hours}:{minutes:02d}:{seconds:02d}"

    def _format_duration_with_ms(self, elapsed: float) -> str:
        """Format duration with milliseconds (mm:ss.mmm)."""
        milliseconds = int((elapsed % 1) * 1000)
        minutes, seconds = divmod(int(elapsed), 60)
        if minutes > 0:
            return f"{minutes}:{seconds:02d}.{milliseconds:03d}"
        return f"{seconds}.{milliseconds:03d}"

    def _format_auto(self, elapsed: float) -> str:
        """Auto format based on duration."""
        if elapsed < 10 and self.format_style == "auto_ms":
            return f"{elapsed:.1f}s"
        elif elapsed < 60:
            return f"{int(elapsed)}s"
        elif elapsed < 3600:
            minutes, seconds = divmod(int(elapsed), 60)
            return f"{minutes}:{seconds:02d}"
        else:
            return self._format_duration(elapsed)

    # Timer control methods
    def start(self) -> None:
        """Start the timer."""
        if not self._running:
            self._start_time = time()
            self._running = True

    def stop(self) -> None:
        """Stop the timer."""
        if self._running and self._start_time:
            self._elapsed += time() - self._start_time
            self._running = False
            self._start_time = None

    def resume(self) -> None:
        """Resume the timer."""
        if not self._running:
            self._start_time = time()
            self._running = True

    def reset(self) -> None:
        """Reset the timer."""
        self._elapsed = 0.0
        self._start_time = time() if self._running else None
        self._state = ComponentState.IN_PROGRESS

    def get_elapsed(self) -> float:
        """Get total elapsed time in seconds."""
        if self._running and self._start_time:
            return self._elapsed + (time() - self._start_time)
        return self._elapsed

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Render the timer component."""
        if not self.visible:
            return
        config = self._state_configs[self._state]

        # Only update time if animating (in_progress)
        if config.animating:
            elapsed = self.get_elapsed()
        else:
            elapsed = self._elapsed

        from rich.style import Style

        style = Style(color=config.color) if config.color else self._style
        text = self._format_time(elapsed)
        yield Segment(text, style)

    def __rich__(self) -> Text:
        """Rich protocol support for direct printing."""
        config = self._state_configs[self._state]

        # Only update time if animating (in_progress)
        if config.animating:
            elapsed = self.get_elapsed()
        else:
            elapsed = self._elapsed

        from rich.style import Style

        style = Style(color=config.color) if config.color else self._style
        return Text(self._format_time(elapsed), style=style)

    def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement:
        """Measure the timer component width for layout."""
        if not self.visible:
            return Measurement(0, 0)
        text = Text(self._format_time(self.get_elapsed()))
        return Measurement.get(console, options, text)

    # State management
    def success(self) -> None:
        """Transition to success state."""
        if not self._state.can_transition_to(ComponentState.SUCCESS):
            return
        self.stop()
        self._state = ComponentState.SUCCESS

    def error(self) -> None:
        """Transition to error state."""
        if not self._state.can_transition_to(ComponentState.ERROR):
            return
        self.stop()
        self._state = ComponentState.ERROR

    def is_running(self) -> bool:
        """Check if the timer is currently running."""
        return self._running
