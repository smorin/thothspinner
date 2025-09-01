# ThothSpinner

A collection of custom spinner components for Python terminal applications, providing enhanced visual feedback for both Rich and Textual libraries.

## Overview

ThothSpinner aims to deliver sophisticated and customizable spinner components that go beyond the standard offerings in popular Python terminal UI libraries. The project focuses on creating two primary implementations:

1. **Rich Spinner Component** - An enhanced spinner for the Rich library with advanced customization options
2. **Textual Spinner Widget** - A reactive spinner widget for Textual applications with integrated state management

## Goals

### Primary Objectives
- Create visually appealing spinner animations that enhance user experience
- Provide extensive customization options for colors, styles, and animation patterns
- Ensure smooth performance with minimal CPU overhead
- Maintain compatibility with the latest versions of Rich and Textual libraries

### Key Features (Planned)
- Multiple pre-defined spinner styles and animations
- Custom animation frame sequences
- Dynamic color transitions and gradients
- Configurable animation speed and smoothness
- Text labels with dynamic updates
- Progress indication integration
- Nested spinner support for hierarchical operations
- Accessibility considerations for terminal readers

## Project Structure

```
thothspinner/
├── config.md           # Configuration specifications and design patterns
├── prd_v1.md          # Product requirements document
├── example_progress.py # Example implementation showcasing progress indicators
├── src/
│   ├── rich_spinner/   # Rich library spinner implementation
│   └── textual_spinner/ # Textual library spinner implementation
└── tests/              # Test suites for both implementations
```

## Requirements

- Python 3.8+
- Rich library (for Rich spinner component)
- Textual library (for Textual spinner widget)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/thothspinner.git
cd thothspinner

# Install dependencies (once package is set up)
pip install -e .
```

## Usage Examples

### Rich Spinner
```python
from thothspinner.rich import ThothSpinner

# Basic usage
with ThothSpinner("Processing...") as spinner:
    # Your long-running operation
    time.sleep(5)

# Advanced customization
spinner = ThothSpinner(
    text="Loading data",
    style="dots",
    color="cyan",
    speed=0.1
)
```

### Textual Spinner
```python
from textual.app import App
from thothspinner.textual import ThothSpinnerWidget

class MyApp(App):
    def compose(self):
        yield ThothSpinnerWidget(label="Loading...")
```

## Development Status

🚧 **Project Status: In Development** 🚧

This project is currently in the initial development phase. Core functionality is being implemented and APIs are subject to change.

### Roadmap
- [ ] Initial project setup and structure
- [ ] Rich spinner basic implementation
- [ ] Textual spinner basic implementation
- [ ] Custom animation patterns
- [ ] Documentation and examples
- [ ] Testing suite
- [ ] Performance optimization
- [ ] PyPI package release

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

[To be determined]

## Acknowledgments

- Inspired by the need for more customizable terminal spinners
- Built upon the excellent Rich and Textual libraries

---

*ThothSpinner - Named after Thoth, the ancient Egyptian deity of wisdom and writing, symbolizing the project's goal of providing wise and elegant visual feedback in terminal applications.*