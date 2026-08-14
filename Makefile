# SpectraAI Native Tooling Makefile
# Supports Linux, macOS, and Windows environments with Make

PYTHON ?= python
NPM ?= npm
UV := $(shell command -v uv 2> /dev/null)

.PHONY: all setup setup-backend setup-frontend run-backend run-frontend test test-backend test-frontend build reset-demo clean help

all: help

help:
	@echo "SpectraAI Development Commands:"
	@echo "  make setup          - Install all backend and frontend dependencies (using uv if available)"
	@echo "  make setup-backend  - Set up Python virtual environment and install backend dependencies"
	@echo "  make setup-frontend - Install Node.js frontend dependencies via npm"
	@echo "  make run-backend    - Start FastAPI backend server on http://localhost:8000"
	@echo "  make run-frontend   - Start Vite frontend dev server on http://localhost:5173"
	@echo "  make test           - Run full test suite (pytest, e2e, frontend smoke)"
	@echo "  make test-backend   - Run Pytest backend test suite"
	@echo "  make test-frontend  - Run frontend smoke test suite"
	@echo "  make build          - Build production frontend bundle"
	@echo "  make reset-demo     - Reset local SQLite database and uploads to clean initial demo state"
	@echo "  make clean          - Remove temporary caches, build artifacts, and test reports"

setup: setup-backend setup-frontend

setup-backend:
ifdef UV
	@echo "Setting up backend with uv..."
	uv venv .venv
	uv pip install -r backend/requirements.txt
else
	@echo "Setting up backend with python venv fallback..."
	$(PYTHON) -m venv .venv
	$(PYTHON) -m pip install -r backend/requirements.txt
endif

setup-frontend:
	@echo "Setting up frontend dependencies..."
	cd frontend && $(NPM) install

run-backend:
	@echo "Starting FastAPI backend on http://localhost:8000..."
	cd backend && $(PYTHON) main.py

run-frontend:
	@echo "Starting Vite dashboard on http://localhost:5173..."
	cd frontend && $(NPM) run dev

test: test-backend test-frontend
	@echo "Running compatibility E2E suite..."
	$(PYTHON) test_e2e.py

test-backend:
	@echo "Running backend Pytest suite..."
	pytest -v

test-frontend:
	@echo "Running frontend smoke suite..."
	cd frontend && $(NPM) test

build:
	@echo "Building frontend production bundle..."
	cd frontend && $(NPM) run build

reset-demo:
	@echo "Resetting local SQLite database and uploads..."
	$(PYTHON) task.py reset-demo

clean:
	@echo "Cleaning temporary files and build artifacts..."
	$(PYTHON) task.py clean
