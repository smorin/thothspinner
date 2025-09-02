"""Progress component for ThothSpinner."""

from typing import Any, Literal

from rich.console import Console, ConsoleOptions, RenderResult
from rich.segment import Segment
from rich.text import Text

from .base import BaseComponent
from .state import ComponentState, StateConfig

FormatStyle = Literal["fraction", "percentage", "of_text", "count_only", "ratio"]


class ProgressComponent(BaseComponent):
    """Progress counter component with multiple display formats."""

    def __init__(
        self,
        current: int = 0,
        total: int = 100,
        format: dict[str, Any] | None = None,
        color: str | None = None,
        zero_pad: bool = False,
    ):
        super().__init__(color)
        self.current = current
        self.total = total
        self.format = format or {"style": "fraction"}
        self.format_style: FormatStyle = self.format.get("style", "fraction")
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
            ComponentState.SUCCESS: StateConfig(animating=False, color="#00FF00", text="100%"),
            ComponentState.ERROR: StateConfig(animating=False, color="#FF0000", text="Failed"),
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
        return Text(self._format_progress(), style=style)

    # Update methods
    def increment(self) -> None:
        """Increment progress by 1."""
        if self.current < self.total:
            self.current += 1

    def set(self, value: int) -> None:
        """Set progress to specific value."""
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
        """Transition to success state."""
        self._state = ComponentState.SUCCESS
        if text:
            self._state_configs[ComponentState.SUCCESS].text = text

    def error(self, text: str | None = None) -> None:
        """Transition to error state."""
        self._state = ComponentState.ERROR
        if text:
            self._state_configs[ComponentState.ERROR].text = text

    def reset(self) -> None:
        """Reset to in_progress state."""
        self._state = ComponentState.IN_PROGRESS
        self.current = 0

    def is_complete(self) -> bool:
        """Check if progress is complete."""
        return self.current >= self.total
