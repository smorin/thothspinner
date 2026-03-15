"""Unit tests for MessageComponent."""

from unittest.mock import MagicMock

import pytest
from rich.console import Console
from rich.text import Text

from thothspinner.rich.components.message import (
    DEFAULT_ACTION_WORDS,
    MessageComponent,
)


class TestMessageComponentInitialization:
    """Test MessageComponent initialization."""

    def test_default_initialization(self):
        """Test component initializes with default values."""
        message = MessageComponent()

        assert message.action_words == DEFAULT_ACTION_WORDS
        assert message.min_interval == 0.5
        assert message.max_interval == 3.0
        assert message.color == "#D97706"
        assert message.suffix == "…"
        assert message.visible is True
        assert message.shimmer_enabled is True
        assert message.shimmer_width == 3
        assert message.shimmer_light_color == "#FFA500"
        assert message.shimmer_speed == 1.0
        assert message.reverse_shimmer is False
        assert message.state == "in_progress"

    def test_custom_word_list_array_syntax(self):
        """Test initializing with custom word list using array syntax."""
        custom_words = ["Testing", "Processing", "Loading"]
        message = MessageComponent(action_words=custom_words)

        assert message.action_words == custom_words
        assert len(message.action_words) == 3

    def test_custom_word_list_replace_mode(self):
        """Test initializing with replace mode."""
        config = {"mode": "replace", "words": ["Custom1", "Custom2"]}
        message = MessageComponent(action_words=config)

        assert message.action_words == ["Custom1", "Custom2"]
        assert "Accomplishing" not in message.action_words

    def test_custom_word_list_add_mode(self):
        """Test initializing with add mode."""
        config = {"mode": "add", "words": ["Custom1", "Custom2"]}
        message = MessageComponent(action_words=config)

        expected_count = len(DEFAULT_ACTION_WORDS) + 2
        assert len(message.action_words) == expected_count
        assert "Custom1" in message.action_words
        assert "Custom2" in message.action_words
        assert "Accomplishing" in message.action_words

    def test_empty_word_list_fallback(self):
        """Test that empty word list falls back to defaults."""
        message = MessageComponent(action_words=[])
        assert message.action_words == DEFAULT_ACTION_WORDS

    def test_custom_interval_configuration(self):
        """Test custom interval configuration."""
        interval = {"min": 1.0, "max": 5.0}
        message = MessageComponent(interval=interval)

        assert message.min_interval == 1.0
        assert message.max_interval == 5.0

    def test_shimmer_configuration(self):
        """Test shimmer configuration."""
        shimmer_config = {
            "enabled": False,
            "width": 5,
            "light_color": "#FFFFFF",
            "speed": 2.0,
            "reverse": True,
        }
        message = MessageComponent(shimmer=shimmer_config)

        assert message.shimmer_enabled is False
        assert message.shimmer_width == 5
        assert message.shimmer_light_color == "#FFFFFF"
        assert message.shimmer_speed == 2.0
        assert message.reverse_shimmer is True

    def test_from_config_factory(self):
        """Test creating component from config dictionary."""
        config = {
            "action_words": ["Test1", "Test2"],
            "interval": {"min": 0.2, "max": 1.0},
            "color": "#FF0000",
            "shimmer": {"enabled": True, "width": 4},
            "suffix": "!!!",
            "visible": False,
        }
        message = MessageComponent.from_config(config)

        assert message.action_words == ["Test1", "Test2"]
        assert message.min_interval == 0.2
        assert message.max_interval == 1.0
        assert message.color == "#FF0000"
        assert message.suffix == "!!!"
        assert message.visible is False


class TestActionWordsManagement:
    """Test action words management features."""

    def test_action_words_property_getter(self):
        """Test action_words property returns copy."""
        message = MessageComponent(action_words=["Word1", "Word2"])
        words = message.action_words
        words.append("Word3")

        # Original should be unchanged
        assert len(message.action_words) == 2

    def test_action_words_property_setter(self):
        """Test action_words setter replaces word list."""
        message = MessageComponent()
        new_words = ["New1", "New2", "New3"]
        message.action_words = new_words

        assert message.action_words == new_words
        assert len(message.action_words) == 3

    def test_action_words_setter_with_empty_list_raises(self):
        """Test that setting empty word list raises error."""
        message = MessageComponent()

        with pytest.raises(ValueError, match="Word list cannot be empty"):
            message.action_words = []

    def test_extend_action_words(self):
        """Test extending action words list."""
        message = MessageComponent(action_words=["Word1", "Word2"])
        message.extend_action_words(["Word3", "Word4"])

        assert len(message.action_words) == 4
        assert "Word3" in message.action_words
        assert "Word4" in message.action_words

    def test_word_list_immutability(self):
        """Test that word lists are properly copied."""
        original = ["Word1", "Word2"]
        message = MessageComponent(action_words=original)

        # Modify original
        original.append("Word3")

        # Component should have copy
        assert len(message.action_words) == 2


class TestWordRotation:
    """Test word rotation logic."""

    def test_word_selection_on_first_render(self):
        """Test that a word is selected on first render."""
        message = MessageComponent(action_words=["TestWord"])

        # Simulate time calculation
        assert message._calculate_next_word_change(0.0) is True
        message._select_new_word()

        assert message._current_word == "TestWord"

    def test_word_rotation_timing(self):
        """Test word changes at correct intervals."""
        message = MessageComponent(
            action_words=["Word1", "Word2"],
            interval={"min": 0.5, "max": 0.5},  # Fixed interval for testing
        )

        # First call should trigger change
        assert message._calculate_next_word_change(0.0) is True

        # Before interval, should not change
        assert message._calculate_next_word_change(0.3) is False

        # After interval, should change
        assert message._calculate_next_word_change(0.6) is True

    def test_word_history_tracking(self):
        """Test that recent words are tracked to avoid repeats."""
        message = MessageComponent(action_words=["Word1", "Word2", "Word3"])

        # Select words and track history
        for _ in range(3):
            message._select_new_word()

        # Check history is bounded
        assert len(message._used_words) <= 5

    def test_random_interval_range(self):
        """Test that intervals are within specified range."""
        message = MessageComponent(interval={"min": 1.0, "max": 3.0})

        # Trigger calculation to set interval
        message._calculate_next_word_change(0.0)

        assert 1.0 <= message._next_interval <= 3.0

    def test_configure_with_custom_text(self):
        """Test configure method with custom text."""
        message = MessageComponent()
        message.configure(text="CustomText")

        assert message._current_word == "CustomText"
        assert message._last_word_change is None  # Timer reset

    def test_configure_trigger_new_word(self):
        """Test configure method to trigger new word."""
        message = MessageComponent(action_words=["Word1", "Word2"])
        message.configure(trigger_new=True)

        assert message._current_word in ["Word1", "Word2"]
        assert message._last_word_change is None  # Timer reset


class TestShimmerEffect:
    """Test shimmer effect implementation."""

    def test_shimmer_position_calculation(self):
        """Test shimmer position changes over time."""
        message = MessageComponent(shimmer={"enabled": True, "width": 3})

        text = "TestWord"
        # Apply shimmer at different times
        result1 = message._apply_shimmer(text, 0.0)
        result2 = message._apply_shimmer(text, 1.0)

        # Results should be Text objects
        assert isinstance(result1, Text)
        assert isinstance(result2, Text)

    def test_shimmer_direction_left_to_right(self):
        """Test left-to-right shimmer direction."""
        message = MessageComponent(shimmer={"enabled": True, "reverse": False})

        assert message.reverse_shimmer is False

    def test_shimmer_direction_right_to_left(self):
        """Test right-to-left shimmer direction."""
        message = MessageComponent(shimmer={"enabled": True, "reverse": True})

        assert message.reverse_shimmer is True

    def test_shimmer_direction_toggle(self):
        """Test toggling shimmer direction."""
        message = MessageComponent()

        # Test property setter
        message.reverse_shimmer = True
        assert message.reverse_shimmer is True

        message.reverse_shimmer = False
        assert message.reverse_shimmer is False

    def test_shimmer_update_via_update_method(self):
        """Test changing shimmer direction via update."""
        message = MessageComponent()

        message.configure(reverse_shimmer=True)
        assert message.reverse_shimmer is True

        message.configure(reverse_shimmer=False)
        assert message.reverse_shimmer is False

    def test_shimmer_reset_on_word_change(self):
        """Test that shimmer resets when word changes."""
        message = MessageComponent()
        message._shimmer_start_time = 10.0

        message.configure(text="NewWord")
        assert message._shimmer_start_time is None

    def test_shimmer_width_configuration(self):
        """Test shimmer width affects rendering."""
        message = MessageComponent(shimmer={"width": 5})

        assert message.shimmer_width == 5

    def test_shimmer_disabled(self):
        """Test rendering without shimmer."""
        message = MessageComponent(shimmer={"enabled": False})

        result = message._render_current_state(0.0)
        assert isinstance(result, Text)
        # When shimmer is disabled, should use base color
        # Check that color is applied (Rich converts to Color object)
        assert result.style is not None
        assert result.style.color is not None


class TestStateManagement:
    """Test component state management."""

    def test_initial_state(self):
        """Test initial state is in_progress."""
        message = MessageComponent()
        assert message.state == "in_progress"

    def test_success_state_transition(self):
        """Test transition to success state."""
        message = MessageComponent()
        message.success("Task completed!")

        assert message.state == "success"
        assert message._static_text == "Task completed!"

    def test_error_state_transition(self):
        """Test transition to error state."""
        message = MessageComponent()
        message.error("Task failed!")

        assert message.state == "error"
        assert message._static_text == "Task failed!"

    def test_invalid_state_transitions(self):
        """Test that invalid transitions are ignored."""
        message = MessageComponent()

        # Transition to success
        message.success()

        # Try to transition directly to error (should be ignored)
        message.error()
        assert message.state == "success"

    def test_reset_state(self):
        """Test resetting to in_progress state."""
        message = MessageComponent()
        message.success()
        message.reset()

        assert message.state == "in_progress"
        assert message._current_word == ""
        assert message._last_word_change is None
        assert len(message._used_words) == 0

    def test_state_affects_rendering(self):
        """Test that state affects what is rendered."""
        message = MessageComponent()

        # In progress state
        result1 = message._render_current_state(0.0)
        assert isinstance(result1, Text)

        # Success state
        message.success("Done!")
        result2 = message._render_current_state(0.0)
        assert isinstance(result2, Text)
        assert result2.plain == "Done!"

        # Error state
        message.reset()
        message.error("Failed!")
        result3 = message._render_current_state(0.0)
        assert isinstance(result3, Text)
        assert result3.plain == "Failed!"

    def test_success_with_default_text(self):
        """Test success with default text."""
        message = MessageComponent()
        message.success()

        assert message._static_text == "Complete!"

    def test_error_with_default_text(self):
        """Test error with default text."""
        message = MessageComponent()
        message.error()

        assert message._static_text == "Failed"


class TestRichIntegration:
    """Test Rich console integration."""

    def test_rich_console_protocol(self):
        """Test __rich_console__ implementation."""
        message = MessageComponent(action_words=["Test"])
        console = Console()

        # Mock get_time
        console.get_time = MagicMock(return_value=0.0)

        # Should yield Text objects
        options = MagicMock()
        result = list(message.__rich_console__(console, options))

        if result:  # Component is visible
            assert all(isinstance(item, Text) for item in result)

    def test_rich_measure_protocol(self):
        """Test __rich_measure__ implementation."""
        message = MessageComponent()
        console = Console()
        options = MagicMock()
        options.max_width = 80

        measurement = message.__rich_measure__(console, options)

        assert measurement.minimum >= 0
        assert measurement.maximum <= options.max_width

    def test_invisible_component_rendering(self):
        """Test that invisible component doesn't render."""
        message = MessageComponent(visible=False)
        console = Console()
        options = MagicMock()

        result = list(message.__rich_console__(console, options))
        assert len(result) == 0

    def test_invisible_component_measurement(self):
        """Test that invisible component has zero width."""
        message = MessageComponent(visible=False)
        console = Console()
        options = MagicMock()

        measurement = message.__rich_measure__(console, options)
        assert measurement.minimum == 0
        assert measurement.maximum == 0

    def test_repr_method(self):
        """Test string representation."""
        message = MessageComponent()
        repr_str = repr(message)

        assert "MessageComponent" in repr_str
        assert "words=" in repr_str
        assert "state=" in repr_str
        assert "shimmer=" in repr_str


class TestPerformanceOptimization:
    """Test performance optimizations."""

    def test_static_state_caching(self):
        """Test that static states are cached."""
        message = MessageComponent()
        console = Console()
        console.get_time = MagicMock(return_value=0.0)
        options = MagicMock()

        # Transition to success
        message.success("Cached")

        # First render
        list(message.__rich_console__(console, options))

        # Second render should use cache
        list(message.__rich_console__(console, options))

        # Cache should be populated
        assert message._cached_terminal_render is not None

    def test_in_progress_not_cached(self):
        """Test that in_progress state is not cached."""
        message = MessageComponent()
        console = Console()
        console.get_time = MagicMock(return_value=0.0)
        options = MagicMock()

        # Render in progress state
        list(message.__rich_console__(console, options))

        # Cache should be empty for animated state
        assert message._cached_terminal_render is None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_very_short_words(self):
        """Test handling of single character words."""
        message = MessageComponent(action_words=["A", "B", "C"])

        result = message._render_current_state(0.0)
        assert isinstance(result, Text)
        assert len(result.plain) >= 2  # At least "A…"

    def test_very_long_words(self):
        """Test handling of very long words."""
        long_word = "A" * 50
        message = MessageComponent(action_words=[long_word])

        result = message._render_current_state(0.0)
        assert isinstance(result, Text)
        assert long_word in result.plain

    def test_shimmer_wider_than_text(self):
        """Test shimmer effect when width exceeds text length."""
        message = MessageComponent(action_words=["Hi"], shimmer={"enabled": True, "width": 10})

        result = message._apply_shimmer("Hi…", 0.0)
        assert isinstance(result, Text)

    def test_rapid_updates(self):
        """Test rapid successive updates."""
        message = MessageComponent()

        for i in range(10):
            message.configure(text=f"Update{i}")
            assert message._current_word == f"Update{i}"

    def test_empty_action_words_recovery(self):
        """Test recovery when all words are in history."""
        message = MessageComponent(action_words=["Only"])

        # Fill history
        for _ in range(10):
            message._select_new_word()

        # Should still work
        assert message._current_word == "Only"
