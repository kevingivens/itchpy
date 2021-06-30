init:
	pip install -e .
	pip install -r requirements-dev.txt

ci:
	pytest tests

coverage:
	pytest --cov=itchpy tests/