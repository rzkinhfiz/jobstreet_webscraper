.PHONY: help install install-dev run test lint format clean setup docker-build docker-run logs

help:
	@echo "JobStreet Scraper - Available Commands"
	@echo "======================================"
	@echo "make install       - Install dependencies"
	@echo "make install-dev   - Install dev dependencies"
	@echo "make setup         - Complete setup (venv + install + playwright)"
	@echo "make run           - Run scraper with default config"
	@echo "make test          - Run salary parser tests"
	@echo "make lint          - Run code linters"
	@echo "make format        - Auto-format code"
	@echo "make clean         - Remove cache and temp files"
	@echo "make logs          - Tail scraper logs"
	@echo "make docker-build  - Build Docker image"
	@echo "make docker-run    - Run scraper in Docker"
	@echo "make docker-compose-up - Start with docker-compose"

install:
	pip install -r requirements.txt
	python -m playwright install chromium

install-dev:
	pip install -r requirements-dev.txt
	python -m playwright install chromium

setup: venv install
	@echo "Setup complete! Activate venv with:"
	@echo "source venv/bin/activate  (Linux/Mac)"
	@echo "venv\\Scripts\\activate    (Windows)"

venv:
	python -m venv venv
	@echo "Virtual environment created"

run:
	python main.py

run-custom:
	@read -p "Enter keywords (space-separated): " keywords; \
	read -p "Enter locations (space-separated): " locations; \
	python main.py --keyword $$keywords --location $$locations

run-config:
	python main.py --config config.yaml

test:
	python test_salary_parser.py

test-all:
	pytest tests/ -v --cov=scraper

lint:
	flake8 scraper/ pipelines/ utils/ main.py config.py
	pylint scraper/ pipelines/ utils/ main.py config.py

format:
	black scraper/ pipelines/ utils/ main.py config.py test_salary_parser.py
	isort scraper/ pipelines/ utils/ main.py config.py test_salary_parser.py

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf build/ dist/

logs:
	tail -f logs/scraper.log

docker-build:
	docker build -t jobstreet-scraper .

docker-run:
	docker run -v $$(pwd)/data:/app/data -v $$(pwd)/logs:/app/logs jobstreet-scraper

docker-compose-up:
	docker-compose up scraper

docker-compose-down:
	docker-compose down

.DEFAULT_GOAL := help
