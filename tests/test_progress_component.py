"""Test suite for ProgressComponent."""

from io import StringIO

import pytest
from rich.console import Console

from thothspinner.rich.components import ProgressComponent
from thothspinner.rich.components.state import ComponentState


class TestProgressComponent:
    """Test suite for ProgressComponent."""

    def test_initialization(self):
        """Test component initialization."""
        progress = ProgressComponent(current=0, total=100)
        assert progress.current == 0
        assert progress.total == 100
        assert progress.format_style == "fraction"

        # Test with custom parameters
        progress2 = ProgressComponent(
            current=50, total=200, format={"style": "percentage"}, color="#FF0000"
        )
        assert progress2.current == 50
        assert progress2.total == 200
        assert progress2.format_style == "percentage"
        assert progress2.color == "#FF0000"

    def test_invalid_color(self):
        """Test invalid color raises ValueError."""
        with pytest.raises(ValueError, match="Invalid hex color"):
            ProgressComponent(color="red")

        with pytest.raises(ValueError, match="Invalid hex color"):
            ProgressComponent(color="#FFF")

        with pytest.raises(ValueError, match="Invalid hex color"):
            ProgressComponent(color="#GGGGGG")

    def test_format_styles(self):
        """Test all format styles."""
        progress = ProgressComponent(current=30, total=100)

        # Test fraction
        progress.format_style = "fraction"
        assert progress._format_progress() == "30/100"

        # Test percentage
        progress.format_style = "percentage"
        assert progress._format_progress() == "30%"

        # Test of_text
        progress.format_style = "of_text"
        assert progress._format_progress() == "30 of 100"

        # Test count_only
        progress.format_style = "count_only"
        assert progress._format_progress() == "30"

        # Test ratio
        progress.format_style = "ratio"
        assert progress._format_progress() == "30:100"

    def test_zero_padding(self):
        """Test zero padding feature."""
        progress = ProgressComponent(
            current=3, total=100, format={"style": "fraction"}, zero_pad=True
        )
        assert progress._format_progress() == "003/100"

        # Test with different total
        progress2 = ProgressComponent(
            current=5, total=1000, format={"style": "fraction"}, zero_pad=True
        )
        assert progress2._format_progress() == "0005/1000"

        # Test with of_text format
        progress3 = ProgressComponent(
            current=7, total=100, format={"style": "of_text"}, zero_pad=True
        )
        assert progress3._format_progress() == "007 of 100"

    def test_update_methods(self):
        """Test progress update methods."""
        progress = ProgressComponent(current=0, total=100)

        # Test increment
        progress.increment()
        assert progress.current == 1

        # Test set
        progress.set(50)
        assert progress.current == 50

        # Test set with overflow
        progress.set(150)
        assert progress.current == 100

        # Test set with negative
        progress.set(-10)
        assert progress.current == 0

        # Test add
        progress.set(10)
        progress.add(5)
        assert progress.current == 15

        # Test set_percentage
        progress.set_percentage(75)
        assert progress.current == 75

    def test_increment_boundary(self):
        """Test increment at boundary."""
        progress = ProgressComponent(current=99, total=100)
        progress.increment()
        assert progress.current == 100

        # Should not exceed total
        progress.increment()
        assert progress.current == 100

    def test_percentage_edge_cases(self):
        """Test percentage format with edge cases."""
        # Test 0%
        progress = ProgressComponent(current=0, total=100, format={"style": "percentage"})
        assert progress._format_progress() == "0%"

        # Test 100%
        progress.set(100)
        assert progress._format_progress() == "100%"

        # Test with zero total (division by zero)
        progress2 = ProgressComponent(current=0, total=0, format={"style": "percentage"})
        assert progress2._format_progress() == "0%"

    def test_state_transitions(self):
        """Test state transitions."""
        progress = ProgressComponent()
        assert progress._state == ComponentState.IN_PROGRESS

        # Test success
        progress.success("Complete!")
        assert progress._state == ComponentState.SUCCESS
        assert progress._state_configs[ComponentState.SUCCESS].text == "Complete!"

        # Test error
        progress.error("Failed")
        assert progress._state == ComponentState.ERROR
        assert progress._state_configs[ComponentState.ERROR].text == "Failed"

        # Test reset
        progress.set(50)
        progress.reset()
        assert progress._state == ComponentState.IN_PROGRESS
        assert progress.current == 0

    def test_state_display(self):
        """Test state affects display."""
        progress = ProgressComponent(current=50, total=100, format={"style": "percentage"})

        # Normal state shows percentage
        assert progress._format_progress() == "50%"

        # Success state shows custom text
        progress.success()
        assert progress._format_progress() == "100%"

        # Error state shows custom text
        progress.error()
        assert progress._format_progress() == "Failed"

    def test_is_complete(self):
        """Test is_complete method."""
        progress = ProgressComponent(current=0, total=100)
        assert not progress.is_complete()

        progress.set(100)
        assert progress.is_complete()

        progress.set(101)  # Should be capped at 100
        assert progress.is_complete()

    def test_rendering(self):
        """Test Rich rendering."""
        console = Console(file=StringIO(), force_terminal=True, width=80)
        progress = ProgressComponent(current=50, total=100, format={"style": "fraction"})

        # Render and capture output
        console.print(progress)
        output = console.file.getvalue()
        assert "50/100" in output

    def test_rich_protocol(self):
        """Test __rich__ protocol method."""
        progress = ProgressComponent(current=25, total=100, format={"style": "percentage"})
        text = progress.__rich__()
        assert str(text) == "25%"

        # Test with color
        progress2 = ProgressComponent(current=50, total=100, color="#00FF00")
        text2 = progress2.__rich__()
        assert text2.style is not None

    def test_console_rendering_with_states(self):
        """Test console rendering with different states."""
        from rich.console import Console

        console = Console(file=StringIO(), force_terminal=True)
        progress = ProgressComponent(current=100, total=100)

        # Create console options with required parameters
        options = console.options

        # Test normal rendering
        segments = list(progress.__rich_console__(console, options))
        assert len(segments) > 0

        # Test success state rendering
        progress.success()
        segments = list(progress.__rich_console__(console, options))
        assert len(segments) > 0

        # Test error state rendering
        progress.error()
        segments = list(progress.__rich_console__(console, options))
        assert len(segments) > 0
