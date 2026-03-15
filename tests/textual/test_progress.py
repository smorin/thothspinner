"""Comprehensive tests for the Textual ProgressWidget."""

import pytest
from rich.text import Text
from textual.app import App, ComposeResult

from thothspinner.core.states import ComponentState
from thothspinner.textual.widgets import ProgressWidget


# Test initialization and defaults
def test_initialization_defaults():
    """Test default initialization values outside app context."""
    widget = ProgressWidget()
    assert widget.current == 0
    assert widget.total == 100
    assert widget.format_style == "fraction"
    assert widget.color == "#D97706"
    assert widget.zero_pad is False
    assert widget.state == ComponentState.IN_PROGRESS
    assert widget._success_text == "100%"
    assert widget._error_text == "Failed"
    assert widget.display is True


def test_initialization_custom():
    """Test custom initialization."""
    widget = ProgressWidget(
        current=50,
        total=200,
        format_style="percentage",
        color="#FF0000",
        zero_pad=True,
        success_text="Done!",
        error_text="Oops",
    )
    assert widget.current == 50
    assert widget.total == 200
    assert widget.format_style == "percentage"
    assert widget.color == "#FF0000"
    assert widget.zero_pad is True
    assert widget._success_text == "Done!"
    assert widget._error_text == "Oops"


def test_initialization_hidden():
    """Test hidden initialization."""
    widget = ProgressWidget(visible=False)
    assert widget.display is False


def test_initialization_clamps_current():
    """Test current is clamped to [0, total] on init."""
    widget = ProgressWidget(current=150, total=100)
    assert widget.current == 100

    widget2 = ProgressWidget(current=-10, total=100)
    assert widget2.current == 0


# Test color validation
def test_color_validation():
    """Test hex color validation."""
    widget = ProgressWidget()

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
        ProgressWidget(color="invalid")


# Test format styles
def test_all_format_styles():
    """Test all 5 format styles."""
    widget = ProgressWidget(current=30, total=100)

    widget._format_style = "fraction"
    assert widget._format_progress() == "30/100"

    widget._format_style = "percentage"
    assert widget._format_progress() == "30%"

    widget._format_style = "of_text"
    assert widget._format_progress() == "30 of 100"

    widget._format_style = "count_only"
    assert widget._format_progress() == "30"

    widget._format_style = "ratio"
    assert widget._format_progress() == "30:100"


def test_zero_padding():
    """Test zero padding with various formats."""
    widget = ProgressWidget(current=3, total=100, zero_pad=True)

    widget._format_style = "fraction"
    assert widget._format_progress() == "003/100"

    widget._format_style = "of_text"
    assert widget._format_progress() == "003 of 100"

    widget._format_style = "count_only"
    assert widget._format_progress() == "003"

    widget._format_style = "ratio"
    assert widget._format_progress() == "003:100"

    # Wider total
    widget2 = ProgressWidget(current=5, total=1000, zero_pad=True, format_style="fraction")
    assert widget2._format_progress() == "0005/1000"


def test_percentage_edge_cases():
    """Test percentage format edge cases."""
    # 0%
    widget = ProgressWidget(current=0, total=100, format_style="percentage")
    assert widget._format_progress() == "0%"

    # 100%
    widget.set(100)
    assert widget._format_progress() == "100%"

    # Zero total (division by zero)
    widget2 = ProgressWidget(current=0, total=0, format_style="percentage")
    assert widget2._format_progress() == "0%"


# Test render output
def test_render_in_progress():
    """Test render output in IN_PROGRESS state."""
    widget = ProgressWidget(current=50, total=100, format_style="fraction")
    rendered = widget.render()
    assert isinstance(rendered, Text)
    assert rendered.plain == "50/100"


def test_render_success():
    """Test render output in SUCCESS state."""
    widget = ProgressWidget()
    widget._state = ComponentState.SUCCESS
    rendered = widget.render()
    assert isinstance(rendered, Text)
    assert rendered.plain == "100%"


def test_render_error():
    """Test render output in ERROR state."""
    widget = ProgressWidget()
    widget._state = ComponentState.ERROR
    rendered = widget.render()
    assert isinstance(rendered, Text)
    assert rendered.plain == "Failed"


def test_render_custom_state_text():
    """Test render with custom success/error text."""
    widget = ProgressWidget(success_text="All done!", error_text="Broken")
    widget._state = ComponentState.SUCCESS
    assert widget.render().plain == "All done!"

    widget._state = ComponentState.ERROR
    assert widget.render().plain == "Broken"


# Test update methods
def test_update_methods():
    """Test progress update methods."""
    widget = ProgressWidget(current=0, total=100)

    # increment
    widget.increment()
    assert widget.current == 1

    # set
    widget.set(50)
    assert widget.current == 50

    # add
    widget.add(5)
    assert widget.current == 55

    # set_percentage
    widget.set_percentage(75)
    assert widget.current == 75


def test_increment_boundary():
    """Test increment at boundary."""
    widget = ProgressWidget(current=99, total=100)
    widget.increment()
    assert widget.current == 100

    # Should not exceed total
    widget.increment()
    assert widget.current == 100


def test_set_clamping():
    """Test set clamps to [0, total]."""
    widget = ProgressWidget(total=100)

    widget.set(150)
    assert widget.current == 100

    widget.set(-10)
    assert widget.current == 0


def test_add_negative():
    """Test add with negative amount."""
    widget = ProgressWidget(current=50, total=100)
    widget.add(-20)
    assert widget.current == 30

    # Clamp at 0
    widget.add(-100)
    assert widget.current == 0


def test_is_complete():
    """Test is_complete method."""
    widget = ProgressWidget(current=0, total=100)
    assert not widget.is_complete()

    widget.set(100)
    assert widget.is_complete()

    widget.set(50)
    assert not widget.is_complete()


# Test state transitions
def test_state_transitions():
    """Test valid and invalid state transitions."""
    widget = ProgressWidget()

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
    assert widget.current == 0

    # IN_PROGRESS -> ERROR
    widget.error()
    assert widget.state == ComponentState.ERROR

    # ERROR -> SUCCESS (invalid, should be ignored)
    widget.success()
    assert widget.state == ComponentState.ERROR


def test_success_with_custom_text():
    """Test success with custom text updates the text."""
    widget = ProgressWidget()
    widget.success("Complete!")
    assert widget._success_text == "Complete!"
    assert widget.render().plain == "Complete!"


def test_error_with_custom_text():
    """Test error with custom text updates the text."""
    widget = ProgressWidget()
    widget.error("Timed out")
    assert widget._error_text == "Timed out"
    assert widget.render().plain == "Timed out"


def test_reset():
    """Test reset returns to IN_PROGRESS and resets current."""
    widget = ProgressWidget(current=50, total=100)
    widget.success()
    widget.reset()
    assert widget.state == ComponentState.IN_PROGRESS
    assert widget.current == 0


@pytest.mark.asyncio
async def test_state_css_classes():
    """Test CSS classes are set correctly on state changes."""

    class StateApp(App):
        def compose(self) -> ComposeResult:
            yield ProgressWidget(id="progress")

    async with StateApp().run_test() as pilot:
        progress = pilot.app.query_one("#progress", ProgressWidget)

        assert "success" not in progress.classes
        assert "error" not in progress.classes

        progress.success()
        await pilot.pause()
        assert "success" in progress.classes
        assert "error" not in progress.classes

        progress.reset()
        await pilot.pause()
        assert "success" not in progress.classes
        assert "error" not in progress.classes

        progress.error()
        await pilot.pause()
        assert "error" in progress.classes
        assert "success" not in progress.classes


# Test reactivity
@pytest.mark.asyncio
async def test_reactivity():
    """Test reactive updates trigger re-renders."""

    class ReactiveApp(App):
        def compose(self) -> ComposeResult:
            yield ProgressWidget(current=0, total=100, format_style="fraction", id="progress")

    async with ReactiveApp().run_test() as pilot:
        progress = pilot.app.query_one("#progress", ProgressWidget)

        assert progress.render().plain == "0/100"

        progress.set(42)
        await pilot.pause()
        assert progress.render().plain == "42/100"

        progress.increment()
        await pilot.pause()
        assert progress.render().plain == "43/100"


# Test visibility
@pytest.mark.asyncio
async def test_visibility_toggle():
    """Test CSS class-based visibility changes."""

    class VisApp(App):
        def compose(self) -> ComposeResult:
            yield ProgressWidget(id="progress")

    async with VisApp().run_test() as pilot:
        progress = pilot.app.query_one("#progress", ProgressWidget)

        assert progress.display is True

        progress.hide()
        await pilot.pause()
        assert progress.display is False

        progress.show()
        await pilot.pause()
        assert progress.display is True

        progress.toggle()
        await pilot.pause()
        assert progress.display is False

        progress.set_visible(True)
        await pilot.pause()
        assert progress.display is True


# Test from_config
def test_from_config():
    """Test factory method from configuration dictionary."""
    config = {
        "current": 25,
        "total": 200,
        "format_style": "percentage",
        "color": "#FFA500",
        "zero_pad": True,
        "success_text": "OK",
        "error_text": "ERR",
        "visible": False,
    }
    widget = ProgressWidget.from_config(config)
    assert widget.current == 25
    assert widget.total == 200
    assert widget.format_style == "percentage"
    assert widget.color == "#FFA500"
    assert widget.zero_pad is True
    assert widget._success_text == "OK"
    assert widget._error_text == "ERR"
    assert widget.display is False


def test_from_config_defaults():
    """Test from_config with empty config uses defaults."""
    widget = ProgressWidget.from_config({})
    assert widget.current == 0
    assert widget.total == 100
    assert widget.format_style == "fraction"
    assert widget.color == "#D97706"


# Test repr
def test_repr():
    """Test string representation."""
    widget = ProgressWidget(current=50, total=100, format_style="percentage")
    repr_str = repr(widget)
    assert "ProgressWidget" in repr_str
    assert "50" in repr_str
    assert "100" in repr_str
    assert "percentage" in repr_str
    assert "IN_PROGRESS" in repr_str


# Test feature parity
def test_feature_parity():
    """Verify all Rich ProgressComponent APIs are available."""
    widget = ProgressWidget()

    # Update methods
    assert hasattr(widget, "increment")
    assert hasattr(widget, "set")
    assert hasattr(widget, "add")
    assert hasattr(widget, "set_percentage")
    assert hasattr(widget, "is_complete")

    # State methods
    assert hasattr(widget, "success")
    assert hasattr(widget, "error")
    assert hasattr(widget, "reset")

    # Properties
    assert hasattr(widget, "current")
    assert hasattr(widget, "total")
    assert hasattr(widget, "format_style")
    assert hasattr(widget, "zero_pad")
    assert hasattr(widget, "state")

    # Factory
    assert hasattr(ProgressWidget, "from_config")

    # Visibility
    assert hasattr(widget, "show")
    assert hasattr(widget, "hide")
    assert hasattr(widget, "toggle")
    assert hasattr(widget, "set_visible")


# Test CSS defaults
def test_css_defaults():
    """Test DEFAULT_CSS is properly defined."""
    assert "ProgressWidget" in ProgressWidget.DEFAULT_CSS
    assert "success" in ProgressWidget.DEFAULT_CSS
    assert "error" in ProgressWidget.DEFAULT_CSS


# Integration test
@pytest.mark.asyncio
async def test_app_integration():
    """Test widget in full Textual app lifecycle."""

    class IntegrationApp(App):
        def compose(self) -> ComposeResult:
            yield ProgressWidget(current=0, total=100, format_style="percentage", id="p1")
            yield ProgressWidget(
                current=50, total=200, format_style="fraction", color="#FF00FF", id="p2"
            )

    async with IntegrationApp().run_test() as pilot:
        p1 = pilot.app.query_one("#p1", ProgressWidget)
        p2 = pilot.app.query_one("#p2", ProgressWidget)

        assert p1.render().plain == "0%"
        assert p2.render().plain == "50/200"
        assert p2.color == "#FF00FF"

        p1.set(100)
        await pilot.pause()
        assert p1.render().plain == "100%"

        p1.success()
        await pilot.pause()
        assert p1.state == ComponentState.SUCCESS
        assert p1.render().plain == "100%"

        p2.error("Timeout")
        await pilot.pause()
        assert p2.state == ComponentState.ERROR
        assert p2.render().plain == "Timeout"

        p2.reset()
        await pilot.pause()
        assert p2.state == ComponentState.IN_PROGRESS
        assert p2.current == 0


@pytest.mark.asyncio
async def test_widget_lifecycle():
    """Test widget mount/unmount lifecycle."""

    class LifecycleApp(App):
        def compose(self) -> ComposeResult:
            yield ProgressWidget(id="progress")

    async with LifecycleApp().run_test() as pilot:
        progress = pilot.app.query_one("#progress", ProgressWidget)
        assert progress.is_mounted

        rendered = progress.render()
        assert isinstance(rendered, Text)

        await progress.remove()
        assert progress not in pilot.app.query(ProgressWidget)
