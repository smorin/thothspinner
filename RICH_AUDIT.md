# Rich Component Audit — Recommendations

## Context

Comprehensive audit of all 7 Rich components and the orchestrator, mirroring the R1-R12 refactoring done for Textual widgets. The Rich components have parallel issues: duplicate state enums, missing transition validation, hardcoded colors, inconsistent patterns, and bugs in the orchestrator.

---

## Recommendations

### R1. **[BUG]** Duplicate `ComponentState` enum — progress/timer use wrong one

**Files:** `src/thothspinner/rich/components/state.py`, `src/thothspinner/rich/components/progress.py:10`, `src/thothspinner/rich/components/timer.py:11`

**Problem:** Two incompatible `ComponentState` enums exist:
- `core/states.py`: `auto()` int values + `can_transition_to()` validation (correct)
- `rich/components/state.py`: string values, no transition validation (inferior)

`progress.py` and `timer.py` import from `rich/components/state.py` (no validation). `spinner.py` and `message.py` import from `core/states.py` (correct).

**Fix:**
1. `progress.py`: Change import to `from ...core.states import ComponentState` + `from .state import StateConfig`
2. `timer.py`: Same import split
3. `rich/components/state.py`: Remove `ComponentState` enum, keep only `StateConfig` dataclass

---

### R2. **[BUG]** Progress and Timer don't validate state transitions

**Files:** `src/thothspinner/rich/components/progress.py:107-117`, `src/thothspinner/rich/components/timer.py:176-184`

**Problem:** `success()` and `error()` directly set `self._state` without `can_transition_to()` checks. Allows invalid transitions like SUCCESS→ERROR.

**Fix:** Add guard `if not self._state.can_transition_to(...): return` before state assignment, matching `spinner.py:117-119` and `message.py:305-306`.

---

### R3. **[WRONG]** Hardcoded hex colors scattered as string literals

**Files:** `spinner.py:226,230`, `message.py:414,417`, `progress.py:42-43`, `timer.py:46-48`, `hint.py:60`, `thothspinner.py:145-147,225-226`

**Problem:** `"#00FF00"`, `"#FF0000"`, `"#D97706"`, `"#FFA500"`, `"#888888"`, `"#FFFF55"` appear as raw literals throughout.

**Fix:** Add constants to `src/thothspinner/core/color.py`:
```python
COLOR_SUCCESS = "#00FF00"
COLOR_ERROR = "#FF0000"
COLOR_DEFAULT = "#D97706"
COLOR_SHIMMER = "#FFA500"
COLOR_HINT = "#888888"
COLOR_TIMER = "#FFFF55"
```
Replace all occurrences across all component files and the orchestrator.

---

### R4. **[WRONG]** Three separate color validation implementations

**Files:** `base.py:21-29`, `hint.py:17-35`, `core/color.py:6-28`

**Problem:** `core/color.py` already has `validate_hex_color()` (shared utility), but:
- `base.py` has `_validate_hex_color()` static method (raises, less thorough)
- `hint.py` has `_is_valid_hex_color()` standalone function (returns bool)
- `spinner.py` and `message.py` have no color validation at all

**Fix:**
1. `base.py`: Remove `_validate_hex_color()`, import and use `validate_hex_color` from `core/color.py`
2. `hint.py`: Remove `_is_valid_hex_color()`, use `validate_hex_color` from `core/color.py`
3. `spinner.py`, `message.py`: Add `validate_hex_color(color)` call in `__init__`

---

### R5. **[WRONG]** `update()` should be `configure()` for consistency with Textual

**Files:** `src/thothspinner/rich/components/message.py:272`, `src/thothspinner/rich/components/hint.py:144`, `src/thothspinner/rich/thothspinner.py:623,660`

**Problem:** The Textual refactoring (R6) renamed `update()` to `configure()` to avoid `Static.update()` conflicts. Rich components should match for API consistency.

**Fix:**
1. `message.py`: Rename `update()` → `configure()`, add `update = configure` alias
2. `hint.py`: Same rename + alias
3. `thothspinner.py`: Update call sites (`message.update(...)` → `message.configure(...)`, `component.update(...)` → `component.configure(...)`)
4. Update tests to use `configure()`

---

### R6. **[BUG]** Unbounded `_render_cache` in MessageComponent

**Files:** `src/thothspinner/rich/components/message.py:222`

**Problem:** `self._render_cache: dict[tuple, Text] = {}` grows without limit. Each unique `(state, static_text)` pair adds an entry.

**Fix:** Replace with single cached value (only used for terminal states):
```python
self._cached_terminal_render: tuple[tuple, Text] | None = None
```
Check against cache key in `__rich_console__`, store single entry. Update `reset()` to set it to `None`.

---

### R7. **[BUG]** `inspect.signature()` called on every state change in hot path

**Files:** `src/thothspinner/rich/thothspinner.py:537-548,556-567`

**Problem:** `import inspect` + `inspect.signature(method)` called inside `_propagate_state()` loop for every component on every state transition. Expensive reflection in hot path.

**Fix:** Replace with try/except TypeError:
```python
try:
    method(message)
except TypeError:
    method()
```
Remove both `import inspect` statements.

---

### R8. **[WRONG]** `set_spinner_style()` recreates entire component

**Files:** `src/thothspinner/rich/thothspinner.py:628-637`

**Problem:** Creates new `SpinnerComponent(**config)` where config includes unfiltered metadata keys. Loses component state (visibility, etc.).

**Fix:** Mutate existing component instead:
```python
spinner = self._components.get("spinner")
if spinner and style in SPINNER_FRAMES:
    spinner_def = SPINNER_FRAMES[style]
    spinner.frames = spinner_def["frames"]
    spinner.interval = spinner_def["interval"]
    spinner._start_time = None
```
Import `SPINNER_FRAMES` at top of file.

---

### R9. **[MISSING]** `__rich_measure__` missing from Progress and Timer

**Files:** `src/thothspinner/rich/components/progress.py`, `src/thothspinner/rich/components/timer.py`

**Problem:** Both inherit `BaseComponent.__rich_measure__` returning `Measurement(1, max_width)` — far too wide, breaks layout.

**Fix:** Add proper `__rich_measure__` to both, following `spinner.py:238-260` pattern:
```python
def __rich_measure__(self, console, options):
    text = Text(self._format_progress())  # or _format_time()
    return Measurement.get(console, options, text)
```
Include visibility check (return `Measurement(0, 0)` when not visible, after R12).

---

### R10. **[BUG]** Auto-clear timer not cancelled on `reset()`

**Files:** `src/thothspinner/rich/thothspinner.py:475-485`

**Problem:** `success()`/`error()` create `threading.Timer` for auto-clear. `start()` cancels it, but `reset()` doesn't. Sequence `success() → reset() → success()` leaves old timer active.

**Fix:** Add to `reset()`:
```python
if self._clear_timer:
    self._clear_timer.cancel()
    self._clear_timer = None
```

---

### R11. **[WRONG]** Magic numbers scattered throughout

**Files:** `message.py`, `spinner.py`, `progress.py`, `hint.py`

**Problem:** `5` (word history), `0.5`/`3.0` (intervals), `3` (shimmer width), `100` (default total), `0.08` (spinner interval) appear as raw numbers.

**Fix:** Extract to module-level constants in each file:
- `message.py`: `WORD_HISTORY_SIZE = 5`, `DEFAULT_MIN_INTERVAL = 0.5`, `DEFAULT_MAX_INTERVAL = 3.0`, `DEFAULT_SHIMMER_WIDTH = 3`, `DEFAULT_SHIMMER_SPEED = 1.0`
- `spinner.py`: `DEFAULT_INTERVAL = 0.08`, `DEFAULT_SPEED = 1.0`, `DEFAULT_STYLE = "npm_dots"`, etc.
- `progress.py`: `DEFAULT_TOTAL = 100`
- `hint.py`: `DEFAULT_TEXT = "(esc to interrupt)"`

---

### R12. **[MISSING]** Visibility support inconsistent across components

**Files:** `src/thothspinner/rich/components/progress.py`, `src/thothspinner/rich/components/timer.py`

**Problem:**
- `HintComponent`: Proper `visible` property with getter/setter
- `SpinnerComponent`, `MessageComponent`: Plain `self.visible` attribute + visibility check in rendering
- `ProgressComponent`, `TimerComponent`: No `visible` attribute, no visibility check in `__rich_console__`

The orchestrator already sets `component.visible = default_visible` on all components (line 282), so progress/timer will error or silently ignore.

**Fix:**
1. `progress.py`: Add `self.visible = True` in `__init__`, add `if not self.visible: return` in `__rich_console__`
2. `timer.py`: Same changes
3. Both: Add visibility check in `__rich_measure__` (added in R9)

---

## Execution Order

Ordered by dependency:

| Order | Issue | Depends On | Files Changed |
|-------|-------|-----------|---------------|
| 1 | R1 | — | `progress.py`, `timer.py`, `state.py` |
| 2 | R2 | R1 | `progress.py`, `timer.py` |
| 3 | R4 | — | `base.py`, `hint.py`, `spinner.py`, `message.py` |
| 4 | R3 | R4 | `core/color.py`, all components, `thothspinner.py` |
| 5 | R11 | R3 | `message.py`, `spinner.py`, `progress.py`, `hint.py` |
| 6 | R5 | — | `message.py`, `hint.py`, `thothspinner.py`, tests |
| 7 | R6 | — | `message.py`, message tests |
| 8 | R7 | — | `thothspinner.py` |
| 9 | R8 | — | `thothspinner.py` |
| 10 | R9 | — | `progress.py`, `timer.py` |
| 11 | R12 | R9 | `progress.py`, `timer.py` |
| 12 | R10 | — | `thothspinner.py` |

## Summary by Severity

| # | Severity | Category | Summary |
|---|----------|----------|---------|
| R1 | BUG | Import | Progress/timer use wrong ComponentState (no validation) |
| R2 | BUG | State | Progress/timer allow invalid state transitions |
| R6 | BUG | Memory | Unbounded render cache in MessageComponent |
| R7 | BUG | Perf | `inspect.signature()` in hot path |
| R10 | BUG | Threading | Auto-clear timer not cancelled on reset |
| R3 | WRONG | Pattern | Hardcoded hex colors throughout |
| R4 | WRONG | DRY | Color validation duplicated 3 ways |
| R5 | WRONG | Naming | `update()` should be `configure()` |
| R8 | WRONG | Pattern | `set_spinner_style()` recreates component |
| R11 | WRONG | Pattern | Magic numbers scattered |
| R9 | MISSING | Feature | `__rich_measure__` missing from progress/timer |
| R12 | MISSING | Feature | Visibility missing from progress/timer |

## Test Updates

**Existing tests to update:**
- `tests/rich/components/test_message.py`: R5 (update→configure), R6 (cache field name)
- `tests/rich/test_hint.py`: R5 (update→configure)

**New test files needed:**
- `tests/rich/components/test_progress.py`: R2, R9, R12
- `tests/rich/components/test_timer.py`: R2, R9, R12

## Verification

After implementing all fixes:
```bash
uv run ruff check src/thothspinner/rich/ --fix
uv run ruff format src/thothspinner/rich/
uv run pytest tests/rich/ -v --no-cov    # Rich tests pass
uv run pytest tests/ -v --no-cov         # Full suite passes (no regressions)
```
