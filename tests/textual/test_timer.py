"""Comprehensive tests for the Textual TimerWidget."""

import time

import pytest
from rich.text import Text
from textual.app import App, ComposeResult

from thothspinner.core.states import ComponentState
from thothspinner.textual.widgets import TimerWidget


# Test initialization and defaults
def test_initialization_defaults():
    """Test default initialization values outside app context."""
    widget = TimerWidget()
    assert widget.format_style == "auto"
    assert widget.precision == 1
    assert widget.color == "#FFFF55"
    assert widget.state == ComponentState.IN_PROGRESS
    assert widget._success_text is None
    assert widget._error_text is None
    assert not widget.running
    assert not widget.paused
    assert widget._elapsed == 0.0
    assert widget._start_time is None
    assert widget.display is True


def test_initialization_custom():
    """Test custom initialization."""
    widget = TimerWidget(
        format_style="seconds_decimal",
        precision=2,
        color="#FF0000",
        success_text="Done!",
        error_text="Oops",
    )
    assert widget.format_style == "seconds_decimal"
    assert widget.precision == 2
    assert widget.color == "#FF0000"
    assert widget._success_text == "Done!"
    assert widget._error_text == "Oops"


def test_initialization_hidden():
    """Test hidden initialization."""
    widget = TimerWidget(visible=False)
    assert widget.display is False


# Test color validation
def test_color_validation():
    """Test hex color validation."""
    widget = TimerWidget()

    widget.color = "#FF0000"
    assert widget.color == "#FF0000"

    with pytest.raises(ValueError, match="Invalid hex color"):
        widget.color = "red"
    with pytest.raises(ValueError, match="Invalid hex color"):
        widget.color = "#FF"
    with pytest.raises(ValueError, match="Invalid hex"):
        widget.color = "#GGGGGG"


def test_color_validation_in_constructor():
    """Test color validation during construction."""
    with pytest.raises(ValueError):
        TimerWidget(color="invalid")


# Test format styles — seconds variants
def test_format_seconds():
    """Test seconds format."""
    widget = TimerWidget(format_style="seconds")
    assert widget._format_time(3.456) == "3s"
    assert widget._format_time(45.789) == "45s"
    assert widget._format_time(0) == "0s"


def test_format_seconds_decimal():
    """Test seconds_decimal format with precision."""
    widget = TimerWidget(format_style="seconds_decimal", precision=1)
    assert widget._format_time(3.456) == "3.5s"

    widget._precision = 2
    assert widget._format_time(3.456) == "3.46s"

    widget._precision = 3
    assert widget._format_time(3.456) == "3.456s"


def test_format_seconds_precise():
    """Test seconds_precise format (always 3 decimals)."""
    widget = TimerWidget(format_style="seconds_precise")
    assert widget._format_time(3.456789) == "3.457s"
    assert widget._format_time(0) == "0.000s"
    assert widget._format_time(10.1) == "10.100s"


def test_format_milliseconds():
    """Test milliseconds format."""
    widget = TimerWidget(format_style="milliseconds")
    assert widget._format_time(1.234) == "1234ms"
    assert widget._format_time(0.567) == "567ms"
    assert widget._format_time(10.001) == "10001ms"


# Test format styles — duration variants
def test_format_duration_mmss():
    """Test mm:ss format."""
    widget = TimerWidget(format_style="mm:ss")
    assert widget._format_time(0) == "00:00"
    assert widget._format_time(59) == "00:59"
    assert widget._format_time(60) == "01:00"
    assert widget._format_time(83) == "01:23"
    assert widget._format_time(3661) == "61:01"  # Shows total minutes


def test_format_duration_hhmmss():
    """Test hh:mm:ss format."""
    widget = TimerWidget(format_style="hh:mm:ss")
    assert widget._format_time(0) == "00:00"
    assert widget._format_time(59) == "00:59"
    assert widget._format_time(3600) == "1:00:00"
    assert widget._format_time(3661) == "1:01:01"
    assert widget._format_time(7323) == "2:02:03"


def test_format_compact():
    """Test compact format (hours only if > 0)."""
    widget = TimerWidget(format_style="compact")
    assert widget._format_time(45) == "0:45"
    assert widget._format_time(60) == "1:00"
    assert widget._format_time(3661) == "1:01:01"


def test_format_full_ms():
    """Test full_ms format with milliseconds."""
    widget = TimerWidget(format_style="full_ms")
    assert widget._format_time(1.234) == "1.234"
    assert widget._format_time(59.999) == "59.999"
    assert widget._format_time(60.123) == "1:00.122"
    assert widget._format_time(123.456) == "2:03.456"


# Test format styles — auto variants
def test_format_auto():
    """Test auto format switching at boundaries."""
    widget = TimerWidget(format_style="auto")

    # Under 60s: show seconds
    assert widget._format_time(5) == "5s"
    assert widget._format_time(59) == "59s"

    # 60s-1hr: show mm:ss
    assert widget._format_time(60) == "1:00"
    assert widget._format_time(90) == "1:30"
    assert widget._format_time(3599) == "59:59"

    # 1hr+: show hh:mm:ss
    assert widget._format_time(3600) == "1:00:00"
    assert widget._format_time(7323) == "2:02:03"


def test_format_auto_ms():
    """Test auto_ms format (decimals under 10s)."""
    widget = TimerWidget(format_style="auto_ms")
    assert widget._format_time(5.5) == "5.5s"
    assert widget._format_time(9.9) == "9.9s"
    assert widget._format_time(10.1) == "10s"
    assert widget._format_time(60) == "1:00"


# Test precision settings
def test_precision_settings():
    """Test precision settings for decimal formats."""
    widget = TimerWidget(format_style="seconds_decimal", precision=0)
    assert widget._format_time(3.789) == "4s"

    widget._precision = 1
    assert widget._format_time(3.789) == "3.8s"

    widget._precision = 2
    assert widget._format_time(3.789) == "3.79s"

    widget._precision = 3
    assert widget._format_time(3.789) == "3.789s"


# Test render output
def test_render_in_progress():
    """Test render output in IN_PROGRESS state."""
    widget = TimerWidget(format_style="seconds")
    widget._elapsed = 5.0
    rendered = widget.render()
    assert isinstance(rendered, Text)
    assert rendered.plain == "5s"


def test_render_success_default():
    """Test render in success state shows frozen time."""
    widget = TimerWidget(format_style="seconds")
    widget._elapsed = 10.0
    widget._state = ComponentState.SUCCESS
    rendered = widget.render()
    assert isinstance(rendered, Text)
    assert rendered.plain == "10s"


def test_render_success_custom_text():
    """Test render in success state with custom text."""
    widget = TimerWidget(success_text="Complete!")
    widget._state = ComponentState.SUCCESS
    rendered = widget.render()
    assert rendered.plain == "Complete!"


def test_render_error_default():
    """Test render in error state shows frozen time."""
    widget = TimerWidget(format_style="seconds")
    widget._elapsed = 5.0
    widget._state = ComponentState.ERROR
    rendered = widget.render()
    assert rendered.plain == "5s"


def test_render_error_custom_text():
    """Test render in error state with custom text."""
    widget = TimerWidget(error_text="Failed!")
    widget._state = ComponentState.ERROR
    rendered = widget.render()
    assert rendered.plain == "Failed!"


# Test timer control methods (sync, no app)
def test_timer_start():
    """Test starting the timer."""
    widget = TimerWidget()
    widget.start()
    assert widget.running
    assert widget._start_time is not None
    assert not widget.paused


def test_timer_stop():
    """Test stopping the timer."""
    widget = TimerWidget()
    widget.start()
    time.sleep(0.05)
    widget.stop()
    assert not widget.running
    assert widget._start_time is None
    assert widget._elapsed > 0


def test_timer_resume():
    """Test resuming the timer."""
    widget = TimerWidget()
    widget.start()
    time.sleep(0.05)
    widget.stop()
    elapsed_after_stop = widget.get_elapsed()

    widget.resume()
    assert widget.running
    time.sleep(0.05)
    assert widget.get_elapsed() > elapsed_after_stop


def test_timer_pause():
    """Test pausing and unpausing the timer."""
    widget = TimerWidget()
    widget.start()
    time.sleep(0.05)

    widget.pause()
    assert widget.paused
    assert widget._start_time is None
    elapsed_when_paused = widget.get_elapsed()
    assert elapsed_when_paused > 0

    # Elapsed should not change while paused
    time.sleep(0.05)
    assert widget.get_elapsed() == elapsed_when_paused

    # Unpause
    widget.pause()
    assert not widget.paused
    assert widget._start_time is not None
    time.sleep(0.05)
    assert widget.get_elapsed() > elapsed_when_paused


def test_timer_reset():
    """Test resetting the timer."""
    widget = TimerWidget()
    widget.start()
    time.sleep(0.05)
    widget.reset()
    assert widget.get_elapsed() < 0.01
    assert widget.state == ComponentState.IN_PROGRESS
    assert not widget.paused


def test_timer_reset_while_stopped():
    """Test resetting while stopped."""
    widget = TimerWidget()
    widget.start()
    time.sleep(0.05)
    widget.stop()
    widget.reset()
    assert widget.get_elapsed() == 0
    assert not widget.running


def test_get_elapsed():
    """Test get_elapsed accumulates correctly."""
    widget = TimerWidget()

    # First cycle
    widget.start()
    time.sleep(0.05)
    widget.stop()
    elapsed1 = widget.get_elapsed()
    assert elapsed1 > 0

    # Second cycle (should accumulate)
    widget.resume()
    time.sleep(0.05)
    widget.stop()
    elapsed2 = widget.get_elapsed()
    assert elapsed2 > elapsed1

    # Frozen after stop
    time.sleep(0.05)
    assert widget.get_elapsed() == elapsed2


def test_is_running():
    """Test is_running method."""
    widget = TimerWidget()
    assert not widget.is_running()

    widget.start()
    assert widget.is_running()

    widget.stop()
    assert not widget.is_running()

    widget.resume()
    assert widget.is_running()


# Test edge cases
def test_edge_cases():
    """Test edge cases."""
    widget = TimerWidget()

    # Stop without start
    widget.stop()
    assert widget.get_elapsed() == 0

    # Double start (should not restart)
    widget.start()
    start_time = widget._start_time
    widget.start()
    assert widget._start_time == start_time

    # Resume while running (should be no-op since already running)
    widget.resume()
    assert widget.running

    # Pause when not in IN_PROGRESS
    widget.stop()
    widget._state = ComponentState.SUCCESS
    widget._timer_active = True  # Force for test
    widget.pause()  # Should be no-op (not IN_PROGRESS)
    assert not widget.paused

    # Pause when not running
    widget._state = ComponentState.IN_PROGRESS
    widget._timer_active = False
    widget.pause()  # Should be no-op (not running)
    assert not widget.paused


# Test state transitions
def test_state_transitions():
    """Test valid and invalid state transitions."""
    widget = TimerWidget()

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


def test_success_stops_timer():
    """Test that success() stops a running timer."""
    widget = TimerWidget()
    widget.start()
    time.sleep(0.05)
    widget.success()
    assert not widget.running
    assert widget._elapsed > 0


def test_error_stops_timer():
    """Test that error() stops a running timer."""
    widget = TimerWidget()
    widget.start()
    time.sleep(0.05)
    widget.error()
    assert not widget.running
    assert widget._elapsed > 0


def test_success_with_custom_text():
    """Test success with custom text updates the text."""
    widget = TimerWidget()
    widget.success("Complete!")
    assert widget._success_text == "Complete!"
    assert widget.render().plain == "Complete!"


def test_error_with_custom_text():
    """Test error with custom text updates the text."""
    widget = TimerWidget()
    widget.error("Timed out")
    assert widget._error_text == "Timed out"
    assert widget.render().plain == "Timed out"


# Test from_config
def test_from_config():
    """Test factory method from configuration dictionary."""
    config = {
        "format_style": "seconds_decimal",
        "precision": 2,
        "color": "#FFA500",
        "success_text": "OK",
        "error_text": "ERR",
        "visible": False,
    }
    widget = TimerWidget.from_config(config)
    assert widget.format_style == "seconds_decimal"
    assert widget.precision == 2
    assert widget.color == "#FFA500"
    assert widget._success_text == "OK"
    assert widget._error_text == "ERR"
    assert widget.display is False


def test_from_config_defaults():
    """Test from_config with empty config uses defaults."""
    widget = TimerWidget.from_config({})
    assert widget.format_style == "auto"
    assert widget.precision == 1
    assert widget.color == "#FFFF55"
    assert widget._success_text is None
    assert widget._error_text is None


# Test repr
def test_repr():
    """Test string representation."""
    widget = TimerWidget(format_style="seconds")
    repr_str = repr(widget)
    assert "TimerWidget" in repr_str
    assert "seconds" in repr_str
    assert "IN_PROGRESS" in repr_str


# Test feature parity
def test_feature_parity():
    """Verify all Rich TimerComponent APIs are available."""
    widget = TimerWidget()

    # Timer control methods
    assert hasattr(widget, "start")
    assert hasattr(widget, "stop")
    assert hasattr(widget, "resume")
    assert hasattr(widget, "pause")
    assert hasattr(widget, "reset")
    assert hasattr(widget, "get_elapsed")
    assert hasattr(widget, "is_running")

    # State methods
    assert hasattr(widget, "success")
    assert hasattr(widget, "error")

    # Properties
    assert hasattr(widget, "format_style")
    assert hasattr(widget, "precision")
    assert hasattr(widget, "state")
    assert hasattr(widget, "running")
    assert hasattr(widget, "paused")

    # Factory
    assert hasattr(TimerWidget, "from_config")

    # Visibility
    assert hasattr(widget, "show")
    assert hasattr(widget, "hide")
    assert hasattr(widget, "toggle")
    assert hasattr(widget, "set_visible")


# Test CSS defaults
def test_css_defaults():
    """Test DEFAULT_CSS is properly defined."""
    assert "TimerWidget" in TimerWidget.DEFAULT_CSS
    assert "success" in TimerWidget.DEFAULT_CSS
    assert "error" in TimerWidget.DEFAULT_CSS


# Async tests with Textual app
@pytest.mark.asyncio
async def test_timer_start_stop():
    """Test timer start/stop in app context."""

    class TimerApp(App):
        def compose(self) -> ComposeResult:
            yield TimerWidget(format_style="seconds", id="timer")

    async with TimerApp().run_test() as pilot:
        timer = pilot.app.query_one("#timer", TimerWidget)
        assert not timer.running

        timer.start()
        await pilot.pause()
        assert timer.running
        assert timer.get_elapsed() > 0

        timer.stop()
        await pilot.pause()
        assert not timer.running
        frozen = timer.get_elapsed()
        await pilot.pause()
        assert timer.get_elapsed() == frozen


@pytest.mark.asyncio
async def test_timer_pause_resume():
    """Test timer pause/resume in app context."""

    class TimerApp(App):
        def compose(self) -> ComposeResult:
            yield TimerWidget(id="timer")

    async with TimerApp().run_test() as pilot:
        timer = pilot.app.query_one("#timer", TimerWidget)

        timer.start()
        await pilot.pause()

        timer.pause()
        await pilot.pause()
        assert timer.paused
        paused_elapsed = timer.get_elapsed()

        await pilot.pause()
        assert timer.get_elapsed() == paused_elapsed

        timer.pause()  # Unpause
        await pilot.pause()
        assert not timer.paused


@pytest.mark.asyncio
async def test_timer_display_updates():
    """Test that render output reflects elapsed time."""

    class TimerApp(App):
        def compose(self) -> ComposeResult:
            yield TimerWidget(format_style="seconds_precise", id="timer")

    async with TimerApp().run_test() as pilot:
        timer = pilot.app.query_one("#timer", TimerWidget)
        assert timer.render().plain == "0.000s"

        timer.start()
        await pilot.pause()
        rendered = timer.render().plain
        assert rendered.endswith("s")


@pytest.mark.asyncio
async def test_state_css_classes():
    """Test CSS classes are set correctly on state changes."""

    class StateApp(App):
        def compose(self) -> ComposeResult:
            yield TimerWidget(id="timer")

    async with StateApp().run_test() as pilot:
        timer = pilot.app.query_one("#timer", TimerWidget)

        assert "success" not in timer.classes
        assert "error" not in timer.classes

        timer.success()
        await pilot.pause()
        assert "success" in timer.classes
        assert "error" not in timer.classes

        timer.reset()
        await pilot.pause()
        assert "success" not in timer.classes
        assert "error" not in timer.classes

        timer.error()
        await pilot.pause()
        assert "error" in timer.classes
        assert "success" not in timer.classes


@pytest.mark.asyncio
async def test_visibility_toggle():
    """Test display property-based visibility changes."""

    class VisApp(App):
        def compose(self) -> ComposeResult:
            yield TimerWidget(id="timer")

    async with VisApp().run_test() as pilot:
        timer = pilot.app.query_one("#timer", TimerWidget)

        assert timer.display is True

        timer.hide()
        await pilot.pause()
        assert timer.display is False

        timer.show()
        await pilot.pause()
        assert timer.display is True

        timer.toggle()
        await pilot.pause()
        assert timer.display is False

        timer.set_visible(True)
        await pilot.pause()
        assert timer.display is True


@pytest.mark.asyncio
async def test_app_integration():
    """Test widget in full Textual app lifecycle."""

    class IntegrationApp(App):
        def compose(self) -> ComposeResult:
            yield TimerWidget(format_style="seconds", id="t1")
            yield TimerWidget(format_style="auto_ms", color="#FF00FF", id="t2")

    async with IntegrationApp().run_test() as pilot:
        t1 = pilot.app.query_one("#t1", TimerWidget)
        t2 = pilot.app.query_one("#t2", TimerWidget)

        assert t1.render().plain == "0s"
        assert t2.color == "#FF00FF"

        t1.start()
        await pilot.pause()
        assert t1.running

        t1.success("Done")
        await pilot.pause()
        assert t1.state == ComponentState.SUCCESS
        assert t1.render().plain == "Done"
        assert not t1.running

        t2.start()
        await pilot.pause()
        t2.error("Timeout")
        await pilot.pause()
        assert t2.state == ComponentState.ERROR
        assert t2.render().plain == "Timeout"

        t2.reset()
        await pilot.pause()
        assert t2.state == ComponentState.IN_PROGRESS


@pytest.mark.asyncio
async def test_widget_lifecycle():
    """Test widget mount/unmount lifecycle."""

    class LifecycleApp(App):
        def compose(self) -> ComposeResult:
            yield TimerWidget(id="timer")

    async with LifecycleApp().run_test() as pilot:
        timer = pilot.app.query_one("#timer", TimerWidget)
        assert timer.is_mounted

        timer.start()
        await pilot.pause()
        assert timer.running

        rendered = timer.render()
        assert isinstance(rendered, Text)

        await timer.remove()
        assert timer not in pilot.app.query(TimerWidget)
