# Changelog

## [Unreleased]

### Bug Fixes

- Use --publish-url instead of --index for TestPyPI
- Run uv lock after version bump

### Features

- Add commit hint to bump recipes

### Miscellaneous

- Update uv.lock for v1.2.2
- Bump version to 1.2.3
- Update uv.lock for v1.2.3
- Bump version to 1.2.4

## [1.2.1] - 2026-04-13

### Bug Fixes

- Auto-commit changelog and push main before tagging
- Auto-commit uv.lock before clean tree check

### Miscellaneous

- Update changelog for v1.2.0 release
- Update pyproject.toml for release
- Update uv.lock for v1.2.1
- Update CHANGELOG.md for v1.2.1

## [1.2.0] - 2026-04-13

### Bug Fixes

- Repair publish flag and skip snapshot tests on non-3.11 Python
- Upgrade Pygments to 2.20.0 for ReDoS vulnerability
- Add missing setup-uv and skip snapshot tests on macOS
- Suppress bandit B311 for UI animation randomness

### Documentation

- Reformat changelog to conventional-changelog style

### Features

- Add actions language scanning and use build-mode in CodeQL
- Add codespell, bandit, and editorconfig-checker to CI
- Harden release recipe with pre-flight checks
- Add uv.lock sync check to release script

### Miscellaneous

- Update lock file

## [1.1.0] - 2026-04-01

### Bug Fixes

- Replace Static.update() with HintWidget.configure() in textual hint demo
- Show Tab/Shift+Tab hint as label instead of Footer binding
- Fix layout, message pin, and spinner refresh bugs
- Add vertical layout mode and guard success race
- Horizontal layout, cycle styles, toggle shimmer, add spacing
- Show feedback when Apply Color input is invalid/empty
- Reset widgets before success/error to allow re-triggering
- Fix right-to-left fade bug and slow down demo animations
- Add __str__ to TimerComponent for f-string formatting
- Replace invalid spinner style names 'line' and 'arc'
- Resolve all pre-existing E501 and test failures
- Resolve ty non-subscriptable error in SpinnerWidget
- Improve MessageComponent, ThothSpinner visibility, and state method handling
- Resolve KeyError on partial render_order and flaky animation test
- Validate orchestrator config at construction
- Use uv run in demo.tape for reliable CLI invocation
- Add ttyd and ffmpeg as vhs dependencies in install recipe
- Install uv before running uvx in yamllint job
- Repair browse TUI layout, preview rendering, and navigation UX

### CI/CD

- Update action versions and add yamllint/actionlint jobs

### Documentation

- Fix invalid spinner styles, add layout param and TimerComponent.__str__
- Update README to reflect recent DX and CI improvements
- Add CLI tools and demo GIF generation steps to README
- Add demo.gif for README
- Update demo.gif
- Expand Quick Start with install, CLI, and example commands
- Move images to docs/images/ and add style browser screenshot

### Features

- Add Footer with Tab/Ctrl+Q navigation hints to all textual demos
- Add Tab and Shift+Tab navigation hints to footer in all textual demos
- Add arc, line, and pulse spinner styles
- Add 7 new spinner styles (pipe, vertical_pulse, quarter, hamburger, moon, clock, earth)
- Add 4 rare spinner styles (dice, snowflake, zodiac, rune)
- Add matrix spinner style
- Add 9 new spinner styles (orbit, diamond, toggle, cursor, suits, notes, heartbeat, weather, rings)
- Add iris, moon_tide, collapse, shield_break styles
- Add bar format and animation smoothing to ProgressWidget (v1.1.0)
- Add configure_state(), per-state color overrides, and ThothSpinner improvements
- Split rotating and pinned message APIs
- Add non-developer experience improvements
- Enrich demo GIF with multi-phase full-component demo and style sampler
- Organize justfile recipes into logical groups

### M08

- Implement Textual SpinnerWidget with animation support

### M09

- Implement Textual ProgressWidget with all Rich format styles

### M10

- Implement Textual TimerWidget with all Rich format styles

### M11

- Implement Textual MessageWidget with shimmer effects

### M12

- Implement Textual ThothSpinnerWidget orchestrator

### Miscellaneous

- Add lefthook git hooks and clean up planning artifacts
- Update uv.lock for v1.0.0 version bump
- Apply best-practice improvements from rich/textual comparison
- Add DX improvements for versioning, changelog, security, and onboarding
- Add vhs to install recipe
- Move vhs/ttyd/ffmpeg to install-readme-animation recipe
- Bump github/codeql-action from 3 to 4
- Bump version to 1.1.0

## [0.1] - 2025-09-01


