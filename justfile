# Default recipe - show help
default:
    @just --list

# Install all dependencies
install:
    uv sync

# Build distribution (wheel + sdist)
build:
    uv build

# Publish to TestPyPI (requires OIDC or UV_PUBLISH_TOKEN)
publish-test:
    uv publish --index-url https://test.pypi.org/legacy/

# Publish to PyPI (requires OIDC or UV_PUBLISH_TOKEN)
publish:
    uv publish

# Tag and push a release (triggers CI publish workflow)
release version:
    just clean
    just build
    git tag v{{version}}
    git push origin v{{version}}

# Format code with ruff
format:
    uv run ruff format src/ tests/ examples/

# Lint code with ruff
lint:
    uv run ruff check src/ tests/ examples/ --fix

# Type check with ty
typecheck:
    uv run ty check src/

# Run all tests
test:
    uv run pytest tests/ -v

# Run tests with coverage
test-cov:
    uv run pytest tests/ -v --cov=src/thothspinner --cov-report=term-missing --cov-report=html
    @echo "Coverage report generated at htmlcov/index.html"

# Run hint example
example-hint:
    uv run python examples/rich/hint_demo.py

# Run Textual hint widget demo
example-textual-hint:
    uv run python examples/textual_hint_demo.py

# Run Textual spinner widget demo
example-textual-spinner:
    uv run python examples/textual_spinner_demo.py

# Run Textual progress widget demo
example-textual-progress:
    uv run python examples/textual_progress_demo.py

# Run Textual timer widget demo
example-textual-timer:
    uv run python examples/textual_timer_demo.py

# Run Textual message widget demo
example-textual-message:
    uv run python examples/textual_message_demo.py

# Run Textual orchestrator demo
example-textual-orchestrator:
    uv run python examples/textual_orchestrator_demo.py

# Run Textual reactive patterns demo
example-textual-reactive:
    uv run python examples/textual_reactive_demo.py

# Run all Textual examples
examples-textual: example-textual-hint example-textual-spinner example-textual-progress example-textual-timer example-textual-message example-textual-orchestrator example-textual-reactive
    @echo "All Textual examples completed!"

# Run spinner example
example-spinner:
    uv run python examples/rich/spinner_demo.py

# Run progress example
example-progress:
    uv run python examples/progress_demo.py

# Run timer example
example-timer:
    uv run python examples/timer_demo.py

# Run message example
example-message:
    uv run python examples/message_demo.py

# Run message shimmer direction example
example-message-shimmer:
    uv run python examples/message_shimmer_demo.py

# Run message custom words example
example-message-words:
    uv run python examples/message_words_demo.py

# Run message word control example
example-message-word-control:
    uv run python examples/message_word_control.py

# Run message states example
example-message-states:
    uv run python examples/message_states_demo.py

# Run combined progress and timer example
example-combined:
    uv run python examples/combined_demo.py

# Run combined with message example
example-combined-message:
    uv run python examples/combined_with_message.py

# Run ThothSpinner basic example
example-thothspinner-basic:
    uv run python examples/thothspinner_basic.py

# Run ThothSpinner configuration example
example-thothspinner-config:
    uv run python examples/thothspinner_config.py

# Run ThothSpinner states example
example-thothspinner-states:
    uv run python examples/thothspinner_states.py

# Run ThothSpinner fade-away example
example-thothspinner-fade:
    uv run python examples/thothspinner_fade.py

# Run ThothSpinner event-triggered updates example
example-thothspinner-events:
    uv run python examples/thothspinner_events.py

# Run ThothSpinner full-featured example
example-thothspinner-full:
    uv run python examples/thothspinner_full.py

# Run all ThothSpinner examples
examples-thothspinner: example-thothspinner-basic example-thothspinner-config example-thothspinner-states example-thothspinner-fade example-thothspinner-events example-thothspinner-full
    @echo "All ThothSpinner examples completed!"

# Run all examples
examples: example-hint example-spinner example-progress example-timer example-message example-message-shimmer example-message-words example-message-word-control example-message-states example-combined example-combined-message examples-thothspinner
    @echo "All examples completed!"

# Run all checks (format, lint, typecheck, test)
all: format lint typecheck test

# Clean build artifacts
clean:
    rm -rf build/ dist/ *.egg-info
    rm -rf .pytest_cache/ .ruff_cache/
    rm -rf htmlcov/ .coverage
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Check environment dependencies
check:
    @make check

# Install lefthook and git hooks
install-lefthook:
    @if command -v lefthook > /dev/null 2>&1; then \
        echo "lefthook is already installed"; \
    else \
        brew install lefthook; \
    fi
    lefthook install

# Show lefthook help
lefthook-help:
    lefthook --help

# Open lefthook docs
lefthook-docs:
    open "https://github.com/evilmartians/lefthook"

# Show lefthook version
lefthook-version:
    lefthook version

# Update lefthook
update-lefthook:
    brew upgrade lefthook || brew install lefthook
    lefthook install