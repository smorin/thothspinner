"""Pytest configuration and fixtures."""

import io

import pytest
from rich.console import Console


def make_console(width: int = 80) -> Console:
    """Create a deterministic console for testing.

    Based on Rich's test patterns, creates a console with:
    - Fixed width for reproducible output
    - Forced terminal mode for ANSI codes
    - Deterministic color system
    - No environment variables
    """
    return Console(
        file=io.StringIO(),
        force_terminal=True,
        width=width,
        color_system="truecolor",
        legacy_windows=False,
        _environ={},
    )


@pytest.fixture
def console() -> Console:
    """Create a test console with standard settings."""
    return make_console(80)


@pytest.fixture
def capture_console() -> Console:
    """Create a console that captures output for assertions."""
    console = make_console(80)
    console.record = True
    return console


class MockClock:
    """A clock that is manually advanced for testing.

    Based on Rich's test patterns for deterministic time testing.
    """

    def __init__(self, time: float = 0.0, auto: bool = True):
        self.time = time
        self.auto = auto

    def __call__(self) -> float:
        """Return current time and optionally auto-advance."""
        try:
            return self.time
        finally:
            if self.auto:
                self.time += 1

    def tick(self, advance: float = 1) -> None:
        """Manually advance the clock."""
        self.time += advance


@pytest.fixture
def mock_time():
    """Provide controllable time for testing."""
    return MockClock()
