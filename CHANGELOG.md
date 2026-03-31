# Changelog

All notable changes to ThothSpinner are documented here.

---

## [1.0.0] — Milestone M14 (2026-03-29)

### Added
- Published to PyPI: `pip install thothspinner`
- GitHub Actions CI/CD pipeline (test, lint, typecheck, publish)
- Package metadata: classifiers, keywords, project URLs
- MIT LICENSE file

---

## [1.1.0] — Milestone M15

### Added
- **Textual ProgressWidget**: `bar` format style with configurable fill characters, width, and bracket styles
- Smooth animated transitions when progress values change (eased rather than instant jumps)

### Notes
- Bar format is Textual-only; Rich ProgressComponent remains text-only
- Fully backward-compatible with existing ProgressWidget API

---

## [0.13.0] — Milestone M13

### Added
- Textual widget documentation (`docs/thothspinner_textual.md`)
- Textual examples gallery (`docs/examples/TEXTUAL_README.md`)
- Rich-to-Textual migration guide (`docs/rich_to_textual_guide.md`)
- Reactive state patterns guide (`docs/textual_reactive_guide.md`)
- Textual troubleshooting guide (`docs/textual_troubleshooting.md`)

---

## [0.12.0] — Milestone M12

### Added
- **TextualThothSpinner**: Orchestrator widget combining all Textual components
- State management across all Textual widgets
- Configuration hierarchy for Textual apps matching Rich API

---

## [0.11.0] — Milestone M11

### Added
- **MessageWidget**: Textual message component with action word rotation
- Reactive shimmer effects with directional control
- State transitions (IN_PROGRESS → SUCCESS/ERROR)

---

## [0.10.0] — Milestone M10

### Added
- **TimerWidget**: Textual timer component with all 10 time format styles
- Reactive start/stop/pause controls
- Lifecycle-aware timer management

---

## [0.9.0] — Milestone M09

### Added
- **ProgressWidget**: Textual progress component with 5 format styles
- Reactive `current` / `total` updates
- State management with CSS classes

---

## [0.8.0] — Milestone M08

### Added
- **SpinnerWidget**: Textual spinner with all 30+ built-in styles
- Speed control (0.25x–8x), pause/resume
- Reactive state transitions

---

## [0.7.0] — Milestone M07

### Added
- **HintWidget**: Textual hint component with reactive text and icon
- Visibility control (`show()`, `hide()`, `toggle()`)
- `fade_in()` / `fade_out()` animations

---

## [0.6.0] — Milestone M06

### Added
- Rich components API reference (`docs/thothspinner_rich.md`)
- Examples gallery with 20+ runnable examples (`docs/examples/README.md`)
- Troubleshooting guide (`docs/troubleshooting.md`)
- Configuration reference (`config.md`)

---

## [0.5.0] — Milestone M05

### Added
- **ThothSpinner**: Orchestrator combining all Rich components
- State management system (IN_PROGRESS → SUCCESS/ERROR)
- `success()`, `error()` transitions with optional auto-clear
- Configuration hierarchy (kwargs and `from_dict()`)

---

## [0.4.0] — Milestone M04

### Added
- **MessageComponent**: Rotating action words with configurable interval
- Shimmer animation effect with directional control (left-to-right, right-to-left, event-triggered)
- `set_message()` for rotating message updates
- `set_message_pinned()` for non-rotating overrides

---

## [0.3.0] — Milestone M03

### Added
- **ProgressComponent**: Counter with 5 format styles (fraction, percentage, of_text, count_only, ratio)
- **TimerComponent**: Elapsed time display with 10 format styles (seconds, mm:ss, hh:mm:ss, auto, milliseconds, etc.)
- State management for both components

---

## [0.2.0] — Milestone M02

### Added
- **SpinnerComponent**: Frame-based animation with 30+ built-in styles (npm_dots, claude_stars, moon, clock, dice, etc.)
- Custom frame support
- State transformation on success/error

---

## [0.1.0] — Milestone M01

### Added
- Project foundation with `uv`, `ruff`, `ty`, `just` toolchain
- **HintComponent**: Static hint text with color support
- Core state system (`ComponentState`: IN_PROGRESS, SUCCESS, ERROR)
- Hex color validation and conversion utilities
- 90%+ test coverage baseline
