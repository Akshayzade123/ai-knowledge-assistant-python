.PHONY: help test test-unit test-integration test-cov test-fast lint format clean install dev-install

# Default target
help:
	@echo "AI Knowledge Assistant - Development Commands"
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run all tests"
	@echo "  make test-unit         - Run unit tests only"
	@echo "  make test-integration  - Run integration tests only"
	@echo "  make test-cov          - Run tests with coverage report"
	@echo "  make test-fast         - Run tests in parallel"
	@echo "  make test-verbose      - Run tests with verbose output"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint              - Run linters (ruff, mypy)"
	@echo "  make format            - Format code (black, ruff)"
	@echo "  make check             - Run all quality checks"
	@echo ""
	@echo "Setup:"
	@echo "  make install           - Install production dependencies"
	@echo "  make dev-install       - Install dev dependencies"
	@echo "  make clean             - Clean temporary files"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build      - Build Docker images"
	@echo "  make docker-up         - Start Docker services"
	@echo "  make docker-down       - Stop Docker services"
	@echo "  make docker-logs       - View Docker logs"
	@echo "  make docker-restart    - Restart API service"

# Testing
test:
	uv run pytest

test-unit:
	uv run pytest -m unit

test-integration:
	uv run pytest -m integration

test-cov:
	uv run pytest --cov=src/app --cov-report=html --cov-report=term-missing

test-fast:
	uv run pytest -n auto

test-verbose:
	uv run pytest -vv

# Code Quality
lint:
	uv run ruff check src/ tests/
	uv run mypy src/

format:
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

check: format lint test

# Setup
install:
	uv sync --no-dev

dev-install:
	uv sync

clean:
	powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force"
	powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Filter '*.egg-info' | Remove-Item -Recurse -Force"
	powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Filter '.pytest_cache' | Remove-Item -Recurse -Force"
	powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Filter '.ruff_cache' | Remove-Item -Recurse -Force"
	powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Filter '.mypy_cache' | Remove-Item -Recurse -Force"
	powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Filter 'htmlcov' | Remove-Item -Recurse -Force"
	powershell -Command "Get-ChildItem -Path . -Recurse -File -Filter '*.pyc' | Remove-Item -Force"
	powershell -Command "if (Test-Path .coverage) { Remove-Item .coverage -Force }"

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

docker-restart:
	docker-compose restart api

docker-clean:
	docker-compose down -v
	docker system prune -f
