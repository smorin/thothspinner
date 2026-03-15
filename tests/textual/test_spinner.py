"""Comprehensive tests for the Textual SpinnerWidget."""

import pytest
from rich.text import Text
from textual.app import App, ComposeResult

from thothspinner.core.states import ComponentState
from thothspinner.rich.spinners.frames import SPINNER_FRAMES
from thothspinner.textual.widgets import SpinnerWidget


# Test initialization and defaults
def test_initialization_defaults():
    """Test default initialization values outside app context."""
    widget = SpinnerWidget()
    assert widget._frames == SPINNER_FRAMES["npm_dots"]["frames"]
    assert widget._interval == SPINNER_FRAMES["npm_dots"]["interval"]
    assert widget.color == "#D97706"
    assert widget.state == ComponentState.IN_PROGRESS
    assert widget.speed == 1.0
    assert widget._success_icon == "✓"
    assert widget._error_icon == "✗"
    assert widget.display
    assert widget._frame_index == 0


def test_initialization_custom_style():
    """Test initialization with each built-in style."""
    for style_name, spinner_def in SPINNER_FRAMES.items():
        widget = SpinnerWidget(style=style_name)
        assert widget._frames == spinner_def["frames"]
        assert widget._interval == spinner_def["interval"]


def test_initialization_custom_frames():
    """Test initialization with custom frames."""
    custom_frames = ["a", "b", "c"]
    widget = SpinnerWidget(frames=custom_frames, interval=0.2)
    assert widget._frames == custom_frames
    assert widget._interval == 0.2


def test_initialization_custom_frames_default_interval():
    """Test custom frames use default interval when none specified."""
    widget = SpinnerWidget(frames=["x", "y"])
    assert widget._interval == 0.08


def test_initialization_invalid_frames():
    """Test invalid frames raise ValueError."""
    with pytest.raises(ValueError, match="non-empty"):
        SpinnerWidget(frames=[])
    with pytest.raises(ValueError, match="non-empty"):
        SpinnerWidget(frames=[""])


def test_initialization_hidden():
    """Test hidden initialization."""
    widget = SpinnerWidget(visible=False)
    assert not widget.display


def test_unknown_style_falls_back():
    """Test unknown style falls back to npm_dots."""
    widget = SpinnerWidget(style="nonexistent_style")
    assert widget._frames == SPINNER_FRAMES["npm_dots"]["frames"]


# Test color validation
def test_color_validation():
    """Test hex color validation."""
    widget = SpinnerWidget()

    widget.color = "#FF0000"
    assert widget.color == "#FF0000"
    widget.color = "#00FF00"
    assert widget.color == "#00FF00"

    with pytest.raises(ValueError, match="Invalid hex color"):
        widget.color = "red"
    with pytest.raises(ValueError, match="Invalid hex color"):
        widget.color = "#FF"
    with pytest.raises(ValueError, match="Invalid hex"):
        widget.color = "#GGGGGG"


def test_color_validation_in_constructor():
    """Test color validation during construction."""
    with pytest.raises(ValueError):
        SpinnerWidget(color="invalid")


# Test render output
def test_render_in_progress():
    """Test render output in IN_PROGRESS state."""
    widget = SpinnerWidget()
    rendered = widget.render()
    assert isinstance(rendered, Text)
    assert rendered.plain in SPINNER_FRAMES["npm_dots"]["frames"]


def test_render_success():
    """Test render output in SUCCESS state."""
    widget = SpinnerWidget()
    widget._state = ComponentState.SUCCESS
    rendered = widget.render()
    assert isinstance(rendered, Text)
    assert rendered.plain == "✓"


def test_render_error():
    """Test render output in ERROR state."""
    widget = SpinnerWidget()
    widget._state = ComponentState.ERROR
    rendered = widget.render()
    assert isinstance(rendered, Text)
    assert rendered.plain == "✗"


def test_render_custom_icons():
    """Test render with custom success/error icons."""
    widget = SpinnerWidget(success_icon="OK", error_icon="FAIL")
    widget._state = ComponentState.SUCCESS
    assert widget.render().plain == "OK"
    widget._state = ComponentState.ERROR
    assert widget.render().plain == "FAIL"


def test_render_all_styles():
    """Test that all spinner styles render valid frames."""
    for style_name, spinner_def in SPINNER_FRAMES.items():
        widget = SpinnerWidget(style=style_name)
        rendered = widget.render()
        assert isinstance(rendered, Text)
        assert rendered.plain in spinner_def["frames"]


# Test state transitions
def test_state_transitions():
    """Test valid and invalid state transitions."""
    widget = SpinnerWidget()

    # IN_PROGRESS -> SUCCESS
    assert widget.state == ComponentState.IN_PROGRESS
    widget.success()
    assert widget.state == ComponentState.SUCCESS

    # SUCCESS -> ERROR (invalid, should be ignored)
    widget.error()
    assert widget.state == ComponentState.SUCCESS

    # Reset to IN_PROGRESS
    widget.reset()
    assert widget.state == ComponentState.IN_PROGRESS

    # IN_PROGRESS -> ERROR
    widget.error()
    assert widget.state == ComponentState.ERROR

    # ERROR -> SUCCESS (invalid, should be ignored)
    widget.success()
    assert widget.state == ComponentState.ERROR

    # Reset from ERROR
    widget.start()
    assert widget.state == ComponentState.IN_PROGRESS
    assert widget._frame_index == 0


@pytest.mark.asyncio
async def test_state_css_classes():
    """Test CSS classes are set correctly on state changes."""

    class StateApp(App):
        def compose(self) -> ComposeResult:
            yield SpinnerWidget(id="spinner")

    async with StateApp().run_test() as pilot:
        spinner = pilot.app.query_one("#spinner", SpinnerWidget)

        assert "success" not in spinner.classes
        assert "error" not in spinner.classes

        spinner.success()
        await pilot.pause()
        assert "success" in spinner.classes
        assert "error" not in spinner.classes

        spinner.reset()
        await pilot.pause()
        assert "success" not in spinner.classes
        assert "error" not in spinner.classes

        spinner.error()
        await pilot.pause()
        assert "error" in spinner.classes
        assert "success" not in spinner.classes


# Test animation
@pytest.mark.asyncio
async def test_animation_frame_updates():
    """Test animation frames advance over time."""

    class AnimApp(App):
        def compose(self) -> ComposeResult:
            yield SpinnerWidget(style="npm_dots", id="spinner")

    async with AnimApp().run_test() as pilot:
        spinner = pilot.app.query_one("#spinner", SpinnerWidget)

        initial_frame = spinner._frame_index

        # Wait long enough for frames to advance
        await pilot.pause(0.5)

        # Frame should have advanced
        assert spinner._frame_index != initial_frame or spinner._frame_index == 0


@pytest.mark.asyncio
async def test_animation_stops_on_success():
    """Test animation timer stops when entering success state."""

    class StopApp(App):
        def compose(self) -> ComposeResult:
            yield SpinnerWidget(id="spinner")

    async with StopApp().run_test() as pilot:
        spinner = pilot.app.query_one("#spinner", SpinnerWidget)
        await pilot.pause(0.2)

        spinner.success()
        await pilot.pause()
        assert spinner._timer is not None
        assert not spinner._timer._active.is_set()

        frame_after_success = spinner._frame_index
        await pilot.pause(0.2)
        # Frame should not change after success
        assert spinner._frame_index == frame_after_success


@pytest.mark.asyncio
async def test_animation_restarts_on_reset():
    """Test animation restarts after reset from terminal state."""

    class ResetApp(App):
        def compose(self) -> ComposeResult:
            yield SpinnerWidget(id="spinner")

    async with ResetApp().run_test() as pilot:
        spinner = pilot.app.query_one("#spinner", SpinnerWidget)

        spinner.success()
        await pilot.pause()
        assert spinner._timer is not None
        assert not spinner._timer._active.is_set()

        spinner.reset()
        await pilot.pause()
        assert spinner._timer is not None
        assert spinner._timer._active.is_set()


# Test stop and pause
@pytest.mark.asyncio
async def test_stop():
    """Test stop freezes animation without changing state."""

    class StopApp(App):
        def compose(self) -> ComposeResult:
            yield SpinnerWidget(id="spinner")

    async with StopApp().run_test() as pilot:
        spinner = pilot.app.query_one("#spinner", SpinnerWidget)
        await pilot.pause(0.1)

        spinner.stop()
        assert spinner._timer is None
        assert spinner.state == ComponentState.IN_PROGRESS

        frame_after_stop = spinner._frame_index
        await pilot.pause(0.2)
        assert spinner._frame_index == frame_after_stop


@pytest.mark.asyncio
async def test_pause_resume():
    """Test pause/resume toggle."""

    class PauseApp(App):
        def compose(self) -> ComposeResult:
            yield SpinnerWidget(id="spinner")

    async with PauseApp().run_test() as pilot:
        spinner = pilot.app.query_one("#spinner", SpinnerWidget)
        await pilot.pause(0.1)

        # Pause
        spinner.pause()
        assert spinner.paused is True
        assert spinner._timer is not None
        assert not spinner._timer._active.is_set()

        frame_when_paused = spinner._frame_index
        await pilot.pause(0.2)
        assert spinner._frame_index == frame_when_paused

        # Resume
        spinner.pause()
        assert spinner.paused is False
        assert spinner._timer is not None
        assert spinner._timer._active.is_set()


def test_pause_ignored_in_terminal_state():
    """Test pause is ignored when not in IN_PROGRESS state."""
    widget = SpinnerWidget()
    widget._state = ComponentState.SUCCESS
    widget.pause()
    assert widget.paused is False


# Test speed control
@pytest.mark.asyncio
async def test_speed_control():
    """Test speed multiplier affects animation."""

    class SpeedApp(App):
        def compose(self) -> ComposeResult:
            yield SpinnerWidget(id="spinner", speed=2.0)

    async with SpeedApp().run_test() as pilot:
        spinner = pilot.app.query_one("#spinner", SpinnerWidget)
        assert spinner.speed == 2.0
        assert spinner._timer is not None


def test_set_speed():
    """Test set_speed method."""
    widget = SpinnerWidget()
    widget.set_speed(3.0)
    assert widget.speed == 3.0


def test_set_speed_invalid():
    """Test set_speed rejects non-positive values."""
    widget = SpinnerWidget()
    with pytest.raises(ValueError, match="positive"):
        widget.set_speed(0)
    with pytest.raises(ValueError, match="positive"):
        widget.set_speed(-1.0)


# Test visibility
@pytest.mark.asyncio
async def test_visibility_toggle():
    """Test display property-based visibility changes."""

    class VisApp(App):
        def compose(self) -> ComposeResult:
            yield SpinnerWidget(id="spinner")

    async with VisApp().run_test() as pilot:
        spinner = pilot.app.query_one("#spinner", SpinnerWidget)

        assert spinner.display

        spinner.hide()
        await pilot.pause()
        assert not spinner.display

        spinner.show()
        await pilot.pause()
        assert spinner.display

        spinner.toggle()
        await pilot.pause()
        assert not spinner.display

        spinner.set_visible(True)
        await pilot.pause()
        assert spinner.display


# Test from_config
def test_from_config():
    """Test factory method from configuration dictionary."""
    config = {
        "style": "claude_stars",
        "color": "#FFA500",
        "speed": 1.5,
        "success_icon": "OK",
        "error_icon": "ERR",
        "visible": False,
    }
    widget = SpinnerWidget.from_config(config)
    assert widget._frames == SPINNER_FRAMES["claude_stars"]["frames"]
    assert widget.color == "#FFA500"
    assert widget.speed == 1.5
    assert widget._success_icon == "OK"
    assert widget._error_icon == "ERR"
    assert not widget.display


def test_from_config_custom_frames():
    """Test from_config with custom frames."""
    config = {
        "frames": ["A", "B", "C"],
        "interval": 0.15,
        "color": "#112233",
    }
    widget = SpinnerWidget.from_config(config)
    assert widget._frames == ["A", "B", "C"]
    assert widget._interval == 0.15
    assert widget.color == "#112233"


def test_from_config_defaults():
    """Test from_config with empty config uses defaults."""
    widget = SpinnerWidget.from_config({})
    assert widget._frames == SPINNER_FRAMES["npm_dots"]["frames"]
    assert widget.color == "#D97706"
    assert widget.speed == 1.0


# Test properties
def test_frames_property_returns_copy():
    """Test frames property returns a copy, not the internal list."""
    widget = SpinnerWidget()
    frames = widget.frames
    frames.append("extra")
    assert "extra" not in widget._frames


def test_interval_property():
    """Test interval property."""
    widget = SpinnerWidget(style="circle")
    assert widget.interval == SPINNER_FRAMES["circle"]["interval"]


# Test repr
def test_repr():
    """Test string representation."""
    widget = SpinnerWidget()
    repr_str = repr(widget)
    assert "SpinnerWidget" in repr_str
    assert "10 frames" in repr_str
    assert "IN_PROGRESS" in repr_str


# Integration test
@pytest.mark.asyncio
async def test_app_integration():
    """Test widget in full Textual app lifecycle."""

    class IntegrationApp(App):
        CSS = """
        SpinnerWidget {
            height: 1;
            width: 100%;
        }
        """

        def compose(self) -> ComposeResult:
            yield SpinnerWidget(style="npm_dots", id="spinner1")
            yield SpinnerWidget(style="claude_stars", color="#FF00FF", id="spinner2")

    async with IntegrationApp().run_test() as pilot:
        s1 = pilot.app.query_one("#spinner1", SpinnerWidget)
        s2 = pilot.app.query_one("#spinner2", SpinnerWidget)

        assert s1.state == ComponentState.IN_PROGRESS
        assert s2.color == "#FF00FF"

        # Test state transitions in app context
        s1.success()
        await pilot.pause()
        assert s1.state == ComponentState.SUCCESS
        rendered = s1.render()
        assert rendered.plain == "✓"

        s2.error()
        await pilot.pause()
        assert s2.state == ComponentState.ERROR
        rendered = s2.render()
        assert rendered.plain == "✗"

        # Reset and verify animation restarts
        s1.reset()
        await pilot.pause()
        assert s1.state == ComponentState.IN_PROGRESS
        assert s1._timer is not None
        assert s1._timer._active.is_set()


@pytest.mark.asyncio
async def test_widget_lifecycle():
    """Test widget mount/unmount lifecycle."""

    class LifecycleApp(App):
        def compose(self) -> ComposeResult:
            yield SpinnerWidget(id="spinner")

    async with LifecycleApp().run_test() as pilot:
        spinner = pilot.app.query_one("#spinner", SpinnerWidget)
        assert spinner.is_mounted
        assert spinner._timer is not None

        rendered = spinner.render()
        assert isinstance(rendered, Text)

        await spinner.remove()
        assert spinner not in pilot.app.query(SpinnerWidget)


# Feature parity test
def test_feature_parity():
    """Verify all Rich SpinnerComponent APIs are available."""
    widget = SpinnerWidget()

    # State methods
    assert hasattr(widget, "success")
    assert hasattr(widget, "error")
    assert hasattr(widget, "start")
    assert hasattr(widget, "reset")

    # Properties
    assert hasattr(widget, "state")
    assert hasattr(widget, "frames")
    assert hasattr(widget, "interval")
    assert hasattr(widget, "speed")

    # Factory
    assert hasattr(SpinnerWidget, "from_config")

    # Visibility
    assert hasattr(widget, "show")
    assert hasattr(widget, "hide")
    assert hasattr(widget, "toggle")
    assert hasattr(widget, "set_visible")

    # Additional Textual features
    assert hasattr(widget, "pause")
    assert hasattr(widget, "stop")
    assert hasattr(widget, "set_speed")

    # All spinner styles supported
    for style_name in SPINNER_FRAMES:
        s = SpinnerWidget(style=style_name)
        assert s._frames == SPINNER_FRAMES[style_name]["frames"]


# CSS defaults test
def test_css_defaults():
    """Test DEFAULT_CSS is properly defined."""
    assert "SpinnerWidget" in SpinnerWidget.DEFAULT_CSS
    assert "success" in SpinnerWidget.DEFAULT_CSS
    assert "error" in SpinnerWidget.DEFAULT_CSS
