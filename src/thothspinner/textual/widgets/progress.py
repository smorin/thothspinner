"""Textual Progress Widget for displaying progress counters in Textual apps."""

from __future__ import annotations

from time import monotonic
from typing import Any, ClassVar, Literal

from rich.text import Text
from textual.reactive import reactive
from textual.timer import Timer
from textual.widgets import Static

from ...core.color import validate_hex_color
from ...core.states import ComponentState

FormatStyle = Literal["fraction", "percentage", "of_text", "count_only", "ratio", "bar"]


class ProgressWidget(Static):
    """A progress counter widget for Textual apps.

    Displays progress in various text formats with state transitions.
    Supports fraction, percentage, of_text, count_only, ratio, and bar formats.

    Example:
        >>> from thothspinner.textual.widgets import ProgressWidget
        >>> progress = ProgressWidget(current=0, total=100, format_style="percentage")
    """

    DEFAULT_CSS: ClassVar[str] = """
    ProgressWidget {
        width: auto;
        height: 1;
        padding: 0;
        background: transparent;
    }

    ProgressWidget.success {
        color: $success;
    }

    ProgressWidget.error {
        color: $error;
    }
    """

    # Reactive properties
    current = reactive(0)
    total = reactive(100)
    color = reactive("#D97706")
    _state = reactive(ComponentState.IN_PROGRESS)

    def __init__(
        self,
        current: int = 0,
        total: int = 100,
        *,
        format_style: FormatStyle = "fraction",
        color: str = "#D97706",
        zero_pad: bool = False,
        success_text: str = "100%",
        error_text: str = "Failed",
        # Bar format params
        bar_width: int = 20,
        bar_filled: str = "█",
        bar_empty: str = "░",
        bar_brackets: bool = True,
        bar_show_percentage: bool = True,
        # Animation params
        animate: bool = False,
        animation_duration: float = 0.3,
        animation_easing: str = "linear",
        visible: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the ProgressWidget.

        Args:
            current: Current progress value.
            total: Total value to complete.
            format_style: Display format style.
            color: Hex color code (#RRGGBB format).
            zero_pad: Whether to zero-pad current value.
            success_text: Text shown in success state.
            error_text: Text shown in error state.
            bar_width: Total character width of the bar (bar format only).
            bar_filled: Character for the filled portion of the bar.
            bar_empty: Character for the empty portion of the bar.
            bar_brackets: Whether to wrap the bar in [ ] brackets.
            bar_show_percentage: Whether to append percentage text after the bar.
            animate: Whether to animate value transitions.
            animation_duration: Transition duration in seconds.
            animation_easing: Easing function name (linear, ease_in, ease_out, ease_in_out).
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
        self._format_style: FormatStyle = format_style
        self._zero_pad = zero_pad
        self._success_text = success_text
        self._error_text = error_text
        self._success_color: str | None = None
        self._error_color: str | None = None
        # Bar config
        self._bar_width = bar_width
        self._bar_filled = bar_filled
        self._bar_empty = bar_empty
        self._bar_brackets = bar_brackets
        self._bar_show_percentage = bar_show_percentage
        # Animation config
        self._animate = animate
        self._animation_duration = animation_duration
        self._animation_easing = animation_easing

        # Animation state — must be before self.current is set (watch_current fires on init)
        self._display_current: float = float(min(max(0, current), total))
        self._animation_timer: Timer | None = None
        self._animation_start_value: float = 0.0
        self._animation_target_value: float = 0.0
        self._animation_start_time: float = 0.0

        self.color = validate_hex_color(color)
        self.total = total
        self.current = min(max(0, current), total)

        if not visible:
            self.display = False

    @property
    def state(self) -> ComponentState:
        """Get the current component state."""
        return self._state

    @property
    def format_style(self) -> FormatStyle:
        """Get the current format style."""
        return self._format_style

    @property
    def zero_pad(self) -> bool:
        """Get the zero-padding setting."""
        return self._zero_pad

    def _format_progress(self) -> str:
        """Format progress based on style.

        Returns:
            Formatted progress string.
        """
        display_int = int(round(self._display_current))
        pad_width = len(str(self.total)) if self._zero_pad else 0
        current_str = str(display_int).zfill(pad_width) if pad_width else str(display_int)

        if self._format_style == "fraction":
            return f"{current_str}/{self.total}"
        elif self._format_style == "percentage":
            percent = (self._display_current / self.total * 100) if self.total > 0 else 0
            return f"{percent:.0f}%"
        elif self._format_style == "of_text":
            return f"{current_str} of {self.total}"
        elif self._format_style == "count_only":
            return current_str
        elif self._format_style == "ratio":
            return f"{current_str}:{self.total}"
        elif self._format_style == "bar":
            ratio = (self._display_current / self.total) if self.total > 0 else 0.0
            filled = round(ratio * self._bar_width)
            bar = self._bar_filled * filled + self._bar_empty * (self._bar_width - filled)
            if self._bar_brackets:
                bar = f"[{bar}]"
            if self._bar_show_percentage:
                pct = ratio * 100
                bar = f"{bar} {pct:.0f}%"
            return bar
        return ""

    def render(self) -> Text:
        """Render the progress widget."""
        if self._state == ComponentState.SUCCESS:
            return Text(self._success_text, style=self._success_color)
        elif self._state == ComponentState.ERROR:
            return Text(self._error_text, style=self._error_color)
        else:
            return Text(self._format_progress(), style=self.color)

    def validate_color(self, color: str) -> str:
        """Validate color before setting."""
        return validate_hex_color(color)

    def watch_current(self) -> None:
        """React to current value changes."""
        if not self._animate:
            self._display_current = float(self.current)
            self.refresh()
            return
        # Cancel any running animation
        if self._animation_timer is not None:
            self._animation_timer.stop()
        self._animation_start_value = self._display_current
        self._animation_target_value = float(self.current)
        # Skip if no movement needed (e.g., reset() sets current=0 when display is already 0)
        if self._animation_start_value == self._animation_target_value:
            self.refresh()
            return
        self._animation_start_time = monotonic()
        self._animation_timer = self.set_interval(1 / 60, self._animation_tick)

    def watch_total(self) -> None:
        """React to total value changes."""
        self.refresh()

    def watch_color(self) -> None:
        """React to color changes."""
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

    # ── Easing functions ──────────────────────────────────────────────────────

    @staticmethod
    def _ease_linear(t: float) -> float:
        return t

    @staticmethod
    def _ease_in(t: float) -> float:
        return t * t

    @staticmethod
    def _ease_out(t: float) -> float:
        return t * (2 - t)

    @staticmethod
    def _ease_in_out(t: float) -> float:
        return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2

    # ── Animation ─────────────────────────────────────────────────────────────

    def _animation_tick(self) -> None:
        """Called at ~60fps during value animation."""
        if self._animation_timer is None:
            return  # cancelled by reset/success/error
        elapsed = monotonic() - self._animation_start_time
        t = min(elapsed / self._animation_duration, 1.0)
        easing_fns = {
            "linear": self._ease_linear,
            "ease_in": self._ease_in,
            "ease_out": self._ease_out,
            "ease_in_out": self._ease_in_out,
        }
        eased_t = easing_fns.get(self._animation_easing, self._ease_linear)(t)
        self._display_current = (
            self._animation_start_value
            + (self._animation_target_value - self._animation_start_value) * eased_t
        )
        self.refresh()
        if t >= 1.0:
            self._animation_timer.stop()
            self._animation_timer = None

    def on_unmount(self) -> None:
        """Cancel animation timer when widget is removed."""
        if self._animation_timer is not None:
            self._animation_timer.stop()
            self._animation_timer = None

    # ── Update methods ────────────────────────────────────────────────────────

    def increment(self) -> None:
        """Increment progress by 1."""
        if self.current < self.total:
            self.current += 1

    def set(self, value: int) -> None:
        """Set progress to specific value, clamped to [0, total].

        Args:
            value: The value to set.
        """
        self.current = min(max(0, value), self.total)

    def add(self, amount: int) -> None:
        """Add amount to current progress.

        Args:
            amount: Amount to add (can be negative).
        """
        self.set(self.current + amount)

    def set_percentage(self, percent: float) -> None:
        """Set progress by percentage (0-100).

        Args:
            percent: Percentage value (0-100).
        """
        value = int(self.total * (percent / 100))
        self.set(value)

    def is_complete(self) -> bool:
        """Check if progress is complete.

        Returns:
            True if current >= total.
        """
        return self.current >= self.total

    # ── State management ──────────────────────────────────────────────────────

    def success(self, text: str | None = None) -> None:
        """Transition to success state.

        Args:
            text: Optional custom success text.
        """
        if self._animation_timer is not None:
            self._animation_timer.stop()
            self._animation_timer = None
        if not self._state.can_transition_to(ComponentState.SUCCESS):
            return
        if text is not None:
            self._success_text = text
        self._state = ComponentState.SUCCESS

    def error(self, text: str | None = None) -> None:
        """Transition to error state.

        Args:
            text: Optional custom error text.
        """
        if self._animation_timer is not None:
            self._animation_timer.stop()
            self._animation_timer = None
        if not self._state.can_transition_to(ComponentState.ERROR):
            return
        if text is not None:
            self._error_text = text
        self._state = ComponentState.ERROR

    def reset(self) -> None:
        """Reset to in_progress state and current to 0."""
        if self._animation_timer is not None:
            self._animation_timer.stop()
            self._animation_timer = None
        self._display_current = 0.0
        self.current = 0
        self._state = ComponentState.IN_PROGRESS

    def configure_state(
        self,
        state: ComponentState,
        *,
        color: str | None = None,
    ) -> None:
        """Update terminal-state color overrides."""
        if color is not None:
            color = validate_hex_color(color)
        if state == ComponentState.SUCCESS:
            self._success_color = color
        elif state == ComponentState.ERROR:
            self._error_color = color
        self.refresh()

    # ── Visibility methods ────────────────────────────────────────────────────

    def show(self) -> None:
        """Show the progress widget."""
        self.display = True

    def hide(self) -> None:
        """Hide the progress widget."""
        self.display = False

    def toggle(self) -> None:
        """Toggle visibility state."""
        self.display = not self.display

    def set_visible(self, visible: bool) -> None:
        """Set visibility.

        Args:
            visible: Whether the widget should be visible.
        """
        self.display = visible

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> ProgressWidget:
        """Create from configuration dictionary.

        Args:
            config: Configuration dictionary with optional keys:
                - current: Current progress value
                - total: Total value
                - format_style: Display format style
                - color: Hex color code
                - zero_pad: Whether to zero-pad
                - success_text: Success state text
                - error_text: Error state text
                - bar_width: Width of the bar (bar format)
                - bar_filled: Filled character (bar format)
                - bar_empty: Empty character (bar format)
                - bar_brackets: Whether to wrap bar in brackets
                - bar_show_percentage: Whether to show percentage after bar
                - animate: Whether to animate transitions
                - animation_duration: Transition duration in seconds
                - animation_easing: Easing function name
                - visible: Whether visible

        Returns:
            A new ProgressWidget instance.
        """
        return cls(
            current=config.get("current", 0),
            total=config.get("total", 100),
            format_style=config.get("format_style", "fraction"),
            color=config.get("color", "#D97706"),
            zero_pad=config.get("zero_pad", False),
            success_text=config.get("success_text", "100%"),
            error_text=config.get("error_text", "Failed"),
            bar_width=config.get("bar_width", 20),
            bar_filled=config.get("bar_filled", "█"),
            bar_empty=config.get("bar_empty", "░"),
            bar_brackets=config.get("bar_brackets", True),
            bar_show_percentage=config.get("bar_show_percentage", True),
            animate=config.get("animate", False),
            animation_duration=config.get("animation_duration", 0.3),
            animation_easing=config.get("animation_easing", "linear"),
            visible=config.get("visible", True),
        )

    def __repr__(self) -> str:
        """Return string representation."""
        base = (
            f"ProgressWidget(current={self.current}, total={self.total}, "
            f"format={self._format_style}, state={self._state.name}"
        )
        if self._format_style == "bar":
            base += (
                f", bar_width={self._bar_width}, bar_brackets={self._bar_brackets}"
                f", bar_show_percentage={self._bar_show_percentage}"
            )
        return base + ")"
