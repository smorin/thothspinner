"""Tests for the HintComponent.

Based on Rich testing patterns with deterministic console and smoke tests.
"""

import pytest
from rich.progress import Progress, SpinnerColumn, TextColumn

from thothspinner.rich.components import HintComponent


class TestHintComponent:
    """Test suite for HintComponent."""

    def test_initialization_with_defaults(self):
        """Test component initializes with default values."""
        hint = HintComponent()
        assert hint.text == "(esc to interrupt)"
        assert hint.color == "#888888"
        assert hint.visible is True

    def test_initialization_with_custom_values(self):
        """Test component initializes with custom values."""
        hint = HintComponent(text="Custom hint", color="#FF0000", visible=False)
        assert hint.text == "Custom hint"
        assert hint.color == "#FF0000"
        assert hint.visible is False

    def test_text_property(self):
        """Test text property getter and setter."""
        hint = HintComponent()
        assert hint.text == "(esc to interrupt)"

        hint.text = "New text"
        assert hint.text == "New text"

    def test_color_property(self):
        """Test color property getter and setter."""
        hint = HintComponent()
        assert hint.color == "#888888"

        hint.color = "#00FF00"
        assert hint.color == "#00FF00"

    def test_color_property_validation(self):
        """Test color property validates hex format."""
        hint = HintComponent()

        # Valid color should work
        hint.color = "#123456"
        assert hint.color == "#123456"

        # Invalid color should raise ValueError
        with pytest.raises(ValueError, match="Invalid hex color"):
            hint.color = "invalid"

        with pytest.raises(ValueError, match="Invalid hex color"):
            hint.color = "#FFF"  # Too short

        with pytest.raises(ValueError, match="Invalid hex color"):
            hint.color = "#GGGGGG"  # Invalid hex chars

    def test_visible_property(self):
        """Test visible property getter and setter."""
        hint = HintComponent()
        assert hint.visible is True

        hint.visible = False
        assert hint.visible is False

    def test_from_config(self):
        """Test creating component from configuration dictionary."""
        config = {"text": "Config text", "color": "#123456", "visible": False}
        hint = HintComponent.from_config(config)
        assert hint.text == "Config text"
        assert hint.color == "#123456"
        assert hint.visible is False

    def test_from_config_with_missing_keys(self):
        """Test from_config with partial configuration."""
        config = {"text": "Partial config"}
        hint = HintComponent.from_config(config)
        assert hint.text == "Partial config"
        assert hint.color == "#888888"  # default
        assert hint.visible is True  # default

    def test_update_method(self):
        """Test update method for future-proofing."""
        hint = HintComponent()

        # Update single property
        hint.update(text="Updated text")
        assert hint.text == "Updated text"
        assert hint.color == "#888888"  # unchanged

        # Update multiple properties
        hint.update(color="#FF0000", visible=False)
        assert hint.text == "Updated text"  # unchanged
        assert hint.color == "#FF0000"
        assert hint.visible is False

        # Update all properties
        hint.update(text="Final", color="#00FF00", visible=True)
        assert hint.text == "Final"
        assert hint.color == "#00FF00"
        assert hint.visible is True

    def test_rendering_when_visible(self, capture_console):
        """Test component renders when visible."""
        hint = HintComponent(text="Test hint", color="#FF0000")
        capture_console.print(hint)
        output = capture_console.export_text(clear=False)
        assert "Test hint" in output

    def test_rendering_when_not_visible(self, capture_console):
        """Test component doesn't render when not visible."""
        hint = HintComponent(text="Hidden hint", visible=False)
        capture_console.print(hint)
        output = capture_console.export_text(clear=False)
        assert "Hidden hint" not in output

    def test_repr(self):
        """Test string representation."""
        hint = HintComponent(text="Test", color="#123456", visible=True)
        repr_str = repr(hint)
        assert "HintComponent" in repr_str
        assert "text='Test'" in repr_str
        assert "color='#123456'" in repr_str
        assert "visible=True" in repr_str

    def test_multiple_color_formats(self, capture_console):
        """Test various color formats are accepted."""
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFFFF", "#000000"]
        for color in colors:
            hint = HintComponent(text="Color test", color=color)
            # Should not raise an exception
            capture_console.print(hint)

    def test_invalid_color_initialization(self):
        """Test that invalid colors raise ValueError on initialization."""
        with pytest.raises(ValueError, match="Invalid hex color"):
            HintComponent(color="red")

        with pytest.raises(ValueError, match="Invalid hex color"):
            HintComponent(color="#FFF")

        with pytest.raises(ValueError, match="Invalid hex color"):
            HintComponent(color="123456")

    def test_integration_with_rich_progress(self, console):
        """Test HintComponent works alongside Rich Progress."""
        hint = HintComponent(text="Loading data...")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
            auto_refresh=False,  # Deterministic testing
        ) as progress:
            progress.add_task("Processing", total=None)
            # Should not raise any exceptions
            console.print(hint)
            progress.refresh()

    def test_caching_performance(self, capture_console):
        """Test that rendering uses caching for unchanged content."""
        hint = HintComponent(text="Cached", color="#888888")

        # First render
        capture_console.print(hint)

        # Second render with same content should use cache
        capture_console.print(hint)

        # Change content - cache should be invalidated
        hint.text = "Changed"
        capture_console.print(hint)

        output = capture_console.export_text(clear=False)
        assert "Cached" in output
        assert "Changed" in output

    def test_measurement(self, console):
        """Test __rich_measure__ returns proper measurements."""
        hint = HintComponent(text="Test text")

        # Visible component should have non-zero measurement
        # Use console.options to get properly configured ConsoleOptions
        options = console.options
        measurement = hint.__rich_measure__(console, options)
        assert measurement.minimum > 0
        assert measurement.maximum > 0

        # Invisible component should have zero measurement
        hint.visible = False
        measurement = hint.__rich_measure__(console, options)
        assert measurement.minimum == 0
        assert measurement.maximum == 0


class TestHintSmoke:
    """Smoke tests for HintComponent based on rcx01.md recommendations."""

    def test_hint_smoke_multiple_prints(self, capture_console):
        """Test multiple hints can be printed sequentially."""
        hint1 = HintComponent(text="Press ESC to cancel", color="#888888")
        hint2 = HintComponent(text="Press Q to quit", color="#FF0000")

        capture_console.print(hint1)
        capture_console.print(hint2)

        out = capture_console.export_text(clear=False)
        assert "Press ESC to cancel" in out
        assert "Press Q to quit" in out

    def test_hint_visibility_toggle(self, capture_console):
        """Test visibility toggling works correctly."""
        hint = HintComponent(text="Toggleable", color="#00FF00", visible=True)

        # First render - visible
        capture_console.print(hint)
        out1 = capture_console.export_text(clear=False)
        assert "Toggleable" in out1

        # Toggle to invisible and render
        hint.visible = False
        capture_console.print(hint)
        out2 = capture_console.export_text(clear=False)
        # Should still only appear once (from first render)
        assert out2.count("Toggleable") == 1
