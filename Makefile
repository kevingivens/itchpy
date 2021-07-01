init:
	pip install -e .
	pip install -r requirements-dev.txt

black:
	black .

ci:
	pytest tests

coverage:
	pytest --cov=itchpy tests/
