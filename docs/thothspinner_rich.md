# ThothSpinner Rich Components API Reference

## Overview

ThothSpinner is a highly configurable progress indicator library for Python, built on top of the Rich library. It provides animated progress components that can be composed together to create beautiful, informative terminal displays.

### Key Features
- 🎨 **Modular Components**: Mix and match spinner, progress, timer, message, and hint components
- 🔄 **State Management**: Built-in success/error states with automatic transitions
- ✨ **Shimmer Effects**: Eye-catching animation effects for enhanced visual appeal
- 🎯 **Thread-Safe**: Proper locking for concurrent operations
- 🚀 **Performance Optimized**: Efficient rendering with minimal CPU usage
- 🎭 **Rich Integration**: Seamless integration with Rich Console and Live displays

## Installation

```bash
# Install with uv (recommended)
uv add thothspinner

# Or with pip
pip install thothspinner
```

## Quick Start

```python
from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live
import time

console = Console()

# Simple usage with default settings
with Live(ThothSpinner(), console=console) as live:
    spinner = live.renderable
    spinner.start()
    
    # Simulate work
    for i in range(100):
        spinner.update_progress(current=i, total=100)
        time.sleep(0.05)
    
    spinner.success("Task completed!")
```

## Components

### HintComponent

Static text component for displaying helper messages or instructions.

#### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | `"(esc to cancel)"` | Text to display |
| `color` | `str` | `"#808080"` | Hex color code for text |
| `visible` | `bool` | `True` | Whether component is visible |

#### Usage

```python
from thothspinner.rich.components import HintComponent
from rich.console import Console

console = Console()
hint = HintComponent(text="Press ESC to cancel", color="#888888")
console.print(hint)
```

#### State Behaviors

| State | Behavior | Configuration |
|-------|----------|---------------|
| `IN_PROGRESS` | Shows helper text | Default color |
| `SUCCESS` | Can show success message or hide | Custom text/color |
| `ERROR` | Can show error hint or hide | Custom text/color |

---

### SpinnerComponent

Animated spinner with customizable frame sequences and styles.

#### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `style` | `str` | `"npm_dots"` | Built-in spinner style |
| `frames` | `List[str]` | Based on style | Custom frame sequence |
| `interval` | `float` | `0.08` | Time between frames in seconds |
| `color` | `str` | `"#D97706"` | Hex color code |
| `success_icon` | `str` | `"✓"` | Icon for success state |
| `error_icon` | `str` | `"✗"` | Icon for error state |

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
- `matrix`: Half-width katakana cycling at high speed (`ｦｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃ`)

#### Usage

```python
from thothspinner.rich.components import SpinnerComponent
from rich.live import Live
import time

spinner = SpinnerComponent(style="claude_stars", color="#FFA500")

with Live(spinner, refresh_per_second=20) as live:
    time.sleep(3)
    spinner.success()  # Shows success icon
```

#### State Behaviors

| State | Behavior | Configuration |
|-------|----------|---------------|
| `IN_PROGRESS` | Animating through frames | Frame interval, color |
| `SUCCESS` | Static success icon | `success_icon`, green color |
| `ERROR` | Static error icon | `error_icon`, red color |

---

### ProgressComponent

Displays progress as a counter with multiple format options.

#### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `current` | `int` | `0` | Current progress value |
| `total` | `Optional[int]` | `100` | Total value for completion |
| `format` | `Dict[str, Any]` | `{"style": "percentage"}` | Display format configuration |
| `color` | `str` | `"#55FF55"` | Hex color code |
| `zero_pad` | `bool` | `False` | Pad numbers with zeros |

#### Format Styles

- `fraction`: "3/10"
- `percentage`: "30%"
- `of_text`: "3 of 10"
- `count_only`: "3"
- `ratio`: "3:10"

#### Usage

```python
from thothspinner.rich.components import ProgressComponent
from rich.live import Live

progress = ProgressComponent(
    current=0,
    total=100,
    format={"style": "percentage"},
    color="#00FF00"
)

with Live(progress) as live:
    for i in range(101):
        progress.set(i)
        time.sleep(0.05)
```

#### Methods

##### `set(value: int) -> None`
Set the current progress value.

##### `increment() -> None`
Increment progress by 1.

##### `set_percentage(percentage: float) -> None`
Set progress as a percentage (0-100).

#### State Behaviors

| State | Behavior | Configuration |
|-------|----------|---------------|
| `IN_PROGRESS` | Shows current/total | Real-time updates |
| `SUCCESS` | Shows 100% or final value | Success color |
| `ERROR` | Shows failure point | Error color |

---

### TimerComponent

Displays elapsed time in various formats with precision control.

#### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `format` | `Dict[str, Any]` | `{"style": "auto"}` | Time format configuration |
| `color` | `str` | `"#FFFF55"` | Hex color code |
| `precision` | `int` | `1` | Decimal places for seconds |

#### Format Styles

- `seconds`: "3s"
- `seconds_decimal`: "3.2s"
- `mm:ss`: "01:23"
- `hh:mm:ss`: "0:01:23"
- `auto`: Changes based on duration
- `milliseconds`: "3245ms"

#### Usage

```python
from thothspinner.rich.components import TimerComponent
from rich.live import Live
import time

timer = TimerComponent(
    format={"style": "auto", "precision": 1},
    color="#FFFF00"
)

with Live(timer) as live:
    timer.start()
    time.sleep(5)
    timer.stop()
```

#### Methods

##### `start() -> None`
Start the timer.

##### `stop() -> None`
Stop the timer at current time.

##### `reset() -> None`
Reset timer to 00:00.

##### `resume() -> None`
Resume the timer from where it was stopped.

##### `__str__() -> str`
Returns the current elapsed time as a formatted string using the configured format style. Enables direct use in f-strings and `str()` calls:

```python
console.print(f"Total time: {timer}")   # e.g. "Total time: 5.2s"
elapsed_str = str(timer)                # e.g. "5.2s"
```

#### State Behaviors

| State | Behavior | Configuration |
|-------|----------|---------------|
| `IN_PROGRESS` | Counting elapsed time | Format style, precision |
| `SUCCESS` | Stops at final time | Success color |
| `ERROR` | Stops at error time | Error color |

---

### MessageComponent

Displays rotating action words with optional shimmer effects.

#### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | Random action word | Initial message text |
| `action_words` | `List[str]` | 87 default words | Word pool for rotation |
| `interval` | `Dict[str, float]` | `{"min": 0.5, "max": 3.0}` | Rotation interval range |
| `color` | `str` | `"#D97706"` | Base color |
| `shimmer` | `Dict[str, Any]` | See below | Shimmer effect config |

#### Shimmer Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | `bool` | `True` | Enable shimmer effect |
| `width` | `int` | `3` | Width of shimmer wave |
| `light_color` | `str` | `"#FFA500"` | Shimmer highlight color |
| `speed` | `float` | `1.0` | Shimmer animation speed |
| `direction` | `str` | `"left-to-right"` | Animation direction |

#### Usage

```python
from thothspinner.rich.components import MessageComponent
from rich.live import Live

message = MessageComponent(
    shimmer={
        "enabled": True,
        "width": 3,
        "direction": "left-to-right"
    }
)

with Live(message, refresh_per_second=20) as live:
    time.sleep(5)
    message.reverse_shimmer = True  # Change direction
```

#### State Behaviors

| State | Behavior | Configuration |
|-------|----------|---------------|
| `IN_PROGRESS` | Rotating words with shimmer | Interval, shimmer settings |
| `SUCCESS` | Static success message | No shimmer, success color |
| `ERROR` | Static error message | No shimmer, error color |

---

## ThothSpinner Orchestrator

The main orchestrator that combines all components into a unified display.

### Configuration

```python
from thothspinner import ThothSpinner

# Simple initialization with kwargs
spinner = ThothSpinner(
    spinner_style="npm_dots",
    message_text="Loading data",
    message_shimmer=True,
    progress_format="percentage",
    timer_format="auto",
    hint_text="(esc to cancel)",
    success_duration=2.0,  # Auto-clear after 2 seconds
    error_duration=5.0     # Auto-clear after 5 seconds
)

# Or with configuration dict
config = {
    "defaults": {
        "color": "#D97706",
        "visible": True
    },
    "elements": {
        "spinner": {"style": "claude_stars"},
        "message": {"shimmer": {"enabled": True}},
        "progress": {"format": {"style": "fraction"}},
        "timer": {"format": {"style": "mm:ss"}},
        "hint": {"text": "Press Ctrl+C to stop"}
    },
    "render_order": ["spinner", "message", "progress", "timer", "hint"]
}

spinner = ThothSpinner.from_dict(config)
```

### Configuration Hierarchy

ThothSpinner uses a three-level configuration hierarchy:

1. **Global Defaults** (lowest priority)
2. **State-Specific Configuration**
3. **Component-Specific Overrides** (highest priority)

```python
config = {
    # Level 1: Global defaults
    "defaults": {
        "color": "#D97706",
        "visible": True
    },
    
    # Level 2: State-specific
    "states": {
        "success": {
            "spinner": {"icon": "✓", "color": "#00FF00"},
            "message": {"text": "Complete!"}
        },
        "error": {
            "spinner": {"icon": "✗", "color": "#FF0000"},
            "message": {"text": "Failed"}
        }
    },
    
    # Level 3: Component-specific
    "elements": {
        "spinner": {"color": "#FFA500"},  # Overrides default
        "progress": {"format": {"style": "percentage"}}
    }
}
```

### Methods

#### State Management

##### `start() -> None`
Begin in `IN_PROGRESS` state, starting all animations.

##### `success(message: Optional[str] = None, duration: Optional[float] = None) -> None`
Transition to success state with optional message and auto-clear duration.

##### `error(message: Optional[str] = None, duration: Optional[float] = None) -> None`
Transition to error state with optional message and auto-clear duration.

##### `reset() -> None`
Return to `IN_PROGRESS` state from any state.

##### `clear() -> None`
Stop and hide all components.

#### Component Control

##### `update_progress(*, current: int, total: Optional[int] = None) -> None`
Update the progress component.

##### `set_message(*, text: str) -> None`
Update the message component text.

##### `set_spinner_style(*, style: str) -> None`
Change the spinner animation style.

##### `set_hint(*, text: str) -> None`
Update the hint text.

##### `set_shimmer_direction(*, direction: str) -> None`
Control shimmer animation direction ("left-to-right" or "right-to-left").

##### `get_component(component_type: str) -> Any`
Access a specific component by type.

##### `update_component(component_type: str, **kwargs) -> None`
Generic update method for any component.

### State System

ThothSpinner implements a three-state system:

| State | Description | Valid Transitions |
|-------|-------------|-------------------|
| `IN_PROGRESS` | Active/working state | → SUCCESS, ERROR |
| `SUCCESS` | Operation completed | → IN_PROGRESS (via reset) |
| `ERROR` | Operation failed | → IN_PROGRESS (via reset) |

### Usage Examples

#### Basic Progress Tracking

```python
from thothspinner import ThothSpinner
from rich.live import Live
import time

with Live(ThothSpinner()) as live:
    spinner = live.renderable
    spinner.start()
    
    for i in range(100):
        spinner.update_progress(current=i, total=100)
        time.sleep(0.05)
    
    spinner.success("Processing complete!")
```

#### File Operations

```python
import os
from pathlib import Path

def process_files(directory: Path):
    files = list(directory.glob("*.txt"))
    
    with Live(ThothSpinner()) as live:
        spinner = live.renderable
        spinner.start()
        
        for i, file in enumerate(files):
            spinner.set_message(text=f"Processing {file.name}")
            spinner.update_progress(current=i, total=len(files))
            
            # Process file
            process_file(file)
        
        spinner.success(f"Processed {len(files)} files")
```

#### Error Handling

```python
with Live(ThothSpinner()) as live:
    spinner = live.renderable
    spinner.start()
    
    try:
        # Risky operation
        result = perform_operation()
        spinner.success("Operation successful")
    except Exception as e:
        spinner.error(f"Operation failed: {str(e)}")
```

#### Custom Configuration

```python
config = {
    "defaults": {"color": "#00FFFF"},
    "elements": {
        "spinner": {"style": "claude_stars", "color": "#FFD700"},
        "message": {
            "shimmer": {
                "enabled": True,
                "width": 5,
                "light_color": "#FFFFFF"
            }
        },
        "progress": {"format": {"style": "fraction", "zero_pad": True}},
        "timer": {"format": {"style": "hh:mm:ss"}},
        "hint": {"text": "Processing... Press Ctrl+C to abort"}
    },
    "states": {
        "success": {
            "behavior": "indicator",
            "duration": 3.0,
            "spinner": {"icon": "🎉"},
            "message": {"text": "Awesome! Task completed!"}
        },
        "error": {
            "behavior": "indicator",
            "duration": 5.0,
            "spinner": {"icon": "❌"},
            "message": {"text": "Oops! Something went wrong"}
        }
    }
}

spinner = ThothSpinner.from_dict(config)
```

## Performance Considerations

### Optimization Tips

1. **Refresh Rate**: Use appropriate refresh rates (10-20 Hz for smooth animation)
2. **Component Selection**: Only include components you need
3. **Shimmer Effects**: Disable on slow terminals if performance is critical
4. **Thread Safety**: All methods are thread-safe with proper locking

### Benchmarks

| Operation | Time | CPU Usage |
|-----------|------|-----------|
| Spinner animation (20 FPS) | - | < 1% |
| Progress update (100 updates/sec) | - | < 2% |
| Full orchestrator (all components) | - | < 5% |

## Migration from Rich Progress

### Before (Rich Progress)

```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    transient=True
) as progress:
    task = progress.add_task("Processing", total=100)
    for i in range(100):
        progress.advance(task, 1)
```

### After (ThothSpinner)

```python
from thothspinner import ThothSpinner
from rich.live import Live

with Live(ThothSpinner(), transient=True) as live:
    spinner = live.renderable
    spinner.start()
    spinner.set_message(text="Processing")
    
    for i in range(100):
        spinner.update_progress(current=i, total=100)
    
    spinner.success()
```

### Key Differences

| Feature | Rich Progress | ThothSpinner |
|---------|--------------|--------------|
| Component Model | Column-based | Component-based |
| State Management | Manual | Built-in states |
| Animation | Per-column | Orchestrated |
| Configuration | Code-based | Dict/kwargs-based |
| Shimmer Effects | Not built-in | Built-in |
| Action Words | Not built-in | Built-in |

## Thread Safety

All ThothSpinner components are thread-safe:

```python
import threading
from thothspinner import ThothSpinner
from rich.live import Live

spinner = ThothSpinner()

def worker(worker_id: int):
    for i in range(50):
        # Thread-safe updates
        spinner.update_progress(current=i * 2, total=100)
        spinner.set_message(text=f"Worker {worker_id}: Processing item {i}")
        time.sleep(0.1)

with Live(spinner) as live:
    spinner.start()
    
    threads = [
        threading.Thread(target=worker, args=(i,))
        for i in range(2)
    ]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    spinner.success("All workers completed")
```

## Advanced Features

### Custom Components

While ThothSpinner provides built-in components, you can extend them:

```python
from thothspinner.rich.components.base import BaseComponent

class CustomComponent(BaseComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Custom initialization
    
    def __rich__(self):
        # Return Rich renderable
        return Text("Custom output", style=self.style)
```

### Event-Driven Updates

```python
class DataProcessor:
    def __init__(self, spinner: ThothSpinner):
        self.spinner = spinner
    
    def on_data_received(self, size: int):
        self.spinner.set_shimmer_direction(direction="right-to-left")
        self.spinner.set_message(text=f"Receiving {size} bytes")
    
    def on_data_sent(self, size: int):
        self.spinner.set_shimmer_direction(direction="left-to-right")
        self.spinner.set_message(text=f"Sending {size} bytes")
```

## Best Practices

### Do's
- ✅ Use context managers (with statements) for proper cleanup
- ✅ Choose appropriate refresh rates (10-20 Hz typically)
- ✅ Handle exceptions and update state accordingly
- ✅ Use thread-safe methods for concurrent operations
- ✅ Provide meaningful progress updates and messages

### Don'ts
- ❌ Don't update too frequently (causes flickering)
- ❌ Don't forget to call `start()` before updates
- ❌ Don't mix direct component access with orchestrator methods
- ❌ Don't ignore state transitions (invalid transitions raise errors)

## API Reference Summary

### Classes
- `ThothSpinner`: Main orchestrator class
- `HintComponent`: Static text display
- `SpinnerComponent`: Animated spinner
- `ProgressComponent`: Progress counter
- `TimerComponent`: Elapsed time display
- `MessageComponent`: Rotating messages with shimmer
- `ComponentState`: State enumeration (IN_PROGRESS, SUCCESS, ERROR)

### Key Methods
- State Management: `start()`, `success()`, `error()`, `reset()`, `clear()`
- Progress Control: `update_progress()`, `set_message()`, `set_hint()`
- Configuration: `from_dict()`, `get_component()`, `update_component()`

### Configuration Keys
- `defaults`: Global default settings
- `elements`: Component-specific configuration
- `render_order`: Component display order
- `states`: State-specific behaviors
- `fade_away`: Fade animation settings

## See Also

- [Examples Gallery](./examples/README.md) - Complete code examples
- [Troubleshooting Guide](./troubleshooting.md) - Common issues and solutions
- [Rich Documentation](https://rich.readthedocs.io/) - Rich library reference
- [GitHub Repository](https://github.com/yourusername/thothspinner) - Source code and issues