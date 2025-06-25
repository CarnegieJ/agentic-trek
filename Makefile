# Makefile for Agentic Trek development

.PHONY: help install install-dev test lint format type-check docs clean run run-ascii run-pygame screenshots

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  type-check   - Run type checking with mypy"
	@echo "  docs         - Build documentation"
	@echo "  clean        - Clean build artifacts"
	@echo "  run          - Run game with pygame interface"
	@echo "  run-ascii    - Run game with ASCII interface"
	@echo "  run-pygame   - Run game with pygame interface"
	@echo "  setup-dev    - Set up development environment"
	@echo "  pre-commit   - Run pre-commit hooks"
	@echo "  screenshots  - Generate screenshots for documentation"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

setup-dev: install-dev
	pre-commit install
	@echo "Development environment set up successfully!"

# Testing
test:
	pytest

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term-missing

test-performance:
	pytest tests/performance/ --benchmark-only

test-ai:
	pytest tests/ai/ -v

# Code quality
lint:
	flake8 src tests
	black --check src tests
	isort --check-only src tests

format:
	black src tests
	isort src tests

type-check:
	mypy src

pre-commit:
	pre-commit run --all-files

# Security
security:
	bandit -r src/

# Documentation
docs:
	cd docs && make html

docs-serve:
	cd docs/_build/html && python -m http.server 8000

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .tox/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Running the game
run:
	python src/main.py

run-ascii:
	python src/main.py --ascii

run-pygame:
	python src/main.py

run-debug:
	python src/main.py --debug

run-help:
	python src/main.py --help

# Development utilities
screenshots:
	python scripts/generate_screenshots.py pygame
	@echo "Run the game and press F5, F6, F7 to capture screenshots"

profile:
	python -m cProfile -o profile.stats src/main.py --ascii
	python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

memory-profile:
	python -m memory_profiler src/main.py --ascii

# Build and distribution
build:
	python -m build

upload-test:
	python -m twine upload --repository testpypi dist/*

upload:
	python -m twine upload dist/*

# Git hooks
install-hooks:
	pre-commit install
	pre-commit install --hook-type commit-msg

# All quality checks
check-all: lint type-check test security
	@echo "All checks passed!"

# Quick development cycle
dev-cycle: format lint type-check test
	@echo "Development cycle complete!"
