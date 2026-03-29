# Rich to Textual Component Conversion Guide

## Table of Contents
1. [Overview](#overview)
2. [Fundamental Paradigm Differences](#fundamental-paradigm-differences)
3. [Architecture Comparison](#architecture-comparison)
4. [Step-by-Step Conversion Process](#step-by-step-conversion-process)
5. [Component Conversion Examples](#component-conversion-examples)
6. [Common Patterns and Anti-Patterns](#common-patterns-and-anti-patterns)
7. [Migration Checklist](#migration-checklist)
8. [Troubleshooting](#troubleshooting)
9. [Examples](#examples)

## Overview

This guide provides a comprehensive walkthrough for converting Rich components to Textual widgets. While Rich and Textual both create terminal user interfaces, they operate on fundamentally different paradigms that require careful consideration during conversion.

### When to Use Each

**Use Rich when:**
- Building CLI output components
- Creating progress indicators for scripts
- Formatting console output
- Building simple, non-interactive displays

**Use Textual when:**
- Building full TUI applications
- Need mouse/keyboard interaction
- Require complex layouts
- Building reactive, stateful interfaces

## Fundamental Paradigm Differences

### 1. Rendering Model

#### Rich: Direct Rendering
```python
# Rich renders directly to console
class RichComponent:
    def __rich_console__(self, console, options):
        yield Text("Hello", style="bold red")
```

#### Textual: Reactive Rendering
```python
# Textual uses reactive properties and render methods
class TextualWidget(Widget):
    text = reactive("Hello")

    def render(self):
        return Text(self.text, style="bold red")
```

**Key Difference:** Rich components are stateless and render on-demand, while Textual widgets maintain state and re-render when reactive properties change.

### 2. Event Handling

#### Rich: No Event System
```python
# Rich has no built-in event handling
class RichSpinner:
    def __rich_console__(self, console, options):
        # Cannot respond to user input
        yield self.get_frame()
```

#### Textual: Comprehensive Event System
```python
# Textual has rich event handling
class TextualSpinner(Widget):
    def on_click(self, event):
        """Handle mouse clicks"""
        self.toggle_pause()

    def on_key(self, event):
        """Handle keyboard input"""
        if event.key == "space":
            self.toggle_pause()
```

### 3. Styling System

#### Rich: Inline Styles
```python
# Rich uses inline style objects
Text("Hello", style=Style(color="red", bold=True))
```

#### Textual: CSS-Based Styling
```python
# Textual uses CSS
class MyWidget(Widget):
    DEFAULT_CSS = """
    MyWidget {
        color: red;
        text-style: bold;
    }
    """
```

### 4. Layout System

#### Rich: Line-Based Output
```python
# Rich outputs line by line
def __rich_console__(self, console, options):
    yield Text("Line 1")
    yield Text("Line 2")
```

#### Textual: Flexbox/Grid Layout
```python
# Textual uses modern layout systems
def compose(self):
    yield Container(
        Label("Item 1"),
        Label("Item 2"),
        id="container"
    )

DEFAULT_CSS = """
#container {
    layout: horizontal;
    align: center middle;
}
"""
```

### 5. Lifecycle Management

#### Rich: Stateless
```python
# Rich components have no lifecycle
class RichComponent:
    def __rich_console__(self, console, options):
        # Renders and forgets
        return Text("Hello")
```

#### Textual: Full Widget Lifecycle
```python
# Textual widgets have lifecycle methods
class TextualWidget(Widget):
    def on_mount(self):
        """Called when widget is added to DOM"""
        self.start_animation()

    def on_unmount(self):
        """Called when widget is removed"""
        self.stop_animation()
```

## Architecture Comparison

### Rich Component Architecture

```python
from rich.console import Console, ConsoleOptions, RenderResult
from rich.text import Text
from rich.style import Style

class RichComponent:
    """A typical Rich component"""

    def __init__(self, text: str, color: str = "white"):
        self.text = text
        self.color = color

    def __rich_console__(
        self,
        console: Console,
        options: ConsoleOptions
    ) -> RenderResult:
        """Rich protocol method for rendering"""
        style = Style(color=self.color)
        yield Text(self.text, style=style)

    def __rich_measure__(
        self,
        console: Console,
        options: ConsoleOptions
    ) -> Measurement:
        """Measure the component width"""
        return Measurement.get(console, options, Text(self.text))
```

### Textual Widget Architecture

```python
from textual.widget import Widget
from textual.reactive import reactive
from textual.app import ComposeResult, RenderResult
from rich.text import Text

class TextualWidget(Widget):
    """Equivalent Textual widget"""

    # CSS for styling
    DEFAULT_CSS = """
    TextualWidget {
        height: 1;
        width: auto;
    }

    TextualWidget.error {
        color: red;
    }
    """

    # Reactive properties trigger re-renders
    text = reactive("Hello")
    color = reactive("white")

    def __init__(self, text: str = "Hello", color: str = "white"):
        super().__init__()
        self.text = text
        self.color = color

    def render(self) -> RenderResult:
        """Render method called when reactive properties change"""
        return Text(self.text, style=f"color: {self.color}")

    def on_mount(self) -> None:
        """Called when widget is mounted to the DOM"""
        self.log("Widget mounted")

    def on_click(self) -> None:
        """Handle click events"""
        self.add_class("error")
```

## Step-by-Step Conversion Process

### Step 1: Analyze the Rich Component

1. **Identify State**: What data does the component track?
2. **Identify Rendering Logic**: How does it produce output?
3. **Identify Updates**: How/when does it change?
4. **Identify Configuration**: What parameters does it accept?

### Step 2: Design the Textual Widget Structure

1. **Define Reactive Properties**: Convert state to reactive properties
2. **Plan Event Handlers**: Determine needed interactions
3. **Design CSS Classes**: Plan styling approach
4. **Consider Composition**: Will it contain other widgets?

### Step 3: Implement Core Widget

```python
# Template for conversion
from textual.widget import Widget
from textual.reactive import reactive
from typing import ClassVar

class ConvertedWidget(Widget):
    # CSS styling
    DEFAULT_CSS: ClassVar[str] = """
    ConvertedWidget {
        /* Base styles */
    }
    """

    # Component classes for styling variants
    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "widget--active",
        "widget--error",
    }

    # Reactive properties (from Rich component state)
    property_name = reactive(default_value)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize non-reactive state

    def render(self):
        """Main rendering logic (from __rich_console__)"""
        pass

    def on_mount(self):
        """Setup logic when widget is added to DOM"""
        pass
```

### Step 4: Convert Rendering Logic

#### Rich Rendering Pattern
```python
def __rich_console__(self, console, options):
    if self.state == "loading":
        yield Spinner("dots")
    else:
        yield Text(self.message)
```

#### Textual Rendering Pattern
```python
def render(self):
    if self.state == "loading":
        return LoadingIndicator()
    else:
        return Text(self.message)

def watch_state(self, old_state, new_state):
    """Called when state changes"""
    self.refresh()  # Trigger re-render
```

### Step 5: Add Interactivity

```python
class InteractiveWidget(Widget):
    can_focus = True  # Allow keyboard focus

    def on_key(self, event):
        """Handle keyboard input"""
        if event.key == "enter":
            self.action_submit()

    def on_click(self, event):
        """Handle mouse clicks"""
        self.focus()

    async def action_submit(self):
        """Action method (can be bound to keys)"""
        await self.process_data()
```

### Step 6: Handle Animation

#### Rich: Time-Based Animation
```python
class RichSpinner:
    def __rich_console__(self, console, options):
        elapsed = time.time() - self.start_time
        frame_idx = int(elapsed / self.interval) % len(self.frames)
        yield Text(self.frames[frame_idx])
```

#### Textual: Refresh-Based Animation
```python
class TextualSpinner(Widget):
    frame_idx = reactive(0)

    def on_mount(self):
        self.set_interval(0.1, self.advance_frame)

    def advance_frame(self):
        self.frame_idx = (self.frame_idx + 1) % len(self.frames)

    def render(self):
        return Text(self.frames[self.frame_idx])
```

## Component Conversion Examples

### Example 1: Converting a Spinner Component

#### Rich Spinner
```python
from rich.console import Console, ConsoleOptions, RenderResult
from rich.text import Text
from rich.style import Style
import time

class RichSpinner:
    """Rich spinner component"""

    def __init__(self, style: str = "dots", color: str = "#D97706"):
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.interval = 0.08
        self.color = color
        self.start_time = time.time()
        self._stopped = False

    def stop(self, icon: str = "✓", color: str = "#00FF00"):
        self._stopped = True
        self.final_icon = icon
        self.final_color = color

    def __rich_console__(
        self,
        console: Console,
        options: ConsoleOptions
    ) -> RenderResult:
        if self._stopped:
            yield Text(self.final_icon, style=Style(color=self.final_color))
        else:
            elapsed = time.time() - self.start_time
            frame_idx = int(elapsed / self.interval) % len(self.frames)
            yield Text(self.frames[frame_idx], style=Style(color=self.color))
```

#### Converted Textual Spinner
```python
from textual.widget import Widget
from textual.reactive import reactive
from textual.timer import Timer
from rich.text import Text
from typing import ClassVar

class TextualSpinner(Widget):
    """Textual spinner widget"""

    DEFAULT_CSS: ClassVar[str] = """
    TextualSpinner {
        height: 1;
        width: 1;
        content-align: center middle;
    }

    TextualSpinner.success {
        color: #00FF00;
    }

    TextualSpinner.error {
        color: #FF0000;
    }
    """

    # Reactive properties
    frame_index = reactive(0)
    is_running = reactive(True)
    final_icon = reactive("")

    def __init__(
        self,
        style: str = "dots",
        color: str = "#D97706",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.interval = 0.08
        self.base_color = color
        self._timer: Timer | None = None

    def on_mount(self) -> None:
        """Start animation when mounted"""
        self._timer = self.set_interval(
            self.interval,
            self.advance_frame,
            pause=not self.is_running
        )

    def advance_frame(self) -> None:
        """Advance to next frame"""
        if self.is_running:
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def stop(self, icon: str = "✓", success: bool = True) -> None:
        """Stop the spinner with final icon"""
        self.is_running = False
        self.final_icon = icon
        if self._timer:
            self._timer.pause()

        # Add appropriate class for styling
        self.add_class("success" if success else "error")

    def render(self) -> Text:
        """Render current frame or final icon"""
        if not self.is_running and self.final_icon:
            return Text(self.final_icon)
        else:
            return Text(
                self.frames[self.frame_index],
                style=f"color: {self.base_color}"
            )

    def on_click(self) -> None:
        """Toggle spinner on click"""
        if self.is_running:
            self.stop("⏸", success=False)
        else:
            self.is_running = True
            self.remove_class("success", "error")
            if self._timer:
                self._timer.resume()
```

### Example 2: Converting a Progress Component

#### Rich Progress Component
```python
from rich.progress import Progress, BarColumn, TextColumn
from rich.console import Console, ConsoleOptions, RenderResult
from rich.table import Table

class RichProgress:
    """Rich progress component"""

    def __init__(self, total: int = 100):
        self.total = total
        self.current = 0
        self.description = "Processing..."

    def update(self, advance: int = 1):
        self.current = min(self.current + advance, self.total)

    def __rich_console__(
        self,
        console: Console,
        options: ConsoleOptions
    ) -> RenderResult:
        # Create a simple progress bar
        percentage = (self.current / self.total) * 100
        filled = int(percentage / 2)  # 50 chars wide
        bar = f"[{'=' * filled}{' ' * (50 - filled)}]"

        table = Table.grid(padding=0)
        table.add_row(
            f"{self.description}",
            bar,
            f"{percentage:.1f}%"
        )
        yield table
```

#### Converted Textual Progress Widget
```python
from textual.widget import Widget
from textual.reactive import reactive, var
from textual.widgets import ProgressBar, Label
from textual.containers import Horizontal
from textual.app import ComposeResult

class TextualProgress(Widget):
    """Textual progress widget"""

    DEFAULT_CSS = """
    TextualProgress {
        height: 3;
        padding: 1;
        border: solid $primary;
    }

    TextualProgress > Horizontal {
        height: 1;
        align: left middle;
    }

    TextualProgress Label {
        width: auto;
        margin: 0 1;
    }

    TextualProgress ProgressBar {
        width: 1fr;
    }

    TextualProgress .percentage {
        width: 6;
        text-align: right;
    }
    """

    # Reactive properties
    total = reactive(100.0)
    current = reactive(0.0)
    description = reactive("Processing...")

    def __init__(
        self,
        total: float = 100,
        description: str = "Processing...",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.total = total
        self.description = description

    def compose(self) -> ComposeResult:
        """Compose child widgets"""
        with Horizontal():
            yield Label(self.description, id="description")
            yield ProgressBar(total=self.total, id="progress")
            yield Label("0.0%", classes="percentage", id="percentage")

    def update_progress(self, advance: float = 1) -> None:
        """Update progress"""
        self.current = min(self.current + advance, self.total)

        # Update child widgets
        self.query_one("#progress", ProgressBar).advance(advance)
        percentage = (self.current / self.total) * 100
        self.query_one("#percentage", Label).update(f"{percentage:.1f}%")

    def watch_description(self, old: str, new: str) -> None:
        """React to description changes"""
        self.query_one("#description", Label).update(new)

    def set_progress(self, value: float) -> None:
        """Set absolute progress value"""
        advance = value - self.current
        if advance > 0:
            self.update_progress(advance)
```

### Example 3: Converting a Timer Component

#### Rich Timer Component
```python
from rich.console import Console, ConsoleOptions, RenderResult
from rich.text import Text
from rich.style import Style
import time

class RichTimer:
    """Rich timer component"""

    def __init__(self, format: str = "mm:ss"):
        self.format = format
        self.start_time = None
        self.elapsed = 0.0
        self.running = False

    def start(self):
        self.start_time = time.time()
        self.running = True

    def stop(self):
        if self.running and self.start_time:
            self.elapsed = time.time() - self.start_time
        self.running = False

    def format_time(self, seconds: float) -> str:
        if self.format == "mm:ss":
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins:02d}:{secs:02d}"
        elif self.format == "seconds":
            return f"{seconds:.1f}s"
        else:
            return str(int(seconds))

    def __rich_console__(
        self,
        console: Console,
        options: ConsoleOptions
    ) -> RenderResult:
        if self.running and self.start_time:
            current_elapsed = time.time() - self.start_time
        else:
            current_elapsed = self.elapsed

        time_str = self.format_time(current_elapsed)
        style = Style(color="#FFFF55" if self.running else "#00FF00")
        yield Text(time_str, style=style)
```

#### Converted Textual Timer Widget
```python
from textual.widget import Widget
from textual.reactive import reactive
from textual.timer import Timer
from rich.text import Text
from datetime import datetime, timedelta
from typing import ClassVar, Literal

TimeFormat = Literal["mm:ss", "hh:mm:ss", "seconds", "milliseconds"]

class TextualTimer(Widget):
    """Textual timer widget"""

    DEFAULT_CSS = """
    TextualTimer {
        height: 1;
        width: auto;
        min-width: 8;
        content-align: center middle;
        padding: 0 1;
    }

    TextualTimer.running {
        color: #FFFF55;
        background: $boost;
    }

    TextualTimer.stopped {
        color: #00FF00;
    }

    TextualTimer.paused {
        color: #FFA500;
    }
    """

    # Reactive properties
    elapsed_seconds = reactive(0.0)
    is_running = reactive(False)
    format_style = reactive("mm:ss")

    def __init__(
        self,
        format: TimeFormat = "mm:ss",
        auto_start: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.format_style = format
        self._timer: Timer | None = None
        self._start_time: float | None = None
        self._pause_elapsed: float = 0.0

        if auto_start:
            # Use set_timer to start after mount
            self.call_after_refresh(self.start)

    def on_mount(self) -> None:
        """Setup timer interval"""
        # Update every 100ms for smooth display
        self._timer = self.set_interval(
            0.1,
            self.update_elapsed,
            pause=True
        )

    def start(self) -> None:
        """Start the timer"""
        if not self.is_running:
            self._start_time = self.time
            self.is_running = True
            self.add_class("running")
            self.remove_class("stopped", "paused")
            if self._timer:
                self._timer.resume()

    def stop(self) -> None:
        """Stop and reset the timer"""
        self.is_running = False
        self._start_time = None
        self._pause_elapsed = 0.0
        self.elapsed_seconds = 0.0
        self.add_class("stopped")
        self.remove_class("running", "paused")
        if self._timer:
            self._timer.pause()

    def pause(self) -> None:
        """Pause the timer"""
        if self.is_running and self._start_time:
            self._pause_elapsed = self.elapsed_seconds
            self.is_running = False
            self.add_class("paused")
            self.remove_class("running")
            if self._timer:
                self._timer.pause()

    def resume(self) -> None:
        """Resume from pause"""
        if not self.is_running and self._pause_elapsed > 0:
            self._start_time = self.time - self._pause_elapsed
            self.is_running = True
            self.add_class("running")
            self.remove_class("paused")
            if self._timer:
                self._timer.resume()

    def update_elapsed(self) -> None:
        """Update elapsed time"""
        if self.is_running and self._start_time is not None:
            self.elapsed_seconds = self.time - self._start_time + self._pause_elapsed

    def format_time(self, seconds: float) -> str:
        """Format time based on style"""
        if self.format_style == "hh:mm:ss":
            td = timedelta(seconds=seconds)
            hours = int(td.total_seconds() // 3600)
            minutes = int((td.total_seconds() % 3600) // 60)
            secs = int(td.total_seconds() % 60)
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        elif self.format_style == "mm:ss":
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes:02d}:{secs:02d}"
        elif self.format_style == "seconds":
            return f"{seconds:.1f}s"
        elif self.format_style == "milliseconds":
            return f"{seconds * 1000:.0f}ms"
        else:
            return str(int(seconds))

    def render(self) -> Text:
        """Render the timer display"""
        time_str = self.format_time(self.elapsed_seconds)
        return Text(time_str)

    def on_click(self) -> None:
        """Toggle timer on click"""
        if self.is_running:
            self.pause()
        elif self._pause_elapsed > 0:
            self.resume()
        else:
            self.start()

    def action_toggle(self) -> None:
        """Action to toggle timer state"""
        self.on_click()

    def action_reset(self) -> None:
        """Action to reset timer"""
        self.stop()
```

## Common Patterns and Anti-Patterns

### Patterns ✅

#### 1. Use Reactive Properties for State
```python
# Good: Reactive properties trigger re-renders
class GoodWidget(Widget):
    count = reactive(0)

    def increment(self):
        self.count += 1  # Automatically triggers render()
```

#### 2. Compose Complex Widgets
```python
# Good: Break down complex UIs into composable widgets
class ComplexWidget(Widget):
    def compose(self) -> ComposeResult:
        yield Header()
        yield ContentArea()
        yield Footer()
```

#### 3. Use CSS for Styling
```python
# Good: Centralized, maintainable styling
class StyledWidget(Widget):
    DEFAULT_CSS = """
    StyledWidget {
        background: $surface;
        color: $text;
        padding: 1;
    }

    StyledWidget:hover {
        background: $boost;
    }
    """
```

#### 4. Handle Lifecycle Properly
```python
# Good: Clean up resources
class ResourceWidget(Widget):
    def on_mount(self):
        self.worker = self.run_worker(self.background_task)

    def on_unmount(self):
        self.worker.cancel()
```

### Anti-Patterns ❌

#### 1. Don't Manually Call Render
```python
# Bad: Manually calling render
class BadWidget(Widget):
    def update_display(self):
        self.display = self.render()  # ❌ Don't do this

# Good: Use refresh or reactive properties
class GoodWidget(Widget):
    text = reactive("Hello")

    def update_display(self):
        self.text = "Updated"  # ✅ Triggers render automatically
```

#### 2. Don't Block the Event Loop
```python
# Bad: Blocking operation
class BadWidget(Widget):
    def on_click(self):
        time.sleep(5)  # ❌ Blocks entire app

# Good: Use async/workers
class GoodWidget(Widget):
    async def on_click(self):
        await asyncio.sleep(5)  # ✅ Non-blocking
```

#### 3. Don't Ignore CSS Classes
```python
# Bad: Inline styling only
class BadWidget(Widget):
    def render(self):
        return Text("Hello", style="color: red")  # Limited

# Good: Use CSS classes for variants
class GoodWidget(Widget):
    DEFAULT_CSS = """
    GoodWidget.error { color: red; }
    GoodWidget.success { color: green; }
    """

    def set_error(self):
        self.add_class("error")
```

#### 4. Don't Recreate Child Widgets
```python
# Bad: Creating widgets in render
class BadWidget(Widget):
    def render(self):
        return Button("Click")  # ❌ Creates new button each render

# Good: Compose stable widget tree
class GoodWidget(Widget):
    def compose(self):
        yield Button("Click", id="btn")  # ✅ Created once
```

## Migration Checklist

### Pre-Migration Analysis
- [ ] Identify all Rich components to convert
- [ ] Document component dependencies
- [ ] List required features (animations, interactions, etc.)
- [ ] Determine if Textual is appropriate for use case

### Component Analysis
- [ ] Map component state to reactive properties
- [ ] Identify rendering logic to convert
- [ ] List required event handlers
- [ ] Plan CSS styling approach

### Implementation
- [ ] Create widget class structure
- [ ] Implement reactive properties
- [ ] Convert rendering logic to `render()` method
- [ ] Add CSS styling
- [ ] Implement event handlers
- [ ] Add lifecycle methods (`on_mount`, `on_unmount`)
- [ ] Handle animations with timers/intervals

### Testing
- [ ] Test basic rendering
- [ ] Verify reactive updates
- [ ] Test all event handlers
- [ ] Verify CSS styling
- [ ] Test lifecycle methods
- [ ] Performance testing
- [ ] Memory leak testing

### Integration
- [ ] Update imports in dependent code
- [ ] Migrate from `rich.live.Live` to Textual app
- [ ] Update configuration/initialization
- [ ] Test in full application context

## Troubleshooting

### Common Issues and Solutions

#### 1. Widget Not Updating
**Problem:** Changes to widget state don't trigger re-render

**Solution:** Ensure you're using reactive properties:
```python
# Wrong
self.value = 10  # Regular attribute

# Right
value = reactive(0)  # Reactive property
self.value = 10  # Now triggers update
```

#### 2. Animation Stuttering
**Problem:** Animations are choppy or inconsistent

**Solution:** Use Textual's timer system:
```python
def on_mount(self):
    # Set consistent interval
    self.set_interval(1/60, self.update_animation)
```

#### 3. CSS Not Applied
**Problem:** Styles defined in CSS not showing

**Solution:** Check CSS selector specificity:
```python
DEFAULT_CSS = """
MyWidget {  /* Less specific */
    color: blue;
}

#my-id {  /* More specific */
    color: red;
}
"""
```

#### 4. Events Not Firing
**Problem:** Click/key handlers not working

**Solution:** Ensure widget can receive focus:
```python
class MyWidget(Widget):
    can_focus = True  # Required for keyboard events
```

#### 5. Layout Issues
**Problem:** Widgets not positioning correctly

**Solution:** Use appropriate layout containers:
```python
def compose(self):
    with Vertical():  # or Horizontal(), Grid()
        yield Widget1()
        yield Widget2()
```

### Performance Optimization

#### 1. Minimize Re-renders
```python
# Use specific watchers instead of general refresh
def watch_specific_value(self, old, new):
    # Only update what changed
    self.query_one("#label").update(new)
```

#### 2. Cache Expensive Computations
```python
from functools import cached_property

class OptimizedWidget(Widget):
    @cached_property
    def expensive_calculation(self):
        return sum(range(1000000))
```

#### 3. Use Virtual Scrolling
```python
# For large lists, use DataTable or similar virtual widgets
from textual.widgets import DataTable

class LargeList(Widget):
    def compose(self):
        yield DataTable()  # Handles thousands of rows efficiently
```

## Summary

Converting Rich components to Textual widgets requires understanding the fundamental paradigm shift from direct, stateless rendering to reactive, event-driven widgets. Key considerations:

1. **State Management**: Convert to reactive properties
2. **Rendering**: Move from `__rich_console__` to `render()`
3. **Styling**: Migrate from inline styles to CSS
4. **Events**: Add interactivity with event handlers
5. **Layout**: Use Textual's modern layout system
6. **Lifecycle**: Implement proper initialization and cleanup

While the conversion requires significant changes, Textual provides a more powerful and flexible framework for building interactive terminal applications. The reactive model, combined with CSS styling and comprehensive event handling, enables rich user experiences that aren't possible with Rich alone.

### Next Steps

1. Start with simple components (labels, progress bars)
2. Gradually add interactivity (buttons, inputs)
3. Build complex compositions (forms, dashboards)
4. Optimize performance as needed
5. Consider hybrid approaches where appropriate

Remember: Rich and Textual serve different purposes. Rich excels at formatted output and simple progress indicators, while Textual shines for interactive applications. Choose the right tool for your specific use case.

# Examples

# ThothSpinner Examples Gallery

This directory contains comprehensive examples demonstrating various uses of ThothSpinner components.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Component Examples](#component-examples)
3. [Configuration Examples](#configuration-examples)
4. [Integration Examples](#integration-examples)
5. [Advanced Patterns](#advanced-patterns)

## Basic Examples

### Simple Spinner

```python
#!/usr/bin/env python3
"""Basic spinner example with default settings."""

from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live
import time

console = Console()

with Live(ThothSpinner(), console=console) as live:
    spinner = live.renderable
    spinner.start()

    # Simulate work
    time.sleep(3)

    spinner.success("Task completed!")
```

### Progress Bar with Percentage

```python
#!/usr/bin/env python3
"""Progress tracking with percentage display."""

from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live
import time

console = Console()

spinner = ThothSpinner(
    progress_format="percentage",
    message_text="Processing items"
)

with Live(spinner, console=console) as live:
    spinner.start()

    for i in range(101):
        spinner.update_progress(current=i, total=100)
        time.sleep(0.02)

    spinner.success("All items processed!")
```

### Timer with Auto Format

```python
#!/usr/bin/env python3
"""Timer that automatically adjusts format based on duration."""

from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live
import time

console = Console()

spinner = ThothSpinner(
    timer_format="auto",
    spinner_style="claude_stars",
    message_text="Running long operation"
)

with Live(spinner, console=console, refresh_per_second=10) as live:
    spinner.start()

    # Simulate long-running task
    for _ in range(70):
        time.sleep(1)

    spinner.success("Operation completed!")
```

## Component Examples

### Spinner Styles Showcase

```python
#!/usr/bin/env python3
"""Demonstrate all available spinner styles."""

from thothspinner.rich.components import SpinnerComponent
from rich.console import Console
from rich.live import Live
import time

console = Console()

styles = [
    "npm_dots",
    "claude_stars",
    "classic",
    "dots",
    "arrows",
    "circle"
]

for style in styles:
    console.print(f"\n[bold]Style: {style}[/bold]")
    spinner = SpinnerComponent(style=style, color="#FFA500")

    with Live(spinner, console=console, refresh_per_second=20) as live:
        time.sleep(3)
        spinner.success()

    time.sleep(0.5)
```

### Progress Format Styles

```python
#!/usr/bin/env python3
"""Show different progress display formats."""

from thothspinner.rich.components import ProgressComponent
from rich.console import Console
from rich.live import Live
import time

console = Console()

formats = [
    ("fraction", "3/10 format"),
    ("percentage", "30% format"),
    ("of_text", "3 of 10 format"),
    ("count_only", "Just the count"),
    ("ratio", "3:10 format")
]

for format_style, description in formats:
    console.print(f"\n[bold]{description}[/bold]")

    progress = ProgressComponent(
        current=0,
        total=10,
        format={"style": format_style},
        color="#00FF00"
    )

    with Live(progress, console=console) as live:
        for i in range(11):
            progress.set(i)
            time.sleep(0.2)
```

### Timer Formats Demonstration

```python
#!/usr/bin/env python3
"""Show different timer display formats."""

from thothspinner.rich.components import TimerComponent
from rich.console import Console
from rich.table import Table
import time

console = Console()

formats = [
    ("seconds", "Simple seconds"),
    ("seconds_decimal", "Seconds with decimal"),
    ("mm:ss", "Minutes and seconds"),
    ("hh:mm:ss", "Full time format"),
    ("milliseconds", "Millisecond precision"),
    ("auto", "Auto-adjusting format")
]

table = Table(title="Timer Formats")
table.add_column("Format", style="cyan")
table.add_column("Description", style="magenta")
table.add_column("Example", style="green")

for format_style, description in formats:
    timer = TimerComponent(format={"style": format_style})
    timer.start()
    timer._elapsed = 125.456  # Set example time
    table.add_row(format_style, description, str(timer))

console.print(table)
```

### Message Component with Shimmer

```python
#!/usr/bin/env python3
"""Demonstrate message rotation with shimmer effect."""

from thothspinner.rich.components import MessageComponent
from rich.console import Console
from rich.live import Live
import time

console = Console()

# Custom action words
custom_words = [
    "Analyzing", "Computing", "Processing",
    "Calculating", "Optimizing", "Compiling"
]

message = MessageComponent(
    action_words=custom_words,
    shimmer={
        "enabled": True,
        "width": 5,
        "light_color": "#FFFFFF",
        "direction": "left-to-right"
    },
    color="#00AAFF"
)

with Live(message, console=console, refresh_per_second=30) as live:
    for i in range(10):
        time.sleep(1)
        if i == 5:
            # Change shimmer direction mid-operation
            message.reverse_shimmer = True

    message.success()
```

## Configuration Examples

### Custom Configuration

```python
#!/usr/bin/env python3
"""Create ThothSpinner with custom configuration."""

from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live
import time

console = Console()

config = {
    "defaults": {
        "color": "#FF69B4",  # Hot pink default
        "visible": True
    },
    "elements": {
        "spinner": {
            "style": "claude_stars",
            "color": "#FFD700"  # Gold spinner
        },
        "message": {
            "text": "Initializing",
            "shimmer": {
                "enabled": True,
                "width": 4,
                "light_color": "#FFFFFF",
                "speed": 1.5
            }
        },
        "progress": {
            "format": {
                "style": "fraction",
                "zero_pad": True
            },
            "color": "#00FF00"
        },
        "timer": {
            "format": {
                "style": "mm:ss",
                "precision": 0
            }
        },
        "hint": {
            "text": "Please wait...",
            "color": "#808080"
        }
    },
    "render_order": ["spinner", "progress", "message", "timer", "hint"],
    "states": {
        "success": {
            "behavior": "indicator",
            "duration": 2.0,
            "spinner": {"icon": "✨"},
            "message": {"text": "Wonderful!"}
        },
        "error": {
            "behavior": "indicator",
            "duration": 5.0,
            "spinner": {"icon": "💥"},
            "message": {"text": "Oh no!"}
        }
    }
}

spinner = ThothSpinner.from_dict(config)

with Live(spinner, console=console) as live:
    spinner.start()

    for i in range(50):
        spinner.update_progress(current=i, total=50)
        spinner.set_message(text=f"Processing item {i+1}")
        time.sleep(0.05)

    spinner.success()
```

### State Transitions

```python
#!/usr/bin/env python3
"""Demonstrate state transitions and behaviors."""

from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live
import time

console = Console()

# Configure different behaviors for each state
spinner = ThothSpinner(
    success_duration=2.0,  # Auto-clear after 2 seconds
    error_duration=3.0     # Auto-clear after 3 seconds
)

with Live(spinner, console=console) as live:
    # Start in IN_PROGRESS state
    spinner.start()
    spinner.set_message(text="Starting process")
    time.sleep(2)

    # Simulate error
    spinner.error("Connection failed")
    time.sleep(3)  # Will auto-clear

    # Reset and try again
    spinner.reset()
    spinner.set_message(text="Retrying connection")
    time.sleep(2)

    # Success this time
    spinner.success("Connected successfully!")
    time.sleep(2)  # Will auto-clear
```

## Integration Examples

### File Processing with Progress

```python
#!/usr/bin/env python3
"""Process files with progress tracking."""

from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live
from pathlib import Path
import time

def process_file(file_path: Path) -> None:
    """Simulate file processing."""
    time.sleep(0.1)  # Simulate work

console = Console()

# Create test files for demo
test_dir = Path("/tmp/thothspinner_demo")
test_dir.mkdir(exist_ok=True)
for i in range(20):
    (test_dir / f"file_{i:02d}.txt").touch()

files = list(test_dir.glob("*.txt"))

spinner = ThothSpinner(
    progress_format="fraction",
    timer_format="seconds_decimal"
)

with Live(spinner, console=console) as live:
    spinner.start()

    for i, file in enumerate(files):
        spinner.set_message(text=f"Processing {file.name}")
        spinner.update_progress(current=i, total=len(files))
        process_file(file)

    spinner.update_progress(current=len(files), total=len(files))
    spinner.success(f"Processed {len(files)} files")

# Cleanup
import shutil
shutil.rmtree(test_dir)
```

### Download Simulation

```python
#!/usr/bin/env python3
"""Simulate file download with dynamic updates."""

from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live
import time
import random

console = Console()

def format_bytes(bytes: int) -> str:
    """Format bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024.0
    return f"{bytes:.1f}TB"

# Simulate 50MB file
total_size = 50 * 1024 * 1024  # 50MB
downloaded = 0

spinner = ThothSpinner(
    message_shimmer=True,
    progress_format="percentage",
    timer_format="auto"
)

with Live(spinner, console=console, refresh_per_second=20) as live:
    spinner.start()

    while downloaded < total_size:
        # Simulate variable download speed
        chunk_size = random.randint(100_000, 500_000)
        downloaded = min(downloaded + chunk_size, total_size)

        # Update display
        percent = (downloaded / total_size) * 100
        spinner.update_progress(current=int(percent), total=100)
        spinner.set_message(
            text=f"Downloading: {format_bytes(downloaded)}/{format_bytes(total_size)}"
        )

        # Simulate network delay
        time.sleep(0.1)

    spinner.success("Download complete!")
```

### Multi-threaded Operations

```python
#!/usr/bin/env python3
"""Demonstrate thread-safe operations with multiple workers."""

from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live
import threading
import time
import random

console = Console()

class Worker:
    def __init__(self, worker_id: int, spinner: ThothSpinner):
        self.worker_id = worker_id
        self.spinner = spinner
        self.items_processed = 0

    def process_items(self, num_items: int):
        """Process items with progress updates."""
        for i in range(num_items):
            # Simulate work
            time.sleep(random.uniform(0.05, 0.15))

            # Thread-safe update
            self.items_processed += 1
            self.spinner.set_message(
                text=f"Worker {self.worker_id}: Item {i+1}/{num_items}"
            )

# Create spinner with thread-safe configuration
spinner = ThothSpinner(
    message_text="Initializing workers",
    progress_format="fraction"
)

num_workers = 3
items_per_worker = 10
total_items = num_workers * items_per_worker

with Live(spinner, console=console) as live:
    spinner.start()

    # Create and start worker threads
    workers = []
    threads = []

    for i in range(num_workers):
        worker = Worker(i + 1, spinner)
        workers.append(worker)

        thread = threading.Thread(
            target=worker.process_items,
            args=(items_per_worker,)
        )
        threads.append(thread)
        thread.start()

    # Monitor progress
    while any(t.is_alive() for t in threads):
        total_processed = sum(w.items_processed for w in workers)
        spinner.update_progress(current=total_processed, total=total_items)
        time.sleep(0.1)

    # Wait for all threads
    for thread in threads:
        thread.join()

    spinner.success(f"All {num_workers} workers completed!")
```

## Advanced Patterns

### Error Recovery Pattern

```python
#!/usr/bin/env python3
"""Demonstrate error handling and recovery."""

from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live
import time
import random

console = Console()

def unreliable_operation():
    """Simulate an operation that might fail."""
    if random.random() < 0.3:  # 30% chance of failure
        raise ConnectionError("Network timeout")
    time.sleep(1)
    return "Success"

spinner = ThothSpinner(
    error_duration=2.0  # Show error for 2 seconds
)

max_retries = 3
retry_count = 0

with Live(spinner, console=console) as live:
    while retry_count < max_retries:
        spinner.start() if retry_count == 0 else spinner.reset()
        spinner.set_message(
            text=f"Attempt {retry_count + 1}/{max_retries}"
        )

        try:
            result = unreliable_operation()
            spinner.success(f"Operation succeeded: {result}")
            break
        except ConnectionError as e:
            retry_count += 1
            if retry_count >= max_retries:
                spinner.error(f"Failed after {max_retries} attempts: {e}")
            else:
                spinner.error(f"Attempt {retry_count} failed: {e}")
                time.sleep(2)  # Wait before retry
```

### Dynamic Component Updates

```python
#!/usr/bin/env python3
"""Show dynamic updates to components during operation."""

from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live
import time

console = Console()

spinner = ThothSpinner()

phases = [
    ("Initializing", "npm_dots", "#FF0000"),
    ("Connecting", "claude_stars", "#FFA500"),
    ("Authenticating", "classic", "#FFFF00"),
    ("Loading data", "circle", "#00FF00"),
    ("Processing", "arrows", "#00FFFF"),
    ("Finalizing", "dots", "#FF00FF")
]

with Live(spinner, console=console, refresh_per_second=20) as live:
    spinner.start()

    for phase, style, color in phases:
        # Update multiple components
        spinner.set_message(text=phase)
        spinner.set_spinner_style(style=style)
        spinner.set_hint(text=f"Phase: {phase}")

        # Update progress for this phase
        for i in range(101):
            spinner.update_progress(current=i, total=100)
            time.sleep(0.01)

        time.sleep(0.5)

    spinner.success("All phases completed!")
```

### Custom Shimmer Direction Control

```python
#!/usr/bin/env python3
"""Control shimmer direction based on events."""

from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live
import time
import random

console = Console()

class DataTransfer:
    def __init__(self, spinner: ThothSpinner):
        self.spinner = spinner
        self.total_sent = 0
        self.total_received = 0

    def send_data(self, size: int):
        """Simulate sending data."""
        self.spinner.set_shimmer_direction(direction="left-to-right")
        self.spinner.set_message(text=f"Sending {size}KB")
        self.total_sent += size
        time.sleep(0.5)

    def receive_data(self, size: int):
        """Simulate receiving data."""
        self.spinner.set_shimmer_direction(direction="right-to-left")
        self.spinner.set_message(text=f"Receiving {size}KB")
        self.total_received += size
        time.sleep(0.5)

spinner = ThothSpinner(
    message_shimmer=True,
    timer_format="seconds_decimal"
)

transfer = DataTransfer(spinner)

with Live(spinner, console=console, refresh_per_second=30) as live:
    spinner.start()

    # Simulate bidirectional data transfer
    for _ in range(10):
        if random.choice([True, False]):
            transfer.send_data(random.randint(10, 100))
        else:
            transfer.receive_data(random.randint(10, 100))

    spinner.success(
        f"Transfer complete! Sent: {transfer.total_sent}KB, "
        f"Received: {transfer.total_received}KB"
    )
```

### Composite Progress Tracking

```python
#!/usr/bin/env python3
"""Track multiple sub-tasks within a main task."""

from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live
import time

console = Console()

tasks = [
    ("Database backup", 30),
    ("File compression", 20),
    ("Network upload", 40),
    ("Verification", 10)
]

total_weight = sum(weight for _, weight in tasks)

spinner = ThothSpinner(
    progress_format="percentage",
    timer_format="mm:ss"
)

with Live(spinner, console=console) as live:
    spinner.start()

    overall_progress = 0

    for task_name, weight in tasks:
        spinner.set_message(text=task_name)
        spinner.set_hint(text=f"Step {tasks.index((task_name, weight)) + 1}/{len(tasks)}")

        # Simulate task progress
        for i in range(101):
            # Calculate weighted overall progress
            task_contribution = (weight / total_weight) * (i / 100) * 100
            current_progress = overall_progress + task_contribution

            spinner.update_progress(
                current=int(current_progress),
                total=100
            )
            time.sleep(0.01)

        overall_progress += (weight / total_weight) * 100

    spinner.success("All tasks completed successfully!")
```

## Running the Examples

All examples can be run directly:

```bash
# Run a specific example
python3 basic_spinner.py

# Or make it executable
chmod +x basic_spinner.py
./basic_spinner.py
```

## Tips and Best Practices

1. **Choose the Right Refresh Rate**: Use 10-20 Hz for smooth animations without excessive CPU usage
2. **Handle Cleanup**: Always use context managers (with statements) to ensure proper cleanup
3. **Thread Safety**: All ThothSpinner methods are thread-safe
4. **State Management**: Use appropriate state transitions (success/error/reset)
5. **Performance**: Disable shimmer effects on slow terminals if needed
6. **User Experience**: Provide meaningful messages and progress updates

## Creating Your Own Examples

When creating examples:

1. Start with a clear purpose
2. Keep examples focused on one concept
3. Include comments explaining key points
4. Handle errors gracefully
5. Clean up any resources (files, threads, etc.)

## Contributing Examples

We welcome new examples! Please ensure they:
- Are well-documented
- Follow Python best practices
- Include error handling
- Are tested and working
- Demonstrate unique use cases

Submit examples via pull request to the ThothSpinner repository.

## See Also

- [Textual Widgets API Reference](./thothspinner_textual.md) - Full Textual widget documentation
- [Rich Components API Reference](./thothspinner_rich.md) - Rich component documentation
- [Textual Examples Gallery](./examples/TEXTUAL_README.md) - Interactive Textual demo apps
