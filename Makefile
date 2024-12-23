.PHONY: venv clean clean-pyc clean-test run stop status test help install test-venv

# Variables
PYTHON := python3
VENV := .venv
TEST_VENV := .venv.test
VENV_BIN := $(VENV)/bin
TEST_VENV_BIN := $(TEST_VENV)/bin
PID_FILE := .app.pid
PORT := 8000

help:
	@echo "Available commands:"
	@echo "  make venv        - Create virtual environment for development"
	@echo "  make test-venv   - Create virtual environment for testing"
	@echo "  make install     - Install project dependencies"
	@echo "  make run         - Start the FastAPI application"
	@echo "  make stop        - Stop the FastAPI application"
	@echo "  make status      - Check if the application is running"
	@echo "  make test        - Run tests in isolated test environment"
	@echo "  make clean       - Remove all build, test, and coverage artifacts"
	@echo "  make clean-pyc   - Remove Python file artifacts"
	@echo "  make clean-test  - Remove test artifacts"

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(VENV_BIN)/pip install --upgrade pip

test-venv:
	@if [ ! -d "$(TEST_VENV)" ]; then \
		$(PYTHON) -m venv $(TEST_VENV); \
		$(TEST_VENV_BIN)/pip install --upgrade pip; \
		$(TEST_VENV_BIN)/pip install -r requirements.txt; \
		$(TEST_VENV_BIN)/pip install -r requirements-test.txt; \
	fi

install: venv
	$(VENV_BIN)/pip install -r requirements.txt

clean: clean-pyc clean-test
	rm -rf $(VENV)
	rm -rf $(TEST_VENV)
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .venv*
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f $(PID_FILE)

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '.pytest_cache' -exec rm -rf {} +

clean-test:
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache
	rm -rf .tox/

run: install
	@if [ -f $(PID_FILE) ]; then \
		echo "Application is already running. Use 'make stop' to stop it first."; \
		exit 1; \
	fi
	$(VENV_BIN)/uvicorn dell_unisphere_mock_api.main:app --host 0.0.0.0 --port $(PORT) --reload & echo $$! > $(PID_FILE)
	@echo "Application started on http://localhost:$(PORT)"

stop:
	@if [ -f $(PID_FILE) ]; then \
		pid=$$(cat $(PID_FILE)); \
		kill -TERM $$pid 2>/dev/null || true; \
		rm $(PID_FILE); \
		echo "Application stopped."; \
	else \
		echo "Application is not running."; \
	fi

status:
	@if [ -f $(PID_FILE) ]; then \
		pid=$$(cat $(PID_FILE)); \
		if ps -p $$pid > /dev/null; then \
			echo "Application is running (PID: $$pid)"; \
		else \
			echo "Application crashed or was killed"; \
			rm $(PID_FILE); \
		fi \
	else \
		echo "Application is not running"; \
	fi

test: test-venv
	$(TEST_VENV_BIN)/pytest -v tests/ --cov=dell_unisphere_mock_api --cov-report=term-missing --cov-report=xml:coverage.xml
