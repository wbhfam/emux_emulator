.PHONY: run test lint

run:
	python3 src/main.py

test:
	python3 -m pytest

lint:
	python3 -m flake8 --max-line-length 80 src tests
