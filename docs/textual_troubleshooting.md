# ThothSpinner Textual Widgets Troubleshooting Guide

This guide helps resolve common issues when using ThothSpinner Textual widgets.

## Table of Contents

1. [Widget Not Rendering](#widget-not-rendering)
2. [Animation Issues](#animation-issues)
3. [State Management Issues](#state-management-issues)
4. [CSS Styling Issues](#css-styling-issues)
5. [Lifecycle Issues](#lifecycle-issues)
6. [Common Error Messages](#common-error-messages)
7. [Debug Utilities](#debug-utilities)
8. [Getting Help](#getting-help)

## Widget Not Rendering

### Problem: Forgot to yield in compose()

**Symptom:**
App runs but the spinner widget never appears on screen.

**Solution:**
```python
from textual.app import App, ComposeResult
from thothspinner.textual.widgets import ThothSpinnerWidget

# ❌ Wrong: returning instead of yielding
class MyApp(App):
    def compose(self) -> ComposeResult:
        spinner = ThothSpinnerWidget()
        # Widget is created but never yielded — nothing renders

# ✅ Correct: yield the widget
class MyApp(App):
    def compose(self) -> ComposeResult:
        yield ThothSpinnerWidget()
```

### Problem: Widget not mounted or display=False

**Symptom:**
Widget was yielded but still invisible.

**Diagnosis checklist:**
- [ ] Did you pass `visible=False` at construction?
- [ ] Did you call `widget.hide()` or set `widget.display = False`?
- [ ] Is a parent container also hidden?

**Solution:**
```python
# ❌ Wrong: creating with visible=False and forgetting to show later
spinner = ThothSpinnerWidget(visible=False)

# ✅ Correct: toggle visibility when ready
spinner = ThothSpinnerWidget(visible=False)
# ... later, when you want it shown:
spinner.show()        # or
spinner.display = True
```

## Animation Issues

### Problem: Spinner not animating

**Symptom:**
Spinner appears but stays frozen on a single frame.

**Diagnosis checklist:**
- [ ] Is the widget actually mounted? (timers require mounting)
- [ ] Has `on_mount` been called? (check with devtools)
- [ ] Is the state still `IN_PROGRESS`?

**Solution:**
```python
from thothspinner.textual.widgets import SpinnerWidget

# ❌ Wrong: trying to set_interval before mount
class MyApp(App):
    def __init__(self):
        super().__init__()
        self.spinner = SpinnerWidget()
        # Timer cannot start here — widget is not yet mounted

# ✅ Correct: SpinnerWidget handles this internally via on_mount
class MyApp(App):
    def compose(self) -> ComposeResult:
        yield SpinnerWidget()  # Timer starts automatically in on_mount
```

### Problem: Timer display not updating

**Symptom:**
TimerWidget shows `0s` and never changes.

**Solution:**
```python
from thothspinner.textual.widgets import TimerWidget

# ❌ Wrong: forgetting to call start()
class MyApp(App):
    def compose(self) -> ComposeResult:
        yield TimerWidget()  # Mounted but not started

# ✅ Correct: start the timer after mount
class MyApp(App):
    def compose(self) -> ComposeResult:
        yield TimerWidget(id="timer")

    def on_mount(self) -> None:
        self.query_one("#timer", TimerWidget).start()
```

### Problem: Shimmer not visible on message

**Symptom:**
MessageWidget text appears but without the shimmer highlight effect.

**Diagnosis checklist:**
- [ ] Is shimmer explicitly disabled? (`shimmer={"enabled": False}`)
- [ ] Is `shimmer_width` set to 0?
- [ ] Is the shimmer color the same as the base color?

**Solution:**
```python
# ❌ Wrong: shimmer disabled or width zero
message = MessageWidget(shimmer={"enabled": False})
message = MessageWidget(shimmer={"width": 0})

# ✅ Correct: enable shimmer with visible width
message = MessageWidget(
    shimmer={
        "enabled": True,
        "width": 3,
        "light_color": "#FFA500",
        "speed": 1.0,
    }
)
```

## State Management Issues

### Problem: Invalid state transition (ValueError)

**Symptom:**
```python
ValueError: Invalid state transition from SUCCESS to ERROR
```

**Solution:**
```python
# ❌ Wrong: transitioning directly between terminal states
spinner.success()
spinner.error()   # Raises ValueError — SUCCESS -> ERROR is invalid

# ✅ Correct: reset to IN_PROGRESS first
spinner.success()
spinner.reset()   # SUCCESS -> IN_PROGRESS (always valid)
spinner.error()   # IN_PROGRESS -> ERROR (valid)
```

Valid transitions:
- `IN_PROGRESS` -> `SUCCESS` | `ERROR` (forward)
- `SUCCESS` | `ERROR` -> `IN_PROGRESS` (reset only)
- `SUCCESS` -> `ERROR` or `ERROR` -> `SUCCESS` (blocked)

### Problem: State not propagating in orchestrator

**Symptom:**
Called `ThothSpinnerWidget.success()` but child widgets (timer, message) did not update.

**Solution:**
```python
# ❌ Wrong: mutating child state directly and expecting orchestrator to follow
widget.spinner.success()  # Only updates SpinnerWidget, not siblings

# ✅ Correct: use the orchestrator's state methods
widget.success(message="All done!")  # Propagates to ALL 5 children
widget.error(message="Something broke")
widget.reset()
```

### Problem: Reactive property not triggering refresh

**Symptom:**
Changed a reactive property but the widget did not visually update.

**Diagnosis checklist:**
- [ ] Is there a `watch_<name>` method calling `self.refresh()`?
- [ ] Are you setting the property on the correct widget instance?
- [ ] Is the widget mounted?

**Solution:**
```python
# ❌ Wrong: setting a private attribute directly
spinner._frame_index = 5  # This IS reactive — but bypassing validation

# ✅ Correct: use the public API or set reactive properties properly
spinner.color = "#FF0000"  # Triggers validate_color -> watch_color -> refresh
```

## CSS Styling Issues

### Problem: DEFAULT_CSS not applying

**Symptom:**
Widget ignores its declared `DEFAULT_CSS` styles.

**Diagnosis checklist:**
- [ ] Is `DEFAULT_CSS` a `ClassVar[str]`?
- [ ] Is an external CSS file overriding the defaults?
- [ ] Does the selector match the widget class name exactly?

**Solution:**
```python
# ❌ Wrong: selector doesn't match class name
class MySpinner(Static):
    DEFAULT_CSS = """
    Spinner {           /* Should be MySpinner, not Spinner */
        height: 1;
    }
    """

# ✅ Correct: selector matches class name
class MySpinner(Static):
    DEFAULT_CSS: ClassVar[str] = """
    MySpinner {
        height: 1;
        width: auto;
    }
    """
```

### Problem: Color not changing

**Symptom:**
Set `spinner.color = "red"` but nothing happens (or raises an error).

**Solution:**
```python
# ❌ Wrong: using a named color string
spinner.color = "red"  # Fails validation — expects #RRGGBB

# ✅ Correct: use hex color format
spinner.color = "#FF0000"  # validate_color accepts #RRGGBB
```

The `validate_color` reactive validator calls `validate_hex_color()`, which requires the `#RRGGBB` format.

### Problem: State CSS classes not appearing

**Symptom:**
Called `spinner.success()` but the `.success` CSS class was not added.

**Solution:**
```python
# The watch__state watcher adds/removes CSS classes automatically.
# If classes are missing, verify the state actually changed:

print(spinner.state)          # Should be ComponentState.SUCCESS
print(spinner.classes)        # Should contain "success"

# Ensure your CSS targets the class:
# SpinnerWidget.success { color: $success; }
# SpinnerWidget.error   { color: $error; }
```

## Lifecycle Issues

### Problem: on_mount vs __init__ timing

**Symptom:**
```python
# RuntimeError or silent failure when creating timers in __init__
```

**Solution:**
```python
# ❌ Wrong: calling set_interval in __init__
class MyWidget(Static):
    def __init__(self):
        super().__init__()
        self.set_interval(0.1, self.tick)  # Widget not mounted yet!

# ✅ Correct: create timers in on_mount
class MyWidget(Static):
    def __init__(self):
        super().__init__()
        self._timer = None  # Placeholder only

    def on_mount(self) -> None:
        self._timer = self.set_interval(0.1, self.tick)
```

All ThothSpinner widgets (SpinnerWidget, MessageWidget, TimerWidget) follow this pattern: timers are created in `on_mount`, not `__init__`.

### Problem: Timer leaks on widget removal

**Symptom:**
After removing a widget, background timers continue to fire, causing errors or high CPU usage.

**Solution:**
```python
# ❌ Wrong: removing widget without cleanup
await spinner.remove()  # Timer may still be scheduled

# ✅ Correct: ThothSpinner widgets clean up in on_unmount automatically
# SpinnerWidget.on_unmount:
#   self._timer.stop()
#   self._timer = None
#
# If writing a custom widget, follow the same pattern:
class MyWidget(Static):
    def on_mount(self) -> None:
        self._timer = self.set_interval(0.1, self.tick)

    def on_unmount(self) -> None:
        if self._timer is not None:
            self._timer.stop()
            self._timer = None
```

### Problem: Widget removal and re-mounting

**Symptom:**
Re-mounting a previously removed widget causes animation to break.

**Solution:**
```python
# ❌ Wrong: reusing a removed widget instance
old_spinner = self.query_one(SpinnerWidget)
await old_spinner.remove()
await self.mount(old_spinner)  # Internal state may be stale

# ✅ Correct: create a fresh widget instance
await self.query_one(SpinnerWidget).remove()
await self.mount(SpinnerWidget(style="npm_dots"))
```

## Common Error Messages

### "Widget is not mounted"

**Cause:** Attempting timer or DOM operations before the widget is in the tree.

**Fix:** Move timer creation to `on_mount()` and guard calls with `self.is_mounted`:
```python
if self.is_mounted:
    self._timer = self.set_interval(0.1, self._tick)
```

### "Invalid state transition from X to Y"

**Cause:** Attempting a forbidden transition (e.g., SUCCESS -> ERROR).

**Fix:** Call `reset()` to return to `IN_PROGRESS` before transitioning to a new terminal state:
```python
widget.reset()
widget.error("New error")
```

### "Speed must be positive"

**Cause:** Passing zero or negative value to `SpinnerWidget.set_speed()`.

**Fix:**
```python
# ❌ Wrong
spinner.set_speed(0)    # Raises ValueError
spinner.set_speed(-1)   # Raises ValueError

# ✅ Correct
spinner.set_speed(0.5)  # Half speed
spinner.set_speed(2.0)  # Double speed
```

### "Word list cannot be empty"

**Cause:** Setting `MessageWidget.action_words` to an empty list.

**Fix:**
```python
# ❌ Wrong
message.action_words = []  # Raises ValueError

# ✅ Correct
message.action_words = ["Loading", "Processing"]
```

### "Invalid component type"

**Cause:** Using an unrecognized component name in config or `get_component()`.

**Fix:**
```python
# Valid component types:
#   "spinner", "message", "progress", "timer", "hint"

# ❌ Wrong
widget.get_component("loading")  # KeyError

# ✅ Correct
widget.get_component("spinner")
```

## Debug Utilities

### Using Textual devtools

Run your app with the Textual developer console for live widget inspection:
```bash
# Terminal 1: start the dev console
textual console

# Terminal 2: run your app with --dev flag
textual run --dev my_app.py
```

The devtools show the widget tree, CSS, events, and log output in real time.

### Console logging patterns

Use Textual's built-in logging to debug widget state:
```python
from textual import log

class MyApp(App):
    def on_mount(self) -> None:
        spinner = self.query_one(SpinnerWidget)
        log(f"Spinner state: {spinner.state}")
        log(f"Spinner mounted: {spinner.is_mounted}")
        log(f"Spinner display: {spinner.display}")
        log(f"Timer active: {spinner._timer is not None}")
```

These messages appear in the Textual dev console (not stdout).

### Widget tree inspection

Inspect the live DOM tree from within the app:
```python
class MyApp(App):
    def key_d(self) -> None:
        """Press 'd' to dump widget tree."""
        tree = self.tree  # The widget tree
        log(tree)

        # Query specific widgets
        spinners = self.query(SpinnerWidget)
        log(f"Found {len(spinners)} spinner widgets")

        # Inspect classes and state
        for widget in spinners:
            log(f"  classes={widget.classes}, state={widget.state}")
```

## Getting Help

If you encounter issues not covered here:

1. **Check the examples**: Review the [examples directory](./examples/README.md)
2. **Read API docs**: See the [Textual widget API reference](./thothspinner_textual.md)
3. **Run devtools**: Use `textual run --dev` to inspect widget state live
4. **Enable logging**:
   ```python
   from textual import log
   log("debug info here")  # Visible in textual console
   ```
5. **Report issues**: [GitHub Issues](https://github.com/yourusername/thothspinner/issues)
6. **Minimal reproduction**: Create a small `App` subclass that reproduces the issue
