"""Message component for Rich console output.

Displays rotating action words with configurable shimmer effects to indicate
activity. Supports word list management, directional shimmer, and state transitions.
"""

from __future__ import annotations

import random
import time
from typing import Any

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.style import Style
from rich.text import Text

from ...core.color import (
    COLOR_DEFAULT,
    COLOR_ERROR,
    COLOR_SHIMMER,
    COLOR_SUCCESS,
    validate_hex_color,
)
from ...core.states import ComponentState

# Message component defaults
WORD_HISTORY_SIZE = 5
DEFAULT_MIN_INTERVAL = 0.5
DEFAULT_MAX_INTERVAL = 3.0
DEFAULT_SHIMMER_WIDTH = 3
DEFAULT_SHIMMER_SPEED = 1.0
DEFAULT_SUCCESS_TEXT = "Complete!"
DEFAULT_ERROR_TEXT = "Failed"

# Default action words list (87 words from PRD)
DEFAULT_ACTION_WORDS = [
    "Accomplishing",
    "Actioning",
    "Actualizing",
    "Baking",
    "Booping",
    "Brewing",
    "Calculating",
    "Cerebrating",
    "Channelling",
    "Churning",
    "Clauding",
    "Coalescing",
    "Cogitating",
    "Computing",
    "Combobulating",
    "Concocting",
    "Conjuring",
    "Considering",
    "Contemplating",
    "Cooking",
    "Crafting",
    "Creating",
    "Crunching",
    "Decoding",
    "Decrypting",
    "Deliberating",
    "Digesting",
    "Digitalizing",
    "Discovering",
    "Divining",
    "Dreaming",
    "Elucidating",
    "Encoding",
    "Engineering",
    "Envisioning",
    "Evaluating",
    "Evolving",
    "Examining",
    "Executing",
    "Exploring",
    "Fabricating",
    "Factoring",
    "Figuring",
    "Formulating",
    "Generating",
    "Grinding",
    "Hatching",
    "Ideating",
    "Imagining",
    "Implementing",
    "Improvising",
    "Innovating",
    "Integrating",
    "Interpreting",
    "Investigating",
    "Iterating",
    "Learning",
    "Manifesting",
    "Mapping",
    "Modeling",
    "Musing",
    "Noodling",
    "Orchestrating",
    "Organizing",
    "Perceiving",
    "Percolating",
    "Pondering",
    "Postulating",
    "Processing",
    "Prototyping",
    "Puzzling",
    "Reasoning",
    "Refining",
    "Reflecting",
    "Resolving",
    "Ruminating",
    "Scheming",
    "Sculpting",
    "Sketching",
    "Solving",
    "Spinning",
    "Structuring",
    "Synthesizing",
    "Thinking",
    "Transmuting",
    "Unfurling",
    "Unravelling",
    "Vibing",
    "Wandering",
    "Whirring",
    "Wibbling",
    "Wizarding",
    "Working",
    "Wrangling",
]


class MessageComponent:
    """Animated message component with shimmer effects for Rich console.

    A component that displays rotating action words with optional shimmer
    animation. Supports word list management, directional control, and
    state transitions.

    Attributes:
        action_words: List of words to rotate through
        interval: Time range for word changes
        color: Base color for text
        shimmer: Shimmer effect configuration
        suffix: Suffix to append to words
        visible: Whether the component should be rendered
        state: Current component state

    Example:
        >>> from rich.console import Console
        >>> from rich.live import Live
        >>> console = Console()
        >>> message = MessageComponent(
        ...     action_words=["Processing", "Analyzing"],
        ...     shimmer={"enabled": True, "width": 3}
        ... )
        >>> with Live(message, console=console, refresh_per_second=20):
        ...     time.sleep(5)
        ...     message.success("Complete!")
    """

    def __init__(
        self,
        action_words: list[str] | dict[str, Any] | None = None,
        interval: dict[str, float] | None = None,
        color: str = COLOR_DEFAULT,
        shimmer: dict[str, Any] | None = None,
        suffix: str = "…",
        visible: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize the MessageComponent.

        Args:
            action_words: Word list configuration. Can be:
                - List of words to replace default list
                - Dict with "mode" ("add"/"replace") and "words"
                - None to use default list
            interval: Time range for word changes {"min": 0.5, "max": 3.0}
            color: Base hex color for text. Defaults to "#D97706".
            shimmer: Shimmer configuration dict with keys:
                - enabled (bool): Whether shimmer is active
                - width (int): Width of shimmer effect
                - light_color (str): Hex color for shimmer
                - speed (float): Shimmer movement speed
                - reverse (bool): Direction of shimmer
            suffix: Suffix to append to words. Defaults to "…".
            visible: Whether to render the component. Defaults to True.
            **kwargs: Additional keyword arguments (reserved for future use).
        """
        # Initialize word list
        self._action_words = DEFAULT_ACTION_WORDS.copy()
        if action_words is not None:
            if isinstance(action_words, list):
                # Simple array syntax - replace mode
                self._action_words = action_words.copy()
            elif isinstance(action_words, dict):
                # Object syntax with mode control
                mode = action_words.get("mode", "replace")
                words = action_words.get("words", [])
                if mode == "replace":
                    self._action_words = words.copy()
                elif mode == "add":
                    self._action_words.extend(words)

        # Validate word list not empty
        if not self._action_words:
            self._action_words = DEFAULT_ACTION_WORDS.copy()

        # Set interval configuration
        interval = interval or {}
        self.min_interval = interval.get("min", DEFAULT_MIN_INTERVAL)
        self.max_interval = interval.get("max", DEFAULT_MAX_INTERVAL)

        # Set shimmer configuration
        shimmer = shimmer or {}
        self.shimmer_enabled = shimmer.get("enabled", True)
        self.shimmer_width = shimmer.get("width", DEFAULT_SHIMMER_WIDTH)
        self.shimmer_light_color = shimmer.get("light_color", COLOR_SHIMMER)
        self.shimmer_speed = shimmer.get("speed", DEFAULT_SHIMMER_SPEED)
        self._reverse_shimmer = shimmer.get("reverse", False)
        if self.shimmer_width <= 0:
            raise ValueError("shimmer width must be positive")
        if self.shimmer_speed <= 0:
            raise ValueError("shimmer speed must be positive")

        # Other configuration
        validate_hex_color(color)
        self.color = color
        self.suffix = suffix
        self.visible = visible

        # Internal state management
        self._state = ComponentState.IN_PROGRESS
        self._current_word = ""
        self._static_text = ""
        self._last_word_change: float | None = None
        self._next_interval: float = 0.0
        self._shimmer_start_time: float | None = None
        self._used_words: list[str] = []  # Track recent words to avoid repeats
        self._cached_terminal_render: tuple[tuple, Text] | None = None

    @property
    def state(self) -> ComponentState:
        """Get the current component state."""
        return self._state

    @property
    def action_words(self) -> list[str]:
        """Get current action words list."""
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
        self._used_words.clear()  # Reset history

    def extend_action_words(self, words: list[str]) -> None:
        """Add words to existing list.

        Args:
            words: List of words to add
        """
        self._action_words.extend(words)

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

    def configure(
        self,
        *,
        text: str | None = None,
        trigger_new: bool = False,
        reverse_shimmer: bool | None = None,
    ) -> None:
        """Configure component properties.

        Args:
            text: Custom text to display (overrides word rotation)
            trigger_new: Force selection of new random word
            reverse_shimmer: Change shimmer direction
        """
        if text is not None:
            self._current_word = text
            self._last_word_change = None  # Reset timer
            self._shimmer_start_time = None  # Reset shimmer

        if trigger_new:
            self._select_new_word()
            self._last_word_change = None  # Reset timer
            self._shimmer_start_time = None  # Reset shimmer

        if reverse_shimmer is not None:
            self._reverse_shimmer = reverse_shimmer

    # Backward-compatible alias
    update = configure

    def success(self, text: str | None = None) -> None:
        """Transition to success state with custom text.

        Args:
            text: Text to display in success state
        """
        if not self._state.can_transition_to(ComponentState.SUCCESS):
            return
        self._state = ComponentState.SUCCESS
        self._static_text = text if text is not None else DEFAULT_SUCCESS_TEXT

    def error(self, text: str | None = None) -> None:
        """Transition to error state with custom text.

        Args:
            text: Text to display in error state
        """
        if not self._state.can_transition_to(ComponentState.ERROR):
            return
        self._state = ComponentState.ERROR
        self._static_text = text if text is not None else DEFAULT_ERROR_TEXT

    def reset(self) -> None:
        """Reset to in_progress state."""
        self._state = ComponentState.IN_PROGRESS
        self._current_word = ""
        self._last_word_change = None
        self._shimmer_start_time = None
        self._used_words.clear()
        self._cached_terminal_render = None

    def _select_new_word(self) -> None:
        """Select a new random word from the pool."""
        if not self._action_words:
            return
        # Get available words (exclude recent ones)
        available = [w for w in self._action_words if w not in self._used_words]
        if not available:
            # If all words were recently used, reset history
            available = self._action_words
            self._used_words.clear()

        self._current_word = random.choice(available)

        # Track in history (keep last 5)
        self._used_words.append(self._current_word)
        if len(self._used_words) > WORD_HISTORY_SIZE:
            self._used_words.pop(0)

    def _calculate_next_word_change(self, current_time: float) -> bool:
        """Determine if word should change based on elapsed time.

        Args:
            current_time: Current time in seconds

        Returns:
            True if word should change, False otherwise
        """
        if self._last_word_change is None:
            self._last_word_change = current_time
            self._next_interval = random.uniform(self.min_interval, self.max_interval)
            return True

        elapsed = current_time - self._last_word_change
        if elapsed >= self._next_interval:
            self._last_word_change = current_time
            self._next_interval = random.uniform(self.min_interval, self.max_interval)
            return True
        return False

    def _apply_shimmer(self, text: str, current_time: float) -> Text:
        """Apply shimmer effect to text using Rich Text spans.

        Args:
            text: Text to apply shimmer to
            current_time: Current time for animation

        Returns:
            Rich Text object with shimmer effect applied
        """
        if self._shimmer_start_time is None:
            self._shimmer_start_time = current_time

        # Calculate shimmer position based on time
        elapsed = current_time - self._shimmer_start_time
        total_positions = len(text) + self.shimmer_width * 2

        if self._reverse_shimmer:
            position = total_positions - int(elapsed * self.shimmer_speed * 10) % total_positions
        else:
            position = int(elapsed * self.shimmer_speed * 10) % total_positions

        # Build styled text with shimmer
        result = Text()
        shimmer_start = position - self.shimmer_width

        for i, char in enumerate(text):
            if shimmer_start <= i < shimmer_start + self.shimmer_width:
                # Apply light color for shimmer effect
                result.append(char, style=Style(color=self.shimmer_light_color))
            else:
                # Apply base color
                result.append(char, style=Style(color=self.color))

        return result

    def _render_current_state(self, current_time: float) -> Text:
        """Render the component based on current state.

        Args:
            current_time: Current time for animations

        Returns:
            Rich Text object to render
        """
        if self._state == ComponentState.SUCCESS:
            # Success state - static text with success color
            return Text(self._static_text, style=Style(color=COLOR_SUCCESS))
        elif self._state == ComponentState.ERROR:
            # Error state - static text with error color
            return Text(self._static_text, style=Style(color=COLOR_ERROR))
        else:
            # In progress state - rotating words with optional shimmer
            # Check if word needs to change
            if self._calculate_next_word_change(current_time):
                self._select_new_word()
                self._shimmer_start_time = None  # Reset shimmer on word change

            # Build display text
            display_text = self._current_word + self.suffix

            # Apply shimmer if enabled
            if self.shimmer_enabled:
                return self._apply_shimmer(display_text, current_time)
            else:
                return Text(display_text, style=Style(color=self.color))

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Render the message component for Rich console.

        Args:
            console: The Rich console instance
            options: Console rendering options

        Yields:
            Rich Text object with styled message
        """
        if not self.visible:
            return

        current_time = console.get_time() if hasattr(console, "get_time") else time.time()

        # Cache terminal states for performance
        if self._state in (ComponentState.SUCCESS, ComponentState.ERROR):
            cache_key = (self._state, self._static_text)
            if self._cached_terminal_render and self._cached_terminal_render[0] == cache_key:
                yield self._cached_terminal_render[1]
                return
            rendered = self._render_current_state(current_time)
            self._cached_terminal_render = (cache_key, rendered)
            yield rendered
            return

        yield self._render_current_state(current_time)

    def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement:
        """Measure the message width for layout.

        Args:
            console: The Rich console instance
            options: Console rendering options

        Returns:
            Measurement of the component's width
        """
        if not self.visible:
            return Measurement(0, 0)

        # Estimate based on longest word + suffix
        if self._state != ComponentState.IN_PROGRESS:
            text = Text(self._static_text)
        else:
            longest_word = max(self._action_words, key=len) if self._action_words else ""
            text = Text(longest_word + self.suffix)

        return Measurement.get(console, options, text)

    def __repr__(self) -> str:
        """Return string representation of the component."""
        return (
            f"MessageComponent(words={len(self._action_words)}, "
            f"state={self._state.name}, shimmer={self.shimmer_enabled})"
        )

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> MessageComponent:
        """Create a MessageComponent from a configuration dictionary.

        Args:
            config: Configuration dictionary

        Returns:
            A new MessageComponent instance
        """
        return cls(
            action_words=config.get("action_words"),
            interval=config.get("interval"),
            color=config.get("color", COLOR_DEFAULT),
            shimmer=config.get("shimmer"),
            suffix=config.get("suffix", "…"),
            visible=config.get("visible", True),
        )
