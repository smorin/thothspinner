# SpinnerComponent Documentation

## Overview

The `SpinnerComponent` is an animated spinner for Rich console output that provides visual feedback during long-running operations. It supports multiple built-in styles, custom frames, state transitions, and full color customization.

## Features

- **14+ Built-in Styles**: NPM dots, Claude stars, classic, arrows, and more
- **Custom Frames**: Define your own animation sequences
- **State Management**: Transition between in-progress, success, and error states
- **Speed Control**: Adjust animation speed with multiplier
- **Color Customization**: Full hex color support
- **Rich Integration**: Seamless integration with Rich's Live display

## Installation

```python
from thothspinner.rich.components import SpinnerComponent
```

## Basic Usage

### Simple Spinner

```python
from rich.console import Console
from rich.live import Live
from thothspinner.rich.components import SpinnerComponent
import time

console = Console()
spinner = SpinnerComponent()

with Live(spinner, console=console, refresh_per_second=20):
    # Perform long-running operation
    time.sleep(5)
```

### With State Transitions

```python
spinner = SpinnerComponent(style="npm_dots", color="#D97706")

with Live(spinner, console=console, refresh_per_second=20):
    # Processing
    time.sleep(3)
    
    # Mark as successful
    spinner.success()
    time.sleep(1)
```

## Configuration Options

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `frames` | `list[str] \| None` | `None` | Custom frame sequence |
| `interval` | `float` | `0.08` | Time between frames in seconds |
| `color` | `str` | `"#D97706"` | Hex color code for spinner |
| `style` | `str` | `"npm_dots"` | Built-in spinner style name |
| `success_icon` | `str` | `"✓"` | Icon for success state |
| `error_icon` | `str` | `"✗"` | Icon for error state |
| `visible` | `bool` | `True` | Whether to render the component |
| `speed` | `float` | `1.0` | Animation speed multiplier |

### Built-in Styles

| Style | Description | Frame Count | Interval |
|-------|-------------|-------------|----------|
| `npm_dots` | Braille pattern dots | 10 | 0.08s |
| `claude_stars` | Animated stars | 10 | 0.1s |
| `classic` | Simple ASCII spinner | 4 | 0.1s |
| `dots` | Dense braille dots | 8 | 0.08s |
| `dots2` | Sparse dots | 8 | 0.08s |
| `dots3` | Alternative dots | 10 | 0.08s |
| `arrows` | Rotating arrows | 8 | 0.1s |
| `circle` | Quarter circles | 4 | 0.12s |
| `square` | Rotating squares | 4 | 0.12s |
| `triangle` | Rotating triangles | 4 | 0.12s |
| `bounce` | Bouncing dot | 4 | 0.12s |
| `box_bounce` | Bouncing box | 4 | 0.12s |
| `star` | Animated stars | 6 | 0.08s |

## State Management

The spinner supports three states:

### IN_PROGRESS (Default)
- Displays animated frames
- Uses configured color
- Cycles through frames at specified interval

### SUCCESS
- Displays success icon (✓)
- Uses green color (#00FF00)
- Static display (no animation)

### ERROR
- Displays error icon (✗)
- Uses red color (#FF0000)
- Static display (no animation)

### State Transition Methods

```python
# Start or restart animation
spinner.start()

# Transition to success state
spinner.success()

# Transition to error state
spinner.error()

# Reset to in_progress state
spinner.reset()
```

## Advanced Usage

### Custom Frames

```python
# Earth rotation spinner
earth_spinner = SpinnerComponent(
    frames=["🌍", "🌎", "🌏"],
    interval=0.3
)

# Clock spinner
clock_spinner = SpinnerComponent(
    frames=["🕐", "🕑", "🕒", "🕓", "🕔", "🕕"],
    interval=0.2
)
```

### Speed Control

```python
# Slow spinner (half speed)
slow_spinner = SpinnerComponent(speed=0.5)

# Fast spinner (double speed)
fast_spinner = SpinnerComponent(speed=2.0)
```

### Configuration from Dictionary

```python
config = {
    "style": "claude_stars",
    "color": "#FFA500",
    "speed": 1.5,
    "success_icon": "✅",
    "error_icon": "❌"
}

spinner = SpinnerComponent.from_config(config)
```

### Combining with Other Components

```python
from rich.table import Table
from thothspinner.rich.components import SpinnerComponent, HintComponent

spinner = SpinnerComponent()
hint = HintComponent(text=" (esc to cancel)")

# Combine in a table
display = Table.grid(padding=1)
display.add_row(spinner, hint)

with Live(display, console=console):
    # Your code here
    pass
```

## Best Practices

### 1. Use Appropriate Refresh Rate
- Use 20 FPS for smooth animation: `refresh_per_second=20`
- Lower rates (10 FPS) are acceptable for simple spinners
- Higher rates provide no visual benefit and waste CPU

### 2. Handle Interrupts in User Code
```python
import signal
import sys

def signal_handler(signum, frame):
    spinner.error()
    console.print("\n[yellow]Interrupted![/yellow]")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
```

### 3. Use Transient Mode for Clean Output
```python
with Live(spinner, transient=True):
    # Spinner disappears after completion
    pass
```

### 4. Combine Multiple Spinners
```python
table = Table.grid(padding=2)
table.add_row(
    SpinnerComponent(style="npm_dots"),
    SpinnerComponent(style="claude_stars"),
    SpinnerComponent(style="classic")
)
```

## Performance Considerations

- **Frame Calculation**: Time-based calculation ensures consistent animation regardless of refresh rate
- **CPU Usage**: Typically under 5% with 20 FPS refresh rate
- **Memory**: Minimal memory footprint with efficient state management
- **Thread Safety**: State transitions are atomic and thread-safe

## Common Issues and Solutions

### Spinner Not Animating
- Ensure you're using `Live` context with appropriate refresh rate
- Check that `visible` property is `True`
- Verify spinner is in `IN_PROGRESS` state

### Unicode Characters Not Displaying
- Some terminals may not support all Unicode characters
- Use ASCII-based styles like `classic` for maximum compatibility
- Test in your target terminal environment

### State Transitions Not Working
- Transitions follow strict rules (see State Management section)
- Cannot transition directly between SUCCESS and ERROR
- Use `reset()` to return to IN_PROGRESS from any state

## Examples

See `examples/rich/spinner_demo.py` for comprehensive demonstrations of all features.

## API Reference

### Class: `SpinnerComponent`

#### Properties
- `state` (ComponentState): Current state of the spinner
- `visible` (bool): Visibility control
- `frames` (list[str]): Animation frames
- `color` (str): Hex color code

#### Methods
- `start()`: Start or restart animation
- `success(message=None)`: Transition to success state
- `error(message=None)`: Transition to error state
- `reset()`: Reset to in_progress state
- `from_config(config)`: Create from configuration dictionary

#### Rich Protocol Methods
- `__rich_console__()`: Render for Rich console
- `__rich_measure__()`: Measure for layout calculations