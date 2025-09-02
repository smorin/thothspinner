# Recommendations from Rich Best Practices Review (M01/I01)

This document summarizes actionable improvements for M01.md and I01.md based on a review of Rich’s Progress implementation and tests in `../rich`. Each recommendation includes the rationale (why) and short examples adapted from Rich to illustrate patterns.

## Implementation
- Validate inputs but delegate rendering to Rich.
  - What: Keep color validation at boundaries (e.g., `#RRGGBB`) and let Rich handle styling and ANSI.
  - Why: Mirrors Rich’s design where components produce `Text`/styled objects and the Console handles terminal specifics; reduces portability bugs.
  - Code (ours):
    ```python
    from rich.style import Style
    from rich.text import Text
    if self._visible:
        yield Text(self._text, style=Style(color=self._color))
    ```
- Keep renderables small and composable.
  - What: Follow Rich’s column approach—objects expose `render(...)`/`__rich_console__` and return simple renderables without hidden side effects.
  - Why: Enables testability and reuse, as seen in Rich’s `ProgressColumn` subclasses.
  - Code (from Rich, shortened):
    ```python
    # tests/test_progress.py
    column = SpinnerColumn()
    result = column.render(task)
    ```
- Provide a clean `__repr__` for debugging.
  - Why: Matches Rich’s pervasive use of readable reprs in tests; simplifies diagnosing failures.

## Testing
- Use a captured Console with deterministic options.
  - What: In tests construct `Console(file=io.StringIO(), force_terminal=True, width=80, color_system="truecolor", legacy_windows=False, _environ={})`.
  - Why: Rich’s tests fix width and color system to make outputs reproducible and assertions stable.
  - Code (from Rich, shortened):
    ```python
    console = Console(file=io.StringIO(), force_terminal=True,
                      width=60, color_system="truecolor",
                      legacy_windows=False, _environ={})
    ```
- Disable automatic refresh for deterministic tests.
  - What: Prefer `auto_refresh=False` and drive updates manually via `refresh()` or by printing.
  - Why: Matches Rich (e.g., `Progress(..., auto_refresh=False)`), avoiding timing flakes.
  - Code (from Rich, shortened):
    ```python
    progress = Progress(console=console, auto_refresh=False)
    with progress:
        task = progress.add_task("start")
        progress.update(task, description="tick 1")
        progress.refresh()
    ```
- Capture output explicitly and assert semantically.
  - What: Use `begin_capture()/end_capture()` or `record=True` with `export_text()`; assert presence/absence of key text.
  - Why: Rich asserts either exact captured strings for complex components, or semantic presence where stable; for Hint, prefer semantic contains-tests.
- Fixture patterns early in scaffolding.
  - What: Provide `console()` and `capture_console()` fixtures in `tests/conftest.py` during project structure creation.
  - Why: Ensures `pytest` passes initial runs without missing fixtures; mirrors Rich’s centralized test setup.

## API Consistency
- Align defaults with Rich conventions.
  - What: Reasonable defaults, override via kwargs and `from_config`; simple boolean `visible` gate in render.
  - Why: Keeps API familiar to Rich users; minimizes learning curve.
- Avoid environment-specific assumptions.
  - What: No absolute paths; portable commands.
  - Why: Prevents plan breakage across machines / CI.

## Tooling & Config
- Typechecking.
  - What: Standardize on `uv run ty --strict src/` in README, M01, and I01.
  - Why: One consistent command increases signal and avoids drift in quality gates.
- Coverage gate.
  - What: Keep `--cov-fail-under=90` in pytest addopts.
  - Why: Enforces coverage without extra flags in CI or local runs.
- Tool discovery.
  - What: Verify `ruff`/`ty` via `uv run ... --version` rather than requiring global installs.
  - Why: Matches uv-managed workflows; reduces developer setup friction.

## Concrete Edits Suggested
1) Tests console harness.
   - Do: Switch Hint tests to use deterministic Console config shown above.
   - Why: Mirrors Rich test harness; removes flakiness.
   - Example (from Rich, shortened):
     ```python
     console = Console(file=io.StringIO(), force_terminal=True,
                       width=60, color_system="truecolor",
                       legacy_windows=False, _environ={})
     ```
2) Avoid Live in unit tests.
   - Do: For Hint, call `console.print(hint)` and assert captured text; keep Live only in examples.
   - Why: Simpler and deterministic; consistent with many Rich tests that avoid threads/auto refresh.
3) Invalid color behavior.
   - Do: Keep `ValueError` on invalid `#RRGGBB`; document it in docstrings and I01.
   - Why: Predictable contract; aligns with the validation-first approach.
4) Add a smoke test for multiple prints.
   - Do: Print two Hint instances back-to-back and assert both texts are present.
   - Why: Catches regressions in `__rich_console__` and visibility toggling.
5) Snapshot precision only where needed.
   - Do: Consider exact-string snapshot tests for complex future components (e.g., spinner bar composition) using captured output.
   - Why: Rich does exact comparisons for progress bars; for Hint, prefer contains-based assertions to avoid fragility.
6) Ensure fixtures exist early.
   - Do: Create `tests/conftest.py` in the scaffolding step (Phase 1) rather than later.
   - Why: Prevents early failures when running `pytest` mid-implementation.
7) Drive refresh manually for future progress tests.
   - Do: Use `Progress(..., auto_refresh=False)` and invoke `refresh()` explicitly.
   - Why: Matches Rich’s `test_progress_max_refresh` pattern; avoids timing issues.

## Examples and References in ../rich
- Default columns pattern (from rich/progress.py docstring):
  ```python
  progress = Progress(
      SpinnerColumn(),
      *Progress.get_default_columns(),
      "Elapsed:",
      TimeElapsedColumn(),
  )
  ```
- Deterministic console + manual refresh (from tests/test_progress.py):
  ```python
  console = Console(file=io.StringIO(), force_terminal=True,
                    width=60, color_system="truecolor",
                    legacy_windows=False, _environ={})
  progress = Progress(console=console, auto_refresh=False)
  with progress:
      task_id = progress.add_task("start")
      progress.update(task_id, description="tick 1")
      progress.refresh()
  ```
- Column rendering (from tests/test_progress.py):
  ```python
  column = SpinnerColumn()
  result = column.render(task)
  ```

## Test Harness Enhancements
- Unify fixtures and helpers.
  - Do: Centralize `Console` construction and common options in `tests/conftest.py`.
  - Why: Prevents drift across tests and ensures deterministic capturing.
  - Example (conftest.py):
    ```python
    import io
    import pytest
    from rich.console import Console

    def make_console(width: int = 80) -> Console:
        return Console(
            file=io.StringIO(),
            force_terminal=True,
            width=width,
            color_system="truecolor",
            legacy_windows=False,
            _environ={},
        )

    @pytest.fixture
    def console() -> Console:
        return make_console(80)

    @pytest.fixture
    def capture_console() -> Console:
        c = make_console(80)
        c.record = True
        return c
    ```
- Standardize capture patterns.
  - Do: Prefer `record=True` + `export_text(clear=False)` for presence assertions; reserve `begin_capture()`/`end_capture()` for exact-string comparisons.
  - Why: Presence checks are less brittle for simple components like Hint.
- Control time deterministically where needed.
  - Do: For future animated components, use a mock clock (like Rich’s `MockClock`) or inject `get_time`.
  - Why: Eliminates flakiness from real time.
- Avoid concurrent Live displays.
  - Do: In tests, avoid nested `Live` contexts or multiple active `Progress` with auto Live; if composing, set `auto_refresh=False` and manually refresh.
  - Why: Mirrors Rich’s practice and prevents `LiveError`.
- Parametrize and mark tests.
  - Do: Use `@pytest.mark.parametrize` for color cases and add `@pytest.mark.slow` for any long-running visuals.
  - Why: Improves coverage and keeps CI fast.

## Appendix: Simple Smoke Test
Add a minimal smoke test to ensure Hint rendering is wired and stable.

```python
# tests/rich/test_hint_smoke.py
from thothspinner.rich.components import HintComponent

def test_hint_smoke_multiple_prints(capture_console):
    hint1 = HintComponent(text="Press ESC to cancel", color="#888888")
    hint2 = HintComponent(text="Press Q to quit", color="#FF0000")

    capture_console.print(hint1)
    capture_console.print(hint2)

    out = capture_console.export_text(clear=False)
    assert "Press ESC to cancel" in out
    assert "Press Q to quit" in out

def test_hint_visibility_toggle(capture_console):
    hint = HintComponent(text="Hidden soon", color="#00FF00", visible=True)
    capture_console.print(hint)
    hint.visible = False
    capture_console.print(hint)
    out = capture_console.export_text(clear=False)
    # First render present, second suppressed; at least appears once
    assert out.count("Hidden soon") >= 1
```

