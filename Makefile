.PHONY: install install-frontend build-frontend dev-frontend run-server run-ui test benchmark ablations clean help

PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip
STREAMLIT ?= .venv/bin/streamlit
PYTEST ?= .venv/bin/pytest

help:
	@echo "Available commands:"
	@echo "  make install          - Install Python backend dependencies in .venv"
	@echo "  make install-frontend - Install React frontend npm dependencies"
	@echo "  make build-frontend   - Build production React client into frontend/dist"
	@echo "  make dev-frontend     - Start Vite hot-reloading dev server on http://localhost:5173"
	@echo "  make run-server       - Launch FastAPI backend serving React Studio on http://localhost:8000"
	@echo "  make test             - Run backend unit and integration test suite with pytest"
	@echo "  make benchmark        - Run F_0.5 benchmark evaluation on sample data"
	@echo "  make ablations        - Run baseline comparison ablations"
	@echo "  make run-ui           - Launch Streamlit alternative interface"
	@echo "  make clean            - Remove cached bytecode and build artifacts"

install:
	$(PIP) install -r requirements.txt
	$(PYTHON) -m spacy download en_core_web_sm
	cd frontend && npm install

install-frontend:
	cd frontend && npm install

build-frontend:
	cd frontend && npm run build

dev-frontend:
	cd frontend && npm run dev

run-server:
	$(PYTHON) -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload

run-ui:
	$(STREAMLIT) run app.py

test:
	$(PYTEST) tests/

benchmark:
	$(PYTHON) -m benchmarks.evaluate --data data/sample_benchmark.jsonl

ablations:
	$(PYTHON) -m benchmarks.run_ablations --data data/sample_benchmark.jsonl

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf frontend/dist
