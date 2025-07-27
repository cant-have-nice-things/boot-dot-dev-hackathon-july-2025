.PHONY: help install install-backend install-frontend install-prod install-prod-backend dev dev-backend dev-frontend build build-backend build-frontend clean test test-backend test-frontend lint lint-backend lint-frontend format format-backend format-frontend fix fix-backend fix-frontend check-deps

# Default target
help:
	@echo "Available commands:"
	@echo "  install           - Install all dependencies (backend + frontend)"
	@echo "  install-backend   - Install backend dependencies"
	@echo "  install-frontend  - Install frontend dependencies"
	@echo "  dev               - Run both backend and frontend in development mode"
	@echo "  dev-backend       - Run backend development server"
	@echo "  dev-frontend      - Run frontend development server"
	@echo "  build             - Build both backend and frontend for production"
	@echo "  build-backend     - Build backend for production"
	@echo "  build-frontend    - Build frontend for production"
	@echo "  test              - Run tests for both backend and frontend"
	@echo "  test-backend      - Run backend tests"
	@echo "  test-frontend     - Run frontend tests"
	@echo "  lint              - Run linting for both backend and frontend"
	@echo "  lint-backend      - Run backend linting"
	@echo "  lint-frontend     - Run frontend linting"
	@echo "  format            - Format code for both backend and frontend"
	@echo "  format-backend    - Format backend code"
	@echo "  format-frontend   - Format frontend code"
	@echo "  fix               - Fix all auto-fixable issues (format + lint --fix)"
	@echo "  clean             - Clean build artifacts and dependencies"
	@echo "  install-prod      - Install production dependencies only"
	@echo "  check-deps        - Check if required tools are installed"

# Production installation (no dev dependencies)
install-prod: install-prod-backend install-frontend

# Installation targets
install: install-backend install-frontend

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && uv sync --group dev

install-prod-backend:
	@echo "Installing backend production dependencies only..."
	cd backend && uv sync

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Development targets
dev:
	@echo "Starting redis and development servers..."
	make redis-start
	@sleep 2  # Give Redis time to start
	make -j2 dev-backend dev-frontend

dev-backend:
	@echo "Starting backend development server..."
	cd backend && uv run uvicorn app.main:app --reload --port 8000

dev-frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

# Redis commands
redis-start:
	@echo "Starting Redis container..."
	@docker run -d --name nice-things-redis -p 6379:6379 -v redis_data:/data redis:7-alpine redis-server --appendonly yes || docker start nice-things-redis
	@echo "Redis available at localhost:6379"

redis-stop:
	@echo "Stopping Redis container..."
	@docker stop nice-things-redis || true

redis-restart:
	@echo "Restarting Redis container..."
	make redis-stop
	@sleep 1
	make redis-start

redis-cli:
	@echo "Connecting to Redis CLI..."
	@docker exec -it nice-things-redis redis-cli

redis-logs:
	@echo "Showing Redis logs..."
	@docker logs nice-things-redis


# Build targets
build: build-backend build-frontend

build-backend:
	@echo "Building backend for production..."
	cd backend && uv build

build-frontend:
	@echo "Building frontend for production..."
	cd frontend && npm run build

# Test targets
test: test-backend test-frontend

test-backend:
	@echo "Running backend tests..."
	cd backend && uv run pytest

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test

# Linting targets
lint: lint-backend lint-frontend

lint-backend:
	@echo "Linting backend code..."
	@cd backend && uv run ruff check . || { echo "❌ Ruff not found. Run 'make install-backend' first."; exit 1; }

lint-frontend:
	@echo "Linting frontend code..."
	@cd frontend && npm run lint || { echo "❌ Frontend linting failed. Check if lint script exists in package.json"; exit 1; }

# Formatting targets (fixes all auto-fixable issues)
format: format-backend format-frontend

format-backend:
	@echo "Formatting backend code..."
	@cd backend && uv run ruff format . || { echo "❌ Ruff not found. Run 'make install-backend' first."; exit 1; }
	@echo "Fixing auto-fixable lint issues..."
	@cd backend && uv run ruff check . --fix || { echo "❌ Ruff not found. Run 'make install-backend' first."; exit 1; }

format-frontend:
	@echo "Formatting frontend code..."
	@cd frontend && npm run format || { echo "❌ Frontend formatting failed. Check if format script exists in package.json"; exit 1; }

# Utility targets
fix: fix-backend fix-frontend

fix-backend:
	@echo "Fixing all auto-fixable backend issues..."
	@cd backend && uv run ruff format . || { echo "❌ Ruff not found. Run 'make install-backend' first."; exit 1; }
	@cd backend && uv run ruff check . --fix || { echo "❌ Ruff not found. Run 'make install-backend' first."; exit 1; }

fix-frontend:
	@echo "Fixing all auto-fixable frontend issues..."
	@cd frontend && npm run format || { echo "❌ Frontend formatting failed. Check if format script exists in package.json"; exit 1; }

clean:
	@echo "Cleaning build artifacts and dependencies..."
	rm -rf backend/dist/
	rm -rf backend/.pytest_cache/
	rm -rf backend/__pycache__/
	rm -rf frontend/dist/
	rm -rf frontend/node_modules/
	rm -rf frontend/.next/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

check-deps:
	@echo "Checking required dependencies..."
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv is not installed. Please install it first."; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo "❌ Node.js is not installed. Please install it first."; exit 1; }
	@command -v npm >/dev/null 2>&1 || { echo "❌ npm is not installed. Please install it first."; exit 1; }
	@echo "✅ All required dependencies are installed!"