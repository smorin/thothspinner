# ThothSpinner

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Rich](https://img.shields.io/badge/rich-14.1+-green.svg)](https://github.com/Textualize/rich)
[![Coverage](https://img.shields.io/badge/coverage-97%25+-brightgreen.svg)](htmlcov/index.html)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue.svg)](docs/thothspinner_rich.md)

A highly configurable progress indicator library for Python, built on Rich. ThothSpinner provides beautiful, composable terminal UI components including spinners, progress bars, timers, and animated messages with shimmer effects.

## ✨ Features

- 🎨 **Modular Components**: Mix and match spinner, progress, timer, message, and hint components
- 🔄 **State Management**: Built-in success/error states with automatic transitions
- ✨ **Shimmer Effects**: Eye-catching animation effects for messages
- 🎯 **Thread-Safe**: Proper locking for concurrent operations
- 🚀 **Performance Optimized**: Efficient rendering with minimal CPU usage
- 🎭 **Rich Integration**: Seamless integration with Rich Console and Live displays

## 📚 Documentation

- **[API Reference](docs/thothspinner_rich.md)** - Complete API documentation for all components
- **[Examples Gallery](docs/examples/README.md)** - Runnable examples for common use cases
- **[Troubleshooting Guide](docs/troubleshooting.md)** - Solutions to common issues

## 🚀 Quick Start

```python
from thothspinner import ThothSpinner
from rich.console import Console
from rich.live import Live
import time

console = Console()

# Simple usage with all components
with Live(ThothSpinner(), console=console) as live:
    spinner = live.renderable
    spinner.start()
    
    # Simulate work with progress
    for i in range(100):
        spinner.update_progress(current=i, total=100)
        time.sleep(0.05)
    
    spinner.success("Task completed!")
```

## 📦 Installation

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- [just](https://github.com/casey/just) command runner (optional)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/thothspinner.git
cd thothspinner

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### Install from PyPI (Coming Soon)

```bash
# Will be available after v1.0.0 release
pip install thothspinner
```

## 🎯 Available Components

### Core Components

- **SpinnerComponent**: Animated spinners with multiple styles (npm_dots, claude_stars, etc.)
- **ProgressComponent**: Progress counters with various formats (percentage, fraction, etc.)
- **TimerComponent**: Elapsed time display with flexible formatting
- **MessageComponent**: Rotating action words with shimmer effects
- **HintComponent**: Static hint text for instructions
- **ThothSpinner**: Orchestrator that combines all components

### Example Usage

```python
from thothspinner import ThothSpinner
from thothspinner.rich.components import SpinnerComponent, ProgressComponent

# Individual components
spinner = SpinnerComponent(style="claude_stars", color="#FFA500")
progress = ProgressComponent(format={"style": "percentage"}, color="#00FF00")

# Or use the orchestrator for everything
spinner = ThothSpinner(
    spinner_style="npm_dots",
    message_text="Processing data",  # initial rotating message text
    message_shimmer=True,
    progress_format="percentage",
    timer_format="auto",
    hint_text="(esc to cancel)"
)
```

`set_message()` updates the current rotating message text. Use
`set_message_pinned()` only when you explicitly want a non-rotating message.

### Configuration

ThothSpinner supports both kwargs and dictionary configuration:

```python
# Using kwargs
spinner = ThothSpinner(
    spinner_style="claude_stars",
    message_shimmer=True,
    success_duration=2.0  # Auto-clear after 2 seconds
)

# Using configuration dictionary
config = {
    "defaults": {"color": "#D97706"},
    "elements": {
        "spinner": {"style": "npm_dots"},
        "message": {"shimmer": {"enabled": True, "width": 3}},
        "progress": {"format": {"style": "percentage"}}
    },
    "states": {
        "success": {
            "spinner": {"icon": "✓", "color": "#00FF00"},
            "message": {"text": "Complete!"}
        }
    }
}
spinner = ThothSpinner.from_dict(config)
```

## 🛠️ Development

### Project Structure

```
thothspinner/
├── src/thothspinner/       # Source code
│   ├── rich/               # Rich-based components
│   │   ├── components/     # Individual components
│   │   └── thothspinner.py # Main orchestrator
│   └── textual/            # Future Textual widgets
├── tests/                  # Test suite (97%+ coverage)
├── docs/                   # Documentation
│   ├── thothspinner_rich.md    # API reference
│   ├── examples/           # Example scripts
│   └── troubleshooting.md # Troubleshooting guide
├── examples/               # Demo scripts
├── justfile                # Task automation
└── pyproject.toml          # Project configuration
```

### Development Commands

```bash
# Format code
just format

# Lint code
just lint

# Type check
just typecheck

# Run tests with coverage
just test-cov

# Run all checks
just all

# Clean build artifacts
just clean
```

### Testing

The project maintains 97%+ test coverage:

```bash
# Run tests
just test

# Run tests with coverage report
just test-cov
# Coverage report generated at htmlcov/index.html

# Run specific test file
just test tests/rich/test_spinner.py
```

## 📖 Examples

### Basic Progress Bar

```python
from thothspinner import ThothSpinner
from rich.live import Live

with Live(ThothSpinner()) as live:
    spinner = live.renderable
    spinner.start()
    
    for i in range(100):
        spinner.update_progress(current=i, total=100)
        time.sleep(0.05)
    
    spinner.success()
```

### File Processing

```python
from pathlib import Path

files = list(Path(".").glob("*.py"))
spinner = ThothSpinner(progress_format="fraction")

with Live(spinner) as live:
    spinner.start()
    
    for i, file in enumerate(files):
        spinner.set_message(text=f"Processing {file.name}")  # rotating message update
        spinner.update_progress(current=i, total=len(files))
        process_file(file)
    
    spinner.success(f"Processed {len(files)} files")
```

### Error Handling

```python
with Live(ThothSpinner()) as live:
    spinner = live.renderable
    spinner.start()
    
    try:
        risky_operation()
        spinner.success("Operation successful")
    except Exception as e:
        spinner.error(f"Operation failed: {e}")
```

More examples in the [Examples Gallery](docs/examples/README.md).

## 🗺️ Roadmap

### Completed Milestones

✅ **M01-M05: Core Rich Components** (v0.5.0)
- All Rich components implemented (Spinner, Progress, Timer, Message, Hint)
- ThothSpinner orchestrator with state management
- 97%+ test coverage across all components
- Thread-safe operations with proper locking

### Current Status

📝 **M06: Documentation** (v0.6.0) - In Progress
- Comprehensive API reference
- Examples gallery with 20+ examples
- Troubleshooting guide
- Performance optimization guide

### Upcoming

- **M07-M12: Textual Components** (v0.7.0 - v0.12.0)
  - Textual-native widgets with feature parity
  - Reactive state management
  - Integration with Textual apps

- **M13: Textual Documentation** (v0.13.0)
  - Textual-specific documentation
  - Integration guides

- **M14: Publishing** (v1.0.0)
  - PyPI package publication
  - GitHub Actions CI/CD
  - Release automation

## 🤝 Contributing

Contributions are welcome! Please:

1. Check the [MILESTONES.md](MILESTONES.md) for current tasks
2. Follow the established code patterns
3. Maintain test coverage above 90%
4. Use the development toolchain (just commands)
5. Write tests for new features
6. Update documentation as needed

For milestone-specific work, reference tasks in the milestone documents (M01.md, M02.md, etc.).

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on the excellent [Rich](https://github.com/Textualize/rich) and [Textual](https://github.com/Textualize/textual) libraries by Will McGugan
- Inspired by various terminal UI libraries including ora, cli-spinners, and progress
- Name inspired by Thoth, ancient Egyptian deity of wisdom and writing
- Development patterns influenced by Rich's battle-tested implementation

## 💬 Support

For issues, questions, or suggestions:

- 📝 [Open an issue](https://github.com/yourusername/thothspinner/issues) on GitHub
- 📚 Check the [Documentation](docs/thothspinner_rich.md)
- 🔍 Review the [Troubleshooting Guide](docs/troubleshooting.md)
- 📧 Contact the maintainers

---

**Current Version:** 0.5.0 | **Python:** 3.11+ | **Coverage:** 97%+ | **[Full Documentation](docs/thothspinner_rich.md)**
