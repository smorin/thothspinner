# Reactive State Management Guide for ThothSpinner Textual Widgets

## 1. Overview

Textual's `reactive` descriptor lets you declare class-level attributes that
automatically trigger callbacks when their values change. ThothSpinner's Textual
widgets use reactive properties for every piece of data that should cause a
visual update -- colors, text content, animation frame indices, and lifecycle
state.

A reactive property is declared at class level:

```python
from textual.reactive import reactive

class MyWidget(Static):
    color = reactive("#D97706")
```

When you write `self.color = "#00FF00"`, Textual intercepts the assignment and:

1. Calls `validate_color(value)` if defined -- to sanitize or reject the value.
2. Stores the new value.
3. Calls `watch_color(...)` if defined -- to run side effects such as `self.refresh()`.

ThothSpinner relies on all three hooks across its widget family.

---

## 2. Reactive Properties in ThothSpinner

Each widget lives in `src/thothspinner/textual/widgets/` and declares its own
set of reactive properties. Properties prefixed with `_` are private
(internal animation/state tracking).

| Widget | Property | Type | Default | Purpose |
|---|---|---|---|---|
| **HintWidget** | `text` | `str` | `""` | Display text |
| | `color` | `str` | `"#888888"` | Hex color for rendering |
| | `icon` | `str` | `""` | Optional prefix icon/emoji |
| | `_state` | `ComponentState` | `IN_PROGRESS` | Lifecycle state |
| **SpinnerWidget** | `color` | `str` | `"#D97706"` | Hex color for frames |
| | `_frame_index` | `int` | `0` | Current animation frame |
| | `_state` | `ComponentState` | `IN_PROGRESS` | Lifecycle state |
| **ProgressWidget** | `current` | `int` | `0` | Current progress value |
| | `total` | `int` | `100` | Total/target value |
| | `color` | `str` | `"#D97706"` | Hex color for rendering |
| | `_state` | `ComponentState` | `IN_PROGRESS` | Lifecycle state |
| **TimerWidget** | `color` | `str` | `"#FFFF55"` | Hex color for rendering |
| | `_state` | `ComponentState` | `IN_PROGRESS` | Lifecycle state |
| **MessageWidget** | `color` | `str` | `"#D97706"` | Base text color |
| | `_state` | `ComponentState` | `IN_PROGRESS` | Lifecycle state |

Every widget shares `color` and `_state`. Additional properties are
widget-specific (e.g. `_frame_index` only makes sense for animations).

---

## 3. Watchers

### The `watch_<property>` pattern

Textual automatically calls a method named `watch_<property>` whenever the
corresponding reactive value changes. ThothSpinner widgets use watchers to
schedule a repaint:

```python
# From src/thothspinner/textual/widgets/hint.py
class HintWidget(Static):
    text = reactive("")

    def watch_text(self) -> None:
        """React to text changes."""
        self.refresh()

    def watch_color(self) -> None:
        """React to color changes."""
        self.refresh()

    def watch_icon(self) -> None:
        """React to icon changes."""
        self.refresh()
```

Calling `self.refresh()` tells Textual to re-invoke `render()` on the next
paint cycle. This is the standard Textual pattern -- change a reactive, the
watcher calls `refresh()`, and `render()` reads the new value.

For private reactives, the watcher name uses the full attribute name including
the underscore prefix:

```python
def watch__frame_index(self) -> None:
    """React to frame index changes."""
    self.refresh()
```

### The `validate_<property>` pattern

Textual calls `validate_<property>(value)` before storing a new value. Every
widget that has a `color` reactive uses this hook to enforce valid hex colors:

```python
# From src/thothspinner/textual/widgets/spinner.py
from ...core.color import validate_hex_color

class SpinnerWidget(Static):
    color = reactive("#D97706")

    def validate_color(self, color: str) -> str:
        """Validate color before setting."""
        return validate_hex_color(color)
```

`validate_hex_color()` normalizes the input and raises `ValueError` for
malformed colors. The validator returns the cleaned value, which Textual
stores as the actual property value.

---

## 4. State Machine Pattern

All widgets share a common lifecycle governed by `ComponentState`, defined in
`src/thothspinner/core/states.py`.

### The `ComponentState` enum

```python
from enum import Enum, auto

class ComponentState(Enum):
    IN_PROGRESS = auto()  # Active/animating state
    SUCCESS     = auto()  # Successful completion (terminal)
    ERROR       = auto()  # Error/failure state (terminal)

    def can_transition_to(self, new_state: ComponentState) -> bool:
        if new_state == ComponentState.IN_PROGRESS:
            return True  # can always reset
        if self == ComponentState.IN_PROGRESS:
            return new_state in (ComponentState.SUCCESS, ComponentState.ERROR)
        return False  # cannot go SUCCESS -> ERROR or ERROR -> SUCCESS
```

### Transition diagram

```
              +-----------+
     reset    |           |   success()
  +---------->|IN_PROGRESS|-------------> SUCCESS
  |           |           |
  |           +-----+-----+
  |                 |
  |    reset        | error()
  +<--- SUCCESS     |
  +<--- ERROR       v
                  ERROR
```

Key rules:
- `IN_PROGRESS` can transition to `SUCCESS` or `ERROR`.
- `SUCCESS` and `ERROR` are terminal -- you cannot go directly between them.
- Any state can transition back to `IN_PROGRESS` (via `reset()`).

### How widgets enforce transitions

Every widget guards its `success()` and `error()` methods:

```python
# From src/thothspinner/textual/widgets/progress.py
def success(self, text: str | None = None) -> None:
    if not self._state.can_transition_to(ComponentState.SUCCESS):
        return  # silently reject invalid transition
    if text is not None:
        self._success_text = text
    self._state = ComponentState.SUCCESS
```

Invalid transitions are silently ignored at the child widget level. The
orchestrator (`ThothSpinnerWidget`) raises `ValueError` instead:

```python
# From src/thothspinner/textual/widgets/thothspinner.py
def _validate_transition(self, new_state: ComponentState) -> None:
    if not self._state.can_transition_to(new_state):
        raise ValueError(
            f"Invalid state transition from {self._state.name} to {new_state.name}"
        )
```

---

## 5. CSS Classes and State

### How `watch__state` manages CSS classes

Every widget's `watch__state` method adds and removes CSS classes to reflect
the current lifecycle state:

```python
# Pattern shared by all widgets
def watch__state(self, new_state: ComponentState) -> None:
    if new_state == ComponentState.IN_PROGRESS:
        self.remove_class("success", "error")
    elif new_state == ComponentState.SUCCESS:
        self.remove_class("error")
        self.add_class("success")
    elif new_state == ComponentState.ERROR:
        self.remove_class("success")
        self.add_class("error")
    self.refresh()
```

Some widgets do extra work in this watcher. `SpinnerWidget` stops its animation
timer on terminal states and restarts it on `IN_PROGRESS`. `TimerWidget` stops
the display refresh timer. `MessageWidget` stops its animation timer.

### Styling with Textual CSS

Each widget ships with `DEFAULT_CSS` that maps these classes to Textual design
tokens:

```css
SpinnerWidget.success {
    color: $success;
}

SpinnerWidget.error {
    color: $error;
}
```

You can override these in your app's CSS:

```css
SpinnerWidget.success {
    color: #22C55E;
    text-style: bold;
}

SpinnerWidget.error {
    color: #EF4444;
    text-style: bold italic;
}
```

The class names (`.success`, `.error`) are stable and form part of the public
API.

---

## 6. Composing Reactive Widgets

### ThothSpinnerWidget: the orchestrator

`ThothSpinnerWidget` (in `src/thothspinner/textual/widgets/thothspinner.py`)
composes all five child widgets into a single coordinated unit. It has its own
`_state` reactive but does **not** use Textual's `data_bind()` to synchronize
state with children.

### Why not `data_bind()`?

`data_bind()` maps one reactive property to another reactive property with the
same name. But each child widget needs *different behavior* on state change:

- **SpinnerWidget** stops its timer and shows a static icon.
- **TimerWidget** freezes the elapsed time display.
- **MessageWidget** stops word rotation and shows final text.
- **HintWidget** hides itself entirely.
- **ProgressWidget** shows success/error text.

A single reactive binding cannot express these varied side effects. Instead,
the orchestrator uses **imperative propagation**.

### Imperative propagation

```python
# From src/thothspinner/textual/widgets/thothspinner.py
def _propagate_state(self, state: ComponentState, message: str | None = None) -> None:
    state_method = state.name.lower()  # "success" or "error"
    for name in self._render_order:
        component = self._components.get(name)
        if component is None:
            continue
        method = getattr(component, state_method, None)
        if method is not None:
            method(message)
```

When you call `thoth_spinner.success("Done!")`, the orchestrator:

1. Validates the transition with `can_transition_to()`.
2. Sets its own `_state = ComponentState.SUCCESS`.
3. Calls `_propagate_state(SUCCESS, "Done!")`, which calls `.success("Done!")`
   on each child in render order.
4. Each child's `.success()` sets its own `_state`, triggering its own
   `watch__state` watcher.

The `reset()` path works similarly, calling `.reset()` on each child and
restoring visibility:

```python
def reset(self) -> None:
    self._cancel_clear_timer()
    self._state = ComponentState.IN_PROGRESS
    for name in self._render_order:
        component = self._components.get(name)
        if component is not None and hasattr(component, "reset"):
            component.reset()
        if component is not None:
            component.display = True
```

### `start()` propagation

`start()` on the orchestrator explicitly starts animated children. When the
orchestrator is in `SUCCESS` or `ERROR`, it first resets all children back to
`IN_PROGRESS` so stale terminal output is cleared before the spinner and timer
restart:

```python
def start(self) -> None:
    if self._state in (ComponentState.SUCCESS, ComponentState.ERROR):
        self._reset_to_in_progress()
    else:
        self._state = ComponentState.IN_PROGRESS
        self._cancel_clear_timer()
    spinner = self._components["spinner"]
    if hasattr(spinner, "start"):
        spinner.start()
    timer = self._components["timer"]
    if hasattr(timer, "start"):
        timer.start()
```

---

## 7. Custom Extensions

### Subclassing a widget

You can subclass any ThothSpinner widget and add your own reactive properties:

```python
from textual.reactive import reactive
from thothspinner.textual.widgets import HintWidget


class StatusHint(HintWidget):
    """A hint widget that also tracks a severity level."""

    severity = reactive("info")

    def validate_severity(self, value: str) -> str:
        allowed = ("info", "warning", "error")
        if value not in allowed:
            raise ValueError(f"severity must be one of {allowed}, got {value!r}")
        return value

    def watch_severity(self, new_severity: str) -> None:
        self.remove_class("info", "warning", "error")
        self.add_class(new_severity)
        self.refresh()
```

### Adding a reactive to an existing widget dynamically

Reactive properties must be declared at class level due to how Textual's
descriptor protocol works. You cannot add them to an instance at runtime.
Always use subclassing.

---

## 8. Common Pitfalls

### Setting a reactive before mount

Textual's reactive watchers depend on the widget being part of a live DOM tree.
Setting a reactive in `__init__` is fine -- Textual defers the watcher call.
However, calling methods that depend on `self.is_mounted` (like starting a
timer) will silently do nothing before mount:

```python
# This is safe -- Textual stores the value for later
def __init__(self):
    super().__init__()
    self.color = "#FF0000"  # watcher deferred until mount

# This is NOT safe -- timer won't start
def __init__(self):
    super().__init__()
    self.start()  # self.is_mounted is False, timer creation skipped
```

Use `on_mount()` for any work that requires the widget to be in the DOM:

```python
def on_mount(self) -> None:
    self._timer = self.set_interval(0.08, self._advance_frame)
```

### Thread safety and Textual's message loop

Textual is single-threaded. All reactive mutations and watcher callbacks run on
the main async event loop. If you need to update a widget from a background
thread (e.g. an `asyncio.to_thread` task), use `app.call_from_thread`:

```python
import asyncio
from textual.app import App

class MyApp(App):
    async def do_work(self) -> None:
        result = await asyncio.to_thread(slow_function)
        # Back on the event loop -- safe to touch reactives
        self.query_one(SpinnerWidget).success()
```

If you call `widget.color = "..."` from a non-Textual thread without
`call_from_thread`, the watcher may fire outside the event loop, causing
rendering corruption or crashes.

### Forgetting `self.refresh()` in a watcher

If you add a custom reactive and define a watcher but forget to call
`self.refresh()`, the widget will not repaint. Textual does not auto-refresh on
reactive changes -- the watcher must explicitly request it.

### Terminal states block further transitions

Once a widget is in `SUCCESS` or `ERROR`, calling `success()` or `error()`
again is silently ignored. You must call `reset()` first to return to
`IN_PROGRESS` before transitioning again:

```python
spinner.success()       # IN_PROGRESS -> SUCCESS
spinner.error()         # ignored (SUCCESS -> ERROR not allowed)
spinner.reset()         # SUCCESS -> IN_PROGRESS
spinner.error()         # IN_PROGRESS -> ERROR (works)
```

---

## Source Reference

- **Widget implementations**: `src/thothspinner/textual/widgets/`
  - `hint.py` -- HintWidget
  - `spinner.py` -- SpinnerWidget
  - `progress.py` -- ProgressWidget
  - `timer.py` -- TimerWidget
  - `message.py` -- MessageWidget
  - `thothspinner.py` -- ThothSpinnerWidget (orchestrator)
- **State machine**: `src/thothspinner/core/states.py` -- `ComponentState` enum with `can_transition_to()` method
