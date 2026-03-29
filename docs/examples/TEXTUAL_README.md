# ThothSpinner Textual Examples Gallery

Interactive Textual application demos showcasing all ThothSpinner widgets.

## Table of Contents

- [Individual Widget Demos](#individual-widget-demos)
- [Orchestrator Demo](#orchestrator-demo)
- [Reactive Patterns Demo](#reactive-patterns-demo)
- [Running Examples](#running-examples)

---

## Individual Widget Demos

### HintWidget Demo

Interactive demo showing text updates, icon management, visibility toggling, and fade animations.

```bash
uv run python examples/textual_hint_demo.py
```

Features demonstrated:
- Text and icon updates via reactive properties
- `show()`, `hide()`, `toggle()` visibility control
- `fade_in()` and `fade_out()` animations
- Auto-hide with `set_timer()`

### SpinnerWidget Demo

Interactive demo with style switching, speed control, and pause/resume.

```bash
uv run python examples/textual_spinner_demo.py
```

Features demonstrated:
- All 23 built-in spinner styles (`npm_dots`, `claude_stars`, `classic`, `dots`, `arc`, `line`, `pulse`, `moon`, `clock`, and more)
- `set_speed()` for 0.25x to 8x speed control
- `pause()` toggle for pause/resume
- `success()`, `error()`, and `reset()` state transitions

### ProgressWidget Demo

Side-by-side comparison of all 5 format styles with batch updates.

```bash
uv run python examples/textual_progress_demo.py
```

Features demonstrated:
- Format styles: `fraction`, `percentage`, `of_text`, `count_only`, `ratio`
- `add()` for batch increments
- `set()` for direct value setting
- `success()` and `reset()` state transitions

### TimerWidget Demo

Multiple timer formats running simultaneously with start/stop/pause controls.

```bash
uv run python examples/textual_timer_demo.py
```

Features demonstrated:
- Format styles: `auto`, `hh:mm:ss`, `milliseconds`
- `start()`, `stop()`, `pause()`, `reset()` controls
- `success()` state transition (freezes display)

### MessageWidget Demo

Shimmer effects, word rotation, and direction control.

```bash
uv run python examples/textual_message_demo.py
```

Features demonstrated:
- Shimmer animation with configurable width and speed
- `reverse_shimmer` direction toggle
- `extend_action_words()` for dynamic word list management
- `configure(text=..., trigger_new=True)` for custom text

---

## Orchestrator Demo

Full ThothSpinnerWidget workflow with progress simulation using Textual workers.

```bash
uv run python examples/textual_orchestrator_demo.py
```

Features demonstrated:
- `start()` -> `update_progress()` -> `success()` workflow
- `set_spinner_style()` runtime style change
- `set_message()` dynamic message updates
- `set_shimmer_direction()` direction control
- `error()` and `reset()` state management
- Background work via `run_worker()`

---

## Reactive Patterns Demo

Demonstrates reactive property updates and how they trigger automatic UI refreshes.

```bash
uv run python examples/textual_reactive_demo.py
```

Features demonstrated:
- Setting `color` reactively across multiple widgets
- Reactive `current` updates on ProgressWidget
- CSS class changes on state transitions (`.success`, `.error`)
- Color validation feedback

---

## Running Examples

All examples are standalone Textual applications. Run any of them with:

```bash
# Run directly
uv run python examples/textual_<name>_demo.py

# Or use just recipes
just example-textual-hint
just example-textual-spinner
just example-textual-progress
just example-textual-timer
just example-textual-message
just example-textual-orchestrator
just example-textual-reactive
```

Press `Ctrl+C` or `q` to exit any demo.

## Tips

- Run with `textual run --dev examples/textual_spinner_demo.py` for the Textual devtools console
- All widgets support CSS customization via `DEFAULT_CSS` or inline `CSS` in your app
- State transitions add CSS classes (`.success`, `.error`) for easy styling

## See Also

- [Textual API Reference](../thothspinner_textual.md) - Full widget API documentation
- [Reactive Guide](../textual_reactive_guide.md) - Deep dive into reactive patterns
- [Rich Examples](./README.md) - Rich component examples
