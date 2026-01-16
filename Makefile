.PHONY: help install test lint format check clean typecheck pre-commit

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync
	uv run pre-commit install

test: ## Run tests
	uv run pytest -q

test-v: ## Run tests with verbose output
	uv run pytest -v

test-cov: ## Run tests with coverage report
	uv run pytest --cov=englog --cov-report=term-missing

lint: ## Run linter
	uv run ruff check src/ tests/

format: ## Format code
	uv run ruff format src/ tests/

fix: ## Auto-fix lint issues
	uv run ruff check --fix src/ tests/

typecheck: ## Run type checker
	uv run ty check src/

pre-commit: ## Run pre-commit on all files
	uv run pre-commit run --all-files

check: lint typecheck test ## Run lint, typecheck, and tests

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .ruff_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
