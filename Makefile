# Makefile for Zimbot project

# Variables
PYTHON_FILES := $(shell find src tests -name "*.py")

# Poetry commands
.PHONY: install update clean format lint test coverage security docs serve-docs

install:
	@echo "Installing dependencies..."
	poetry install --no-root

update:
	@echo "Updating dependencies..."
	poetry update

# Development commands
format:
	@echo "Formatting code..."
	poetry run black $(PYTHON_FILES)
	poetry run isort $(PYTHON_FILES)

lint-soft:
	@echo "Running soft linting (warnings only)..."
	-poetry run flake8 $(PYTHON_FILES) --exit-zero
	-poetry run pylint src --exit-zero
	-poetry run mypy src --ignore-missing-imports

lint:
	@echo "Running strict linting..."
	poetry run flake8 $(PYTHON_FILES)
	poetry run pylint src
	poetry run mypy src

test:
	@echo "Running tests..."
	poetry run pytest

coverage:
	@echo "Generating coverage reports..."
	poetry run pytest --cov=zimbot --cov-report=xml --cov-report=html

security:
	@echo "Running security checks..."
	poetry run safety check
	poetry run pip-audit
	poetry run bandit -r src

# Conditional Security Checks based on config.yaml
.SECONDARY: config.yaml
security-conditional:
	@echo "Checking if security checks are enabled in config.yaml..."
	@ENABLED=$(shell python -c "import yaml; config = yaml.safe_load(open('config.yaml')); print(config.get('security', {}).get('enable_security', True))")
	@if [ "$$ENABLED" = "true" ]; then \
		$(MAKE) security; \
	else \
		echo "Security checks are disabled in config.yaml."; \
	fi

# Documentation commands
docs:
	@echo "Building documentation..."
	poetry run sphinx-build -W -b html docs/source docs/build/html

serve-docs:
	@echo "Serving documentation locally..."
	poetry run sphinx-autobuild docs/source docs/build/html

# Development workflow shortcuts
.PHONY: dev-setup dev-update check check-soft

dev-setup: install
	@echo "Setting up pre-commit hooks..."
	poetry run pre-commit install
	@echo "Development environment setup complete!"

dev-update: update format lint-soft test
	@echo "Development environment updated and checked!"

check: format lint test security
	@echo "All checks completed!"

check-soft: format lint-soft test
	@echo "Soft checks completed!"

# Help command
help:
	@echo "Available commands:"
	@echo "  install        - Install project dependencies"
	@echo "  update         - Update project dependencies"
	@echo "  format         - Format code with black and isort"
	@echo "  lint           - Run strict linting checks"
	@echo "  lint-soft      - Run linting with warnings only"
	@echo "  test           - Run tests with coverage"
	@echo "  coverage       - Generate coverage reports"
	@echo "  security        - Run security checks (safety, pip-audit, bandit)"
	@echo "  security-conditional - Run security checks based on config.yaml"
	@echo "  docs           - Build documentation"
	@echo "  serve-docs     - Serve documentation locally"
	@echo "  dev-setup      - Complete development environment setup"
	@echo "  dev-update     - Update and check development environment"
	@echo "  check          - Run all strict checks"
	@echo "  check-soft     - Run all checks in warning mode"
