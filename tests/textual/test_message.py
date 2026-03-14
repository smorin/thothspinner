"""Comprehensive tests for the Textual MessageWidget."""

import pytest
from rich.text import Text
from textual.app import App, ComposeResult

from thothspinner.core.states import ComponentState
from thothspinner.rich.components.message import DEFAULT_ACTION_WORDS
from thothspinner.textual.widgets import MessageWidget


# Test initialization and defaults
def test_initialization_defaults():
    """Test default initialization values outside app context."""
    widget = MessageWidget()
    assert widget.action_words == DEFAULT_ACTION_WORDS
    assert widget._min_interval == 0.5
    assert widget._max_interval == 3.0
    assert widget.color == "#D97706"
    assert widget._suffix == "…"
    assert widget._success_text == "Complete!"
    assert widget._error_text == "Failed"
    assert widget.state == ComponentState.IN_PROGRESS
    assert widget._shimmer_enabled is True
    assert widget._shimmer_width == 3
    assert widget._shimmer_light_color == "#FFA500"
    assert widget._shimmer_speed == 1.0
    assert widget.reverse_shimmer is False
    assert widget._current_word == ""
    assert "hidden" not in widget.classes


def test_initialization_custom():
    """Test custom initialization."""
    widget = MessageWidget(
        action_words=["Testing", "Processing"],
        interval={"min": 1.0, "max": 5.0},
        color="#FF0000",
        shimmer={
            "enabled": False,
            "width": 5,
            "light_color": "#FFFFFF",
            "speed": 2.0,
            "reverse": True,
        },
        suffix="!!!",
        success_text="Done!",
        error_text="Oops",
    )
    assert widget.action_words == ["Testing", "Processing"]
    assert widget._min_interval == 1.0
    assert widget._max_interval == 5.0
    assert widget.color == "#FF0000"
    assert widget._suffix == "!!!"
    assert widget._success_text == "Done!"
    assert widget._error_text == "Oops"
    assert widget._shimmer_enabled is False
    assert widget._shimmer_width == 5
    assert widget._shimmer_light_color == "#FFFFFF"
    assert widget._shimmer_speed == 2.0
    assert widget.reverse_shimmer is True


def test_initialization_hidden():
    """Test hidden initialization."""
    widget = MessageWidget(visible=False)
    assert "hidden" in widget.classes


def test_initialization_word_list_array():
    """Test initializing with array syntax replaces defaults."""
    custom = ["Word1", "Word2", "Word3"]
    widget = MessageWidget(action_words=custom)
    assert widget.action_words == custom
    assert len(widget.action_words) == 3


def test_initialization_word_list_replace_mode():
    """Test initializing with replace mode dict."""
    config = {"mode": "replace", "words": ["Custom1", "Custom2"]}
    widget = MessageWidget(action_words=config)
    assert widget.action_words == ["Custom1", "Custom2"]
    assert "Accomplishing" not in widget.action_words


def test_initialization_word_list_add_mode():
    """Test initializing with add mode dict."""
    config = {"mode": "add", "words": ["Custom1", "Custom2"]}
    widget = MessageWidget(action_words=config)
    expected_count = len(DEFAULT_ACTION_WORDS) + 2
    assert len(widget.action_words) == expected_count
    assert "Custom1" in widget.action_words
    assert "Accomplishing" in widget.action_words


def test_initialization_empty_words_fallback():
    """Test that empty word list falls back to defaults."""
    widget = MessageWidget(action_words=[])
    assert widget.action_words == DEFAULT_ACTION_WORDS


def test_initialization_custom_interval():
    """Test custom interval configuration."""
    widget = MessageWidget(interval={"min": 1.0, "max": 5.0})
    assert widget._min_interval == 1.0
    assert widget._max_interval == 5.0


def test_initialization_shimmer_config():
    """Test shimmer configuration."""
    shimmer_config = {
        "enabled": False,
        "width": 5,
        "light_color": "#FFFFFF",
        "speed": 2.0,
        "reverse": True,
    }
    widget = MessageWidget(shimmer=shimmer_config)
    assert widget._shimmer_enabled is False
    assert widget._shimmer_width == 5
    assert widget._shimmer_light_color == "#FFFFFF"
    assert widget._shimmer_speed == 2.0
    assert widget.reverse_shimmer is True


# Test color validation
def test_color_validation():
    """Test hex color validation."""
    widget = MessageWidget()

    widget.color = "#FF0000"
    assert widget.color == "#FF0000"

    with pytest.raises(ValueError, match="must start with #"):
        widget.color = "red"
    with pytest.raises(ValueError, match="must be #RRGGBB"):
        widget.color = "#FF"
    with pytest.raises(ValueError, match="Invalid hex"):
        widget.color = "#GGGGGG"


def test_color_validation_in_constructor():
    """Test color validation during construction."""
    with pytest.raises(ValueError):
        MessageWidget(color="invalid")


# Test action words management
def test_action_words_getter_returns_copy():
    """Test that action_words getter returns a copy."""
    widget = MessageWidget(action_words=["Word1", "Word2"])
    words = widget.action_words
    words.append("Word3")
    assert len(widget.action_words) == 2


def test_action_words_setter():
    """Test action_words setter replaces word list."""
    widget = MessageWidget()
    new_words = ["New1", "New2", "New3"]
    widget.action_words = new_words
    assert widget.action_words == new_words


def test_action_words_setter_empty_raises():
    """Test that setting empty word list raises error."""
    widget = MessageWidget()
    with pytest.raises(ValueError, match="Word list cannot be empty"):
        widget.action_words = []


def test_extend_action_words():
    """Test extending action words list."""
    widget = MessageWidget(action_words=["Word1", "Word2"])
    widget.extend_action_words(["Word3", "Word4"])
    assert len(widget.action_words) == 4
    assert "Word3" in widget.action_words
    assert "Word4" in widget.action_words


def test_word_list_immutability():
    """Test that word lists are properly copied."""
    original = ["Word1", "Word2"]
    widget = MessageWidget(action_words=original)
    original.append("Word3")
    assert len(widget.action_words) == 2


# Test word rotation
def test_word_selection_on_first_render():
    """Test that first call triggers word change."""
    widget = MessageWidget(action_words=["TestWord"])
    assert widget._calculate_next_word_change(0.0) is True
    widget._select_new_word()
    assert widget._current_word == "TestWord"


def test_word_rotation_timing():
    """Test word changes at correct intervals."""
    widget = MessageWidget(
        action_words=["Word1", "Word2"],
        interval={"min": 0.5, "max": 0.5},
    )
    assert widget._calculate_next_word_change(0.0) is True
    assert widget._calculate_next_word_change(0.3) is False
    assert widget._calculate_next_word_change(0.6) is True


def test_word_history_tracking():
    """Test that recent words are tracked to avoid repeats."""
    widget = MessageWidget(action_words=["Word1", "Word2", "Word3"])
    for _ in range(3):
        widget._select_new_word()
    assert len(widget._used_words) <= 5


def test_random_interval_range():
    """Test that intervals are within specified range."""
    widget = MessageWidget(interval={"min": 1.0, "max": 3.0})
    widget._calculate_next_word_change(0.0)
    assert 1.0 <= widget._next_interval <= 3.0


def test_update_with_custom_text():
    """Test update method with custom text."""
    widget = MessageWidget()
    widget.update(text="CustomText")
    assert widget._current_word == "CustomText"
    assert widget._last_word_change is None


def test_update_trigger_new():
    """Test update method to trigger new word."""
    widget = MessageWidget(action_words=["Word1", "Word2"])
    widget.update(trigger_new=True)
    assert widget._current_word in ["Word1", "Word2"]
    assert widget._last_word_change is None


def test_update_reverse_shimmer():
    """Test update method changes shimmer direction."""
    widget = MessageWidget()
    widget.update(reverse_shimmer=True)
    assert widget.reverse_shimmer is True
    widget.update(reverse_shimmer=False)
    assert widget.reverse_shimmer is False


# Test shimmer effect
def test_shimmer_position_calculation():
    """Test shimmer position changes over time."""
    widget = MessageWidget(shimmer={"enabled": True, "width": 3})
    text = "TestWord"
    result1 = widget._apply_shimmer(text, 0.0)
    result2 = widget._apply_shimmer(text, 1.0)
    assert isinstance(result1, Text)
    assert isinstance(result2, Text)


def test_shimmer_direction_left_to_right():
    """Test left-to-right shimmer direction."""
    widget = MessageWidget(shimmer={"enabled": True, "reverse": False})
    assert widget.reverse_shimmer is False


def test_shimmer_direction_right_to_left():
    """Test right-to-left shimmer direction."""
    widget = MessageWidget(shimmer={"enabled": True, "reverse": True})
    assert widget.reverse_shimmer is True


def test_shimmer_direction_toggle():
    """Test toggling shimmer direction via property."""
    widget = MessageWidget()
    widget.reverse_shimmer = True
    assert widget.reverse_shimmer is True
    widget.reverse_shimmer = False
    assert widget.reverse_shimmer is False


def test_shimmer_width_config():
    """Test shimmer width configuration."""
    widget = MessageWidget(shimmer={"width": 5})
    assert widget._shimmer_width == 5


def test_shimmer_disabled_render():
    """Test rendering without shimmer uses base color."""
    widget = MessageWidget(
        action_words=["Test"],
        shimmer={"enabled": False},
    )
    # Force a word to be set
    widget._current_word = "Test"
    rendered = widget.render()
    assert isinstance(rendered, Text)
    assert rendered.plain == "Test…"


def test_shimmer_wider_than_text():
    """Test shimmer effect when width exceeds text length."""
    widget = MessageWidget(
        action_words=["Hi"],
        shimmer={"enabled": True, "width": 10},
    )
    result = widget._apply_shimmer("Hi…", 0.0)
    assert isinstance(result, Text)


# Test render output
def test_render_in_progress():
    """Test render in IN_PROGRESS state."""
    widget = MessageWidget(
        action_words=["TestWord"],
        shimmer={"enabled": False},
    )
    rendered = widget.render()
    assert isinstance(rendered, Text)
    # Should contain a word + suffix
    assert rendered.plain.endswith("…")


def test_render_success():
    """Test render in success state."""
    widget = MessageWidget()
    widget._state = ComponentState.SUCCESS
    rendered = widget.render()
    assert rendered.plain == "Complete!"
    assert "#00FF00" in str(rendered.style)


def test_render_success_custom_text():
    """Test render in success state with custom text."""
    widget = MessageWidget(success_text="All done!")
    widget._state = ComponentState.SUCCESS
    assert widget.render().plain == "All done!"


def test_render_error():
    """Test render in error state."""
    widget = MessageWidget()
    widget._state = ComponentState.ERROR
    rendered = widget.render()
    assert rendered.plain == "Failed"
    assert "#FF0000" in str(rendered.style)


def test_render_error_custom_text():
    """Test render in error state with custom text."""
    widget = MessageWidget(error_text="Broken")
    widget._state = ComponentState.ERROR
    assert widget.render().plain == "Broken"


# Test state transitions
def test_state_transitions():
    """Test valid and invalid state transitions."""
    widget = MessageWidget()

    assert widget.state == ComponentState.IN_PROGRESS
    widget.success()
    assert widget.state == ComponentState.SUCCESS

    # SUCCESS -> ERROR (invalid)
    widget.error()
    assert widget.state == ComponentState.SUCCESS

    widget.reset()
    assert widget.state == ComponentState.IN_PROGRESS

    widget.error()
    assert widget.state == ComponentState.ERROR

    # ERROR -> SUCCESS (invalid)
    widget.success()
    assert widget.state == ComponentState.ERROR


def test_success_with_default_text():
    """Test success with default text."""
    widget = MessageWidget()
    widget.success()
    assert widget._success_text == "Complete!"


def test_error_with_default_text():
    """Test error with default text."""
    widget = MessageWidget()
    widget.error()
    assert widget._error_text == "Failed"


def test_success_with_custom_text():
    """Test success with custom text updates the text."""
    widget = MessageWidget()
    widget.success("Done!")
    assert widget._success_text == "Done!"
    assert widget.render().plain == "Done!"


def test_error_with_custom_text():
    """Test error with custom text updates the text."""
    widget = MessageWidget()
    widget.error("Timed out")
    assert widget._error_text == "Timed out"
    assert widget.render().plain == "Timed out"


def test_reset_clears_state():
    """Test reset clears word state and history."""
    widget = MessageWidget()
    widget._current_word = "SomeWord"
    widget._used_words = ["A", "B", "C"]
    widget._shimmer_start_time = 10.0
    widget.success()
    widget.reset()

    assert widget.state == ComponentState.IN_PROGRESS
    assert widget._current_word == ""
    assert widget._last_word_change is None
    assert widget._shimmer_start_time is None
    assert len(widget._used_words) == 0


# Test from_config
def test_from_config():
    """Test factory method from configuration dictionary."""
    config = {
        "action_words": ["Test1", "Test2"],
        "interval": {"min": 0.2, "max": 1.0},
        "color": "#FFA500",
        "shimmer": {"enabled": True, "width": 4},
        "suffix": "!!!",
        "success_text": "OK",
        "error_text": "ERR",
        "visible": False,
    }
    widget = MessageWidget.from_config(config)
    assert widget.action_words == ["Test1", "Test2"]
    assert widget._min_interval == 0.2
    assert widget._max_interval == 1.0
    assert widget.color == "#FFA500"
    assert widget._suffix == "!!!"
    assert widget._success_text == "OK"
    assert widget._error_text == "ERR"
    assert "hidden" in widget.classes


def test_from_config_defaults():
    """Test from_config with empty config uses defaults."""
    widget = MessageWidget.from_config({})
    assert widget.action_words == DEFAULT_ACTION_WORDS
    assert widget.color == "#D97706"
    assert widget._suffix == "…"


# Test repr
def test_repr():
    """Test string representation."""
    widget = MessageWidget()
    repr_str = repr(widget)
    assert "MessageWidget" in repr_str
    assert f"words={len(DEFAULT_ACTION_WORDS)}" in repr_str
    assert "IN_PROGRESS" in repr_str
    assert "shimmer=True" in repr_str


# Test feature parity
def test_feature_parity():
    """Verify all Rich MessageComponent APIs are available."""
    widget = MessageWidget()

    # Word management
    assert hasattr(widget, "action_words")
    assert hasattr(widget, "extend_action_words")

    # Control methods
    assert hasattr(widget, "update")
    assert hasattr(widget, "success")
    assert hasattr(widget, "error")
    assert hasattr(widget, "reset")

    # Properties
    assert hasattr(widget, "state")
    assert hasattr(widget, "reverse_shimmer")

    # Factory
    assert hasattr(MessageWidget, "from_config")

    # Visibility
    assert hasattr(widget, "show")
    assert hasattr(widget, "hide")
    assert hasattr(widget, "toggle")
    assert hasattr(widget, "set_visible")


# Test CSS defaults
def test_css_defaults():
    """Test DEFAULT_CSS is properly defined."""
    assert "MessageWidget" in MessageWidget.DEFAULT_CSS
    assert "hidden" in MessageWidget.DEFAULT_CSS
    assert "display: none" in MessageWidget.DEFAULT_CSS
    assert "success" in MessageWidget.DEFAULT_CSS
    assert "error" in MessageWidget.DEFAULT_CSS


# Test edge cases
def test_edge_cases_short_words():
    """Test handling of single character words."""
    widget = MessageWidget(action_words=["A", "B", "C"], shimmer={"enabled": False})
    rendered = widget.render()
    assert isinstance(rendered, Text)
    assert len(rendered.plain) >= 2  # At least "A…"


def test_edge_cases_long_words():
    """Test handling of very long words."""
    long_word = "A" * 50
    widget = MessageWidget(action_words=[long_word], shimmer={"enabled": False})
    rendered = widget.render()
    assert isinstance(rendered, Text)
    assert long_word in rendered.plain


def test_rapid_updates():
    """Test rapid successive updates."""
    widget = MessageWidget()
    for i in range(10):
        widget.update(text=f"Update{i}")
        assert widget._current_word == f"Update{i}"


def test_empty_action_words_recovery():
    """Test recovery when all words are in history."""
    widget = MessageWidget(action_words=["Only"])
    for _ in range(10):
        widget._select_new_word()
    assert widget._current_word == "Only"


# Async tests with Textual app
@pytest.mark.asyncio
async def test_animation_starts_on_mount():
    """Test that animation timer starts when mounted."""

    class MsgApp(App):
        def compose(self) -> ComposeResult:
            yield MessageWidget(id="msg")

    async with MsgApp().run_test() as pilot:
        msg = pilot.app.query_one("#msg", MessageWidget)
        assert msg._animation_timer is not None
        await pilot.pause()


@pytest.mark.asyncio
async def test_word_rotation_in_app():
    """Test that word rotation happens in app context."""

    class MsgApp(App):
        def compose(self) -> ComposeResult:
            yield MessageWidget(
                action_words=["Word1", "Word2"],
                shimmer={"enabled": False},
                id="msg",
            )

    async with MsgApp().run_test() as pilot:
        msg = pilot.app.query_one("#msg", MessageWidget)
        await pilot.pause()
        rendered = msg.render()
        # Should have selected a word
        assert rendered.plain in ["Word1…", "Word2…"]


@pytest.mark.asyncio
async def test_state_css_classes():
    """Test CSS classes are set correctly on state changes."""

    class StateApp(App):
        def compose(self) -> ComposeResult:
            yield MessageWidget(id="msg")

    async with StateApp().run_test() as pilot:
        msg = pilot.app.query_one("#msg", MessageWidget)

        assert "success" not in msg.classes
        assert "error" not in msg.classes

        msg.success()
        await pilot.pause()
        assert "success" in msg.classes
        assert "error" not in msg.classes

        msg.reset()
        await pilot.pause()
        assert "success" not in msg.classes
        assert "error" not in msg.classes

        msg.error()
        await pilot.pause()
        assert "error" in msg.classes
        assert "success" not in msg.classes


@pytest.mark.asyncio
async def test_visibility_toggle():
    """Test CSS class-based visibility changes."""

    class VisApp(App):
        def compose(self) -> ComposeResult:
            yield MessageWidget(id="msg")

    async with VisApp().run_test() as pilot:
        msg = pilot.app.query_one("#msg", MessageWidget)

        assert "hidden" not in msg.classes

        msg.hide()
        await pilot.pause()
        assert "hidden" in msg.classes

        msg.show()
        await pilot.pause()
        assert "hidden" not in msg.classes

        msg.toggle()
        await pilot.pause()
        assert "hidden" in msg.classes

        msg.set_visible(True)
        await pilot.pause()
        assert "hidden" not in msg.classes


@pytest.mark.asyncio
async def test_app_integration():
    """Test widget in full Textual app lifecycle."""

    class IntegrationApp(App):
        def compose(self) -> ComposeResult:
            yield MessageWidget(
                action_words=["Loading", "Processing"],
                shimmer={"enabled": False},
                id="m1",
            )
            yield MessageWidget(
                action_words=["Analyzing"],
                color="#FF00FF",
                id="m2",
            )

    async with IntegrationApp().run_test() as pilot:
        m1 = pilot.app.query_one("#m1", MessageWidget)
        m2 = pilot.app.query_one("#m2", MessageWidget)

        await pilot.pause()
        assert m1.state == ComponentState.IN_PROGRESS
        assert m2.color == "#FF00FF"

        m1.success("Done")
        await pilot.pause()
        assert m1.state == ComponentState.SUCCESS
        assert m1.render().plain == "Done"

        m2.error("Timeout")
        await pilot.pause()
        assert m2.state == ComponentState.ERROR
        assert m2.render().plain == "Timeout"

        m2.reset()
        await pilot.pause()
        assert m2.state == ComponentState.IN_PROGRESS


@pytest.mark.asyncio
async def test_widget_lifecycle():
    """Test widget mount/unmount lifecycle."""

    class LifecycleApp(App):
        def compose(self) -> ComposeResult:
            yield MessageWidget(id="msg")

    async with LifecycleApp().run_test() as pilot:
        msg = pilot.app.query_one("#msg", MessageWidget)
        assert msg.is_mounted
        assert msg._animation_timer is not None

        rendered = msg.render()
        assert isinstance(rendered, Text)

        await msg.remove()
        assert msg not in pilot.app.query(MessageWidget)


@pytest.mark.asyncio
async def test_success_stops_animation():
    """Test that success() stops the animation timer."""

    class MsgApp(App):
        def compose(self) -> ComposeResult:
            yield MessageWidget(id="msg")

    async with MsgApp().run_test() as pilot:
        msg = pilot.app.query_one("#msg", MessageWidget)
        assert msg._animation_timer is not None

        msg.success()
        await pilot.pause()
        assert msg._animation_timer is None


@pytest.mark.asyncio
async def test_error_stops_animation():
    """Test that error() stops the animation timer."""

    class MsgApp(App):
        def compose(self) -> ComposeResult:
            yield MessageWidget(id="msg")

    async with MsgApp().run_test() as pilot:
        msg = pilot.app.query_one("#msg", MessageWidget)
        assert msg._animation_timer is not None

        msg.error()
        await pilot.pause()
        assert msg._animation_timer is None


@pytest.mark.asyncio
async def test_reset_restarts_animation():
    """Test that reset() restarts the animation timer."""

    class MsgApp(App):
        def compose(self) -> ComposeResult:
            yield MessageWidget(id="msg")

    async with MsgApp().run_test() as pilot:
        msg = pilot.app.query_one("#msg", MessageWidget)

        msg.success()
        await pilot.pause()
        assert msg._animation_timer is None

        msg.reset()
        await pilot.pause()
        assert msg._animation_timer is not None
