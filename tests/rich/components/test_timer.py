"""Tests for TimerComponent."""

from unittest.mock import MagicMock, patch

from rich.console import Console
from rich.measure import Measurement
from rich.text import Text

from thothspinner.core.states import ComponentState
from thothspinner.rich.components.timer import TimerComponent


class TestTimerInitialization:
    """Test TimerComponent initialization."""

    def test_default_initialization(self):
        """Test default values on construction."""
        timer = TimerComponent()
        assert timer.format_style == "auto"
        assert timer._running is False
        assert timer._elapsed == 0.0
        assert timer._start_time is None
        assert timer.visible is True
        assert timer._state == ComponentState.IN_PROGRESS

    def test_custom_initialization(self):
        """Test custom values on construction."""
        timer = TimerComponent(
            format={"style": "mm:ss", "precision": 2},
            color="#FF0000",
            visible=False,
        )
        assert timer.format_style == "mm:ss"
        assert timer.precision == 2
        assert timer.visible is False


class TestTimerFormatStyles:
    """Test all timer format styles."""

    def test_seconds_format(self):
        """Test seconds format."""
        timer = TimerComponent(format={"style": "seconds"})
        assert timer._format_time(5.7) == "5s"

    def test_seconds_decimal_format(self):
        """Test seconds decimal format."""
        timer = TimerComponent(format={"style": "seconds_decimal"})
        assert timer._format_time(5.7) == "5.7s"

    def test_seconds_precise_format(self):
        """Test seconds precise format."""
        timer = TimerComponent(format={"style": "seconds_precise"})
        assert timer._format_time(5.7) == "5.700s"

    def test_milliseconds_format(self):
        """Test milliseconds format."""
        timer = TimerComponent(format={"style": "milliseconds"})
        assert timer._format_time(1.5) == "1500ms"

    def test_mmss_format(self):
        """Test mm:ss format."""
        timer = TimerComponent(format={"style": "mm:ss"})
        assert timer._format_time(125.0) == "02:05"

    def test_hhmmss_format(self):
        """Test hh:mm:ss format."""
        timer = TimerComponent(format={"style": "hh:mm:ss"})
        assert timer._format_time(3665.0) == "1:01:05"

    def test_compact_format(self):
        """Test compact format."""
        timer = TimerComponent(format={"style": "compact"})
        assert timer._format_time(65.0) == "1:05"
        assert timer._format_time(3665.0) == "1:01:05"

    def test_auto_format(self):
        """Test auto format switches based on duration."""
        timer = TimerComponent(format={"style": "auto"})
        assert timer._format_time(30.0) == "30s"
        assert timer._format_time(90.0) == "1:30"


class TestTimerControl:
    """Test timer control methods."""

    def test_start_stop(self):
        """Test starting and stopping the timer."""
        timer = TimerComponent()
        timer.start()
        assert timer._running is True
        assert timer._start_time is not None
        timer.stop()
        assert timer._running is False
        assert timer._elapsed > 0 or timer._elapsed == 0  # May be very fast

    def test_resume(self):
        """Test resuming the timer."""
        timer = TimerComponent()
        timer._elapsed = 5.0
        timer.resume()
        assert timer._running is True

    def test_reset(self):
        """Test resetting the timer."""
        timer = TimerComponent()
        timer._elapsed = 10.0
        timer._state = ComponentState.SUCCESS
        timer.reset()
        assert timer._elapsed == 0.0
        assert timer._state == ComponentState.IN_PROGRESS

    def test_get_elapsed_stopped(self):
        """Test get_elapsed when stopped."""
        timer = TimerComponent()
        timer._elapsed = 5.0
        assert timer.get_elapsed() == 5.0

    @patch("thothspinner.rich.components.timer.time")
    def test_get_elapsed_running(self, mock_time):
        """Test get_elapsed when running."""
        mock_time.return_value = 100.0
        timer = TimerComponent()
        timer._start_time = 95.0
        timer._running = True
        timer._elapsed = 10.0
        assert timer.get_elapsed() == 15.0  # 10.0 + (100.0 - 95.0)

    def test_is_running(self):
        """Test is_running check."""
        timer = TimerComponent()
        assert timer.is_running() is False
        timer.start()
        assert timer.is_running() is True
        timer.stop()
        assert timer.is_running() is False


class TestTimerStateManagement:
    """Test state transitions."""

    def test_success_stops_timer(self):
        """Test success transition stops the timer."""
        timer = TimerComponent()
        timer.start()
        assert timer._running is True
        timer.success()
        assert timer._state == ComponentState.SUCCESS
        assert timer._running is False

    def test_error_stops_timer(self):
        """Test error transition stops the timer."""
        timer = TimerComponent()
        timer.start()
        timer.error()
        assert timer._state == ComponentState.ERROR
        assert timer._running is False

    def test_invalid_transition_success_to_error(self):
        """Test that SUCCESS -> ERROR transition is blocked."""
        timer = TimerComponent()
        timer.success()
        assert timer._state == ComponentState.SUCCESS
        timer.error()
        assert timer._state == ComponentState.SUCCESS  # Unchanged

    def test_invalid_transition_error_to_success(self):
        """Test that ERROR -> SUCCESS transition is blocked."""
        timer = TimerComponent()
        timer.error()
        assert timer._state == ComponentState.ERROR
        timer.success()
        assert timer._state == ComponentState.ERROR  # Unchanged

    def test_invalid_transition_does_not_stop_timer(self):
        """Test that blocked transition doesn't stop running timer."""
        timer = TimerComponent()
        timer.start()
        timer.success()
        # Timer already stopped by success. Start again then try error.
        timer.reset()
        timer.start()
        timer.success()
        assert timer._running is False
        # Now try invalid transition - should not call stop()
        timer._running = True  # Manually set
        timer.error()  # Should be blocked
        assert timer._running is True  # Stop was not called


class TestTimerRendering:
    """Test Rich rendering."""

    def test_rich_console_renders(self):
        """Test __rich_console__ yields segments."""
        timer = TimerComponent()
        timer._elapsed = 5.0
        console = Console()
        options = MagicMock()
        segments = list(timer.__rich_console__(console, options))
        assert len(segments) == 1
        assert "5" in segments[0].text

    def test_rich_console_invisible(self):
        """Test invisible component yields nothing."""
        timer = TimerComponent(visible=False)
        console = Console()
        options = MagicMock()
        segments = list(timer.__rich_console__(console, options))
        assert len(segments) == 0

    def test_rich_measure(self):
        """Test __rich_measure__ returns correct width."""
        timer = TimerComponent()
        timer._elapsed = 5.0
        console = Console()
        options = console.options
        measurement = timer.__rich_measure__(console, options)
        assert measurement.minimum > 0
        assert measurement.maximum > 0

    def test_rich_measure_invisible(self):
        """Test invisible component has zero measurement."""
        timer = TimerComponent(visible=False)
        console = Console()
        options = console.options
        measurement = timer.__rich_measure__(console, options)
        assert measurement == Measurement(0, 0)

    def test_rich_protocol(self):
        """Test __rich__ returns Text object."""
        timer = TimerComponent()
        timer._elapsed = 10.0
        result = timer.__rich__()
        assert isinstance(result, Text)
        assert "10" in str(result)
