# Default recipe - show help
default:
    @just --list

# Install all dependencies
install:
    uv sync

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