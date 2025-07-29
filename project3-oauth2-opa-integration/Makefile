.DEFAULT_GOAL := help

help:  ## Show this help message
	@echo ""
	@echo "\033[1;33mAvailable commands:\033[0m"
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install:  ## Install dependencies with Poetry
	poetry install

format:  ## Format code using Ruff (Black-compatible)
	poetry run ruff format .

lint:  ## Run static analysis with Ruff and Mypy
	poetry run ruff check .
	poetry run mypy oauth2_opa_integration

test:  ## Run tests with Pytest and show coverage
	poetry run pytest

precommit:  ## Run pre-commit hooks manually
	poetry run pre-commit run --all-files
