.PHONY: check help clean

help:
	@echo "Available targets:"
	@echo "  check    - Check development environment"
	@echo "  clean    - Remove build artifacts"
	@echo "  help     - Show this help message"

check:
	@echo "Checking development environment..."
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv not found. Install from: https://docs.astral.sh/uv/"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 not found"; exit 1; }
	@command -v just >/dev/null 2>&1 || { echo "❌ just not found. Install from: https://github.com/casey/just"; exit 1; }
	@echo "✅ All dependencies found"
	@python3 --version
	@uv --version
	@just --version

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete