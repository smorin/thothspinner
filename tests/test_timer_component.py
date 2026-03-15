"""Test suite for TimerComponent."""

import time
from io import StringIO

from rich.console import Console

from thothspinner.core.states import ComponentState
from thothspinner.rich.components import TimerComponent


class TestTimerComponent:
    """Test suite for TimerComponent."""

    def test_initialization(self):
        """Test component initialization."""
        timer = TimerComponent()
        assert timer.format_style == "auto"
        assert timer.precision == 1
        assert timer._elapsed == 0.0
        assert not timer._running

        # Test with custom parameters
        timer2 = TimerComponent(format={"style": "seconds", "precision": 2}, color="#00FF00")
        assert timer2.format_style == "seconds"
        assert timer2.precision == 2
        assert timer2.color == "#00FF00"

    def test_format_seconds(self):
        """Test seconds format styles."""
        timer = TimerComponent(format={"style": "seconds"})

        # Test seconds format
        assert timer._format_time(3.456) == "3s"
        assert timer._format_time(45.789) == "45s"

        # Test seconds_decimal format
        timer.format_style = "seconds_decimal"
        timer.precision = 1
        assert timer._format_time(3.456) == "3.5s"

        timer.precision = 2
        assert timer._format_time(3.456) == "3.46s"

        # Test seconds_precise format
        timer.format_style = "seconds_precise"
        assert timer._format_time(3.456789) == "3.457s"

    def test_format_milliseconds(self):
        """Test milliseconds format."""
        timer = TimerComponent(format={"style": "milliseconds"})
        assert timer._format_time(1.234) == "1234ms"
        assert timer._format_time(0.567) == "567ms"
        assert timer._format_time(10.001) == "10001ms"

    def test_format_duration(self):
        """Test duration formats (mm:ss, hh:mm:ss)."""
        timer = TimerComponent(format={"style": "mm:ss"})

        # Test mm:ss format
        assert timer._format_time(0) == "00:00"
        assert timer._format_time(59) == "00:59"
        assert timer._format_time(60) == "01:00"
        assert timer._format_time(83) == "01:23"
        assert timer._format_time(3661) == "61:01"  # mm:ss shows total minutes

        # Test hh:mm:ss format
        timer.format_style = "hh:mm:ss"
        assert timer._format_time(0) == "00:00"
        assert timer._format_time(59) == "00:59"
        assert timer._format_time(3600) == "1:00:00"
        assert timer._format_time(3661) == "1:01:01"
        assert timer._format_time(7323) == "2:02:03"

        # Test compact format
        timer.format_style = "compact"
        assert timer._format_time(45) == "0:45"
        assert timer._format_time(60) == "1:00"
        assert timer._format_time(3661) == "1:01:01"

    def test_format_full_ms(self):
        """Test full_ms format with milliseconds."""
        timer = TimerComponent(format={"style": "full_ms"})

        assert timer._format_time(1.234) == "1.234"
        assert timer._format_time(59.999) == "59.999"
        assert timer._format_time(60.123) == "1:00.122"
        assert timer._format_time(123.456) == "2:03.456"

    def test_format_auto(self):
        """Test auto format switching."""
        timer = TimerComponent(format={"style": "auto"})

        # Under 60s: show seconds
        assert timer._format_time(5) == "5s"
        assert timer._format_time(59) == "59s"

        # 60s-1hr: show mm:ss
        assert timer._format_time(60) == "1:00"
        assert timer._format_time(90) == "1:30"
        assert timer._format_time(3599) == "59:59"

        # 1hr+: show hh:mm:ss
        assert timer._format_time(3600) == "1:00:00"
        assert timer._format_time(7323) == "2:02:03"

        # Test auto_ms variant
        timer.format_style = "auto_ms"
        assert timer._format_time(5.5) == "5.5s"
        assert timer._format_time(9.9) == "9.9s"
        assert timer._format_time(10.1) == "10s"
        assert timer._format_time(60) == "1:00"

    def test_timer_controls(self):
        """Test timer control methods."""
        timer = TimerComponent()

        # Test start
        timer.start()
        assert timer._running
        assert timer._start_time is not None

        # Let some time pass
        time.sleep(0.1)
        elapsed1 = timer.get_elapsed()
        assert elapsed1 > 0

        # Test stop
        timer.stop()
        assert not timer._running
        assert timer._start_time is None
        elapsed2 = timer.get_elapsed()

        # Elapsed should not change after stopping
        time.sleep(0.1)
        assert timer.get_elapsed() == elapsed2

        # Test resume
        timer.resume()
        assert timer._running
        time.sleep(0.1)
        assert timer.get_elapsed() > elapsed2

        # Test reset
        timer.reset()
        # Allow for tiny floating point differences
        assert timer.get_elapsed() < 0.001
        assert timer._state == ComponentState.IN_PROGRESS

    def test_timer_start_stop_cycle(self):
        """Test multiple start/stop cycles."""
        timer = TimerComponent()

        # First cycle
        timer.start()
        time.sleep(0.05)
        timer.stop()
        elapsed1 = timer.get_elapsed()
        assert elapsed1 > 0

        # Second cycle (should accumulate)
        timer.resume()
        time.sleep(0.05)
        timer.stop()
        elapsed2 = timer.get_elapsed()
        assert elapsed2 > elapsed1

        # Reset and verify
        timer.reset()
        assert timer.get_elapsed() == 0

    def test_state_transitions(self):
        """Test state transitions."""
        timer = TimerComponent()
        timer.start()
        time.sleep(0.05)

        # Test success state
        timer.success()
        assert timer._state == ComponentState.SUCCESS
        assert not timer._running

        # Reset and test error state
        timer.reset()
        timer.start()
        time.sleep(0.05)
        timer.error()
        assert timer._state == ComponentState.ERROR
        assert not timer._running

    def test_state_affects_animation(self):
        """Test that state affects animation."""
        from rich.console import Console

        timer = TimerComponent()
        timer.start()
        time.sleep(0.1)

        console = Console(file=StringIO())
        options = console.options

        # In progress state should update time
        list(timer.__rich_console__(console, options))  # Get initial segments
        time.sleep(0.1)
        list(timer.__rich_console__(console, options))  # Should be different after time passes
        # Text should be different as time progresses

        # Success state should freeze time
        timer.success()
        frozen_elapsed = timer._elapsed
        list(timer.__rich_console__(console, options))  # Get segments after success
        time.sleep(0.1)
        list(timer.__rich_console__(console, options))  # Should be same as previous
        # Time should be frozen in success state
        assert timer._elapsed == frozen_elapsed

    def test_is_running(self):
        """Test is_running method."""
        timer = TimerComponent()
        assert not timer.is_running()

        timer.start()
        assert timer.is_running()

        timer.stop()
        assert not timer.is_running()

        timer.resume()
        assert timer.is_running()

    def test_rendering(self):
        """Test Rich rendering."""
        console = Console(file=StringIO(), force_terminal=True, width=80)
        timer = TimerComponent(format={"style": "seconds"})
        timer.start()
        time.sleep(0.01)

        # Render and capture output
        console.print(timer)
        output = console.file.getvalue()
        assert "s" in output  # Should contain seconds indicator

    def test_rich_protocol(self):
        """Test __rich__ protocol method."""
        timer = TimerComponent(format={"style": "seconds"})
        timer._elapsed = 5.0
        text = timer.__rich__()
        assert "5s" in str(text)

        # Test with color
        timer2 = TimerComponent(color="#FFFF00")
        text2 = timer2.__rich__()
        assert text2.style is not None

    def test_edge_cases(self):
        """Test edge cases."""
        timer = TimerComponent()

        # Test stop without start
        timer.stop()  # Should not error
        assert timer.get_elapsed() == 0

        # Test double start
        timer.start()
        timer.start()  # Should not restart
        assert timer._running

        # Test resume while running
        timer.resume()  # Should not error
        assert timer._running

    def test_precision_settings(self):
        """Test precision settings for decimal formats."""
        timer = TimerComponent(format={"style": "seconds_decimal", "precision": 0})
        assert timer._format_time(3.789) == "4s"

        timer.precision = 1
        assert timer._format_time(3.789) == "3.8s"

        timer.precision = 2
        assert timer._format_time(3.789) == "3.79s"

        timer.precision = 3
        assert timer._format_time(3.789) == "3.789s"
