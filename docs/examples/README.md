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
    "dots",
    "line",
    "arc",
    "pulse"
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
    ("Authenticating", "arc", "#FFFF00"),
    ("Loading data", "circle", "#00FF00"),
    ("Processing", "line", "#00FFFF"),
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