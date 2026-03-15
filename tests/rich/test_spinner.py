"""Unit tests for SpinnerComponent."""

from __future__ import annotations

import io

import pytest
from rich.console import Console

from thothspinner.core.states import ComponentState
from thothspinner.rich.components import SpinnerComponent


class TestSpinnerComponent:
    """Test suite for SpinnerComponent."""

    def test_empty_frames_raises(self):
        """Test that empty frames list raises ValueError."""
        with pytest.raises(ValueError, match="frames must not be empty"):
            SpinnerComponent(frames=[])

    def test_initialization_defaults(self):
        """Test M02-TS03: Component instantiation with defaults."""
        spinner = SpinnerComponent()
        assert spinner.visible is True
        assert spinner.state == ComponentState.IN_PROGRESS
        assert len(spinner.frames) == 10  # npm_dots default
        assert spinner.interval == 0.08
        assert spinner.color == "#D97706"
        assert spinner.success_icon == "✓"
        assert spinner.error_icon == "✗"
        assert spinner.speed == 1.0

    def test_initialization_custom_style(self):
        """Test spinner initialization with different built-in style."""
        spinner = SpinnerComponent(style="claude_stars")
        assert len(spinner.frames) == 10  # claude_stars has 10 frames
        assert spinner.interval == 0.1  # claude_stars interval

    def test_initialization_custom_frames(self):
        """Test M02-TS05: Custom frames initialization."""
        custom_frames = ["1", "2", "3", "4"]
        spinner = SpinnerComponent(frames=custom_frames, interval=0.2)
        assert spinner.frames == custom_frames
        assert spinner.interval == 0.2

    def test_frame_animation_timing(self):
        """Test M02-TS04: Frame timing accuracy."""
        spinner = SpinnerComponent(style="npm_dots")

        # Test frame advancement
        frame1 = spinner._calculate_frame(0.0)
        assert frame1 == 0

        # Advance one interval
        frame2 = spinner._calculate_frame(0.08)
        assert frame2 == 1

        # Advance multiple intervals (10 intervals)
        frame3 = spinner._calculate_frame(0.8)
        assert frame3 == 0  # Should wrap around (10 % 10)

    def test_speed_multiplier(self):
        """Test speed multiplier effect on frame calculation."""
        spinner = SpinnerComponent(speed=2.0)

        frame1 = spinner._calculate_frame(0.0)
        assert frame1 == 0

        # With 2x speed, should advance twice as fast
        frame2 = spinner._calculate_frame(0.04)  # Half interval at 2x speed
        assert frame2 == 1

    def test_state_transitions(self):
        """Test M02-TS07: State transitions and their effects."""
        spinner = SpinnerComponent()

        # Initial state
        assert spinner.state == ComponentState.IN_PROGRESS

        # Transition to success
        spinner.success()
        assert spinner.state == ComponentState.SUCCESS

        # Cannot transition from success to error directly
        spinner.error()
        assert spinner.state == ComponentState.SUCCESS  # Should stay in SUCCESS

        # Reset to in_progress
        spinner.reset()
        assert spinner.state == ComponentState.IN_PROGRESS

        # Transition to error
        spinner.error()
        assert spinner.state == ComponentState.ERROR

        # Can reset from error
        spinner.reset()
        assert spinner.state == ComponentState.IN_PROGRESS

    def test_success_state_rendering(self):
        """Test M02-TS08: Success state rendering."""
        console = Console(file=io.StringIO(), force_terminal=True, width=80)
        spinner = SpinnerComponent()

        # Transition to success
        spinner.success()

        # Render and check output
        console.print(spinner)
        output = console.file.getvalue()
        assert "✓" in output
        # Check for green color (ANSI code)
        assert "\x1b[38;2;0;255;0m" in output or "00ff00" in output.lower()

    def test_error_state_rendering(self):
        """Test M02-TS09: Error state rendering."""
        console = Console(file=io.StringIO(), force_terminal=True, width=80)
        spinner = SpinnerComponent()

        # Transition to error
        spinner.error()

        # Render and check output
        console.print(spinner)
        output = console.file.getvalue()
        assert "✗" in output
        # Check for red color (ANSI code)
        assert "\x1b[38;2;255;0;0m" in output or "ff0000" in output.lower()

    def test_visibility_control(self):
        """Test visibility property controls rendering."""
        console = Console(file=io.StringIO(), force_terminal=True, width=80)
        spinner = SpinnerComponent(visible=False)

        console.print(spinner)
        output = console.file.getvalue()
        # Should have minimal output when not visible
        assert len(output.strip()) < 10  # Just newline/formatting

    def test_from_config(self):
        """Test M02-TS10: Configuration loading from dict."""
        config = {
            "style": "claude_stars",
            "color": "#FFA500",
            "speed": 1.5,
            "success_icon": "✅",
            "error_icon": "❌",
            "visible": False,
        }
        spinner = SpinnerComponent.from_config(config)

        assert len(spinner.frames) == 10  # claude_stars frames
        assert spinner.color == "#FFA500"
        assert spinner.speed == 1.5
        assert spinner.success_icon == "✅"
        assert spinner.error_icon == "❌"
        assert spinner.visible is False

    def test_custom_frames_config(self):
        """Test configuration with custom frames."""
        config = {"frames": ["A", "B", "C"], "interval": 0.5, "color": "#123456"}
        spinner = SpinnerComponent.from_config(config)

        assert spinner.frames == ["A", "B", "C"]
        assert spinner.interval == 0.5
        assert spinner.color == "#123456"

    def test_start_method_resets_animation(self):
        """Test that start() method resets animation."""
        spinner = SpinnerComponent()

        # Simulate some animation progress
        spinner._start_time = 100.0
        spinner._state = ComponentState.SUCCESS

        # Call start
        spinner.start()

        assert spinner._start_time is None
        assert spinner.state == ComponentState.IN_PROGRESS

    def test_repr(self):
        """Test string representation."""
        spinner = SpinnerComponent(style="npm_dots")
        repr_str = repr(spinner)
        assert "SpinnerComponent" in repr_str
        assert "10 frames" in repr_str
        assert "IN_PROGRESS" in repr_str

    def test_measure(self):
        """Test measurement for layout calculations."""
        console = Console()
        spinner = SpinnerComponent()

        measurement = spinner.__rich_measure__(console, console.options)
        assert measurement.minimum >= 0
        assert measurement.maximum >= measurement.minimum

        # Test with visibility off
        spinner.visible = False
        measurement = spinner.__rich_measure__(console, console.options)
        assert measurement.minimum == 0
        assert measurement.maximum == 0

    def test_animation_in_progress_state(self):
        """Test that spinner animates in IN_PROGRESS state."""
        console = Console(file=io.StringIO(), force_terminal=True, width=80)
        spinner = SpinnerComponent(style="classic")  # Simple frames: |, /, -, \

        # Should render first frame
        console.print(spinner)
        output = console.file.getvalue()
        assert "|" in output  # First frame of classic spinner
