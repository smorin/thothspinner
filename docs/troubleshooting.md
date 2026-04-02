# ThothSpinner Troubleshooting Guide

This guide helps resolve common issues when using ThothSpinner with Rich.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Display Problems](#display-problems)
3. [Performance Issues](#performance-issues)
4. [Terminal Compatibility](#terminal-compatibility)
5. [State Management Issues](#state-management-issues)
6. [Thread Safety](#thread-safety)
7. [Configuration Problems](#configuration-problems)
8. [Memory Management](#memory-management)
9. [Integration Issues](#integration-issues)
10. [Common Error Messages](#common-error-messages)

## Installation Issues

### Problem: ImportError when importing ThothSpinner

**Symptom:**
```python
ImportError: cannot import name 'ThothSpinner' from 'thothspinner'
```

**Solution:**
```bash
# Ensure ThothSpinner is installed
uv add thothspinner

# Or with pip
pip install thothspinner

# Verify installation
python -c "import thothspinner; print(thothspinner.__version__)"
```

### Problem: Rich dependency not found

**Symptom:**
```python
ModuleNotFoundError: No module named 'rich'
```

**Solution:**
```bash
# Rich should be installed automatically, but if not:
uv add rich>=13.0.0

# Verify Rich installation
python -c "import rich; print(rich.__version__)"
```

## Display Problems

### Problem: No output visible

**Symptom:**
Components don't appear in terminal.

**Diagnosis & Solution:**
```python
from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live

console = Console()

# ❌ Wrong: Forgetting to use Live
spinner = ThothSpinner()
spinner.start()  # Nothing visible

# ✅ Correct: Use with Live context
with Live(ThothSpinner(), console=console) as live:
    spinner = live.renderable
    spinner.start()  # Now visible
```

### Problem: Flickering or jumpy animation

**Symptom:**
Animation appears to stutter or jump.

**Solution:**
```python
# Adjust refresh rate (default is often too high)
with Live(spinner, console=console, refresh_per_second=10) as live:
    # 10 Hz is usually smooth enough
    pass

# For very smooth animation
with Live(spinner, console=console, refresh_per_second=20) as live:
    # 20 Hz for smooth shimmer effects
    pass
```

### Problem: Components overlapping or misaligned

**Symptom:**
Text appears garbled or overlapping.

**Solution:**
```python
# Ensure proper terminal width
console = Console(width=120)  # Set explicit width

# Or check terminal capabilities
if console.is_terminal:
    print(f"Terminal width: {console.width}")
    print(f"Terminal height: {console.height}")

# Use vertical layout if space is limited
config = {
    "layout": "vertical"  # Stack components vertically
}
spinner = ThothSpinner.from_dict(config)
```

## Performance Issues

### Problem: High CPU usage

**Symptom:**
CPU usage above 10% for simple spinner.

**Diagnosis:**
```python
import psutil
import os

# Monitor CPU usage
process = psutil.Process(os.getpid())
print(f"CPU usage: {process.cpu_percent()}%")
```

**Solutions:**

1. **Reduce refresh rate:**
```python
# Lower refresh rate for less CPU usage
with Live(spinner, refresh_per_second=4) as live:
    # 4 Hz is enough for simple progress
    pass
```

2. **Disable shimmer effects:**
```python
spinner = ThothSpinner(
    message_shimmer=False  # Disable CPU-intensive shimmer
)
```

3. **Use fewer components:**
```python
config = {
    "elements": {
        "spinner": {"visible": True},
        "progress": {"visible": True},
        # Disable unused components
        "timer": {"visible": False},
        "message": {"visible": False},
        "hint": {"visible": False}
    }
}
```

### Problem: Slow updates

**Symptom:**
Progress updates lag behind actual progress.

**Solution:**
```python
# Batch updates instead of updating every iteration
with Live(spinner, refresh_per_second=10) as live:
    spinner.start()

    # ❌ Wrong: Update on every iteration
    for i in range(10000):
        spinner.update_progress(current=i, total=10000)
        do_work()

    # ✅ Better: Update every N iterations
    for i in range(10000):
        if i % 100 == 0:  # Update every 100 items
            spinner.update_progress(current=i, total=10000)
        do_work()
```

## Terminal Compatibility

### Problem: Colors not displaying correctly

**Symptom:**
ANSI codes visible or colors missing.

**Diagnosis:**
```python
from rich.console import Console

console = Console()
print(f"Color system: {console.color_system}")
print(f"Terminal support: {console.is_terminal}")
print(f"Supports Unicode: {console.is_unicode_safe}")
```

**Solutions:**

1. **Force color system:**
```python
# Force specific color system
console = Console(color_system="256")  # or "truecolor", "standard", "auto"
```

2. **Disable colors entirely:**
```python
console = Console(color_system=None)
```

3. **Check terminal environment:**
```bash
# Set TERM environment variable
export TERM=xterm-256color

# For Windows Terminal
export COLORTERM=truecolor
```

### Problem: Unicode characters not displaying

**Symptom:**
Spinner shows boxes or question marks.

**Solution:**
```python
# Use ASCII-safe spinner
from thothspinner.rich.components import SpinnerComponent

# Create custom ASCII frames
ascii_spinner = SpinnerComponent(
    frames=["-", "\\", "|", "/"],
    interval=0.1
)

# Or check Unicode support
if not console.is_unicode_safe:
    # Fall back to ASCII
    config = {
        "elements": {
            "spinner": {"frames": ["-", "\\", "|", "/"]}
        }
    }
```

### Problem: Wrong terminal dimensions

**Symptom:**
Components wrap unexpectedly.

**Solution:**
```python
import shutil

# Get actual terminal size
columns, rows = shutil.get_terminal_size()
console = Console(width=columns, height=rows)

# Or let Rich auto-detect
console = Console()  # Auto-detects size
```

## State Management Issues

### Problem: Invalid state transition error

**Symptom:**
```python
ValueError: Invalid state transition from SUCCESS to ERROR
```

**Solution:**
```python
# ❌ Wrong: Direct transition between terminal states
spinner.success()
spinner.error()  # Raises error

# ✅ Correct: Reset first
spinner.success()
spinner.reset()  # Return to IN_PROGRESS
spinner.error()  # Now valid
```

### Problem: State not updating visually

**Symptom:**
Called `success()` but display doesn't change.

**Solution:**
```python
# Ensure you're inside Live context
with Live(spinner, console=console) as live:
    spinner.start()
    # ... work ...
    spinner.success()  # Updates immediately

    # Keep alive to see the success state
    time.sleep(2)  # Show success for 2 seconds
```

## Thread Safety

### Problem: Garbled output with multiple threads

**Symptom:**
Text appears mixed up when updating from threads.

**Solution:**
```python
import threading
from thothspinner import ThothSpinner

# ThothSpinner is thread-safe, but ensure proper usage
spinner = ThothSpinner()

def worker(worker_id):
    # ✅ Thread-safe updates
    spinner.set_message(text=f"Worker {worker_id}")
    spinner.update_progress(current=worker_id, total=10)

# Create threads
threads = [
    threading.Thread(target=worker, args=(i,))
    for i in range(5)
]

with Live(spinner) as live:
    spinner.start()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
```

### Problem: Deadlock when updating from callbacks

**Symptom:**
Application freezes when updating spinner from event callbacks.

**Solution:**
```python
import threading

# Use queue for thread-safe communication
from queue import Queue

update_queue = Queue()

def update_worker():
    """Dedicated thread for spinner updates."""
    while True:
        update = update_queue.get()
        if update is None:
            break

        action, args = update
        if action == "progress":
            spinner.update_progress(**args)
        elif action == "message":
            spinner.set_message(**args)

# Start update thread
update_thread = threading.Thread(target=update_worker)
update_thread.start()

# From callbacks, queue updates
def on_data_received(size):
    update_queue.put(("message", {"text": f"Received {size} bytes"}))
```

## Configuration Problems

### Problem: Configuration not applying

**Symptom:**
Settings in config dict ignored.

**Solution:**
```python
# ❌ Wrong: Mixing config dict and kwargs incorrectly
spinner = ThothSpinner(
    config={"elements": {"spinner": {"color": "#FF0000"}}},
    spinner_style="dots"  # This might override config
)

# ✅ Correct: Use from_dict for full config control
config = {
    "elements": {
        "spinner": {
            "style": "dots",
            "color": "#FF0000"
        }
    }
}
spinner = ThothSpinner.from_dict(config)

# Or use kwargs only
spinner = ThothSpinner(
    spinner_style="dots",
    spinner_color="#FF0000"  # Note: this param doesn't exist
)
```

### Problem: Invalid component type error

**Symptom:**
```python
KeyError: Invalid component type: 'loading'
```

**Solution:**
```python
# Valid component types
valid_types = ["spinner", "message", "progress", "timer", "hint"]

# ❌ Wrong: Using invalid type
config = {
    "elements": {
        "loading": {}  # Invalid type
    }
}

# ✅ Correct: Use valid types
config = {
    "elements": {
        "spinner": {},  # Valid
        "message": {}   # Valid
    }
}
```

## Memory Management

### Problem: Memory leak during long operations

**Symptom:**
Memory usage grows continuously.

**Diagnosis:**
```python
import tracemalloc
import gc

# Start tracing
tracemalloc.start()

# Your code here
with Live(spinner) as live:
    # ... long operation ...
    pass

# Check memory
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory: {peak / 1024 / 1024:.1f} MB")
tracemalloc.stop()

# Force garbage collection
gc.collect()
```

**Solutions:**

1. **Clear references:**
```python
# Ensure cleanup
spinner = ThothSpinner()
try:
    with Live(spinner) as live:
        # Work
        pass
finally:
    spinner.clear()
    del spinner  # Explicit cleanup
```

2. **Limit history:**
```python
# For MessageComponent with many words
config = {
    "elements": {
        "message": {
            "action_words": ["Word1", "Word2"],  # Limit word count
            "interval": {"min": 1.0, "max": 2.0}  # Slower rotation
        }
    }
}
```

## Integration Issues

### Problem: Conflicts with logging output

**Symptom:**
Log messages interfere with spinner display.

**Solution:**
```python
import logging
from rich.logging import RichHandler

# Use Rich's logging handler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, show_time=False)]
)

# Logs will now work with Live display
with Live(spinner, console=console) as live:
    spinner.start()
    logging.info("This won't break the display")
```

### Problem: Input() breaks the display

**Symptom:**
Calling `input()` corrupts the spinner.

**Solution:**
```python
# Temporarily stop Live display for input
with Live(spinner, console=console) as live:
    spinner.start()

    # Stop for input
    live.stop()
    user_input = input("Enter value: ")
    live.start()  # Resume

    spinner.set_message(text=f"Processing: {user_input}")
```

## Common Error Messages

### "No active Live instance"

**Cause:** Trying to update spinner outside Live context.

**Fix:**
```python
# Always use within Live context
with Live(spinner) as live:
    # All updates here
    spinner.start()
```

### "Component not found"

**Cause:** Accessing non-existent component.

**Fix:**
```python
try:
    component = spinner.get_component("spinner")
except KeyError:
    print("Component doesn't exist")
```

### "Thread lock timeout"

**Cause:** Deadlock in multi-threaded code.

**Fix:**
```python
# Use timeouts for debugging
import threading

spinner._lock = threading.RLock()
if spinner._lock.acquire(timeout=5):
    try:
        # Operations
        pass
    finally:
        spinner._lock.release()
else:
    print("Lock timeout - possible deadlock")
```

## Getting Help

If you encounter issues not covered here:

1. **Check the examples**: Review [examples directory](./examples/README.md)
2. **Read API docs**: See [API reference](./thothspinner_rich.md)
3. **Enable debug mode**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```
4. **Report issues**: [GitHub Issues](https://github.com/yourusername/thothspinner/issues)
5. **Minimal reproduction**: Create a minimal example that reproduces the issue

## Debug Utilities

### Performance Profiling

```python
import cProfile
import pstats

# Profile your code
profiler = cProfile.Profile()
profiler.enable()

# Your ThothSpinner code
with Live(spinner) as live:
    # Operations
    pass

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

### Visual Debugging

```python
from rich import inspect

# Inspect spinner configuration
inspect(spinner.config, methods=False)

# Check component states
for name in ["spinner", "message", "progress", "timer", "hint"]:
    component = spinner.get_component(name)
    print(f"{name}: visible={component.visible}, state={component.state}")
```

### Terminal Capabilities Check

```python
from rich.console import Console

console = Console()

# Full diagnostic
print(f"Terminal: {console.is_terminal}")
print(f"TTY: {console.is_tty}")
print(f"Color system: {console.color_system}")
print(f"Unicode safe: {console.is_unicode_safe}")
print(f"Size: {console.width}x{console.height}")
print(f"Encoding: {console.encoding}")
```

## Best Practices Summary

1. **Always use Live context** for display
2. **Choose appropriate refresh rates** (10-20 Hz)
3. **Handle state transitions properly** (reset between terminal states)
4. **Use thread-safe methods** for concurrent updates
5. **Profile performance** for long-running operations
6. **Test on target terminals** for compatibility
7. **Clean up resources** in finally blocks
8. **Batch updates** for better performance
9. **Use configuration hierarchy** for flexibility
10. **Monitor memory usage** in long-running applications
