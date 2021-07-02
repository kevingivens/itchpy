init:
	pip install -e .
	pip install -r requirements-dev.txt

lint:
	flake8 --ignore=E501,F821 itchpy

black:
	black .

ci:
	pytest tests

coverage:
	pytest --cov=itchpy tests/
