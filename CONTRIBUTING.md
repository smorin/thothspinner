# Contributing to ThothSpinner

Thank you for your interest in contributing! This guide covers everything you need to get set up and submit changes.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [just](https://github.com/casey/just) — `brew install just` or `cargo install just`
- Python 3.11+

Verify your environment:

```bash
make check
```

## Setup

```bash
git clone https://github.com/smorin/thothspinner.git
cd thothspinner
uv sync
```

## Development Workflow

All common tasks are available via `just`:

```bash
just format      # auto-format with ruff
just lint        # lint with ruff (auto-fix)
just typecheck   # type-check with ty
just test        # run tests
just test-cov    # run tests with coverage report
just all         # format → lint → typecheck → test
```

Run `just` with no arguments to see all available commands.

## Code Style

- **Formatter**: `ruff format` (line length 100, double quotes)
- **Linter**: `ruff check` (E, W, F, I, B, UP rules)
- **Type checker**: `ty check src/`

All three must pass before a PR is merged. The CI pipeline enforces this automatically.

## Testing

Tests live in `tests/`. The project targets 97%+ coverage — new code should include tests.

```bash
just test           # run full suite
just test-cov       # run with HTML coverage report (htmlcov/index.html)
uv run pytest tests/test_specific.py  # run a single file
```

Use `pytest-asyncio` for async tests (Textual components).

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add bar format style to ProgressWidget
fix: correct timer precision at 1-hour boundary
docs: update Textual API reference
chore: bump rich to 14.2
test: add coverage for shimmer direction
```

Types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `perf`, `ci`

## Submitting a Pull Request

1. Fork the repo and create a branch from `main`
2. Make your changes and run `just all` — all checks must pass
3. Open a PR targeting `main`
4. A CI run (test matrix × 3 Python versions, lint, typecheck) will start automatically

PRs that fail CI will not be merged.

## Running Examples

```bash
just example-hint
just example-spinner
just examples-thothspinner   # all Rich examples
just examples-textual        # all Textual examples
```

## Reporting Bugs

Open an issue at [github.com/smorin/thothspinner/issues](https://github.com/smorin/thothspinner/issues). Include:
- Python version and OS
- Minimal reproducible example
- Expected vs. actual behavior

## Release Process

See [RELEASE.md](RELEASE.md) for the full release workflow (maintainers only).
