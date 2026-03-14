"""Tests for ThothSpinnerWidget orchestrator."""

from __future__ import annotations

from typing import Any

import pytest
from textual.app import App, ComposeResult

from thothspinner.core.states import ComponentState
from thothspinner.textual.widgets.hint import HintWidget
from thothspinner.textual.widgets.message import MessageWidget
from thothspinner.textual.widgets.progress import ProgressWidget
from thothspinner.textual.widgets.spinner import SpinnerWidget
from thothspinner.textual.widgets.thothspinner import ThothSpinnerWidget
from thothspinner.textual.widgets.timer import TimerWidget

# ============================================================
# Sync tests — widget construction outside app context
# ============================================================


class TestInitialization:
    """Test ThothSpinnerWidget construction."""

    def test_initialization_defaults(self):
        """Default construction creates all 5 components."""
        widget = ThothSpinnerWidget()
        assert isinstance(widget.spinner, SpinnerWidget)
        assert isinstance(widget.message, MessageWidget)
        assert isinstance(widget.progress, ProgressWidget)
        assert isinstance(widget.timer, TimerWidget)
        assert isinstance(widget.hint, HintWidget)
        assert widget.state == ComponentState.IN_PROGRESS

    def test_initialization_custom_spinner_style(self):
        """Custom spinner_style passed to SpinnerWidget."""
        widget = ThothSpinnerWidget(spinner_style="dots")
        assert widget.spinner is not None

    def test_initialization_custom_progress_format(self):
        """Custom progress_format passed to ProgressWidget."""
        widget = ThothSpinnerWidget(progress_format="percentage")
        assert widget.progress.format_style == "percentage"

    def test_initialization_custom_timer_format(self):
        """Custom timer_format passed to TimerWidget."""
        widget = ThothSpinnerWidget(timer_format="seconds")
        assert widget.timer.format_style == "seconds"

    def test_initialization_custom_hint_text(self):
        """Custom hint_text passed to HintWidget."""
        widget = ThothSpinnerWidget(hint_text="Press q to quit")
        assert widget.hint.text == "Press q to quit"

    def test_initialization_hidden(self):
        """visible=False adds hidden class."""
        widget = ThothSpinnerWidget(visible=False)
        assert "hidden" in widget.classes

    def test_initialization_durations(self):
        """success_duration and error_duration stored."""
        widget = ThothSpinnerWidget(success_duration=2.0, error_duration=5.0)
        assert widget.success_duration == 2.0
        assert widget.error_duration == 5.0

    def test_initialization_with_config_dict(self):
        """Full config dict applied to components."""
        widget = ThothSpinnerWidget(
            config={
                "defaults": {"color": "#00FFFF"},
                "elements": {
                    "hint": {"text": "custom hint"},
                },
            }
        )
        assert widget.hint.text == "custom hint"

    def test_initialization_config_durations(self):
        """Durations from config dict applied."""
        widget = ThothSpinnerWidget(
            config={
                "durations": {"success": 3.0, "error": 7.0},
            }
        )
        assert widget.success_duration == 3.0
        assert widget.error_duration == 7.0


class TestConfigHierarchy:
    """Test configuration resolution and hierarchy."""

    def test_defaults_applied(self):
        """Default config values applied to all components."""
        widget = ThothSpinnerWidget()
        assert widget.config["defaults"]["color"] == "#D97706"
        assert widget.config["defaults"]["visible"] is True

    def test_element_overrides_defaults(self):
        """Element-specific config overrides defaults."""
        widget = ThothSpinnerWidget(
            config={
                "defaults": {"color": "#111111"},
                "elements": {"spinner": {"color": "#222222"}},
            }
        )
        resolved = widget._resolve_config("spinner")
        assert resolved["color"] == "#222222"

    def test_config_invalid_component(self):
        """Invalid component type in elements raises KeyError."""
        with pytest.raises(KeyError, match="Invalid component type"):
            ThothSpinnerWidget(config={"elements": {"invalid_widget": {"color": "#000000"}}})

    def test_kwargs_override_config(self):
        """Constructor kwargs applied to element configs."""
        widget = ThothSpinnerWidget(hint_text="Custom")
        assert widget.hint.text == "Custom"


class TestRenderOrder:
    """Test render order control."""

    def test_default_render_order(self):
        """Default order: spinner, message, progress, timer, hint."""
        widget = ThothSpinnerWidget()
        assert widget._render_order == (
            "spinner",
            "message",
            "progress",
            "timer",
            "hint",
        )

    def test_custom_render_order(self):
        """Custom render order applied."""
        order = ["hint", "timer", "spinner"]
        widget = ThothSpinnerWidget(render_order=order)
        assert widget._render_order == ("hint", "timer", "spinner")

    def test_render_order_from_config(self):
        """Render order from config dict."""
        widget = ThothSpinnerWidget(config={"render_order": ["timer", "spinner", "message"]})
        assert widget._render_order == ("timer", "spinner", "message")

    def test_invalid_render_order(self):
        """Invalid component in render_order raises KeyError."""
        with pytest.raises(KeyError, match="Invalid components"):
            ThothSpinnerWidget(render_order=["spinner", "invalid"])

    def test_render_order_immutable(self):
        """Render order stored as tuple (immutable)."""
        widget = ThothSpinnerWidget()
        assert isinstance(widget._render_order, tuple)


class TestComponentAccess:
    """Test component access properties and get_component."""

    def test_spinner_property(self):
        """Access spinner via property."""
        widget = ThothSpinnerWidget()
        assert isinstance(widget.spinner, SpinnerWidget)

    def test_message_property(self):
        """Access message via property."""
        widget = ThothSpinnerWidget()
        assert isinstance(widget.message, MessageWidget)

    def test_progress_property(self):
        """Access progress via property."""
        widget = ThothSpinnerWidget()
        assert isinstance(widget.progress, ProgressWidget)

    def test_timer_property(self):
        """Access timer via property."""
        widget = ThothSpinnerWidget()
        assert isinstance(widget.timer, TimerWidget)

    def test_hint_property(self):
        """Access hint via property."""
        widget = ThothSpinnerWidget()
        assert isinstance(widget.hint, HintWidget)

    def test_get_component_valid(self):
        """get_component returns correct child."""
        widget = ThothSpinnerWidget()
        assert widget.get_component("spinner") is widget.spinner
        assert widget.get_component("message") is widget.message
        assert widget.get_component("progress") is widget.progress
        assert widget.get_component("timer") is widget.timer
        assert widget.get_component("hint") is widget.hint

    def test_get_component_invalid(self):
        """get_component raises KeyError for invalid type."""
        widget = ThothSpinnerWidget()
        with pytest.raises(KeyError, match="Invalid component type"):
            widget.get_component("nonexistent")


class TestStateManagement:
    """Test state transitions and propagation."""

    def test_initial_state(self):
        """Initial state is IN_PROGRESS."""
        widget = ThothSpinnerWidget()
        assert widget.state == ComponentState.IN_PROGRESS

    def test_success_transition(self):
        """Success transitions orchestrator and all children."""
        widget = ThothSpinnerWidget()
        widget.success()
        assert widget.state == ComponentState.SUCCESS
        assert widget.spinner.state == ComponentState.SUCCESS
        assert widget.message.state == ComponentState.SUCCESS
        assert widget.progress.state == ComponentState.SUCCESS
        assert widget.timer.state == ComponentState.SUCCESS

    def test_error_transition(self):
        """Error transitions orchestrator and all children."""
        widget = ThothSpinnerWidget()
        widget.error()
        assert widget.state == ComponentState.ERROR
        assert widget.spinner.state == ComponentState.ERROR
        assert widget.message.state == ComponentState.ERROR
        assert widget.progress.state == ComponentState.ERROR
        assert widget.timer.state == ComponentState.ERROR

    def test_success_with_message(self):
        """Success with message passed to children."""
        widget = ThothSpinnerWidget()
        widget.success("Done!")
        assert widget.state == ComponentState.SUCCESS

    def test_error_with_message(self):
        """Error with message passed to children."""
        widget = ThothSpinnerWidget()
        widget.error("Oops!")
        assert widget.state == ComponentState.ERROR

    def test_invalid_transition_success_to_error(self):
        """SUCCESS → ERROR raises ValueError."""
        widget = ThothSpinnerWidget()
        widget.success()
        with pytest.raises(ValueError, match="Invalid state transition"):
            widget.error()

    def test_invalid_transition_error_to_success(self):
        """ERROR → SUCCESS raises ValueError."""
        widget = ThothSpinnerWidget()
        widget.error()
        with pytest.raises(ValueError, match="Invalid state transition"):
            widget.success()

    def test_reset(self):
        """Reset returns orchestrator and children to IN_PROGRESS."""
        widget = ThothSpinnerWidget()
        widget.success()
        widget.reset()
        assert widget.state == ComponentState.IN_PROGRESS
        assert widget.spinner.state == ComponentState.IN_PROGRESS
        assert widget.message.state == ComponentState.IN_PROGRESS
        assert widget.progress.state == ComponentState.IN_PROGRESS
        assert widget.timer.state == ComponentState.IN_PROGRESS

    def test_clear_hides_all(self):
        """Clear hides all child widgets."""
        widget = ThothSpinnerWidget()
        widget.clear()
        for component in widget._components.values():
            assert "hidden" in component.classes

    def test_stop_aliases_clear(self):
        """Stop is an alias for clear."""
        widget = ThothSpinnerWidget()
        widget.stop()
        for component in widget._components.values():
            assert "hidden" in component.classes

    def test_start_resets_to_in_progress(self):
        """Start sets state to IN_PROGRESS."""
        widget = ThothSpinnerWidget()
        widget.success()
        # Reset first to allow transition
        widget.reset()
        widget.start()
        assert widget.state == ComponentState.IN_PROGRESS


class TestConvenienceMethods:
    """Test convenience methods for component control."""

    def test_update_progress(self):
        """update_progress delegates to progress widget."""
        widget = ThothSpinnerWidget()
        widget.update_progress(current=50)
        assert widget.progress.current == 50

    def test_update_progress_with_total(self):
        """update_progress with total updates both values."""
        widget = ThothSpinnerWidget()
        widget.update_progress(current=25, total=200)
        assert widget.progress.current == 25
        assert widget.progress.total == 200

    def test_set_message(self):
        """set_message delegates to message widget."""
        widget = ThothSpinnerWidget()
        widget.set_message(text="Processing data...")
        assert widget.message._current_word == "Processing data..."

    def test_set_hint(self):
        """set_hint delegates to hint widget."""
        widget = ThothSpinnerWidget()
        widget.set_hint(text="Press q to quit")
        assert widget.hint.text == "Press q to quit"

    def test_set_shimmer_direction(self):
        """set_shimmer_direction delegates to message widget."""
        widget = ThothSpinnerWidget()
        widget.set_shimmer_direction(direction="right-to-left")
        assert widget.message.reverse_shimmer is True

    def test_set_shimmer_direction_left(self):
        """set_shimmer_direction left-to-right."""
        widget = ThothSpinnerWidget()
        widget.set_shimmer_direction(direction="right-to-left")
        widget.set_shimmer_direction(direction="left-to-right")
        assert widget.message.reverse_shimmer is False

    def test_update_component_generic(self):
        """update_component with generic kwargs."""
        widget = ThothSpinnerWidget()
        widget.update_component("hint", text="New hint")
        assert widget.hint.text == "New hint"

    def test_update_component_invalid(self):
        """update_component raises KeyError for invalid type."""
        widget = ThothSpinnerWidget()
        with pytest.raises(KeyError, match="Invalid component type"):
            widget.update_component("nonexistent", text="foo")


class TestFactory:
    """Test from_dict factory method."""

    def test_from_dict_basic(self):
        """from_dict creates widget from config."""
        config = {
            "spinner_style": "dots",
            "hint_text": "custom hint",
        }
        widget = ThothSpinnerWidget.from_dict(config)
        assert widget.hint.text == "custom hint"

    def test_from_dict_with_overrides(self):
        """from_dict kwargs override config."""
        config = {
            "hint_text": "from config",
        }
        widget = ThothSpinnerWidget.from_dict(config, hint_text="from kwargs")
        assert widget.hint.text == "from kwargs"

    def test_from_dict_with_durations(self):
        """from_dict handles duration params."""
        config = {
            "success_duration": 2.0,
            "error_duration": 5.0,
        }
        widget = ThothSpinnerWidget.from_dict(config)
        assert widget.success_duration == 2.0
        assert widget.error_duration == 5.0

    def test_from_dict_with_render_order(self):
        """from_dict handles render_order."""
        config = {
            "render_order": ["timer", "spinner"],
        }
        widget = ThothSpinnerWidget.from_dict(config)
        assert widget._render_order == ("timer", "spinner")

    def test_from_dict_with_nested_config(self):
        """from_dict passes remaining keys as config dict."""
        config = {
            "defaults": {"color": "#00FFFF"},
            "elements": {"hint": {"text": "nested"}},
        }
        widget = ThothSpinnerWidget.from_dict(config)
        assert widget.hint.text == "nested"


class TestVisibility:
    """Test visibility methods."""

    def test_show(self):
        """show() removes hidden class."""
        widget = ThothSpinnerWidget(visible=False)
        widget.show()
        assert "hidden" not in widget.classes

    def test_hide(self):
        """hide() adds hidden class."""
        widget = ThothSpinnerWidget()
        widget.hide()
        assert "hidden" in widget.classes

    def test_toggle(self):
        """toggle() toggles hidden class."""
        widget = ThothSpinnerWidget()
        widget.toggle()
        assert "hidden" in widget.classes
        widget.toggle()
        assert "hidden" not in widget.classes

    def test_set_visible_true(self):
        """set_visible(True) removes hidden."""
        widget = ThothSpinnerWidget(visible=False)
        widget.set_visible(True)
        assert "hidden" not in widget.classes

    def test_set_visible_false(self):
        """set_visible(False) adds hidden."""
        widget = ThothSpinnerWidget()
        widget.set_visible(False)
        assert "hidden" in widget.classes


class TestRepr:
    """Test string representation."""

    def test_repr_default(self):
        """repr shows state and components."""
        widget = ThothSpinnerWidget()
        r = repr(widget)
        assert "ThothSpinnerWidget" in r
        assert "IN_PROGRESS" in r
        assert "spinner" in r

    def test_repr_after_success(self):
        """repr reflects success state."""
        widget = ThothSpinnerWidget()
        widget.success()
        assert "SUCCESS" in repr(widget)


class TestFeatureParity:
    """Verify API parity with Rich ThothSpinner."""

    def test_all_rich_methods_exist(self):
        """All key Rich ThothSpinner methods have Textual equivalents."""
        widget = ThothSpinnerWidget()
        # State management
        assert hasattr(widget, "start")
        assert hasattr(widget, "success")
        assert hasattr(widget, "error")
        assert hasattr(widget, "reset")
        assert hasattr(widget, "clear")
        assert hasattr(widget, "stop")
        # Component access
        assert hasattr(widget, "get_component")
        assert hasattr(widget, "spinner")
        assert hasattr(widget, "message")
        assert hasattr(widget, "progress")
        assert hasattr(widget, "timer")
        assert hasattr(widget, "hint")
        # Convenience methods
        assert hasattr(widget, "update_progress")
        assert hasattr(widget, "set_message")
        assert hasattr(widget, "set_hint")
        assert hasattr(widget, "set_spinner_style")
        assert hasattr(widget, "set_shimmer_direction")
        assert hasattr(widget, "update_component")
        # Factory
        assert hasattr(widget, "from_dict")
        # Properties
        assert hasattr(widget, "state")
        assert hasattr(widget, "config")

    def test_state_property_type(self):
        """State property returns ComponentState enum."""
        widget = ThothSpinnerWidget()
        assert isinstance(widget.state, ComponentState)


# ============================================================
# Async tests — Textual app context
# ============================================================


class ThothSpinnerApp(App):
    """Test app for ThothSpinnerWidget."""

    def __init__(self, **kwargs: Any) -> None:
        self.thoth_kwargs = kwargs
        super().__init__()

    def compose(self) -> ComposeResult:
        yield ThothSpinnerWidget(**self.thoth_kwargs)


@pytest.mark.asyncio
async def test_compose_yields_all_components():
    """All 5 child widgets mounted in app."""
    app = ThothSpinnerApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        thoth = app.query_one(ThothSpinnerWidget)
        # Check child widgets are in the DOM
        spinners = app.query(SpinnerWidget)
        messages = app.query(MessageWidget)
        progresses = app.query(ProgressWidget)
        timers = app.query(TimerWidget)
        hints = app.query(HintWidget)
        assert len(spinners) == 1
        assert len(messages) == 1
        assert len(progresses) == 1
        assert len(timers) == 1
        assert len(hints) == 1
        assert thoth.state == ComponentState.IN_PROGRESS


@pytest.mark.asyncio
async def test_success_in_app():
    """Success propagates to all children in app context."""
    app = ThothSpinnerApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        thoth = app.query_one(ThothSpinnerWidget)
        thoth.success("All done!")
        await pilot.pause()
        assert thoth.state == ComponentState.SUCCESS
        assert thoth.spinner.state == ComponentState.SUCCESS
        assert thoth.message.state == ComponentState.SUCCESS
        assert thoth.progress.state == ComponentState.SUCCESS
        assert thoth.timer.state == ComponentState.SUCCESS


@pytest.mark.asyncio
async def test_error_in_app():
    """Error propagates to all children in app context."""
    app = ThothSpinnerApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        thoth = app.query_one(ThothSpinnerWidget)
        thoth.error("Something failed")
        await pilot.pause()
        assert thoth.state == ComponentState.ERROR
        assert thoth.spinner.state == ComponentState.ERROR
        assert thoth.message.state == ComponentState.ERROR


@pytest.mark.asyncio
async def test_reset_in_app():
    """Reset returns to IN_PROGRESS in app context."""
    app = ThothSpinnerApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        thoth = app.query_one(ThothSpinnerWidget)
        thoth.success()
        await pilot.pause()
        thoth.reset()
        await pilot.pause()
        assert thoth.state == ComponentState.IN_PROGRESS
        assert thoth.spinner.state == ComponentState.IN_PROGRESS


@pytest.mark.asyncio
async def test_auto_clear_success():
    """Components hidden after success_duration."""
    app = ThothSpinnerApp(success_duration=0.1)
    async with app.run_test() as pilot:
        await pilot.pause()
        thoth = app.query_one(ThothSpinnerWidget)
        thoth.success()
        await pilot.pause()
        assert thoth.state == ComponentState.SUCCESS
        # Wait for auto-clear
        await pilot.pause(delay=0.2)
        # Children should be hidden
        for component in thoth._components.values():
            assert "hidden" in component.classes


@pytest.mark.asyncio
async def test_auto_clear_error():
    """Components hidden after error_duration."""
    app = ThothSpinnerApp(error_duration=0.1)
    async with app.run_test() as pilot:
        await pilot.pause()
        thoth = app.query_one(ThothSpinnerWidget)
        thoth.error()
        await pilot.pause()
        # Wait for auto-clear
        await pilot.pause(delay=0.2)
        for component in thoth._components.values():
            assert "hidden" in component.classes


@pytest.mark.asyncio
async def test_auto_clear_cancelled_on_reset():
    """Auto-clear cancelled when reset is called."""
    app = ThothSpinnerApp(success_duration=1.0)
    async with app.run_test() as pilot:
        await pilot.pause()
        thoth = app.query_one(ThothSpinnerWidget)
        thoth.success()
        await pilot.pause()
        # Reset before auto-clear fires
        thoth.reset()
        await pilot.pause()
        assert thoth._clear_timer_handle is None
        assert thoth.state == ComponentState.IN_PROGRESS


@pytest.mark.asyncio
async def test_visibility_toggle_in_app():
    """show/hide/toggle work in app context."""
    app = ThothSpinnerApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        thoth = app.query_one(ThothSpinnerWidget)
        thoth.hide()
        await pilot.pause()
        assert "hidden" in thoth.classes
        thoth.show()
        await pilot.pause()
        assert "hidden" not in thoth.classes


@pytest.mark.asyncio
async def test_clear_hides_all_in_app():
    """clear() hides all children in app context."""
    app = ThothSpinnerApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        thoth = app.query_one(ThothSpinnerWidget)
        thoth.clear()
        await pilot.pause()
        for component in thoth._components.values():
            assert "hidden" in component.classes


@pytest.mark.asyncio
async def test_start_in_app():
    """start() starts spinner and timer."""
    app = ThothSpinnerApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        thoth = app.query_one(ThothSpinnerWidget)
        thoth.start()
        await pilot.pause()
        assert thoth.state == ComponentState.IN_PROGRESS
        assert thoth.timer.running is True


@pytest.mark.asyncio
async def test_full_workflow():
    """Complete lifecycle: start → progress updates → success."""
    app = ThothSpinnerApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        thoth = app.query_one(ThothSpinnerWidget)

        # Start
        thoth.start()
        await pilot.pause()

        # Update progress
        thoth.update_progress(current=25, total=100)
        await pilot.pause()
        assert thoth.progress.current == 25

        thoth.update_progress(current=100)
        await pilot.pause()
        assert thoth.progress.current == 100

        # Set message
        thoth.set_message(text="Finalizing")
        await pilot.pause()

        # Success
        thoth.success("Complete!")
        await pilot.pause()
        assert thoth.state == ComponentState.SUCCESS


@pytest.mark.asyncio
async def test_multiple_instances():
    """Two orchestrators in the same app."""

    class MultiApp(App):
        def compose(self) -> ComposeResult:
            yield ThothSpinnerWidget(id="thoth1")
            yield ThothSpinnerWidget(id="thoth2")

    app = MultiApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        thoth1 = app.query_one("#thoth1", ThothSpinnerWidget)
        thoth2 = app.query_one("#thoth2", ThothSpinnerWidget)

        thoth1.success()
        await pilot.pause()
        assert thoth1.state == ComponentState.SUCCESS
        assert thoth2.state == ComponentState.IN_PROGRESS


@pytest.mark.asyncio
async def test_convenience_methods_in_app():
    """Convenience methods work in running app."""
    app = ThothSpinnerApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        thoth = app.query_one(ThothSpinnerWidget)

        thoth.update_progress(current=50, total=200)
        await pilot.pause()
        assert thoth.progress.current == 50
        assert thoth.progress.total == 200

        thoth.set_hint(text="Almost done")
        await pilot.pause()
        assert thoth.hint.text == "Almost done"

        thoth.set_shimmer_direction(direction="right-to-left")
        assert thoth.message.reverse_shimmer is True
