"""ThothSpinner orchestrator for Rich console output.

Unified orchestrator that combines all spinner components into a coordinated
display with state management and configuration hierarchy.
"""

from __future__ import annotations

import threading
import time
from threading import RLock
from typing import Any, TypedDict

from rich.columns import Columns
from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.measure import Measurement
from rich.text import Text

from thothspinner.core.color import COLOR_DEFAULT, COLOR_ERROR, COLOR_SUCCESS
from thothspinner.core.states import ComponentState
from thothspinner.rich.components import (
    HintComponent,
    MessageComponent,
    ProgressComponent,
    SpinnerComponent,
    TimerComponent,
)


class ElementConfig(TypedDict, total=False):
    """Type hints for element configuration."""

    color: str
    visible: bool
    style: str
    shimmer: dict[str, Any]
    format: dict[str, Any]
    text: str
    success_icon: str
    error_icon: str


class ThothSpinnerConfig(TypedDict, total=False):
    """Type hints for configuration structure."""

    defaults: dict[str, Any]
    elements: dict[str, ElementConfig]
    render_order: list[str]
    states: dict[str, dict[str, Any]]
    fade_away: dict[str, Any]
    durations: dict[str, float | None]


class ThothSpinner:
    """Unified orchestrator for all spinner components.

    Combines multiple progress indication components (spinner, message,
    progress, timer, hint) into a single coordinated display following
    Rich's renderable protocol.

    Args:
        spinner_style: Built-in spinner style name. Defaults to "npm_dots".
        message_text: Initial message text. Defaults to "Loading".
        message_shimmer: Enable shimmer effect on message. Defaults to True.
        progress_format: Progress display format. Defaults to "percentage".
        timer_format: Timer display format. Defaults to "auto".
        hint_text: Hint text to display. Defaults to "(esc to cancel)".
        success_duration: Auto-clear duration for success state in seconds.
        error_duration: Auto-clear duration for error state in seconds.
        **config: Additional configuration as dict.

    Example:
        >>> from rich.console import Console
        >>> from rich.live import Live
        >>> spinner = ThothSpinner()
        >>> with Live(spinner, console=console):
        ...     spinner.start()
        ...     # Do work...
        ...     spinner.success()

    Attributes:
        config: Current configuration
        state: Current state (IN_PROGRESS, SUCCESS, ERROR)
    """

    def __init__(
        self,
        *,  # keyword-only arguments like Rich's Status
        spinner_style: str = "npm_dots",
        message_text: str = "Loading",
        message_shimmer: bool = True,
        progress_format: str = "percentage",
        timer_format: str = "auto",
        hint_text: str = "(esc to cancel)",
        success_duration: float | None = None,
        error_duration: float | None = None,
        **config: Any,
    ) -> None:
        """Initialize with keyword arguments following Rich patterns."""
        # Thread safety like Rich's Progress
        self._lock = RLock()

        # Simplified registry with short names
        self._components: dict[str, Any] = {}
        self._component_visibility_defaults: dict[str, bool] = {}
        # Immutable render order (tuple prevents mutations)
        self._render_order: tuple[str, ...] = ("spinner", "message", "progress", "timer", "hint")

        # Use ComponentState enum for type safety
        self._state: ComponentState = ComponentState.IN_PROGRESS

        # Auto-clear durations
        self.success_duration = success_duration
        self.error_duration = error_duration
        self._clear_timer: threading.Timer | None = None

        # Track timing
        self._start_time: float | None = None
        self._fade_start_time: float | None = None
        self._fade_progress: int | None = None

        # Build configuration from kwargs and config dict
        kwargs_dict = {
            "spinner_style": spinner_style,
            "message_text": message_text,
            "message_shimmer": message_shimmer,
            "progress_format": progress_format,
            "timer_format": timer_format,
            "hint_text": hint_text,
            "success_duration": success_duration,
            "error_duration": error_duration,
        }
        self.config = self._build_config(config, kwargs_dict)

        # Eagerly create all components (like Rich's Status creates Spinner)
        self._create_all_components()

    def _build_config(self, config_dict: dict[str, Any], kwargs: dict[str, Any]) -> dict[str, Any]:
        """Build configuration from kwargs and optional config dict.

        Uses TypedDict for hints but accepts plain dicts at runtime.
        """
        # Start with defaults
        result = {
            "defaults": {
                "color": COLOR_DEFAULT,
                "visible": True,
                "success": {"color": COLOR_SUCCESS, "behavior": "indicator"},
                "error": {"color": COLOR_ERROR, "behavior": "indicator"},
            },
            "elements": {},
            "render_order": list(self._render_order),  # Convert tuple to list for config
            "durations": {
                "success": kwargs.get("success_duration"),
                "error": kwargs.get("error_duration"),
            },
        }

        # Merge any passed config dict
        if config_dict:
            result.update(config_dict)

        # Apply kwargs as element configs (merge, don't replace)
        if kwargs.get("spinner_style"):
            result.setdefault("elements", {}).setdefault("spinner", {})["style"] = kwargs[
                "spinner_style"
            ]
        if kwargs.get("message_text"):
            msg_config = result.setdefault("elements", {}).setdefault("message", {})
            msg_config["text"] = kwargs["message_text"]
            msg_config.setdefault("shimmer", {})["enabled"] = kwargs.get("message_shimmer", True)
        if kwargs.get("progress_format"):
            prog_config = result.setdefault("elements", {}).setdefault("progress", {})
            prog_config.setdefault("format", {})["style"] = kwargs["progress_format"]
        if kwargs.get("timer_format"):
            timer_config = result.setdefault("elements", {}).setdefault("timer", {})
            timer_config.setdefault("format", {})["style"] = kwargs["timer_format"]
        if kwargs.get("hint_text"):
            result.setdefault("elements", {}).setdefault("hint", {})["text"] = kwargs["hint_text"]

        # Validate component types
        valid_types = set(self._render_order)
        for component_type in result.get("elements", {}):
            if component_type not in valid_types:
                raise KeyError(
                    f"Invalid component type: {component_type}. Valid types: {valid_types}"
                )

        return result

    def _get_state_settings(self, state: ComponentState) -> dict[str, Any]:
        """Resolve top-level settings for a terminal state."""
        state_name = state.name.lower()
        settings: dict[str, Any] = {}

        for source in (
            self.config.get("defaults", {}).get(state_name, {}),
            self.config.get("states", {}).get(state_name, {}),
        ):
            if not isinstance(source, dict):
                continue
            for key, value in source.items():
                if key not in self._render_order:
                    settings[key] = value

        return settings

    def _resolve_config(
        self, component_type: str, state: ComponentState | None = None
    ) -> dict[str, Any]:
        """Resolve configuration with proper inheritance: component > state > global.

        Raises KeyError for invalid component types.
        """
        if component_type not in self._render_order:
            raise KeyError(f"Invalid component type: {component_type}")

        config = {
            key: value
            for key, value in self.config.get("defaults", {}).items()
            if key not in {"success", "error"}
        }

        # Apply state-specific config if provided
        if state:
            config.update(
                {
                    key: value
                    for key, value in self._get_state_settings(state).items()
                    if key not in {"behavior", "duration", "message"}
                }
            )
            state_name = state.name.lower()
            if state_name in self.config.get("states", {}):
                state_config = self.config["states"][state_name]
                if component_type in state_config:
                    config.update(state_config[component_type])

        # Apply component-specific config
        if component_type in self.config.get("elements", {}):
            config.update(self.config["elements"][component_type])

        return config

    def _get_state_component_overrides(
        self, component_type: str, state: ComponentState
    ) -> dict[str, Any]:
        """Resolve component overrides defined directly under ``states.<state>``."""
        state_name = state.name.lower()
        overrides: dict[str, Any] = {}

        for source in (
            self.config.get("defaults", {}).get(state_name, {}),
            self.config.get("states", {}).get(state_name, {}),
        ):
            if not isinstance(source, dict):
                continue
            component_overrides = source.get(component_type)
            if isinstance(component_overrides, dict):
                overrides.update(component_overrides)

        return overrides

    def _validate_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Validate and normalize configuration.

        Uses TypedDict for hints but accepts plain dicts.
        """
        # Ensure defaults exist
        if "defaults" not in config:
            config["defaults"] = {
                "color": COLOR_DEFAULT,
                "visible": True,
                "success": {"color": COLOR_SUCCESS, "behavior": "indicator"},
                "error": {"color": COLOR_ERROR, "behavior": "indicator"},
            }

        # Ensure elements dict exists
        if "elements" not in config:
            config["elements"] = {}

        # Validate component types in elements
        valid_components = set(self._render_order)
        for component_type in config["elements"]:
            if component_type not in valid_components:
                raise KeyError(
                    f"Invalid component type: {component_type}. "
                    f"Valid types: {sorted(valid_components)}"
                )

        # Validate element configs are dicts
        for key, value in config["elements"].items():
            if not isinstance(value, dict):
                raise ValueError(f"Element config for {key} must be a dict, got {type(value)}")

        # Validate render_order if provided
        if "render_order" in config:
            order = config["render_order"]
            invalid = set(order) - valid_components
            if invalid:
                raise KeyError(f"Invalid components in render_order: {invalid}")
            # Store as tuple for immutability
            self._render_order = tuple(order)

        return config

    def _create_all_components(self) -> None:
        """Eagerly create all 5 components on initialization.

        Like Rich's Status which creates its Spinner immediately.
        """
        with self._lock:
            # Resolve configs once so component visibility defaults survive construction and reset.
            resolved_configs = {name: self._resolve_config(name) for name in self._render_order}
            self._component_visibility_defaults = {
                name: bool(config.get("visible", True)) for name, config in resolved_configs.items()
            }

            spinner_config = self._filter_component_config(resolved_configs["spinner"])
            message_config = self._filter_component_config(resolved_configs["message"])
            progress_config = self._filter_component_config(resolved_configs["progress"])
            timer_config = self._filter_component_config(resolved_configs["timer"])
            hint_config = self._filter_component_config(resolved_configs["hint"])

            self._components = {
                "spinner": SpinnerComponent(**spinner_config),
                "message": MessageComponent(**message_config),
                "progress": ProgressComponent(**progress_config),
                "timer": TimerComponent(**timer_config),
                "hint": HintComponent(**hint_config),
            }

            for name, component in self._components.items():
                component.visible = self._component_visibility_defaults[name]

            # Validate render order matches actual components
            if "render_order" in self.config:
                order = self.config["render_order"]
                invalid = set(order) - set(self._components.keys())
                if invalid:
                    raise KeyError(f"Invalid components in render_order: {invalid}")
                # Convert to immutable tuple
                self._render_order = tuple(order)

    def _filter_component_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Filter out properties that shouldn't be passed to component init.

        Some properties like 'success' and 'error' are state configs, not init params.
        'visible' is a property, not an init parameter.
        """
        # Properties that are metadata, not component init parameters
        exclude_keys = {"success", "error", "behavior", "duration", "visible"}
        return {k: v for k, v in config.items() if k not in exclude_keys}

    def get_component(self, component_type: str) -> Any:
        """Type-based component access with validation.

        Args:
            component_type: Type of component ("spinner", "message", etc.)

        Returns:
            The requested component

        Raises:
            KeyError: If component_type is invalid
        """
        with self._lock:
            if component_type not in self._components:
                raise KeyError(
                    f"Invalid component type: {component_type}. "
                    f"Valid types: {list(self._components.keys())}"
                )
            return self._components[component_type]

    def __rich__(self) -> Columns | Text:
        """Rich protocol for rendering all components."""
        with self._lock:
            # Use render_order for consistent display
            visible = [
                self._components[name]
                for name in self._render_order
                if name in self._components and self._components[name].visible
            ]

            # Handle fade-away animation if active
            if self._fade_progress is not None:
                visible = self._apply_fade_away(visible)

            # Return empty text if no visible components
            if not visible:
                return Text("")

            return Columns(visible, padding=(0, 1))

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Advanced rendering with console access for width constraints.

        Thread-safe rendering with proper locking.
        """
        with self._lock:
            # Filter visible components using immutable render_order
            visible = [
                self._components[name]
                for name in self._render_order
                if name in self._components and self._components[name].visible
            ]

            if not visible:
                yield Text("")
                return

            # Handle fade-away animation
            if self._fade_progress is not None:
                visible = self._apply_fade_away(visible)

            # Use Columns for horizontal layout with proper spacing
            if self.config.get("layout", "horizontal") == "vertical":
                # Vertical layout using Group
                yield Group(*visible)
            else:
                # Horizontal layout (default) using Columns
                yield Columns(visible, padding=(0, 1), expand=False)

    def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement:
        """Measure the minimum and maximum width of the renderable.

        Implements Rich protocol for width calculation.
        """
        with self._lock:
            visible = [
                self._components[name]
                for name in self._render_order
                if name in self._components and self._components[name].visible
            ]

            if not visible:
                return Measurement(0, 0)

            # Calculate total width with padding
            measurements = [Measurement.get(console, options, comp) for comp in visible]
            padding_width = (len(visible) - 1) * 2  # padding between components

            min_width = sum(m.minimum for m in measurements) + padding_width
            max_width = sum(m.maximum for m in measurements) + padding_width

            return Measurement(min_width, max_width)

    # State Management Methods

    def _validate_transition(self, new_state: ComponentState) -> None:
        """Validate state transitions using enum's built-in validation.

        Raises:
            ValueError: If transition is invalid
        """
        if not self._state.can_transition_to(new_state):
            raise ValueError(
                f"Invalid state transition from {self._state.name} to {new_state.name}"
            )

    @property
    def state(self) -> ComponentState:
        """Get the current component state."""
        with self._lock:
            return self._state

    def start(self) -> None:
        """Begin in in_progress state.

        Thread-safe. Cancels any pending auto-clear timer and starts
        all child components.
        """
        with self._lock:
            self._state = ComponentState.IN_PROGRESS
            self._start_time = time.time()

            # Cancel any pending auto-clear
            if self._clear_timer:
                self._clear_timer.cancel()
                self._clear_timer = None

            for name in self._render_order:
                component = self._components[name]
                if hasattr(component, "start"):
                    component.start()

    def success(self, message: str | None = None, duration: float | None = None) -> None:
        """Transition to success state with optional auto-clear.

        Thread-safe. Propagates success to all child components and
        optionally schedules auto-clear via a daemon timer thread.

        Args:
            message: Optional success message to display.
            duration: Override default success_duration for auto-clear (seconds).

        Raises:
            ValueError: If current state cannot transition to SUCCESS.
        """
        with self._lock:
            self._validate_transition(ComponentState.SUCCESS)
            self._state = ComponentState.SUCCESS

            # Propagate to components
            self._propagate_state(ComponentState.SUCCESS, message)

            # Handle auto-clear with threading.Timer
            clear_duration = self._get_clear_duration(ComponentState.SUCCESS, duration)
            if clear_duration is not None:
                if self._clear_timer:
                    self._clear_timer.cancel()
                self._clear_timer = threading.Timer(clear_duration, self.clear)
                self._clear_timer.daemon = True
                self._clear_timer.start()

    def error(self, message: str | None = None, duration: float | None = None) -> None:
        """Transition to error state with optional auto-clear.

        Thread-safe. Propagates error to all child components and
        optionally schedules auto-clear via a daemon timer thread.

        Args:
            message: Optional error message to display.
            duration: Override default error_duration for auto-clear (seconds).

        Raises:
            ValueError: If current state cannot transition to ERROR.
        """
        with self._lock:
            self._validate_transition(ComponentState.ERROR)
            self._state = ComponentState.ERROR

            # Propagate to components
            self._propagate_state(ComponentState.ERROR, message)

            # Handle auto-clear with threading.Timer
            clear_duration = self._get_clear_duration(ComponentState.ERROR, duration)
            if clear_duration is not None:
                if self._clear_timer:
                    self._clear_timer.cancel()
                self._clear_timer = threading.Timer(clear_duration, self.clear)
                self._clear_timer.daemon = True
                self._clear_timer.start()

    def reset(self) -> None:
        """Return to in_progress state.

        Thread-safe. Cancels any pending auto-clear timer, resets all
        child components, and restores visibility.
        """
        with self._lock:
            # Cancel any pending auto-clear timer
            if self._clear_timer:
                self._clear_timer.cancel()
                self._clear_timer = None

            self._state = ComponentState.IN_PROGRESS
            self._fade_progress = None

            for name in self._render_order:
                component = self._components[name]
                if hasattr(component, "reset"):
                    component.reset()
                component.visible = self._component_visibility_defaults.get(name, True)

    def clear(self) -> None:
        """Stop and clear display.

        Thread-safe. Hides all components and cancels pending timers.
        """
        with self._lock:
            # Cancel any pending auto-clear
            if self._clear_timer:
                self._clear_timer.cancel()
                self._clear_timer = None

            # Clear all components
            for name in self._render_order:
                component = self._components[name]
                component.visible = False

    def stop(self) -> None:
        """Alias for clear() to match Rich's Status API."""
        self.clear()

    def _propagate_state(self, state: ComponentState, message: str | None = None) -> None:
        """Propagate state changes to all components.

        Thread-safe propagation with proper locking.
        Must be called with lock held.
        """

        def invoke_state_method(
            component: Any, method_name: str, terminal_text: str | None
        ) -> None:
            """Invoke a terminal-state method, preserving component defaults."""
            if not hasattr(component, method_name):
                return

            method = getattr(component, method_name)
            if terminal_text is None:
                method()
                return

            try:
                method(terminal_text)
            except TypeError:
                method()

        state_name = state.name.lower()
        state_settings = self._get_state_settings(state)
        behavior = state_settings.get("behavior", "indicator")

        # Check for fade-away
        fade_config = self.config.get("fade_away", {})
        if fade_config.get("enabled", False) and state in (
            ComponentState.SUCCESS,
            ComponentState.ERROR,
        ):
            self._start_fade_away()

        for name in self._render_order:
            component = self._components[name]
            component_config = self._resolve_config(name, state)
            state_component_overrides = self._get_state_component_overrides(name, state)
            terminal_text = self._resolve_terminal_text(
                state_component_overrides, state_settings, message
            )
            self._apply_terminal_overrides(
                name,
                component,
                state,
                component_config,
                state_component_overrides,
                terminal_text,
            )

            # Apply state-specific configuration
            if behavior == "disappear":
                component.visible = False
            else:
                invoke_state_method(component, state_name, terminal_text)

    def _get_clear_duration(self, state: ComponentState, override: float | None) -> float | None:
        """Resolve auto-clear duration with state config precedence."""
        if override is not None:
            return override

        state_settings = self._get_state_settings(state)
        configured_duration = state_settings.get("duration")
        if configured_duration is not None:
            return configured_duration

        state_name = state.name.lower()
        if state == ComponentState.SUCCESS and self.success_duration is not None:
            return self.success_duration
        if state == ComponentState.ERROR and self.error_duration is not None:
            return self.error_duration

        return self.config.get("durations", {}).get(state_name)

    def _resolve_terminal_text(
        self,
        state_component_overrides: dict[str, Any],
        state_settings: dict[str, Any],
        message: str | None,
    ) -> str | None:
        """Resolve terminal text with explicit method message precedence."""
        if message is not None:
            return message
        if "text" in state_component_overrides:
            return state_component_overrides["text"]
        state_message = state_settings.get("message")
        return state_message if isinstance(state_message, str) else None

    def _apply_terminal_overrides(
        self,
        name: str,
        component: Any,
        state: ComponentState,
        component_config: dict[str, Any],
        state_component_overrides: dict[str, Any],
        terminal_text: str | None,
    ) -> None:
        """Apply state-specific icon/text/color overrides to a component."""
        color = state_component_overrides.get("color", component_config.get("color"))
        icon = None
        if name == "spinner":
            icon_key = "success_icon" if state == ComponentState.SUCCESS else "error_icon"
            icon = state_component_overrides.get("icon", state_component_overrides.get(icon_key))

        if hasattr(component, "configure_state"):
            kwargs: dict[str, Any] = {}
            if color is not None:
                kwargs["color"] = color
            if terminal_text is not None and name in {"progress", "timer"}:
                kwargs["text"] = terminal_text
            if icon is not None:
                kwargs["icon"] = icon
            if kwargs:
                component.configure_state(state, **kwargs)
            return

        if color is not None and hasattr(component, "color"):
            component.color = color

    # Fade-Away Animation

    def _start_fade_away(self) -> None:
        """Initialize fade-away animation."""
        self._fade_start_time = time.time()
        self._fade_progress = 0

    def _apply_fade_away(self, components: list[Any]) -> list[Any]:
        """Apply fade-away animation to components."""
        if not self._fade_start_time:
            return components

        fade_config = self.config.get("fade_away", {})
        if not fade_config.get("enabled", False):
            return components

        direction = fade_config.get("direction", "left-to-right")
        interval = fade_config.get("interval", 0.05)

        elapsed = time.time() - self._fade_start_time
        faded_count = int(elapsed / interval)

        if direction == "left-to-right":
            return components[faded_count:] if faded_count < len(components) else []
        else:  # right-to-left
            if faded_count == 0:
                return components
            return components[:-faded_count] if faded_count < len(components) else []

    # Component Control Methods (Hybrid Approach)

    def update_progress(self, *, current: int, total: int | None = None) -> None:
        """Update progress component.

        Thread-safe. Silently ignored if progress component is not found.

        Args:
            current: New progress value.
            total: Optional new total value.
        """
        with self._lock:
            try:
                progress = self.get_component("progress")
                if total is not None:
                    progress.total = total
                progress.set(current)
            except KeyError:
                pass  # Component not found, silently ignore

    def set_message(self, *, text: str) -> None:
        """Update message component text.

        Thread-safe. Silently ignored if message component is not found.

        Args:
            text: New message text to display.
        """
        with self._lock:
            try:
                message = self.get_component("message")
                if hasattr(message, "configure"):
                    message.configure(text=text)
            except KeyError:
                pass

    def set_spinner_style(self, *, style: str) -> None:
        """Change spinner animation style at runtime.

        Thread-safe. Mutates the spinner in place rather than recreating it.

        Args:
            style: Name of a built-in spinner style from SPINNER_FRAMES.
        """
        from thothspinner.rich.spinners.frames import SPINNER_FRAMES

        with self._lock:
            spinner = self._components.get("spinner")
            if spinner is None:
                return
            if style in SPINNER_FRAMES:
                spinner_def = SPINNER_FRAMES[style]
                spinner.frames = spinner_def["frames"]
                spinner.interval = spinner_def["interval"]
                spinner._start_time = None  # Reset animation

    def set_hint(self, *, text: str) -> None:
        """Update hint text.

        Thread-safe. Silently ignored if hint component is not found.

        Args:
            text: New hint text to display.
        """
        with self._lock:
            try:
                hint = self.get_component("hint")
                hint.text = text
            except KeyError:
                pass

    def update_component(self, component_type: str, **kwargs) -> None:
        """Generic update method for flexibility.

        Args:
            component_type: Type of component to update
            **kwargs: Attributes to update

        Raises:
            KeyError: If component_type is invalid
        """
        with self._lock:
            component = self.get_component(component_type)  # Will raise KeyError if invalid
            if hasattr(component, "configure"):
                component.configure(**kwargs)
            else:
                # Set attributes directly if no update method
                for key, value in kwargs.items():
                    if hasattr(component, key):
                        setattr(component, key, value)

    def set_shimmer_direction(self, *, direction: str) -> None:
        """Control message shimmer animation direction.

        Thread-safe. Silently ignored if message component is not found.

        Args:
            direction: Either "left-to-right" or "right-to-left".
        """
        with self._lock:
            try:
                message = self.get_component("message")
                if hasattr(message, "reverse_shimmer"):
                    message.reverse_shimmer = direction == "right-to-left"
            except KeyError:
                pass

    @classmethod
    def from_dict(cls, config: dict[str, Any], **kwargs) -> ThothSpinner:
        """Create ThothSpinner from configuration dict.

        Args:
            config: Configuration dictionary
            **kwargs: Additional keyword arguments override config

        Returns:
            ThothSpinner instance
        """
        # Merge kwargs into config
        merged_config = config.copy()
        merged_config.update(kwargs)
        return cls(**merged_config)
