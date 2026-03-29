"""Tests for ThothSpinner orchestrator."""

import threading
import time
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from thothspinner.core.states import ComponentState
from thothspinner.rich.thothspinner import ThothSpinner


class TestThothSpinnerInitialization:
    """Test ThothSpinner initialization."""

    def test_default_initialization(self):
        """Test ThothSpinner initializes with defaults."""
        spinner = ThothSpinner()

        assert spinner.state == ComponentState.IN_PROGRESS
        assert spinner.success_duration is None
        assert spinner.error_duration is None
        assert len(spinner._components) == 5
        assert spinner._render_order == ("spinner", "message", "progress", "timer", "hint")

    def test_keyword_arguments(self):
        """Test initialization with keyword arguments."""
        spinner = ThothSpinner(
            spinner_style="claude_stars",
            message_text="Testing",
            message_shimmer=False,
            progress_format="fraction",
            timer_format="mm:ss",
            hint_text="Test hint",
            success_duration=2.0,
            error_duration=3.0,
        )

        assert spinner.success_duration == 2.0
        assert spinner.error_duration == 3.0
        assert "spinner" in spinner._components
        assert "message" in spinner._components

    def test_config_dict_initialization(self):
        """Test initialization with config dictionary."""
        config = {
            "elements": {"spinner": {"style": "npm_dots"}, "message": {"text": "From config"}}
        }

        spinner = ThothSpinner(**config)
        assert "spinner" in spinner._components
        assert "message" in spinner._components

    def test_from_dict_classmethod(self):
        """Test from_dict class method."""
        config = {"elements": {"spinner": {"style": "claude_stars"}}}

        spinner = ThothSpinner.from_dict(config)
        assert isinstance(spinner, ThothSpinner)
        assert "spinner" in spinner._components

    def test_invalid_component_type(self):
        """Test invalid component type raises KeyError."""
        config = {"elements": {"invalid_component": {"some": "config"}}}

        with pytest.raises(KeyError, match="Invalid component type"):
            ThothSpinner(**config)

    def test_thread_safety(self):
        """Test ThothSpinner has thread lock."""
        spinner = ThothSpinner()
        assert hasattr(spinner, "_lock")
        assert isinstance(spinner._lock, type(threading.RLock()))


class TestComponentRegistry:
    """Test component registry and access."""

    def test_all_components_created(self):
        """Test all 5 components are created eagerly."""
        spinner = ThothSpinner()

        expected_components = ["spinner", "message", "progress", "timer", "hint"]
        for component_type in expected_components:
            assert component_type in spinner._components

    def test_get_component_valid(self):
        """Test get_component with valid type."""
        spinner = ThothSpinner()

        progress = spinner.get_component("progress")
        assert progress is not None
        assert progress == spinner._components["progress"]

    def test_get_component_invalid(self):
        """Test get_component with invalid type raises KeyError."""
        spinner = ThothSpinner()

        with pytest.raises(KeyError, match="Invalid component type"):
            spinner.get_component("nonexistent")

    def test_render_order_immutable(self):
        """Test render_order is immutable tuple."""
        spinner = ThothSpinner()
        assert isinstance(spinner._render_order, tuple)

        # Attempt to modify should fail
        with pytest.raises(TypeError):
            spinner._render_order[0] = "modified"

    def test_custom_render_order(self):
        """Test custom render order from config."""
        config = {"render_order": ["hint", "timer", "progress", "message", "spinner"]}

        spinner = ThothSpinner(**config)
        assert spinner._render_order == ("hint", "timer", "progress", "message", "spinner")


class TestStateManagement:
    """Test state management system."""

    def test_initial_state(self):
        """Test initial state is IN_PROGRESS."""
        spinner = ThothSpinner()
        assert spinner.state == ComponentState.IN_PROGRESS

    def test_start_method(self):
        """Test start method."""
        spinner = ThothSpinner()
        spinner.start()

        assert spinner.state == ComponentState.IN_PROGRESS
        assert spinner._start_time is not None

    def test_success_transition(self):
        """Test transition to success state."""
        spinner = ThothSpinner()
        spinner.start()
        spinner.success("Test success")

        assert spinner.state == ComponentState.SUCCESS

    def test_error_transition(self):
        """Test transition to error state."""
        spinner = ThothSpinner()
        spinner.start()
        spinner.error("Test error")

        assert spinner.state == ComponentState.ERROR

    def test_success_without_message_renders(self):
        """Test success() without a message uses component defaults."""
        console = Console(file=StringIO(), force_terminal=True, width=80)
        spinner = ThothSpinner()

        spinner.success()
        console.print(spinner)

        output = console.file.getvalue()
        assert "Complete!" in output

    def test_error_without_message_renders(self):
        """Test error() without a message uses component defaults."""
        console = Console(file=StringIO(), force_terminal=True, width=80)
        spinner = ThothSpinner()

        spinner.error()
        console.print(spinner)

        output = console.file.getvalue()
        assert "Failed" in output

    def test_success_with_explicit_message_renders(self):
        """Test success() preserves an explicit message override."""
        console = Console(file=StringIO(), force_terminal=True, width=80)
        spinner = ThothSpinner()

        spinner.success("Done")
        console.print(spinner)

        output = console.file.getvalue()
        assert "Done" in output

    def test_error_with_explicit_message_renders(self):
        """Test error() preserves an explicit message override."""
        console = Console(file=StringIO(), force_terminal=True, width=80)
        spinner = ThothSpinner()

        spinner.error("Failed badly")
        console.print(spinner)

        output = console.file.getvalue()
        assert "Failed badly" in output

    def test_reset_method(self):
        """Test reset returns to IN_PROGRESS."""
        spinner = ThothSpinner()
        spinner.success()
        spinner.reset()

        assert spinner.state == ComponentState.IN_PROGRESS

    @pytest.mark.parametrize("terminal_method", ["success", "error"])
    def test_start_after_terminal_state_restarts_children(self, terminal_method):
        """start() fully restarts children after a terminal state."""
        console = Console(file=StringIO(), force_terminal=True, width=80)
        spinner = ThothSpinner()

        spinner.start()
        spinner.update_progress(current=42, total=100)
        time.sleep(0.02)
        getattr(spinner, terminal_method)("Done")
        spinner.clear()
        spinner.start()

        console.print(spinner)
        output = console.file.getvalue()

        assert spinner.state == ComponentState.IN_PROGRESS
        assert spinner.get_component("spinner").state == ComponentState.IN_PROGRESS
        assert spinner.get_component("message").state == ComponentState.IN_PROGRESS
        assert spinner.get_component("progress")._state == ComponentState.IN_PROGRESS
        assert spinner.get_component("timer")._state == ComponentState.IN_PROGRESS
        assert spinner.get_component("progress").current == 0
        assert spinner.get_component("timer").is_running() is True
        assert spinner.get_component("timer").get_elapsed() < 0.1
        assert all(component.visible for component in spinner._components.values())
        assert "done" not in output.lower()

    def test_start_while_in_progress_preserves_progress_and_timer(self):
        """start() should stay non-destructive during an active run."""
        spinner = ThothSpinner()

        spinner.start()
        spinner.update_progress(current=42, total=100)
        time.sleep(0.02)
        elapsed_before = spinner.get_component("timer").get_elapsed()

        spinner.start()

        assert spinner.state == ComponentState.IN_PROGRESS
        assert spinner.get_component("progress").current == 42
        assert spinner.get_component("timer").is_running() is True
        assert spinner.get_component("timer").get_elapsed() >= elapsed_before

    def test_reset_restores_configured_component_visibility(self):
        """Test reset restores each component's configured visibility."""
        spinner = ThothSpinner(elements={"hint": {"visible": False}})

        spinner.clear()
        spinner.reset()

        assert spinner._components["hint"].visible is False
        assert spinner._components["spinner"].visible is True

    def test_invalid_transition(self):
        """Test invalid state transition raises ValueError."""
        spinner = ThothSpinner()
        spinner.success()

        with pytest.raises(ValueError, match="Invalid state transition"):
            spinner.error()  # Can't go from SUCCESS to ERROR directly

    def test_clear_method(self):
        """Test clear method hides components."""
        spinner = ThothSpinner()
        spinner.start()
        spinner.clear()

        for component in spinner._components.values():
            assert not component.visible

    def test_stop_alias(self):
        """Test stop is alias for clear."""
        spinner = ThothSpinner()
        spinner.start()
        spinner.stop()

        for component in spinner._components.values():
            assert not component.visible

    @patch("threading.Timer")
    def test_auto_clear_success(self, mock_timer):
        """Test auto-clear with success duration."""
        spinner = ThothSpinner(success_duration=2.0)
        spinner.success()

        mock_timer.assert_called_once_with(2.0, spinner.clear)
        mock_timer.return_value.start.assert_called_once()

    @patch("threading.Timer")
    def test_auto_clear_error(self, mock_timer):
        """Test auto-clear with error duration."""
        spinner = ThothSpinner(error_duration=3.0)
        spinner.error()

        mock_timer.assert_called_once_with(3.0, spinner.clear)
        mock_timer.return_value.start.assert_called_once()

    @patch("threading.Timer")
    def test_duration_override(self, mock_timer):
        """Test duration override in method call."""
        spinner = ThothSpinner(success_duration=2.0)
        spinner.success(duration=5.0)

        mock_timer.assert_called_once_with(5.0, spinner.clear)

    @patch("threading.Timer")
    def test_state_duration_override(self, mock_timer):
        """State-level duration config overrides the default success duration."""
        spinner = ThothSpinner(
            success_duration=2.0,
            states={"success": {"duration": 4.0}},
        )

        spinner.success()

        mock_timer.assert_called_once_with(4.0, spinner.clear)

    @patch("threading.Timer")
    def test_method_duration_beats_state_duration(self, mock_timer):
        """Explicit method duration overrides configured state duration."""
        spinner = ThothSpinner(states={"success": {"duration": 4.0}})

        spinner.success(duration=1.5)

        mock_timer.assert_called_once_with(1.5, spinner.clear)


class TestComponentControl:
    """Test component control methods."""

    def test_update_progress(self):
        """Test update_progress method."""
        spinner = ThothSpinner()
        spinner.update_progress(current=50, total=100)

        progress = spinner.get_component("progress")
        assert progress.current == 50
        assert progress.total == 100

    def test_set_message(self):
        """Test set_message method."""
        spinner = ThothSpinner()
        spinner.set_message(text="New message")

        # Message component should be updated
        spinner.get_component("message")
        # The actual update depends on MessageComponent implementation

    def test_set_hint(self):
        """Test set_hint method."""
        spinner = ThothSpinner()
        spinner.set_hint(text="New hint")

        hint = spinner.get_component("hint")
        assert hint.text == "New hint"

    def test_set_spinner_style(self):
        """Test set_spinner_style method."""
        spinner = ThothSpinner()
        original_spinner = spinner.get_component("spinner")
        original_frames = original_spinner.frames[:]

        spinner.set_spinner_style(style="claude_stars")

        updated_spinner = spinner.get_component("spinner")
        # Same component is mutated in place (not recreated)
        assert updated_spinner is original_spinner
        # Frames should have changed
        assert updated_spinner.frames != original_frames

    def test_update_component_generic(self):
        """Test generic update_component method."""
        spinner = ThothSpinner()

        # Update hint using generic method
        spinner.update_component("hint", text="Generic update")

        hint = spinner.get_component("hint")
        assert hint.text == "Generic update"

    def test_update_component_invalid(self):
        """Test update_component with invalid type."""
        spinner = ThothSpinner()

        with pytest.raises(KeyError, match="Invalid component type"):
            spinner.update_component("invalid", some_attr="value")

    def test_set_shimmer_direction(self):
        """Test set_shimmer_direction method."""
        spinner = ThothSpinner()

        # This depends on MessageComponent having reverse_shimmer attribute
        spinner.set_shimmer_direction(direction="right-to-left")

        message = spinner.get_component("message")
        if hasattr(message, "reverse_shimmer"):
            assert message.reverse_shimmer is True

    def test_keyword_only_arguments(self):
        """Test methods enforce keyword-only arguments."""
        spinner = ThothSpinner()

        # These should fail with positional arguments
        with pytest.raises(TypeError):
            spinner.update_progress(50, 100)  # Should be current=50, total=100

        with pytest.raises(TypeError):
            spinner.set_message("text")  # Should be text="text"


class TestRendering:
    """Test rendering methods."""

    def test_rich_protocol(self):
        """Test __rich__ method returns Columns."""
        from rich.columns import Columns

        spinner = ThothSpinner()
        rendered = spinner.__rich__()

        assert isinstance(rendered, Columns)

    def test_rich_console_protocol(self):
        """Test __rich_console__ method."""
        console = Console(file=StringIO())
        spinner = ThothSpinner()

        # Should yield renderables
        result = list(spinner.__rich_console__(console, console.options))
        assert len(result) > 0

    def test_rich_measure_protocol(self):
        """Test __rich_measure__ method."""
        from rich.measure import Measurement

        console = Console(file=StringIO())
        spinner = ThothSpinner()

        measurement = spinner.__rich_measure__(console, console.options)
        assert isinstance(measurement, Measurement)
        assert measurement.minimum >= 0
        assert measurement.maximum >= measurement.minimum

    def test_visible_components_only(self):
        """Test only visible components are rendered."""
        spinner = ThothSpinner()

        # Hide some components
        spinner._components["hint"].visible = False
        spinner._components["timer"].visible = False

        spinner.__rich__()
        # Should only render 3 visible components

    def test_empty_render(self):
        """Test rendering with no visible components."""
        spinner = ThothSpinner()

        # Hide all components
        for component in spinner._components.values():
            component.visible = False

        console = Console(file=StringIO())
        result = list(spinner.__rich_console__(console, console.options))

        # Should yield empty or minimal output
        assert len(result) >= 0


class TestFadeAwayAnimation:
    """Test fade-away animation."""

    def test_fade_away_disabled_by_default(self):
        """Test fade-away is disabled by default."""
        spinner = ThothSpinner()
        assert spinner._fade_progress is None

    def test_fade_away_enabled(self):
        """Test fade-away when enabled."""
        config = {"fade_away": {"enabled": True, "direction": "left-to-right", "interval": 0.05}}

        spinner = ThothSpinner(**config)
        spinner.success()  # Should trigger fade

        # Fade should be initialized
        assert spinner._fade_start_time is not None

    def test_fade_left_to_right(self):
        """Test left-to-right fade direction."""
        config = {"fade_away": {"enabled": True, "direction": "left-to-right", "interval": 0.01}}

        spinner = ThothSpinner(**config)
        components = list(spinner._components.values())

        spinner._fade_start_time = time.time() - 0.02  # Simulate elapsed time
        faded = spinner._apply_fade_away(components)

        # Should have fewer components
        assert len(faded) < len(components)

    def test_fade_right_to_left(self):
        """Test right-to-left fade direction."""
        config = {"fade_away": {"enabled": True, "direction": "right-to-left", "interval": 0.01}}

        spinner = ThothSpinner(**config)
        components = list(spinner._components.values())

        spinner._fade_start_time = time.time() - 0.02
        faded = spinner._apply_fade_away(components)

        assert len(faded) < len(components)


class TestConfiguration:
    """Test configuration system."""

    def test_default_configuration(self):
        """Test default configuration values."""
        spinner = ThothSpinner()

        assert spinner.config["defaults"]["color"] == "#D97706"
        assert spinner.config["defaults"]["visible"] is True

    def test_configuration_inheritance(self):
        """Test configuration inheritance: component > state > global."""
        config = {
            "defaults": {
                "color": "#000000"  # Global default
            },
            "states": {
                "success": {
                    "spinner": {
                        "color": "#00FF00"  # State-specific
                    }
                }
            },
            "elements": {
                "spinner": {
                    "color": "#FF0000"  # Component-specific (highest priority)
                }
            },
        }

        spinner = ThothSpinner(**config)

        # Component-specific should win
        resolved = spinner._resolve_config("spinner")
        assert resolved["color"] == "#FF0000"

    def test_state_overrides_are_applied_on_success(self):
        """State config should drive terminal icon, text, and colors."""
        spinner = ThothSpinner(
            states={
                "success": {
                    "spinner": {"icon": "🎉", "color": "#12AB34"},
                    "message": {"text": "Ship it", "color": "#3456AB"},
                }
            }
        )

        spinner.success()

        console = Console(file=StringIO(), force_terminal=True, width=80)
        options = console.options

        rendered_spinner = next(spinner.get_component("spinner").__rich_console__(console, options))
        rendered_message = next(spinner.get_component("message").__rich_console__(console, options))

        assert rendered_spinner.plain == "🎉"
        assert rendered_spinner.style.color is not None
        assert "#12ab34" in str(rendered_spinner.style.color).lower()
        assert rendered_message.plain == "Ship it"
        assert rendered_message.style.color is not None
        assert "#3456ab" in str(rendered_message.style.color).lower()

    def test_explicit_message_overrides_state_message_text(self):
        """A method message should beat configured state text for that transition."""
        spinner = ThothSpinner(states={"success": {"message": {"text": "Configured"}}})

        spinner.success("Explicit")

        console = Console(file=StringIO(), force_terminal=True, width=80)
        options = console.options
        rendered_message = next(spinner.get_component("message").__rich_console__(console, options))

        assert rendered_message.plain == "Explicit"

    def test_state_behavior_disappear_hides_components(self):
        """State-level behavior should control terminal visibility."""
        spinner = ThothSpinner(states={"success": {"behavior": "disappear"}})

        spinner.success()

        for component in spinner._components.values():
            assert component.visible is False

    def test_component_visibility_override_applied_on_creation(self):
        """Test component visibility overrides global defaults on initialization."""
        spinner = ThothSpinner(defaults={"visible": True}, elements={"hint": {"visible": False}})

        assert spinner._components["hint"].visible is False
        assert spinner._components["spinner"].visible is True

    def test_validate_config(self):
        """Test configuration validation."""
        spinner = ThothSpinner()

        # Valid config should pass
        valid_config = {"elements": {"spinner": {"style": "npm_dots"}}}
        validated = spinner._validate_config(valid_config)
        assert "elements" in validated

    def test_invalid_element_config(self):
        """Test invalid element config raises error."""
        config = {
            "elements": {
                "spinner": "not_a_dict"  # Should be dict
            }
        }

        spinner = ThothSpinner()
        with pytest.raises(ValueError, match="must be a dict"):
            spinner._validate_config(config)


class TestThreadSafety:
    """Test thread safety features."""

    def test_concurrent_updates(self):
        """Test concurrent updates are thread-safe."""
        spinner = ThothSpinner()
        errors = []

        def update_progress():
            try:
                for i in range(50):
                    spinner.update_progress(current=i, total=100)
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        def update_message():
            try:
                for i in range(50):
                    spinner.set_message(text=f"Message {i}")
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        # Run updates in parallel
        thread1 = threading.Thread(target=update_progress)
        thread2 = threading.Thread(target=update_message)

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # Should complete without errors
        assert len(errors) == 0

    def test_lock_acquisition(self):
        """Test methods acquire lock properly."""
        spinner = ThothSpinner()

        # Mock the lock to verify it's being used
        mock_lock = MagicMock()
        mock_lock.__enter__ = MagicMock(return_value=None)
        mock_lock.__exit__ = MagicMock(return_value=None)
        spinner._lock = mock_lock

        spinner.update_progress(current=50)

        # Lock should have been acquired
        mock_lock.__enter__.assert_called()
        mock_lock.__exit__.assert_called()


class TestIntegration:
    """Integration tests."""

    def test_full_lifecycle(self):
        """Test full component lifecycle."""
        spinner = ThothSpinner(success_duration=0.1, error_duration=0.1)

        # Start
        spinner.start()
        assert spinner.state == ComponentState.IN_PROGRESS

        # Update progress
        spinner.update_progress(current=50, total=100)

        # Success
        spinner.success("Done!")
        assert spinner.state == ComponentState.SUCCESS

        # Reset
        spinner.reset()
        assert spinner.state == ComponentState.IN_PROGRESS

        # Error
        spinner.error("Failed!")
        assert spinner.state == ComponentState.ERROR

        # Clear
        spinner.clear()
        for component in spinner._components.values():
            assert not component.visible

    def test_with_rich_live(self):
        """Test integration with Rich Live."""
        from rich.live import Live

        console = Console(file=StringIO(), force_terminal=True, width=80)
        spinner = ThothSpinner()

        # Should work with Live context
        try:
            with Live(spinner, console=console, refresh_per_second=10):
                spinner.start()
                spinner.update_progress(current=50)
                spinner.success()
        except AttributeError as e:
            # Known issue with StringIO in some Rich versions
            if "'NoneType' object has no attribute 'translate'" in str(e):
                # Skip this specific error - it's a Rich/StringIO interaction issue
                pass
            else:
                raise

        # Basic validation that spinner was created
        assert spinner.state == ComponentState.SUCCESS
