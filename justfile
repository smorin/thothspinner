# Default recipe - show help
default:
    @just --list --unsorted

# ─── Setup ────────────────────────────────────────────────────────────

# Install all dependencies
[group: 'setup']
install:
    uv sync

# Check environment dependencies
[group: 'setup']
check:
    @make check

# Install tools needed to regenerate demo.gif (macOS only)
[group: 'setup']
install-readme-animation:
    brew install vhs ttyd ffmpeg

# Clean build artifacts
[group: 'setup']
clean:
    rm -rf build/ dist/ *.egg-info
    rm -rf .pytest_cache/ .ruff_cache/
    rm -rf htmlcov/ .coverage
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ─── Quality ──────────────────────────────────────────────────────────

# Run all checks (format, lint, typecheck, security, test)
[group: 'quality']
all: format lint typecheck security test

# Format code with ruff
[group: 'quality']
format:
    uv run ruff format src/ tests/ examples/

# Lint code with ruff
[group: 'quality']
lint:
    uv run ruff check src/ tests/ examples/ --fix

# Type check with ty
[group: 'quality']
typecheck:
    uv run ty check src/

# Run bandit security linter
[group: 'quality']
security:
    uvx bandit -r src/

# ─── Testing ──────────────────────────────────────────────────────────

# Run all tests
[group: 'testing']
test:
    uv run pytest tests/ -v

# Run tests with coverage
[group: 'testing']
test-cov:
    uv run pytest tests/ -v --cov=src/thothspinner --cov-report=term-missing --cov-report=html
    @echo "Coverage report generated at htmlcov/index.html"

# Regenerate pytest-textual-snapshot snapshots
[group: 'testing']
update-snapshots:
    uv run pytest tests/ --snapshot-update

# ─── Versioning ───────────────────────────────────────────────────────

# Show current version from pyproject.toml
[group: 'versioning']
current-version:
    @grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'

# Bump patch version (1.0.0 → 1.0.1)
[group: 'versioning']
bump-patch:
    #!/usr/bin/env python3
    import re, pathlib
    f = pathlib.Path('pyproject.toml')
    c = f.read_text()
    m = re.search(r'(version = ")(\d+)\.(\d+)\.(\d+)(")', c)
    new_v = f'{m.group(2)}.{m.group(3)}.{int(m.group(4))+1}'
    f.write_text(c[:m.start()] + f'{m.group(1)}{new_v}{m.group(5)}' + c[m.end():])
    print(f'Bumped patch: {m.group(2)}.{m.group(3)}.{m.group(4)} -> {new_v}')

# Bump minor version (1.0.0 → 1.1.0)
[group: 'versioning']
bump-minor:
    #!/usr/bin/env python3
    import re, pathlib
    f = pathlib.Path('pyproject.toml')
    c = f.read_text()
    m = re.search(r'(version = ")(\d+)\.(\d+)\.(\d+)(")', c)
    new_v = f'{m.group(2)}.{int(m.group(3))+1}.0'
    f.write_text(c[:m.start()] + f'{m.group(1)}{new_v}{m.group(5)}' + c[m.end():])
    print(f'Bumped minor: {m.group(2)}.{m.group(3)}.{m.group(4)} -> {new_v}')

# Bump major version (1.0.0 → 2.0.0)
[group: 'versioning']
bump-major:
    #!/usr/bin/env python3
    import re, pathlib
    f = pathlib.Path('pyproject.toml')
    c = f.read_text()
    m = re.search(r'(version = ")(\d+)\.(\d+)\.(\d+)(")', c)
    new_v = f'{int(m.group(2))+1}.0.0'
    f.write_text(c[:m.start()] + f'{m.group(1)}{new_v}{m.group(5)}' + c[m.end():])
    print(f'Bumped major: {m.group(2)}.{m.group(3)}.{m.group(4)} -> {new_v}')

# ─── Release ──────────────────────────────────────────────────────────

# Generate CHANGELOG.md from git history (requires git-cliff)
[group: 'release']
changelog:
    uvx git-cliff -o CHANGELOG.md

# Build distribution (wheel + sdist)
[group: 'release']
build:
    uv build

# Publish to TestPyPI (requires OIDC or UV_PUBLISH_TOKEN)
[group: 'release']
publish-test:
    uv publish --index-url https://test.pypi.org/legacy/

# Publish to PyPI (requires OIDC or UV_PUBLISH_TOKEN)
[group: 'release']
publish:
    uv publish

# Tag and push a release (triggers CI publish workflow)
[group: 'release']
release version="":
    ./scripts/release.sh {{version}}

# ─── Examples: Rich ───────────────────────────────────────────────────

# Run all examples
[group: 'examples']
examples: example-hint example-spinner example-progress example-timer example-message example-message-shimmer example-message-words example-message-word-control example-message-states example-combined example-combined-message examples-thothspinner
    @echo "All examples completed!"

# Run hint example
[group: 'examples']
example-hint:
    uv run python examples/rich/hint_demo.py

# Run spinner example
[group: 'examples']
example-spinner:
    uv run python examples/rich/spinner_demo.py

# Run progress example
[group: 'examples']
example-progress:
    uv run python examples/progress_demo.py

# Run timer example
[group: 'examples']
example-timer:
    uv run python examples/timer_demo.py

# Run message example
[group: 'examples']
example-message:
    uv run python examples/message_demo.py

# Run message shimmer direction example
[group: 'examples']
example-message-shimmer:
    uv run python examples/message_shimmer_demo.py

# Run message custom words example
[group: 'examples']
example-message-words:
    uv run python examples/message_words_demo.py

# Run message word control example
[group: 'examples']
example-message-word-control:
    uv run python examples/message_word_control.py

# Run message states example
[group: 'examples']
example-message-states:
    uv run python examples/message_states_demo.py

# Run combined progress and timer example
[group: 'examples']
example-combined:
    uv run python examples/combined_demo.py

# Run combined with message example
[group: 'examples']
example-combined-message:
    uv run python examples/combined_with_message.py

# ─── Examples: Textual ────────────────────────────────────────────────

# Run all Textual examples
[group: 'examples']
examples-textual: example-textual-hint example-textual-spinner example-textual-progress example-textual-timer example-textual-message example-textual-orchestrator example-textual-reactive
    @echo "All Textual examples completed!"

# Run Textual hint widget demo
[group: 'examples']
example-textual-hint:
    uv run python examples/textual_hint_demo.py

# Run Textual spinner widget demo
[group: 'examples']
example-textual-spinner:
    uv run python examples/textual_spinner_demo.py

# Run Textual progress widget demo
[group: 'examples']
example-textual-progress:
    uv run python examples/textual_progress_demo.py

# Run Textual timer widget demo
[group: 'examples']
example-textual-timer:
    uv run python examples/textual_timer_demo.py

# Run Textual message widget demo
[group: 'examples']
example-textual-message:
    uv run python examples/textual_message_demo.py

# Run Textual orchestrator demo
[group: 'examples']
example-textual-orchestrator:
    uv run python examples/textual_orchestrator_demo.py

# Run Textual reactive patterns demo
[group: 'examples']
example-textual-reactive:
    uv run python examples/textual_reactive_demo.py

# ─── Examples: ThothSpinner ───────────────────────────────────────────

# Run all ThothSpinner examples
[group: 'examples']
examples-thothspinner: example-thothspinner-basic example-thothspinner-config example-thothspinner-states example-thothspinner-fade example-thothspinner-events example-thothspinner-full
    @echo "All ThothSpinner examples completed!"

# Run ThothSpinner basic example
[group: 'examples']
example-thothspinner-basic:
    uv run python examples/thothspinner_basic.py

# Run ThothSpinner configuration example
[group: 'examples']
example-thothspinner-config:
    uv run python examples/thothspinner_config.py

# Run ThothSpinner states example
[group: 'examples']
example-thothspinner-states:
    uv run python examples/thothspinner_states.py

# Run ThothSpinner fade-away example
[group: 'examples']
example-thothspinner-fade:
    uv run python examples/thothspinner_fade.py

# Run ThothSpinner event-triggered updates example
[group: 'examples']
example-thothspinner-events:
    uv run python examples/thothspinner_events.py

# Run ThothSpinner full-featured example
[group: 'examples']
example-thothspinner-full:
    uv run python examples/thothspinner_full.py

# ─── Docs ─────────────────────────────────────────────────────────────

# Generate demo.gif for README (requires: brew install vhs)
[group: 'docs']
demo-gif:
    vhs demo.tape

# ─── Git Hooks (lefthook) ────────────────────────────────────────────

# Install lefthook and git hooks
[group: 'git-hooks']
install-lefthook:
    @if command -v lefthook > /dev/null 2>&1; then \
        echo "lefthook is already installed"; \
    else \
        brew install lefthook; \
    fi
    lefthook install

# Update lefthook
[group: 'git-hooks']
update-lefthook:
    brew upgrade lefthook || brew install lefthook
    lefthook install

# Show lefthook version
[group: 'git-hooks']
lefthook-version:
    lefthook version

# Show lefthook help
[group: 'git-hooks']
lefthook-help:
    lefthook --help

# Open lefthook docs
[group: 'git-hooks']
lefthook-docs:
    open "https://github.com/evilmartians/lefthook"
