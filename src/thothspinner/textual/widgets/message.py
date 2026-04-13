"""Textual Message Widget for displaying rotating action words with shimmer effects."""

from __future__ import annotations

import random
from time import monotonic
from typing import Any, ClassVar

from rich.style import Style
from rich.text import Text
from textual.reactive import reactive
from textual.timer import Timer as TextualTimer
from textual.widgets import Static

from ...core.color import validate_hex_color
from ...core.states import ComponentState
from ...rich.components.message import DEFAULT_ACTION_WORDS


class MessageWidget(Static):
    """An animated message widget with shimmer effects for Textual apps.

    Displays rotating action words with optional shimmer animation.
    Supports word list management, directional control, and state transitions.

    Example:
        >>> from thothspinner.textual.widgets import MessageWidget
        >>> message = MessageWidget(
        ...     action_words=["Processing", "Analyzing"],
        ...     shimmer={"enabled": True, "width": 3},
        ... )
    """

    DEFAULT_CSS: ClassVar[str] = """
    MessageWidget {
        width: auto;
        height: 1;
        padding: 0;
        background: transparent;
    }

    MessageWidget.success {
        color: $success;
    }

    MessageWidget.error {
        color: $error;
    }
    """

    # Reactive properties
    color = reactive("#D97706")
    _state = reactive(ComponentState.IN_PROGRESS)

    def __init__(
        self,
        action_words: list[str] | dict[str, Any] | None = None,
        *,
        interval: dict[str, float] | None = None,
        color: str = "#D97706",
        shimmer: dict[str, Any] | None = None,
        suffix: str = "…",
        text: str | None = None,
        success_text: str = "Complete!",
        error_text: str = "Failed",
        visible: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the MessageWidget.

        Args:
            action_words: Word list configuration. Can be:
                - List of words to replace default list
                - Dict with "mode" ("add"/"replace") and "words"
                - None to use default list
            interval: Time range for word changes {"min": 0.5, "max": 3.0}.
            color: Base hex color for text (#RRGGBB format).
            shimmer: Shimmer configuration dict with keys:
                - enabled (bool): Whether shimmer is active (default True)
                - width (int): Width of shimmer effect (default 3)
                - light_color (str): Hex color for shimmer (default "#FFA500")
                - speed (float): Shimmer movement speed (default 1.0)
                - reverse (bool): Direction of shimmer (default False)
            suffix: Suffix to append to words.
            text: Initial rotating message text to show before normal rotation resumes.
            success_text: Text shown in success state.
            error_text: Text shown in error state.
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

        # Initialize word list
        self._action_words = DEFAULT_ACTION_WORDS.copy()
        if action_words is not None:
            if isinstance(action_words, list):
                self._action_words = action_words.copy()
            elif isinstance(action_words, dict):
                mode = action_words.get("mode", "replace")
                words = action_words.get("words", [])
                if mode == "replace":
                    self._action_words = words.copy()
                elif mode == "add":
                    self._action_words.extend(words)

        # Fallback to defaults if empty
        if not self._action_words:
            self._action_words = DEFAULT_ACTION_WORDS.copy()

        # Interval configuration
        interval = interval or {}
        self._min_interval = interval.get("min", 0.5)
        self._max_interval = interval.get("max", 3.0)

        # Shimmer configuration
        shimmer = shimmer or {}
        self._shimmer_enabled = shimmer.get("enabled", True)
        self._shimmer_width = shimmer.get("width", 3)
        self._shimmer_light_color = shimmer.get("light_color", "#FFA500")
        self._shimmer_speed = shimmer.get("speed", 1.0)
        self._reverse_shimmer = shimmer.get("reverse", False)

        # Other configuration
        self._suffix = suffix
        self._success_text = success_text
        self._error_text = error_text
        self._success_color: str | None = None
        self._error_color: str | None = None
        self.color = validate_hex_color(color)

        # Internal animation state
        self._current_word: str = ""
        self._used_words: list[str] = []
        self._last_word_change: float | None = None
        self._next_interval: float = 0.0
        self._shimmer_start_time: float | None = None
        self._animation_timer: TextualTimer | None = None
        self._pinned_text: bool = False
        self._manual_text_pending: bool = False
        self._restart_rotation_on_next_render: bool = False

        if text is not None:
            self._set_rotating_text(text, restart_rotation=False)

        if not visible:
            self.display = False

    # --- Properties ---

    @property
    def state(self) -> ComponentState:
        """Get the current component state."""
        return self._state

    @property
    def action_words(self) -> list[str]:
        """Get current action words list (returns copy)."""
        return self._action_words.copy()

    @action_words.setter
    def action_words(self, words: list[str]) -> None:
        """Replace entire word list.

        Args:
            words: New list of action words

        Raises:
            ValueError: If word list is empty
        """
        if not words:
            raise ValueError("Word list cannot be empty")
        self._action_words = words.copy()
        self._used_words.clear()

    @property
    def reverse_shimmer(self) -> bool:
        """Get shimmer direction."""
        return self._reverse_shimmer

    @reverse_shimmer.setter
    def reverse_shimmer(self, value: bool) -> None:
        """Set shimmer direction.

        Args:
            value: True for right-to-left, False for left-to-right
        """
        self._reverse_shimmer = value

    # --- Timer management ---

    def on_mount(self) -> None:
        """Start animation timer when widget is mounted."""
        self._animation_timer = self.set_interval(0.1, self._tick)
        if self._state != ComponentState.IN_PROGRESS:
            self._animation_timer.pause()

    def on_unmount(self) -> None:
        """Stop animation timer when widget is unmounted."""
        if self._animation_timer is not None:
            self._animation_timer.stop()
            self._animation_timer = None

    def _start_animation_timer(self) -> None:
        """Resume the animation refresh timer."""
        if self._animation_timer is not None:
            self._animation_timer.resume()
        else:
            self._animation_timer = self.set_interval(0.1, self._tick)

    def _stop_animation_timer(self) -> None:
        """Pause the animation timer."""
        if self._animation_timer is not None:
            self._animation_timer.pause()

    def _tick(self) -> None:
        """Refresh display on timer tick."""
        self.refresh()

    # --- Word rotation ---

    def _calculate_next_word_change(self, current_time: float) -> bool:
        """Determine if word should change based on elapsed time.

        Args:
            current_time: Current monotonic time in seconds

        Returns:
            True if word should change, False otherwise
        """
        if self._pinned_text:
            return False

        if self._last_word_change is None:
            self._last_word_change = current_time
            self._next_interval = random.uniform(self._min_interval, self._max_interval)  # nosec B311  # UI animation, not crypto
            return True

        elapsed = current_time - self._last_word_change
        if elapsed >= self._next_interval:
            self._last_word_change = current_time
            self._next_interval = random.uniform(self._min_interval, self._max_interval)  # nosec B311  # UI animation, not crypto
            return True
        return False

    def _select_new_word(self) -> None:
        """Select a new random word from the pool."""
        available = [w for w in self._action_words if w not in self._used_words]
        if not available:
            available = self._action_words
            self._used_words.clear()

        self._current_word = random.choice(available)  # nosec B311  # UI animation, not crypto

        self._used_words.append(self._current_word)
        if len(self._used_words) > 5:
            self._used_words.pop(0)

    def _clear_manual_text(self) -> None:
        """Clear the one-frame rotating text override state."""
        self._manual_text_pending = False
        self._restart_rotation_on_next_render = False

    def _set_rotating_text(self, text: str, *, restart_rotation: bool) -> None:
        """Show ``text`` once while keeping this widget in rotating mode."""
        self._current_word = text
        self._pinned_text = False
        self._manual_text_pending = True
        self._restart_rotation_on_next_render = restart_rotation
        self._shimmer_start_time = None

    def _set_pinned_text(self, text: str) -> None:
        """Pin ``text`` until another rotation-related API clears the pin."""
        self._current_word = text
        self._pinned_text = True
        self._clear_manual_text()
        self._shimmer_start_time = None

    # --- Shimmer effect ---

    def _apply_shimmer(self, text: str, current_time: float) -> Text:
        """Apply shimmer effect to text.

        Args:
            text: Text to apply shimmer to
            current_time: Current monotonic time for animation

        Returns:
            Rich Text object with shimmer effect applied
        """
        if self._shimmer_start_time is None:
            self._shimmer_start_time = current_time

        elapsed = current_time - self._shimmer_start_time
        total_positions = len(text) + self._shimmer_width * 2

        if self._reverse_shimmer:
            position = total_positions - int(elapsed * self._shimmer_speed * 10) % total_positions
        else:
            position = int(elapsed * self._shimmer_speed * 10) % total_positions

        result = Text()
        shimmer_start = position - self._shimmer_width

        for i, char in enumerate(text):
            if shimmer_start <= i < shimmer_start + self._shimmer_width:
                result.append(char, style=Style(color=self._shimmer_light_color))
            else:
                result.append(char, style=Style(color=self.color))

        return result

    # --- Rendering ---

    def render(self) -> Text:
        """Render the message widget."""
        if self._state == ComponentState.SUCCESS:
            return Text(self._success_text, style=self._success_color or "")
        elif self._state == ComponentState.ERROR:
            return Text(self._error_text, style=self._error_color or "")
        else:
            current_time = monotonic()

            # set_message() updates the current rotating word for one render only.
            if self._manual_text_pending:
                if self._restart_rotation_on_next_render:
                    self._last_word_change = current_time
                    self._next_interval = random.uniform(self._min_interval, self._max_interval)  # nosec B311  # UI animation, not crypto
                self._clear_manual_text()
            elif self._calculate_next_word_change(current_time):
                self._select_new_word()
                self._shimmer_start_time = None

            display_text = self._current_word + self._suffix

            if self._shimmer_enabled:
                return self._apply_shimmer(display_text, current_time)
            else:
                return Text(display_text, style=self.color)

    # --- Reactive watchers ---

    def validate_color(self, color: str) -> str:
        """Validate color before setting."""
        return validate_hex_color(color)

    def watch_color(self) -> None:
        """React to color changes."""
        self.refresh()

    def watch__state(self, new_state: ComponentState) -> None:
        """React to state changes."""
        if new_state == ComponentState.IN_PROGRESS:
            self.remove_class("success", "error")
            if self.is_mounted:
                self._start_animation_timer()
        elif new_state == ComponentState.SUCCESS:
            self._stop_animation_timer()
            self.remove_class("error")
            self.add_class("success")
        elif new_state == ComponentState.ERROR:
            self._stop_animation_timer()
            self.remove_class("success")
            self.add_class("error")
        self.refresh()

    # --- Public methods ---

    def extend_action_words(self, words: list[str]) -> None:
        """Add words to existing list.

        Args:
            words: List of words to add
        """
        self._action_words.extend(words)

    def configure(
        self,
        *,
        text: str | None = None,
        pinned_text: str | None = None,
        restart_rotation: bool = False,
        trigger_new: bool = False,
        reverse_shimmer: bool | None = None,
    ) -> None:
        """Update component state.

        Args:
            text: Update the current rotating message text without pinning it.
            pinned_text: Pin a message so it remains visible until rotation resumes.
            restart_rotation: Restart the rotation timer after showing ``text`` once.
            trigger_new: Force selection of new random word
            reverse_shimmer: Change shimmer direction
        """
        if text is not None:
            self._set_rotating_text(text, restart_rotation=restart_rotation)

        if pinned_text is not None:
            self._set_pinned_text(pinned_text)

        if trigger_new:
            self._clear_manual_text()
            self._pinned_text = False
            self._select_new_word()
            self._shimmer_start_time = None

        if reverse_shimmer is not None:
            self._reverse_shimmer = reverse_shimmer

        self.refresh()

    # --- State management ---

    def success(self, text: str | None = None) -> None:
        """Transition to success state.

        Args:
            text: Optional custom success text.
        """
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
        if not self._state.can_transition_to(ComponentState.ERROR):
            return
        if text is not None:
            self._error_text = text
        self._state = ComponentState.ERROR

    def reset(self) -> None:
        """Reset to in_progress state."""
        self._current_word = ""
        self._last_word_change = None
        self._shimmer_start_time = None
        self._used_words.clear()
        self._pinned_text = False
        self._clear_manual_text()
        self._state = ComponentState.IN_PROGRESS

    def configure_state(self, state: ComponentState, *, color: str | None = None) -> None:
        """Update terminal-state color overrides."""
        if color is not None:
            color = validate_hex_color(color)
        if state == ComponentState.SUCCESS:
            self._success_color = color
        elif state == ComponentState.ERROR:
            self._error_color = color
        self.refresh()

    # --- Visibility methods ---

    def show(self) -> None:
        """Show the message widget."""
        self.display = True

    def hide(self) -> None:
        """Hide the message widget."""
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

    # --- Factory ---

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> MessageWidget:
        """Create from configuration dictionary.

        Args:
            config: Configuration dictionary with optional keys:
                - action_words: Word list configuration
                - interval: Time range for word changes
                - color: Hex color code
                - shimmer: Shimmer configuration
                - suffix: Suffix to append to words
                - success_text: Success state text
                - error_text: Error state text
                - visible: Whether visible

        Returns:
            A new MessageWidget instance.
        """
        return cls(
            action_words=config.get("action_words"),
            interval=config.get("interval"),
            color=config.get("color", "#D97706"),
            shimmer=config.get("shimmer"),
            suffix=config.get("suffix", "…"),
            text=config.get("text"),
            success_text=config.get("success_text", "Complete!"),
            error_text=config.get("error_text", "Failed"),
            visible=config.get("visible", True),
        )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"MessageWidget(words={len(self._action_words)}, "
            f"state={self._state.name}, shimmer={self._shimmer_enabled})"
        )
