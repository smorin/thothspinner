"""Progress component for ThothSpinner."""

from __future__ import annotations

import difflib
from typing import Any, Literal, cast

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.text import Text

from ...core.color import COLOR_ERROR, COLOR_SUCCESS
from ...core.states import ComponentState
from .base import BaseComponent
from .state import StateConfig

FormatStyle = Literal["fraction", "percentage", "of_text", "count_only", "ratio"]

# Progress component defaults
DEFAULT_TOTAL = 100


class ProgressComponent(BaseComponent):
    """Progress counter component with multiple display formats."""

    def __init__(
        self,
        current: int = 0,
        total: int = DEFAULT_TOTAL,
        format: dict[str, Any] | None = None,
        color: str | None = None,
        zero_pad: bool = False,
        visible: bool = True,
    ):
        """Initialize the ProgressComponent.

        Args:
            current: Initial progress value. Defaults to 0.
            total: Total value for completion. Defaults to 100.
            format: Format configuration dict with key "style" set to one of:
                "fraction" (e.g., "42/100"), "percentage" (e.g., "42%"),
                "of_text" (e.g., "42 of 100"), "count_only" (e.g., "42"),
                "ratio" (e.g., "42:100"). Defaults to {"style": "fraction"}.
            color: Hex color code for display. Defaults to None (inherits).
            zero_pad: Whether to zero-pad the current value. Defaults to False.
            visible: Whether to render the component. Defaults to True.
        """
        super().__init__(color)
        self.visible = visible
        self.current = current
        self.total = total
        self.format = format or {"style": "fraction"}
        self.format_style: FormatStyle = cast(FormatStyle, self.format.get("style", "fraction"))
        _valid_format_styles = frozenset(
            {"fraction", "percentage", "of_text", "count_only", "ratio"}
        )
        if self.format_style not in _valid_format_styles:
            available = sorted(_valid_format_styles)
            suggestions = difflib.get_close_matches(self.format_style, available, n=3, cutoff=0.6)
            hint = f" Did you mean {suggestions[0]!r}?" if suggestions else ""
            raise ValueError(
                f"Unknown progress format style {self.format_style!r}.{hint} "
                f"Available styles: {', '.join(available)}"
            )
        self.zero_pad = zero_pad
        self._state = ComponentState.IN_PROGRESS
        self._state_configs = self._get_default_state_configs()

    def _get_default_state_configs(self) -> dict[ComponentState, StateConfig]:
        """Get default state configurations."""
        return {
            ComponentState.IN_PROGRESS: StateConfig(
                animating=False,  # Progress doesn't animate
                color=self.color,
            ),
            ComponentState.SUCCESS: StateConfig(animating=False, color=COLOR_SUCCESS, text="100%"),
            ComponentState.ERROR: StateConfig(animating=False, color=COLOR_ERROR, text="Failed"),
        }

    def _format_progress(self) -> str:
        """Format progress based on style."""
        if self._state != ComponentState.IN_PROGRESS:
            config = self._state_configs[self._state]
            if config.text:
                return config.text

        # Calculate padding width
        pad_width = len(str(self.total)) if self.zero_pad else 0
        current_str = str(self.current).zfill(pad_width) if pad_width else str(self.current)

        if self.format_style == "fraction":
            return f"{current_str}/{self.total}"
        elif self.format_style == "percentage":
            percent = (self.current / self.total * 100) if self.total > 0 else 0
            return f"{percent:.0f}%"
        elif self.format_style == "of_text":
            return f"{current_str} of {self.total}"
        elif self.format_style == "count_only":
            return current_str
        elif self.format_style == "ratio":
            return f"{current_str}:{self.total}"
        return ""

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Render the progress component."""
        if not self.visible:
            return
        config = self._state_configs[self._state]
        from rich.style import Style

        style = Style(color=config.color) if config.color else self._style
        text = self._format_progress()
        yield Segment(text, style)

    def __rich__(self) -> Text:
        """Rich protocol support for direct printing."""
        config = self._state_configs[self._state]
        from rich.style import Style

        style = Style(color=config.color) if config.color else self._style
        return Text(self._format_progress(), style=style or "")

    def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement:
        """Measure the progress component width for layout."""
        if not self.visible:
            return Measurement(0, 0)
        text = Text(self._format_progress())
        return Measurement.get(console, options, text)

    # Update methods
    def increment(self) -> None:
        """Increment progress by 1."""
        if self.current < self.total:
            self.current += 1

    def set(self, value: int) -> None:
        """Set progress to specific value, clamped to [0, total]."""
        self.current = min(max(0, value), self.total)

    def set_percentage(self, percent: float) -> None:
        """Set progress by percentage (0-100)."""
        value = int(self.total * (percent / 100))
        self.set(value)

    def add(self, amount: int) -> None:
        """Add amount to current progress."""
        self.set(self.current + amount)

    # State management
    def success(self, text: str | None = None) -> None:
        """Transition to success state.

        Args:
            text: Optional custom success text. Defaults to "100%".
        """
        if not self._state.can_transition_to(ComponentState.SUCCESS):
            return
        self._state = ComponentState.SUCCESS
        if text:
            self._state_configs[ComponentState.SUCCESS].text = text

    def error(self, text: str | None = None) -> None:
        """Transition to error state.

        Args:
            text: Optional custom error text. Defaults to "Failed".
        """
        if not self._state.can_transition_to(ComponentState.ERROR):
            return
        self._state = ComponentState.ERROR
        if text:
            self._state_configs[ComponentState.ERROR].text = text

    def reset(self) -> None:
        """Reset to in_progress state."""
        self._state = ComponentState.IN_PROGRESS
        self.current = 0

    def configure_state(
        self,
        state: ComponentState,
        *,
        text: str | None = None,
        color: str | None = None,
    ) -> None:
        """Update terminal-state text or color overrides."""
        if state not in self._state_configs:
            return
        if text is not None:
            self._state_configs[state].text = text
        if color is not None:
            self._state_configs[state].color = color

    def is_complete(self) -> bool:
        """Check if progress has reached or exceeded total."""
        return self.current >= self.total
