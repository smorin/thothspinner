"""Tests for ProgressComponent."""

from unittest.mock import MagicMock

from rich.console import Console
from rich.measure import Measurement
from rich.text import Text

from thothspinner.core.states import ComponentState
from thothspinner.rich.components.progress import ProgressComponent


class TestProgressInitialization:
    """Test ProgressComponent initialization."""

    def test_default_initialization(self):
        """Test default values on construction."""
        progress = ProgressComponent()
        assert progress.current == 0
        assert progress.total == 100
        assert progress.format_style == "fraction"
        assert progress.zero_pad is False
        assert progress.visible is True
        assert progress._state == ComponentState.IN_PROGRESS

    def test_custom_initialization(self):
        """Test custom values on construction."""
        progress = ProgressComponent(
            current=10, total=50, format={"style": "percentage"}, zero_pad=True, visible=False
        )
        assert progress.current == 10
        assert progress.total == 50
        assert progress.format_style == "percentage"
        assert progress.zero_pad is True
        assert progress.visible is False


class TestProgressFormatStyles:
    """Test all progress format styles."""

    def test_fraction_format(self):
        """Test fraction format (default)."""
        progress = ProgressComponent(current=25, total=100)
        assert progress._format_progress() == "25/100"

    def test_percentage_format(self):
        """Test percentage format."""
        progress = ProgressComponent(current=25, total=100, format={"style": "percentage"})
        assert progress._format_progress() == "25%"

    def test_of_text_format(self):
        """Test 'of' text format."""
        progress = ProgressComponent(current=25, total=100, format={"style": "of_text"})
        assert progress._format_progress() == "25 of 100"

    def test_count_only_format(self):
        """Test count only format."""
        progress = ProgressComponent(current=25, total=100, format={"style": "count_only"})
        assert progress._format_progress() == "25"

    def test_ratio_format(self):
        """Test ratio format."""
        progress = ProgressComponent(current=25, total=100, format={"style": "ratio"})
        assert progress._format_progress() == "25:100"

    def test_zero_pad(self):
        """Test zero padding."""
        progress = ProgressComponent(current=5, total=100, zero_pad=True)
        assert progress._format_progress() == "005/100"


class TestProgressUpdates:
    """Test progress update methods."""

    def test_increment(self):
        """Test incrementing progress."""
        progress = ProgressComponent(current=0, total=10)
        progress.increment()
        assert progress.current == 1

    def test_increment_at_max(self):
        """Test increment does nothing at max."""
        progress = ProgressComponent(current=10, total=10)
        progress.increment()
        assert progress.current == 10

    def test_set(self):
        """Test setting progress value."""
        progress = ProgressComponent(total=100)
        progress.set(50)
        assert progress.current == 50

    def test_set_clamps(self):
        """Test set clamps to valid range."""
        progress = ProgressComponent(total=100)
        progress.set(200)
        assert progress.current == 100
        progress.set(-10)
        assert progress.current == 0

    def test_set_percentage(self):
        """Test setting progress by percentage."""
        progress = ProgressComponent(total=200)
        progress.set_percentage(50)
        assert progress.current == 100

    def test_add(self):
        """Test adding to progress."""
        progress = ProgressComponent(current=10, total=100)
        progress.add(15)
        assert progress.current == 25

    def test_is_complete(self):
        """Test completion check."""
        progress = ProgressComponent(current=99, total=100)
        assert progress.is_complete() is False
        progress.increment()
        assert progress.is_complete() is True


class TestProgressStateManagement:
    """Test state transitions."""

    def test_success_transition(self):
        """Test transition to success state."""
        progress = ProgressComponent()
        progress.success()
        assert progress._state == ComponentState.SUCCESS

    def test_success_with_custom_text(self):
        """Test success with custom text."""
        progress = ProgressComponent()
        progress.success("All done!")
        assert progress._state == ComponentState.SUCCESS
        assert progress._format_progress() == "All done!"

    def test_error_transition(self):
        """Test transition to error state."""
        progress = ProgressComponent()
        progress.error()
        assert progress._state == ComponentState.ERROR

    def test_error_with_custom_text(self):
        """Test error with custom text."""
        progress = ProgressComponent()
        progress.error("Something broke")
        assert progress._state == ComponentState.ERROR
        assert progress._format_progress() == "Something broke"

    def test_invalid_transition_success_to_error(self):
        """Test that SUCCESS -> ERROR transition is blocked."""
        progress = ProgressComponent()
        progress.success()
        assert progress._state == ComponentState.SUCCESS
        progress.error()
        assert progress._state == ComponentState.SUCCESS  # Unchanged

    def test_invalid_transition_error_to_success(self):
        """Test that ERROR -> SUCCESS transition is blocked."""
        progress = ProgressComponent()
        progress.error()
        assert progress._state == ComponentState.ERROR
        progress.success()
        assert progress._state == ComponentState.ERROR  # Unchanged

    def test_reset(self):
        """Test reset to in_progress."""
        progress = ProgressComponent(current=50, total=100)
        progress.success()
        progress.reset()
        assert progress._state == ComponentState.IN_PROGRESS
        assert progress.current == 0


class TestProgressRendering:
    """Test Rich rendering."""

    def test_rich_console_renders(self):
        """Test __rich_console__ yields segments."""
        progress = ProgressComponent(current=25, total=100)
        console = Console()
        options = MagicMock()
        segments = list(progress.__rich_console__(console, options))
        assert len(segments) == 1
        assert segments[0].text == "25/100"

    def test_rich_console_invisible(self):
        """Test invisible component yields nothing."""
        progress = ProgressComponent(visible=False)
        console = Console()
        options = MagicMock()
        segments = list(progress.__rich_console__(console, options))
        assert len(segments) == 0

    def test_rich_measure(self):
        """Test __rich_measure__ returns correct width."""
        progress = ProgressComponent(current=25, total=100)
        console = Console()
        options = console.options
        measurement = progress.__rich_measure__(console, options)
        assert measurement.minimum > 0
        assert measurement.maximum > 0

    def test_rich_measure_invisible(self):
        """Test invisible component has zero measurement."""
        progress = ProgressComponent(visible=False)
        console = Console()
        options = console.options
        measurement = progress.__rich_measure__(console, options)
        assert measurement == Measurement(0, 0)

    def test_rich_protocol(self):
        """Test __rich__ returns Text object."""
        progress = ProgressComponent(current=10, total=50)
        result = progress.__rich__()
        assert isinstance(result, Text)
        assert str(result) == "10/50"
