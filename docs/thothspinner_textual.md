# ThothSpinner Textual Widgets API Reference

## Overview

ThothSpinner provides Textual widgets for building interactive terminal applications with animated progress indicators. Each widget uses Textual's reactive system for automatic UI updates and supports CSS styling and state management.

### Key Features
- **Reactive Properties**: Automatic re-rendering when values change
- **CSS Styling**: Customizable via Textual CSS with state-based classes
- **State Management**: Built-in IN_PROGRESS/SUCCESS/ERROR state machine
- **Compose Pattern**: Drop widgets into any Textual app via `compose()`
- **Lifecycle Aware**: Timers start/stop automatically on mount/unmount

## Installation

```bash
uv add thothspinner
```

Requires `textual>=0.40.0` (installed automatically as a dependency).

## Quick Start

```python
from textual.app import App, ComposeResult
from thothspinner.textual import TextualThothSpinner

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield TextualThothSpinner(
            spinner_style="npm_dots",
            message_text="Processing",
            hint_text="(esc to cancel)",
        )

    def on_mount(self) -> None:
        spinner = self.query_one(TextualThothSpinner)
        spinner.start()
        self.do_work(spinner)

    async def do_work(self, spinner):
        for i in range(100):
            spinner.update_progress(current=i, total=100)
            await asyncio.sleep(0.05)
        spinner.success("Done!")

if __name__ == "__main__":
    MyApp().run()
```

## Shared Patterns

All ThothSpinner widgets share these patterns:

### Reactive Properties

Changing a reactive property automatically triggers `refresh()`:

```python
widget.color = "#FF0000"  # Automatically re-renders
widget.text = "New text"  # Automatically re-renders
```

### CSS Classes

State transitions add/remove CSS classes:

| State | CSS Class | Applied By |
|-------|-----------|-----------|
| `SUCCESS` | `.success` | `watch__state()` |
| `ERROR` | `.error` | `watch__state()` |
| `IN_PROGRESS` | (none) | Removes `.success` and `.error` |

### Visibility

All widgets support `show()`, `hide()`, `toggle()`, and `set_visible(bool)`. These control the Textual `display` property.

### State System

All components use `ComponentState` from `thothspinner.core.states`:

| State | Description | Valid Transitions |
|-------|-------------|-------------------|
| `IN_PROGRESS` | Active/working | -> SUCCESS, ERROR |
| `SUCCESS` | Completed | -> IN_PROGRESS (via `reset()`) |
| `ERROR` | Failed | -> IN_PROGRESS (via `reset()`) |

### Factory Method

Every widget supports `from_config(config: dict)` for creation from configuration dictionaries.

---

## Components

### HintWidget

Static text widget for displaying helper messages, keyboard shortcuts, or status information.

#### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | `""` | Text to display |
| `color` | `str` | `"#888888"` | Hex color code (#RRGGBB) |
| `visible` | `bool` | `True` | Initial visibility |
| `icon` | `str` | `""` | Optional icon/emoji prefix |

All parameters after `text` are keyword-only.

#### Default CSS

```css
HintWidget {
    width: auto;
    height: 1;
    padding: 0;
    background: transparent;
}

HintWidget.success { color: $success; }
HintWidget.error   { color: $error; }
HintWidget.warning { color: $warning; }
```

#### Reactive Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `text` | `str` | `""` | Display text |
| `color` | `str` | `"#888888"` | Hex color (validated) |
| `icon` | `str` | `""` | Icon prefix |

#### Usage

```python
from thothspinner.textual.widgets import HintWidget

hint = HintWidget("Press ESC to cancel", color="#888888")
hint.set_icon("💡")
hint.text = "Updated hint"  # Reactive, triggers refresh
```

#### Methods

##### `set_icon(icon: str) -> None`
Set an icon/emoji prefix before the text.

##### `clear_icon() -> None`
Remove the icon prefix.

##### `configure(**kwargs) -> None`
Batch update properties (text, color, icon).

##### `fade_in(duration: float = 0.3) -> None`
Animate widget appearance using opacity.

##### `fade_out(duration: float = 0.3) -> None`
Animate widget disappearance, then hide.

##### `animate_color_change(new_color: str, duration: float = 0.5) -> None`
Animate color transition to a new hex color.

##### `success(text: str | None = None) -> None`
Transition to success state (hides widget).

##### `error(text: str | None = None) -> None`
Transition to error state (hides widget).

##### `reset() -> None`
Reset to in_progress state and show widget.

##### `from_config(config: dict) -> HintWidget` *(classmethod)*
Create a HintWidget from a configuration dictionary.

Also supports shared visibility methods: `show()`, `hide()`, `toggle()`, `set_visible(bool)` — see [Shared Patterns](#shared-patterns).

#### State Behaviors

| State | Behavior | Effect |
|-------|----------|--------|
| `IN_PROGRESS` | Shows helper text | Normal display |
| `SUCCESS` | Hides widget | `.success` CSS class |
| `ERROR` | Hides widget | `.error` CSS class |

---

### SpinnerWidget

Animated spinner that cycles through frames with configurable styles and speed.

#### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `style` | `str` | `"npm_dots"` | Built-in spinner style |
| `frames` | `list[str] \| None` | From style | Custom frame sequence |
| `interval` | `float \| None` | From style | Custom interval (seconds) |
| `color` | `str` | `"#D97706"` | Hex color code |
| `success_icon` | `str` | `"✓"` | Icon for success state |
| `error_icon` | `str` | `"✗"` | Icon for error state |
| `speed` | `float` | `1.0` | Animation speed multiplier |
| `visible` | `bool` | `True` | Initial visibility |

All parameters after `style` are keyword-only.

#### Built-in Styles

- `npm_dots`: Unicode braille pattern animation
- `claude_stars`: Animated star pattern
- `classic`: Classic rotating bar animation
- `dots`: Simple dot animation
- `dots2`, `dots3`: Dot animation variants
- `arrows`: Animated arrow sequence
- `circle`: Circle animation
- `square`: Square pattern animation
- `triangle`: Triangle rotation animation
- `bounce`: Bouncing dot animation
- `box_bounce`: Box bounce animation
- `star`: Star animation
- `arc`: Quarter-circle arc rotation
- `line`: Dashes cycling through thin to thick (`-` → `—` → `─` → `━`)
- `pulse`: Horizontal block that grows and shrinks (`▏` → `█` → `▏`)
- `vertical_pulse`: Vertical block that grows and shrinks (`▁` → `█` → `▁`)
- `pipe`: Box-drawing corners rotating (`┤┘┴└├┌┬┐`)
- `quarter`: Quarter-circle fill rotating (`◴◷◶◵`)
- `hamburger`: Three-bar menu morphing (`☱☲☴`)

**Emoji styles** (2-column-wide frames — work well standalone; may shift adjacent text in horizontal layouts):

- `moon`: Lunar phases (`🌑🌒🌓🌔🌕🌖🌗🌘`)
- `clock`: Clock face cycling through hours (`🕛🕐🕑…🕚`)
- `earth`: Globe rotating (`🌍🌎🌏`)
- `dice`: Rolling die faces (`⚀⚁⚂⚃⚄⚅`)
- `snowflake`: Crystal forming and dissolving (`·∗✦❄✦∗·`)
- `zodiac`: Cycling through the 12 zodiac signs (`♈♉♊…♓`)
- `rune`: Elder Futhark letters cycling (`ᚠᚢᚦᚨᚱᚲ…`)

#### Default CSS

```css
SpinnerWidget {
    width: auto;
    height: 1;
    padding: 0;
    background: transparent;
}

SpinnerWidget.success { color: $success; }
SpinnerWidget.error   { color: $error; }
```

#### Reactive Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `color` | `str` | `"#D97706"` | Hex color (validated) |

#### Read-only Properties

| Property | Type | Description |
|----------|------|-------------|
| `state` | `ComponentState` | Current state |
| `frames` | `list[str]` | Frame list (copy) |
| `interval` | `float` | Base animation interval |
| `speed` | `float` | Speed multiplier |
| `paused` | `bool` | Whether animation is paused |

#### Lifecycle

- `on_mount()`: Creates animation timer with `set_interval()`
- `on_unmount()`: Stops and clears the animation timer

#### Methods

##### `start() -> None`
Start or restart the spinner animation. Resets to frame 0 and IN_PROGRESS state.

##### `stop() -> None`
Stop animation without changing state. Freezes on current frame.

##### `pause() -> None`
Toggle pause/resume of the animation. Only works in IN_PROGRESS state.

##### `set_speed(speed: float) -> None`
Set the animation speed multiplier. Raises `ValueError` if speed <= 0.

##### `set_style(style: str) -> None`
Change the spinner animation style at runtime. Raises `KeyError` for unknown styles.

##### `success(message: str | None = None) -> None`
Transition to success state. Displays `success_icon`.

##### `error(message: str | None = None) -> None`
Transition to error state. Displays `error_icon`.

##### `reset() -> None`
Reset to in_progress state (alias for `start()`).

##### `from_config(config: dict) -> SpinnerWidget` *(classmethod)*
Create a SpinnerWidget from a configuration dictionary.

Also supports shared visibility methods: `show()`, `hide()`, `toggle()`, `set_visible(bool)` — see [Shared Patterns](#shared-patterns).

#### State Behaviors

| State | Behavior | Effect |
|-------|----------|--------|
| `IN_PROGRESS` | Animating through frames | Timer running |
| `SUCCESS` | Static success icon | Timer paused, `.success` CSS class |
| `ERROR` | Static error icon | Timer paused, `.error` CSS class |

---

### ProgressWidget

Displays progress as a counter with multiple text format options.

#### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `current` | `int` | `0` | Current progress value |
| `total` | `int` | `100` | Total value for completion |
| `format_style` | `FormatStyle` | `"fraction"` | Display format |
| `color` | `str` | `"#D97706"` | Hex color code |
| `zero_pad` | `bool` | `False` | Zero-pad current value |
| `success_text` | `str` | `"100%"` | Text for success state |
| `error_text` | `str` | `"Failed"` | Text for error state |
| `visible` | `bool` | `True` | Initial visibility |

Parameters after `total` are keyword-only.

#### Format Styles

| Style | Example | Description |
|-------|---------|-------------|
| `"fraction"` | `"42/100"` | Current/total |
| `"percentage"` | `"42%"` | Percentage |
| `"of_text"` | `"42 of 100"` | Verbose |
| `"count_only"` | `"42"` | Just the count |
| `"ratio"` | `"42:100"` | Colon-separated |

#### Default CSS

```css
ProgressWidget {
    width: auto;
    height: 1;
    padding: 0;
    background: transparent;
}

ProgressWidget.success { color: $success; }
ProgressWidget.error   { color: $error; }
```

#### Reactive Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `current` | `int` | `0` | Current progress value |
| `total` | `int` | `100` | Total value |
| `color` | `str` | `"#D97706"` | Hex color (validated) |

#### Methods

##### `increment() -> None`
Increment progress by 1 (capped at total).

##### `set(value: int) -> None`
Set progress to a specific value, clamped to [0, total].

##### `add(amount: int) -> None`
Add amount to current progress (can be negative).

##### `set_percentage(percent: float) -> None`
Set progress by percentage (0-100).

##### `is_complete() -> bool`
Returns `True` if current >= total.

##### `success(text: str | None = None) -> None`
Transition to success state. Optional custom text overrides `success_text`.

##### `error(text: str | None = None) -> None`
Transition to error state. Optional custom text overrides `error_text`.

##### `reset() -> None`
Reset to in_progress state and current to 0.

##### `from_config(config: dict) -> ProgressWidget` *(classmethod)*
Create a ProgressWidget from a configuration dictionary.

Also supports shared visibility methods: `show()`, `hide()`, `toggle()`, `set_visible(bool)` — see [Shared Patterns](#shared-patterns).

#### State Behaviors

| State | Behavior | Effect |
|-------|----------|--------|
| `IN_PROGRESS` | Shows formatted progress | Real-time updates via reactive `current` |
| `SUCCESS` | Shows success text | `.success` CSS class |
| `ERROR` | Shows error text | `.error` CSS class |

---

### TimerWidget

Displays elapsed time with start/stop/pause/resume controls and multiple format options.

#### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `format_style` | `TimerFormat` | `"auto"` | Time display format |
| `precision` | `int` | `1` | Decimal places for decimal formats |
| `color` | `str` | `"#FFFF55"` | Hex color code |
| `success_text` | `str \| None` | `None` | Optional text for success state |
| `error_text` | `str \| None` | `None` | Optional text for error state |
| `visible` | `bool` | `True` | Initial visibility |

All parameters after `format_style` are keyword-only.

#### Format Styles

| Style | Example | Description |
|-------|---------|-------------|
| `"seconds"` | `"5s"` | Whole seconds |
| `"seconds_decimal"` | `"5.0s"` | Seconds with precision |
| `"seconds_precise"` | `"5.123s"` | 3 decimal places |
| `"milliseconds"` | `"5000ms"` | Milliseconds |
| `"mm:ss"` | `"01:23"` | Minutes:seconds |
| `"hh:mm:ss"` | `"0:01:23"` | Hours:minutes:seconds |
| `"compact"` | `"1:23"` | Minimal format |
| `"full_ms"` | `"1:23.456"` | With milliseconds |
| `"auto"` | Varies | Auto-selects based on duration |
| `"auto_ms"` | Varies | Auto with ms for short durations |

#### Default CSS

```css
TimerWidget {
    width: auto;
    height: 1;
    padding: 0;
    background: transparent;
}

TimerWidget.success { color: $success; }
TimerWidget.error   { color: $error; }
```

#### Reactive Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `color` | `str` | `"#FFFF55"` | Hex color (validated) |

#### Read-only Properties

| Property | Type | Description |
|----------|------|-------------|
| `state` | `ComponentState` | Current state |
| `format_style` | `TimerFormat` | Current format |
| `precision` | `int` | Current precision |
| `running` | `bool` | Whether timer is active |
| `paused` | `bool` | Whether timer is paused |

#### Lifecycle

- `on_mount()`: Creates a 0.1s display refresh timer
- `on_unmount()`: Stops and clears the display timer

#### Methods

##### `start() -> None`
Start the timer. Records start time and begins display updates.

##### `stop() -> None`
Stop the timer. Accumulates elapsed time.

##### `resume() -> None`
Resume the timer after stopping.

##### `pause() -> None`
Toggle pause/resume. Preserves accumulated time. Only works in IN_PROGRESS state.

##### `reset() -> None`
Reset elapsed time to zero. Preserves running/paused state.

##### `get_elapsed() -> float`
Get total elapsed time in seconds (including current running period).

##### `is_running() -> bool`
Check if the timer is currently running.

##### `success(text: str | None = None) -> None`
Transition to success state. Stops the timer and freezes display.

##### `error(text: str | None = None) -> None`
Transition to error state. Stops the timer and freezes display.

##### `from_config(config: dict) -> TimerWidget` *(classmethod)*
Create a TimerWidget from a configuration dictionary.

Also supports shared visibility methods: `show()`, `hide()`, `toggle()`, `set_visible(bool)` — see [Shared Patterns](#shared-patterns).

#### State Behaviors

| State | Behavior | Effect |
|-------|----------|--------|
| `IN_PROGRESS` | Counting elapsed time | Display timer running |
| `SUCCESS` | Frozen at final time | Display timer stopped, `.success` CSS class |
| `ERROR` | Frozen at error time | Display timer stopped, `.error` CSS class |

---

### MessageWidget

Displays rotating action words with optional shimmer animation effects.

#### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `action_words` | `list[str] \| dict \| None` | 87 default words | Word list config |
| `interval` | `dict[str, float] \| None` | `{"min": 0.5, "max": 3.0}` | Rotation interval range |
| `color` | `str` | `"#D97706"` | Base hex color |
| `shimmer` | `dict[str, Any] \| None` | See below | Shimmer effect config |
| `suffix` | `str` | `"…"` | Suffix appended to words (Unicode ellipsis) |
| `success_text` | `str` | `"Complete!"` | Text for success state |
| `error_text` | `str` | `"Failed"` | Text for error state |
| `visible` | `bool` | `True` | Initial visibility |

All parameters after `action_words` are keyword-only.

#### Action Words Configuration

```python
# List: replaces defaults
MessageWidget(action_words=["Loading", "Processing", "Analyzing"])

# Dict with mode:
MessageWidget(action_words={"mode": "add", "words": ["Customizing"]})      # adds to defaults
MessageWidget(action_words={"mode": "replace", "words": ["Step 1", "Step 2"]})  # replaces
```

#### Shimmer Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled` | `bool` | `True` | Enable shimmer effect |
| `width` | `int` | `3` | Width of shimmer wave |
| `light_color` | `str` | `"#FFA500"` | Shimmer highlight color |
| `speed` | `float` | `1.0` | Shimmer movement speed |
| `reverse` | `bool` | `False` | Shimmer direction |

#### Default CSS

```css
MessageWidget {
    width: auto;
    height: 1;
    padding: 0;
    background: transparent;
}

MessageWidget.success { color: $success; }
MessageWidget.error   { color: $error; }
```

#### Reactive Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `color` | `str` | `"#D97706"` | Hex color (validated) |

#### Properties

| Property | Type | Settable | Description |
|----------|------|----------|-------------|
| `state` | `ComponentState` | No | Current state |
| `action_words` | `list[str]` | Yes | Word list (getter returns copy) |
| `reverse_shimmer` | `bool` | Yes | Shimmer direction |

#### Lifecycle

- `on_mount()`: Creates 0.1s animation timer for shimmer and word rotation
- `on_unmount()`: Stops the animation timer

#### Methods

##### `extend_action_words(words: list[str]) -> None`
Add words to the existing word list.

##### `configure(*, text: str | None = None, trigger_new: bool = False, reverse_shimmer: bool | None = None) -> None`
Update component state. Set custom text, force new word selection, or change shimmer direction.

##### `success(text: str | None = None) -> None`
Transition to success state. Shows `success_text`.

##### `error(text: str | None = None) -> None`
Transition to error state. Shows `error_text`.

##### `reset() -> None`
Reset to in_progress state. Clears word history and restarts rotation.

##### `from_config(config: dict) -> MessageWidget` *(classmethod)*
Create a MessageWidget from a configuration dictionary.

Also supports shared visibility methods: `show()`, `hide()`, `toggle()`, `set_visible(bool)` — see [Shared Patterns](#shared-patterns).

#### State Behaviors

| State | Behavior | Effect |
|-------|----------|--------|
| `IN_PROGRESS` | Rotating words with shimmer | Animation timer running |
| `SUCCESS` | Static success text | Timer paused, `.success` CSS class |
| `ERROR` | Static error text | Timer paused, `.error` CSS class |

---

## ThothSpinnerWidget Orchestrator

The main orchestrator composes all 5 widgets into a single coordinated horizontal display with unified state management.

### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `spinner_style` | `str` | `"npm_dots"` | Spinner animation style |
| `message_text` | `str` | `"Loading"` | Initial message text |
| `message_shimmer` | `bool` | `True` | Enable message shimmer |
| `progress_format` | `str` | `"fraction"` | Progress format style |
| `timer_format` | `str` | `"auto"` | Timer format style |
| `hint_text` | `str` | `"(esc to cancel)"` | Hint text |
| `success_duration` | `float \| None` | `None` | Auto-clear delay (seconds) |
| `error_duration` | `float \| None` | `None` | Auto-clear delay (seconds) |
| `config` | `dict \| None` | `None` | Full config dict (overrides kwargs) |
| `render_order` | `list[str] \| None` | All 5 components | Display order |
| `layout` | `str` | `"horizontal"` | Display orientation: `"horizontal"` or `"vertical"` |

All parameters are keyword-only.

### Configuration Hierarchy

Config resolves in order: defaults -> element-specific overrides -> kwargs.

```python
config = {
    "defaults": {
        "color": "#D97706",
        "visible": True,
    },
    "elements": {
        "spinner": {"style": "claude_stars"},
        "message": {"shimmer": {"enabled": True, "width": 5}},
        "progress": {"format_style": "percentage"},
        "timer": {"format_style": "hh:mm:ss"},
        "hint": {"text": "Custom hint"},
    },
    "render_order": ["spinner", "message", "progress", "timer", "hint"],
    "durations": {
        "success": 2.0,
        "error": 3.0,
    },
}

spinner = ThothSpinnerWidget(config=config)
# Or:
spinner = ThothSpinnerWidget.from_dict(config)
```

### Default CSS

```css
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
```

### Component Access

| Property | Type | Description |
|----------|------|-------------|
| `spinner` | `SpinnerWidget` | The spinner child widget |
| `message` | `MessageWidget` | The message child widget |
| `progress` | `ProgressWidget` | The progress child widget |
| `timer` | `TimerWidget` | The timer child widget |
| `hint` | `HintWidget` | The hint child widget |
| `state` | `ComponentState` | Current orchestrator state |

### Methods

#### State Management

##### `start() -> None`
Start in IN_PROGRESS state. Starts spinner animation and timer.

##### `success(message: str | None = None, duration: float | None = None) -> None`
Transition to success state. Propagates to all children. Optional auto-clear after `duration` seconds.

##### `error(message: str | None = None, duration: float | None = None) -> None`
Transition to error state. Propagates to all children. Optional auto-clear after `duration` seconds.

##### `reset() -> None`
Reset to IN_PROGRESS. Resets all children and restores visibility.

##### `clear() -> None`
Hide all child widgets and cancel auto-clear timer.

##### `stop() -> None`
Alias for `clear()`.

#### Component Control

##### `update_progress(*, current: int, total: int | None = None) -> None`
Update the progress component values.

##### `set_message(*, text: str) -> None`
Update the message component text.

##### `set_hint(*, text: str) -> None`
Update the hint component text.

##### `set_spinner_style(*, style: str) -> None`
Change spinner animation style at runtime.

##### `set_shimmer_direction(*, direction: str) -> None`
Set shimmer direction: `"left-to-right"` or `"right-to-left"`.

##### `get_component(component_type: str) -> Widget`
Get a child widget by type name. Raises `KeyError` for invalid types.

##### `update_component(component_type: str, **kwargs) -> None`
Generic update for any child widget. Calls `configure()` if available, otherwise sets attributes directly.

#### Factory

##### `from_dict(config: dict, **kwargs) -> ThothSpinnerWidget`
Create from configuration dict. kwargs override config values.

### Usage Examples

#### Basic Textual App

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from thothspinner.textual import TextualThothSpinner

class ProgressApp(App):
    CSS = """
    ThothSpinnerWidget {
        dock: bottom;
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield TextualThothSpinner(id="spinner")
        yield Footer()

    def on_mount(self) -> None:
        spinner = self.query_one("#spinner", TextualThothSpinner)
        spinner.start()
```

#### Worker Pattern

```python
from textual.app import App, ComposeResult
from textual.worker import Worker, get_current_worker
from thothspinner.textual import TextualThothSpinner

class WorkerApp(App):
    def compose(self) -> ComposeResult:
        yield TextualThothSpinner(id="spinner")

    def on_mount(self) -> None:
        self.query_one("#spinner", TextualThothSpinner).start()
        self.run_worker(self.do_work)

    async def do_work(self) -> None:
        spinner = self.query_one("#spinner", TextualThothSpinner)
        for i in range(100):
            spinner.update_progress(current=i, total=100)
            await asyncio.sleep(0.05)
        spinner.success("Complete!")
```

#### Error Handling

```python
def on_mount(self) -> None:
    spinner = self.query_one(TextualThothSpinner)
    spinner.start()
    try:
        result = perform_operation()
        spinner.success("Operation successful")
    except Exception as e:
        spinner.error(f"Failed: {e}")
```

### State Propagation

The orchestrator uses imperative state propagation (not `data_bind()`). When `success()` or `error()` is called, the orchestrator calls the corresponding method on each child widget. Each child responds appropriately:

- **Spinner**: Shows success/error icon, stops animation
- **Message**: Shows success/error text, stops shimmer
- **Progress**: Shows success/error text
- **Timer**: Stops timing, freezes display
- **Hint**: Hides itself

---

## Integration with Textual Apps

### Embedding in compose()

```python
def compose(self) -> ComposeResult:
    yield Header()
    yield TextualThothSpinner(id="progress-spinner")
    yield MyMainContent()
    yield Footer()
```

### Querying

```python
spinner = self.query_one(TextualThothSpinner)
# Or by ID:
spinner = self.query_one("#progress-spinner", TextualThothSpinner)
```

### Worker Pattern for Background Tasks

Use Textual workers for long-running operations to keep the UI responsive:

```python
from textual.worker import Worker

def on_mount(self) -> None:
    self.run_worker(self.background_task)

async def background_task(self) -> None:
    spinner = self.query_one(TextualThothSpinner)
    spinner.start()
    # ... do work ...
    spinner.success()
```

For more migration and integration patterns, see the [Rich to Textual Migration Guide](./rich_to_textual_guide.md).

---

## Rich vs Textual Differences

| Aspect | Rich (ThothSpinner) | Textual (ThothSpinnerWidget) |
|--------|---------------------|------------------------------|
| Rendering | Stateless `__rich_console__()` | Reactive `render()` |
| State | Manual with `threading.RLock` | Reactive properties, automatic refresh |
| Styling | Inline `Style` objects | CSS with `DEFAULT_CSS` |
| Animation | Time-based during render | `set_interval()` timers |
| Layout | `Columns` for horizontal | `Horizontal` container via `compose()` |
| Lifecycle | None (stateless) | `on_mount()` / `on_unmount()` |
| Threading | Thread-safe (RLock) | Textual's message loop (single-threaded UI) |
| Interactivity | None | Full keyboard/mouse via Textual |

For a complete conversion guide, see [Rich to Textual Migration Guide](./rich_to_textual_guide.md).

---

## Performance Considerations

1. **Timer Intervals**: Display timers run at 10 Hz (0.1s). The spinner timer interval depends on the style (typically 0.08s). Avoid creating excessive timers.
2. **Shimmer Effects**: The shimmer animation calls `refresh()` at 10 Hz. Disable shimmer (`shimmer={"enabled": False}`) on slow terminals.
3. **Component Count**: The orchestrator creates all 5 widgets. Hide unused ones via config (`"visible": False`) to reduce render work.
4. **Workers vs Threads**: Use Textual workers (`run_worker()`) instead of raw threads for background tasks. Workers integrate with Textual's event loop.

---

## API Reference Summary

### Classes

- `ThothSpinnerWidget` (alias: `TextualThothSpinner`): Main orchestrator
- `HintWidget`: Static text display with icon support
- `SpinnerWidget`: Animated spinner with multiple styles
- `ProgressWidget`: Progress counter with format options
- `TimerWidget`: Elapsed time display with controls
- `MessageWidget`: Rotating messages with shimmer effect
- `ComponentState`: State enum (IN_PROGRESS, SUCCESS, ERROR)

### Key Methods

- State: `start()`, `success()`, `error()`, `reset()`, `clear()`, `stop()`
- Progress: `update_progress()`, `set_message()`, `set_hint()`
- Configuration: `from_dict()`, `from_config()`, `get_component()`, `update_component()`
- Visibility: `show()`, `hide()`, `toggle()`, `set_visible()`

### Import Paths

```python
# Orchestrator (recommended)
from thothspinner.textual import TextualThothSpinner

# Individual widgets
from thothspinner.textual.widgets import (
    HintWidget,
    SpinnerWidget,
    ProgressWidget,
    TimerWidget,
    MessageWidget,
    ThothSpinnerWidget,
)
```

## See Also

- [Textual Examples Gallery](./examples/TEXTUAL_README.md) - Complete Textual app examples
- [Textual Troubleshooting Guide](./textual_troubleshooting.md) - Common issues and solutions
- [Reactive State Management Guide](./textual_reactive_guide.md) - Reactive patterns deep dive
- [Rich to Textual Migration Guide](./rich_to_textual_guide.md) - Converting from Rich
- [Rich API Reference](./thothspinner_rich.md) - Rich components documentation
- [Textual Documentation](https://textual.textualize.io/) - Textual framework reference
