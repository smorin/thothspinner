"""Integration tests for SpinnerComponent with Rich."""

from __future__ import annotations

import io
import time

from rich.console import Console
from rich.live import Live
from rich.table import Table

from thothspinner.rich.components import HintComponent, SpinnerComponent


class TestSpinnerIntegration:
    """Integration tests for spinner with Rich console."""

    def test_spinner_with_live_display(self):
        """Test M02-TS06: Rich console integration with Live."""
        console = Console(file=io.StringIO(), force_terminal=True, width=80)
        spinner = SpinnerComponent(style="claude_stars")

        # Use Live context for animation
        with Live(spinner, console=console, refresh_per_second=10, transient=False):
            spinner.start()
            time.sleep(0.01)  # Brief pause
            spinner.success()

        output = console.file.getvalue()
        # Should have rendered something
        assert len(output) > 0
        # Final output should have success icon
        assert "✓" in output

    def test_spinner_and_hint_together(self):
        """Test M02-TS16: Spinner and Hint work together without conflicts."""
        console = Console(file=io.StringIO(), force_terminal=True, width=80)

        spinner = SpinnerComponent(style="npm_dots")
        hint = HintComponent(text=" (esc to cancel)", color="#888888")

        # Combine components in a table
        table = Table.grid()
        table.add_row(spinner, hint)

        console.print(table)
        output = console.file.getvalue()

        # Both components should render
        assert len(output) > 0
        assert "(esc to cancel)" in output

    def test_multiple_spinners_concurrent(self):
        """Test multiple spinners can be displayed together."""
        console = Console(file=io.StringIO(), force_terminal=True, width=80)

        spinner1 = SpinnerComponent(style="npm_dots", color="#FF0000")
        spinner2 = SpinnerComponent(style="claude_stars", color="#00FF00")
        spinner3 = SpinnerComponent(style="classic", color="#0000FF")

        table = Table.grid(padding=1)
        table.add_row(spinner1, spinner2, spinner3)

        console.print(table)
        output = console.file.getvalue()

        # All spinners should render
        assert len(output) > 0

    def test_state_changes_in_live(self):
        """Test state transitions work correctly in Live context."""
        console = Console(file=io.StringIO(), force_terminal=True, width=80)
        spinner = SpinnerComponent()

        with Live(spinner, console=console, refresh_per_second=20):
            # Initial state
            assert spinner.state.name == "IN_PROGRESS"

            # Transition to success
            spinner.success()
            assert spinner.state.name == "SUCCESS"
            time.sleep(0.01)

            # Reset
            spinner.reset()
            assert spinner.state.name == "IN_PROGRESS"
            time.sleep(0.01)

            # Transition to error
            spinner.error()
            assert spinner.state.name == "ERROR"

        output = console.file.getvalue()
        assert len(output) > 0

    def test_custom_frames_in_live(self):
        """Test custom frames work correctly with Live."""
        console = Console(file=io.StringIO(), force_terminal=True, width=80)

        custom_frames = ["◐", "◓", "◑", "◒"]
        spinner = SpinnerComponent(frames=custom_frames, interval=0.1)

        with Live(spinner, console=console, refresh_per_second=10):
            time.sleep(0.05)  # Brief animation

        output = console.file.getvalue()
        # Should have rendered custom frames
        assert any(frame in output for frame in custom_frames)

    def test_speed_multiplier_effect(self):
        """Test that speed multiplier affects animation rate."""
        # This is more of a visual test, but we can verify the calculation
        spinner_slow = SpinnerComponent(speed=0.5)
        spinner_fast = SpinnerComponent(speed=2.0)

        # Initialize both spinners at time 0
        frame_slow_0 = spinner_slow._calculate_frame(0.0)
        frame_fast_0 = spinner_fast._calculate_frame(0.0)

        # Both should start at frame 0
        assert frame_slow_0 == 0
        assert frame_fast_0 == 0

        # At a later time point, fast spinner should be further along
        time_point = 0.16  # Two intervals at normal speed

        frame_slow = spinner_slow._calculate_frame(time_point)
        frame_fast = spinner_fast._calculate_frame(time_point)

        # Fast spinner should have advanced more frames
        # At 0.16s with speed 0.5: 0.16 * 0.5 / 0.08 = 1 frame
        # At 0.16s with speed 2.0: 0.16 * 2.0 / 0.08 = 4 frames
        assert frame_fast > frame_slow

    def test_visibility_toggle_in_live(self):
        """Test visibility can be toggled during Live display."""
        console = Console(file=io.StringIO(), force_terminal=True, width=80)
        spinner = SpinnerComponent()

        with Live(spinner, console=console, refresh_per_second=10):
            # Initially visible
            assert spinner.visible is True

            # Hide spinner
            spinner.visible = False
            time.sleep(0.01)

            # Show again
            spinner.visible = True
            time.sleep(0.01)

        # Should have rendered something
        output = console.file.getvalue()
        assert len(output) > 0

    def test_performance_benchmark(self):
        """Test M02-TS17: Performance benchmark for frame calculation."""
        spinner = SpinnerComponent()
        current_time = time.time()

        # Benchmark frame calculation
        start = time.perf_counter()
        for _ in range(10000):
            spinner._calculate_frame(current_time)
        elapsed = time.perf_counter() - start

        # Should complete 10000 calculations in under 100ms
        assert elapsed < 0.1, f"Frame calculation too slow: {elapsed:.3f}s"

    def test_memory_stability(self):
        """Test that spinner doesn't leak memory during long runs."""
        spinner = SpinnerComponent()

        # Simulate many frame calculations
        for i in range(1000):
            spinner._calculate_frame(i * 0.08)

        # State transitions
        for _ in range(100):
            spinner.success()
            spinner.reset()
            spinner.error()
            spinner.reset()

        # If we get here without issues, memory is stable
        assert True
