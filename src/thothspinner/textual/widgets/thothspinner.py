"""Textual ThothSpinner Orchestrator Widget.

Unified orchestrator that composes all 5 spinner components (Spinner, Message,
Progress, Timer, Hint) into a single coordinated Textual widget with unified
state management, configuration hierarchy, and component access.

Design notes (R8):
    This orchestrator uses imperative state propagation (_propagate_state calling
    each child's success/error/reset methods) rather than Textual's data_bind().
    data_bind() maps reactive-to-reactive, but our children need different behavior
    on state change (spinner shows icon, timer freezes, message shows text, hint
    hides). Imperative propagation is the correct pattern here.
"""

from __future__ import annotations

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.timer import Timer as TextualTimer
from textual.widget import Widget

from ...core.states import ComponentState
from .hint import HintWidget
from .message import MessageWidget
from .progress import ProgressWidget
from .spinner import SpinnerWidget
from .timer import TimerWidget


class ThothSpinnerWidget(Widget, can_focus=False):
    """Unified orchestrator widget composing all 5 spinner components.

    Combines SpinnerWidget, MessageWidget, ProgressWidget, TimerWidget, and
    HintWidget into a single coordinated display with unified state management,
    configuration hierarchy, and convenient component access.

    Args:
        spinner_style: Built-in spinner style name. Defaults to "npm_dots".
        message_text: Initial message text. Defaults to "Loading".
        message_shimmer: Enable shimmer effect on message. Defaults to True.
        progress_format: Progress display format. Defaults to "fraction".
        timer_format: Timer display format. Defaults to "auto".
        hint_text: Hint text to display. Defaults to "(esc to cancel)".
        success_duration: Auto-clear duration for success state in seconds.
        error_duration: Auto-clear duration for error state in seconds.
        config: Full configuration dict (overrides kwargs).
        render_order: Component display order list.
        name: Optional name for the widget.
        id: Optional ID for the widget.
        classes: Optional CSS classes.
        disabled: Whether the widget is disabled.

    Example:
        >>> from thothspinner.textual.widgets import ThothSpinnerWidget
        >>> spinner = ThothSpinnerWidget(spinner_style="npm_dots")
    """

    DEFAULT_CSS: ClassVar[str] = """
    ThothSpinnerWidget {
        width: auto;
        height: 1;
        padding: 0;
        background: transparent;
        layout: horizontal;
    }

    ThothSpinnerWidget Horizontal {
        width: auto;
        height: 1;
    }

    ThothSpinnerWidget.-vertical {
        height: auto;
    }

    ThothSpinnerWidget.-vertical Vertical {
        height: auto;
        width: 100%;
    }

    ThothSpinnerWidget.-vertical SpinnerWidget {
        width: 100%;
        margin: 0 0 1 0;
    }

    ThothSpinnerWidget.-vertical MessageWidget {
        width: 100%;
        margin: 0 0 1 0;
    }

    ThothSpinnerWidget.-vertical ProgressWidget {
        width: 100%;
        margin: 0 0 1 0;
    }

    ThothSpinnerWidget.-vertical TimerWidget {
        width: 100%;
        margin: 0 0 1 0;
    }

    ThothSpinnerWidget.-vertical HintWidget {
        width: 100%;
        margin: 0 0 1 0;
    }
    """

    _state = reactive(ComponentState.IN_PROGRESS)

    # Valid component names and default render order
    VALID_COMPONENTS: ClassVar[tuple[str, ...]] = (
        "spinner",
        "message",
        "progress",
        "timer",
        "hint",
    )

    def __init__(
        self,
        *,
        spinner_style: str = "npm_dots",
        message_text: str = "Loading",
        message_shimmer: bool = True,
        progress_format: str = "fraction",
        timer_format: str = "auto",
        hint_text: str = "(esc to cancel)",
        success_duration: float | None = None,
        error_duration: float | None = None,
        config: dict[str, Any] | None = None,
        render_order: list[str] | None = None,
        layout: str = "horizontal",
        visible: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize the ThothSpinnerWidget."""
        self._layout_mode = layout
        _cls_parts = [c for c in (classes or "").split() if c]
        if layout == "vertical":
            _cls_parts.insert(0, "-vertical")
        super().__init__(
            name=name,
            id=id,
            classes=" ".join(_cls_parts) if _cls_parts else None,
            disabled=disabled,
        )

        # Store durations for auto-clear
        self.success_duration = success_duration
        self.error_duration = error_duration
        self._clear_timer_handle: TextualTimer | None = None

        # Build configuration from kwargs and optional config dict
        kwargs_dict = {
            "spinner_style": spinner_style,
            "message_text": message_text,
            "message_shimmer": message_shimmer,
            "progress_format": progress_format,
            "timer_format": timer_format,
            "hint_text": hint_text,
        }
        self.config = self._build_config(config or {}, kwargs_dict)

        # Set render order
        if render_order is not None:
            self._validate_render_order(render_order)
            self._render_order: tuple[str, ...] = tuple(render_order)
        elif "render_order" in self.config:
            order = self.config["render_order"]
            self._validate_render_order(order)
            self._render_order = tuple(order)
        else:
            self._render_order = self.VALID_COMPONENTS

        # Eagerly create all child widgets
        self._components: dict[str, Widget] = {}
        self._create_all_components()

        if not visible:
            self.display = False

    def _build_config(self, config_dict: dict[str, Any], kwargs: dict[str, Any]) -> dict[str, Any]:
        """Build configuration from kwargs and optional config dict.

        Args:
            config_dict: User-provided configuration dict.
            kwargs: Constructor keyword arguments.

        Returns:
            Merged configuration dictionary.
        """
        result: dict[str, Any] = {
            "defaults": {
                "color": "#D97706",
                "visible": True,
            },
            "elements": {},
        }

        # Merge user config dict first
        if config_dict:
            if "defaults" in config_dict:
                result["defaults"].update(config_dict["defaults"])
            if "elements" in config_dict:
                result["elements"].update(config_dict["elements"])
            if "render_order" in config_dict:
                result["render_order"] = config_dict["render_order"]
            if "durations" in config_dict:
                durations = config_dict["durations"]
                if "success" in durations and durations["success"] is not None:
                    self.success_duration = self.success_duration or durations["success"]
                if "error" in durations and durations["error"] is not None:
                    self.error_duration = self.error_duration or durations["error"]

        # Apply kwargs as element configs (setdefault so config dict takes priority)
        elements = result["elements"]
        if kwargs.get("spinner_style"):
            elements.setdefault("spinner", {}).setdefault("style", kwargs["spinner_style"])
        if kwargs.get("message_text"):
            msg = elements.setdefault("message", {})
            msg.setdefault("action_words", [kwargs["message_text"]])
        if "message_shimmer" in kwargs:
            msg = elements.setdefault("message", {})
            msg.setdefault("shimmer", {}).setdefault("enabled", kwargs["message_shimmer"])
        if kwargs.get("progress_format"):
            elements.setdefault("progress", {}).setdefault(
                "format_style", kwargs["progress_format"]
            )
        if kwargs.get("timer_format"):
            elements.setdefault("timer", {}).setdefault("format_style", kwargs["timer_format"])
        if kwargs.get("hint_text"):
            elements.setdefault("hint", {}).setdefault("text", kwargs["hint_text"])

        # Validate element keys
        for component_type in elements:
            if component_type not in self.VALID_COMPONENTS:
                raise KeyError(
                    f"Invalid component type: {component_type}. "
                    f"Valid types: {list(self.VALID_COMPONENTS)}"
                )

        return result

    def _validate_render_order(self, order: list[str]) -> None:
        """Validate render order contains only valid component names.

        Args:
            order: List of component names.

        Raises:
            KeyError: If any component name is invalid.
        """
        invalid = set(order) - set(self.VALID_COMPONENTS)
        if invalid:
            raise KeyError(
                f"Invalid components in render_order: {invalid}. "
                f"Valid types: {list(self.VALID_COMPONENTS)}"
            )

    def _resolve_config(self, component_type: str) -> dict[str, Any]:
        """Resolve configuration for a component with inheritance.

        Config hierarchy: defaults -> element-specific overrides.

        Args:
            component_type: Type of component.

        Returns:
            Resolved configuration dictionary.
        """
        config: dict[str, Any] = {}

        # Apply defaults (only color and visible)
        defaults = self.config.get("defaults", {})
        if "color" in defaults:
            config["color"] = defaults["color"]
        if "visible" in defaults:
            config["visible"] = defaults["visible"]

        # Apply element-specific config (overrides defaults)
        element_config = self.config.get("elements", {}).get(component_type, {})
        config.update(element_config)

        return config

    def _create_all_components(self) -> None:
        """Create all 5 child widgets from resolved configs."""
        spinner_config = self._resolve_config("spinner")
        message_config = self._resolve_config("message")
        progress_config = self._resolve_config("progress")
        timer_config = self._resolve_config("timer")
        hint_config = self._resolve_config("hint")

        self._components = {
            "spinner": SpinnerWidget.from_config(spinner_config),
            "message": MessageWidget.from_config(message_config),
            "progress": ProgressWidget.from_config(progress_config),
            "timer": TimerWidget.from_config(timer_config),
            "hint": HintWidget.from_config(hint_config),
        }

    def compose(self) -> ComposeResult:
        """Yield child widgets in render order within a Horizontal or Vertical container."""
        container = Vertical() if self._layout_mode == "vertical" else Horizontal()
        with container:
            for name in self._render_order:
                if name in self._components:
                    yield self._components[name]

    # --- Properties ---

    @property
    def state(self) -> ComponentState:
        """Get the current orchestrator state."""
        return self._state

    @property
    def spinner(self) -> SpinnerWidget:
        """Access the spinner child widget."""
        return self._components["spinner"]  # type: ignore[return-value]

    @property
    def message(self) -> MessageWidget:
        """Access the message child widget."""
        return self._components["message"]  # type: ignore[return-value]

    @property
    def progress(self) -> ProgressWidget:
        """Access the progress child widget."""
        return self._components["progress"]  # type: ignore[return-value]

    @property
    def timer(self) -> TimerWidget:
        """Access the timer child widget."""
        return self._components["timer"]  # type: ignore[return-value]

    @property
    def hint(self) -> HintWidget:
        """Access the hint child widget."""
        return self._components["hint"]  # type: ignore[return-value]

    def get_component(self, component_type: str) -> Widget:
        """Get a component by type name.

        Args:
            component_type: Type of component ("spinner", "message", etc.)

        Returns:
            The requested child widget.

        Raises:
            KeyError: If component_type is invalid.
        """
        if component_type not in self._components:
            raise KeyError(
                f"Invalid component type: {component_type}. "
                f"Valid types: {list(self._components.keys())}"
            )
        return self._components[component_type]

    # --- State management ---

    def _validate_transition(self, new_state: ComponentState) -> None:
        """Validate state transition.

        Args:
            new_state: Target state.

        Raises:
            ValueError: If transition is invalid.
        """
        if not self._state.can_transition_to(new_state):
            raise ValueError(
                f"Invalid state transition from {self._state.name} to {new_state.name}"
            )

    def start(self) -> None:
        """Start the orchestrator in in_progress state.

        Starts the spinner animation and timer.
        """
        self._state = ComponentState.IN_PROGRESS
        self._cancel_clear_timer()

        # Start animated components
        spinner = self._components["spinner"]
        if hasattr(spinner, "start"):
            spinner.start()  # type: ignore[union-attr]

        timer = self._components["timer"]
        if hasattr(timer, "start"):
            timer.start()  # type: ignore[union-attr]

    def success(self, message: str | None = None, duration: float | None = None) -> None:
        """Transition to success state.

        Propagates success to all child widgets and optionally schedules auto-clear.

        Args:
            message: Optional success message passed to children.
            duration: Override default success_duration for auto-clear.
        """
        self._validate_transition(ComponentState.SUCCESS)
        self._state = ComponentState.SUCCESS
        self._propagate_state(ComponentState.SUCCESS, message)

        clear_duration = duration or self.success_duration
        if clear_duration is not None:
            self._schedule_clear(clear_duration)

    def error(self, message: str | None = None, duration: float | None = None) -> None:
        """Transition to error state.

        Propagates error to all child widgets and optionally schedules auto-clear.

        Args:
            message: Optional error message passed to children.
            duration: Override default error_duration for auto-clear.
        """
        self._validate_transition(ComponentState.ERROR)
        self._state = ComponentState.ERROR
        self._propagate_state(ComponentState.ERROR, message)

        clear_duration = duration or self.error_duration
        if clear_duration is not None:
            self._schedule_clear(clear_duration)

    def reset(self) -> None:
        """Reset to in_progress state.

        Resets all child widgets and cancels any pending auto-clear.
        """
        self._cancel_clear_timer()
        self._state = ComponentState.IN_PROGRESS

        for name in self._render_order:
            component = self._components.get(name)
            if component is not None and hasattr(component, "reset"):
                component.reset()  # type: ignore[union-attr]
            if component is not None:
                component.display = True

    def clear(self) -> None:
        """Hide all child widgets and cancel auto-clear timer."""
        self._cancel_clear_timer()
        for component in self._components.values():
            component.display = False

    def stop(self) -> None:
        """Alias for clear() -- stop and hide display."""
        self.clear()

    def _propagate_state(self, state: ComponentState, message: str | None = None) -> None:
        """Propagate state change to all child widgets.

        Args:
            state: The new state to propagate.
            message: Optional message to pass to child state methods.
        """
        state_method = state.name.lower()  # "success" or "error"

        for name in self._render_order:
            component = self._components.get(name)
            if component is None:
                continue

            method = getattr(component, state_method, None)
            if method is not None:
                method(message)

    # --- Auto-clear timer ---

    def _schedule_clear(self, duration: float) -> None:
        """Schedule auto-clear after a duration.

        Args:
            duration: Seconds before auto-clear.
        """
        self._cancel_clear_timer()
        if self.is_mounted:
            self._clear_timer_handle = self.set_timer(duration, self.clear)

    def _cancel_clear_timer(self) -> None:
        """Cancel any pending auto-clear timer."""
        if self._clear_timer_handle is not None:
            self._clear_timer_handle.stop()
            self._clear_timer_handle = None

    # --- Lifecycle ---

    def on_unmount(self) -> None:
        """Clean up timers when widget is unmounted."""
        self._cancel_clear_timer()

    # --- Reactive watchers ---

    def watch__state(self, new_state: ComponentState) -> None:
        """React to state changes by updating CSS classes."""
        if new_state == ComponentState.IN_PROGRESS:
            self.remove_class("success", "error")
        elif new_state == ComponentState.SUCCESS:
            self.remove_class("error")
            self.add_class("success")
        elif new_state == ComponentState.ERROR:
            self.remove_class("success")
            self.add_class("error")

    # --- Convenience methods ---

    def update_progress(self, *, current: int, total: int | None = None) -> None:
        """Update the progress component.

        Args:
            current: Current progress value.
            total: Optional new total value.
        """
        progress = self._components["progress"]
        if total is not None:
            progress.total = total  # type: ignore[union-attr]
        progress.set(current)  # type: ignore[union-attr]

    def set_message(self, *, text: str) -> None:
        """Update the message component text.

        Args:
            text: New message text to display.
        """
        message = self._components["message"]
        message.configure(text=text)  # type: ignore[union-attr]

    def set_hint(self, *, text: str) -> None:
        """Update the hint component text.

        Args:
            text: New hint text to display.
        """
        hint = self._components["hint"]
        hint.text = text  # type: ignore[union-attr]

    def set_spinner_style(self, *, style: str) -> None:
        """Change the spinner animation style at runtime.

        Mutates the existing SpinnerWidget in-place rather than replacing it,
        avoiding issues with widget lifecycle and DOM ownership.

        Args:
            style: Built-in spinner style name.
        """
        spinner = self._components["spinner"]
        if hasattr(spinner, "set_style"):
            spinner.set_style(style)  # type: ignore[union-attr]

    def set_shimmer_direction(self, *, direction: str) -> None:
        """Control shimmer direction on the message widget.

        Args:
            direction: "left-to-right" or "right-to-left".
        """
        message = self._components["message"]
        if hasattr(message, "reverse_shimmer"):
            message.reverse_shimmer = direction == "right-to-left"  # type: ignore[union-attr]

    def update_component(self, component_type: str, **kwargs: Any) -> None:
        """Generic update method for any component.

        Args:
            component_type: Type of component to update.
            **kwargs: Attributes to update on the component.

        Raises:
            KeyError: If component_type is invalid.
        """
        component = self.get_component(component_type)
        if hasattr(component, "configure"):
            component.configure(**kwargs)  # type: ignore[union-attr]
        else:
            for key, value in kwargs.items():
                if hasattr(component, key):
                    setattr(component, key, value)

    # --- Visibility ---

    def show(self) -> None:
        """Show the orchestrator widget."""
        self.display = True

    def hide(self) -> None:
        """Hide the orchestrator widget."""
        self.display = False

    def toggle(self) -> None:
        """Toggle visibility state."""
        self.display = not self.display

    def set_visible(self, visible: bool) -> None:
        """Set visibility.

        Args:
            visible: Whether the widget should be visible.
        """
        self.display = visible

    # --- Factory ---

    @classmethod
    def from_dict(cls, config: dict[str, Any], **kwargs: Any) -> ThothSpinnerWidget:
        """Create ThothSpinnerWidget from configuration dict.

        Args:
            config: Configuration dictionary (not mutated).
            **kwargs: Additional keyword arguments override config.

        Returns:
            ThothSpinnerWidget instance.
        """
        # R5: Copy to avoid mutating the caller's dict
        config = config.copy()

        # Extract top-level kwargs from config copy
        init_kwargs: dict[str, Any] = {}
        if "spinner_style" in config:
            init_kwargs["spinner_style"] = config.pop("spinner_style")
        if "message_text" in config:
            init_kwargs["message_text"] = config.pop("message_text")
        if "message_shimmer" in config:
            init_kwargs["message_shimmer"] = config.pop("message_shimmer")
        if "progress_format" in config:
            init_kwargs["progress_format"] = config.pop("progress_format")
        if "timer_format" in config:
            init_kwargs["timer_format"] = config.pop("timer_format")
        if "hint_text" in config:
            init_kwargs["hint_text"] = config.pop("hint_text")
        if "success_duration" in config:
            init_kwargs["success_duration"] = config.pop("success_duration")
        if "error_duration" in config:
            init_kwargs["error_duration"] = config.pop("error_duration")
        if "render_order" in config:
            init_kwargs["render_order"] = config.pop("render_order")

        # Remaining config goes as config dict
        if config:
            init_kwargs["config"] = config

        # kwargs override everything
        init_kwargs.update(kwargs)
        return cls(**init_kwargs)

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"ThothSpinnerWidget(state={self._state.name}, components={list(self._render_order)})"
        )
