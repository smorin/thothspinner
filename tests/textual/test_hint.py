"""Comprehensive tests for the Textual HintWidget."""

import pytest
from rich.text import Text
from textual.app import App, ComposeResult

from thothspinner.textual.widgets import HintWidget


# Test initialization and defaults
def test_initialization_defaults():
    """Test default initialization values outside app context."""
    widget = HintWidget()
    assert widget.text == ""
    assert widget.color == "#888888"
    assert widget.icon == ""
    assert "hidden" not in widget.classes


def test_initialization_custom():
    """Test custom initialization."""
    widget = HintWidget(text="Custom", color="#FF0000", icon="⚠", visible=False)
    assert widget.text == "Custom"
    assert widget.color == "#FF0000"
    assert widget.icon == "⚠"
    assert "hidden" in widget.classes


def test_widget_construction_outside_app():
    """Test widget can be constructed outside app context."""

    class TestApp(App):
        def __init__(self):
            super().__init__()
            # Should not raise errors
            self.hint1 = HintWidget()
            self.hint2 = HintWidget("Pre-constructed")

    app = TestApp()
    assert app.hint1.text == ""
    assert app.hint2.text == "Pre-constructed"


# Test text update reactivity
@pytest.mark.asyncio
async def test_text_reactivity():
    """Test text updates trigger re-renders with pilot."""

    class HintApp(App):
        def compose(self) -> ComposeResult:
            yield HintWidget(text="Initial", id="hint")

    async with HintApp().run_test() as pilot:
        hint = pilot.app.query_one("#hint", HintWidget)

        # Test initial value
        assert hint.text == "Initial"

        # Test reactive change
        hint.text = "Updated"
        await pilot.pause()  # Allow reactive system to process
        assert hint.text == "Updated"

        # Test render output
        rendered = hint.render()
        assert "Updated" in str(rendered)

        # Test multiple rapid changes
        for i in range(10):
            hint.text = f"Change {i}"
        await pilot.pause()
        assert hint.text == "Change 9"


# Test color validation and style changes
def test_color_validation():
    """Test hex color validation."""
    widget = HintWidget()

    # Valid colors
    widget.color = "#FF0000"
    assert widget.color == "#FF0000"
    widget.color = "#00FF00"
    assert widget.color == "#00FF00"

    # Invalid colors should raise
    with pytest.raises(ValueError, match="must start with #"):
        widget.color = "red"
    with pytest.raises(ValueError, match="must be #RRGGBB"):
        widget.color = "#FF"
    with pytest.raises(ValueError, match="Invalid hex"):
        widget.color = "#GGGGGG"


@pytest.mark.asyncio
async def test_style_rendering():
    """Test style application in rendering."""

    class StyledApp(App):
        def compose(self) -> ComposeResult:
            yield HintWidget(text="Styled", color="#FF00FF", id="hint")

    async with StyledApp().run_test() as pilot:
        hint = pilot.app.query_one("#hint", HintWidget)
        rendered = hint.render()
        assert hint.color in str(rendered.style)


# Test visibility toggles
@pytest.mark.asyncio
async def test_visibility_toggle():
    """Test CSS class-based visibility changes."""

    class VisibilityApp(App):
        def compose(self) -> ComposeResult:
            yield HintWidget(text="Test", visible=True, id="hint")

    async with VisibilityApp().run_test() as pilot:
        hint = pilot.app.query_one("#hint", HintWidget)

        # Initially visible
        assert "hidden" not in hint.classes

        # Hide widget
        hint.hide()
        await pilot.pause()
        assert "hidden" in hint.classes

        # Show widget
        hint.show()
        await pilot.pause()
        assert "hidden" not in hint.classes

        # Toggle visibility
        hint.toggle()
        await pilot.pause()
        assert "hidden" in hint.classes

        # Test set_visible method
        hint.set_visible(True)
        await pilot.pause()
        assert "hidden" not in hint.classes


# Integration test with Textual app
@pytest.mark.asyncio
async def test_app_integration():
    """Test widget in full Textual app with pilot."""

    class IntegrationApp(App):
        CSS = """
        HintWidget {
            height: 1;
            width: 100%;
        }
        HintWidget.error {
            color: red;
        }
        """

        def compose(self) -> ComposeResult:
            yield HintWidget(text="App Hint", id="hint1")
            yield HintWidget(text="With Icon", icon="ℹ", color="#00FF00", id="hint2")

    async with IntegrationApp().run_test() as pilot:
        # Test multiple hints
        hint1 = pilot.app.query_one("#hint1", HintWidget)
        hint2 = pilot.app.query_one("#hint2", HintWidget)

        assert hint1.text == "App Hint"
        assert hint2.text == "With Icon"
        assert hint2.icon == "ℹ"

        # Test CSS class styling
        hint1.add_class("error")
        await pilot.pause()
        assert "error" in hint1.classes

        # Test batch updates
        hint1.update(text="Batch Update", color="#FF00FF")
        await pilot.pause()
        assert hint1.text == "Batch Update"
        assert hint1.color == "#FF00FF"


# Test widget lifecycle and render output
@pytest.mark.asyncio
async def test_widget_lifecycle():
    """Test widget mount/unmount lifecycle."""

    class LifecycleApp(App):
        mount_count = 0

        def compose(self) -> ComposeResult:
            yield HintWidget(text="Lifecycle", id="hint")

    async with LifecycleApp().run_test() as pilot:
        hint = pilot.app.query_one("#hint", HintWidget)

        # Test widget is mounted
        assert hint.is_mounted

        # Test render output
        rendered = hint.render()
        assert isinstance(rendered, Text)
        assert "Lifecycle" in str(rendered)

        # Test with icon
        hint.icon = "⚠"
        await pilot.pause()
        rendered = hint.render()
        assert "⚠ Lifecycle" in str(rendered)

        # Test unmount
        await hint.remove()
        # Widget removal is complete after the remove() completes
        # No need for pause after remove since it's an async operation
        # After remove() completes, widget should be unmounted
        # However, in Textual, is_mounted may still be True
        # because the widget reference still exists
        # We should test that it's not in the app's DOM instead
        assert hint not in pilot.app.query(HintWidget)


def test_render_output():
    """Test render method output directly."""
    widget = HintWidget(text="Test [b]bold[/b] text")
    rendered = widget.render()
    assert isinstance(rendered, Text)
    assert rendered.plain == "Test [b]bold[/b] text"

    # Test empty render
    empty_widget = HintWidget()
    empty_rendered = empty_widget.render()
    assert empty_rendered.plain == ""


# Performance test for rapid reactive updates
@pytest.mark.asyncio
async def test_performance_rapid_updates():
    """Test rapid reactive updates don't cause issues."""

    class PerformanceApp(App):
        def compose(self) -> ComposeResult:
            yield HintWidget(id="hint")

    async with PerformanceApp().run_test() as pilot:
        hint = pilot.app.query_one("#hint", HintWidget)

        # Rapid text updates
        for i in range(100):
            hint.text = f"Update {i}"
            if i % 10 == 0:
                await pilot.pause()

        assert hint.text == "Update 99"

        # Rapid color changes
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"]
        for _ in range(20):
            for color in colors:
                hint.color = color
        await pilot.pause()
        assert hint.color == "#FF00FF"

        # Rapid visibility toggles
        for _ in range(50):
            hint.toggle()
        await pilot.pause()
        # 50 toggles = back to original state
        assert "hidden" not in hint.classes


# Verify feature parity with Rich HintComponent
def test_feature_parity():
    """Verify all Rich features are available."""
    # Test from_config factory method
    config = {"text": "Config", "color": "#123456", "visible": False, "icon": "ℹ"}
    widget = HintWidget.from_config(config)
    assert widget.text == "Config"
    assert widget.color == "#123456"
    assert widget.icon == "ℹ"
    assert "hidden" in widget.classes

    # Test update method for batch changes
    widget.update(text="New Text", color="#654321", icon="⚠")
    assert widget.text == "New Text"
    assert widget.color == "#654321"
    assert widget.icon == "⚠"

    # Test icon manipulation
    widget.set_icon("✅")
    assert widget.icon == "✅"
    widget.clear_icon()
    assert widget.icon == ""

    # Test all visibility methods
    widget.show()
    assert "hidden" not in widget.classes
    widget.hide()
    assert "hidden" in widget.classes
    widget.toggle()
    assert "hidden" not in widget.classes


@pytest.mark.asyncio
async def test_animation_support():
    """Test animation methods."""

    class AnimationApp(App):
        def compose(self) -> ComposeResult:
            yield HintWidget(text="Animated", id="hint")

    async with AnimationApp().run_test() as pilot:
        hint = pilot.app.query_one("#hint", HintWidget)

        # Test fade in
        hint.hide()
        await pilot.pause()
        hint.fade_in(duration=0.1)
        await pilot.pause()
        assert "hidden" not in hint.classes

        # Test fade out
        hint.fade_out(duration=0.1)
        await pilot.pause(0.2)  # Wait for animation
        assert "hidden" in hint.classes


# Test icon content building
def test_build_content():
    """Test content building with icons."""
    widget = HintWidget()

    # Test with text only
    widget.text = "Hello"
    widget.icon = ""
    assert widget._build_content() == "Hello"

    # Test with icon only
    widget.text = ""
    widget.icon = "⚠"
    assert widget._build_content() == "⚠"

    # Test with both
    widget.text = "Warning"
    widget.icon = "⚠"
    assert widget._build_content() == "⚠ Warning"

    # Test with empty
    widget.text = ""
    widget.icon = ""
    assert widget._build_content() == ""


# Test reactive watchers
@pytest.mark.asyncio
async def test_reactive_watchers():
    """Test reactive property watchers trigger correctly."""

    class WatcherApp(App):
        def compose(self) -> ComposeResult:
            yield HintWidget(id="hint")

    async with WatcherApp().run_test() as pilot:
        hint = pilot.app.query_one("#hint", HintWidget)

        # Test text watcher
        hint.text = "Watch text"
        await pilot.pause()
        rendered = hint.render()
        assert "Watch text" in str(rendered)

        # Test color watcher
        hint.color = "#112233"
        await pilot.pause()
        assert hint.color == "#112233"

        # Test icon watcher
        hint.icon = "👀"
        await pilot.pause()
        rendered = hint.render()
        assert "👀" in str(rendered)


# Test edge cases
def test_edge_cases():
    """Test edge cases and error handling."""
    widget = HintWidget()

    # Test invalid color in update
    widget.update(text="Valid", color="#AABBCC")
    assert widget.color == "#AABBCC"

    with pytest.raises(ValueError):
        widget.update(color="invalid")

    # Test non-existent attribute in update
    widget.update(nonexistent="value")  # Should not raise

    # Test validate_color method
    assert widget.validate_color("#112233") == "#112233"
    with pytest.raises(ValueError):
        widget.validate_color("not-a-color")


# Test CSS defaults
def test_css_defaults():
    """Test DEFAULT_CSS is properly defined."""
    assert "HintWidget" in HintWidget.DEFAULT_CSS
    assert "hidden" in HintWidget.DEFAULT_CSS
    assert "display: none" in HintWidget.DEFAULT_CSS
    assert "error" in HintWidget.DEFAULT_CSS
    assert "warning" in HintWidget.DEFAULT_CSS
    assert "success" in HintWidget.DEFAULT_CSS
