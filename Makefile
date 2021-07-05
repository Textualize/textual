test:
	pytest --cov-report term-missing --cov=textual tests/ -vv
typecheck:
	mypy -p rich --strict
format:
	black .
format-check:
	black --check .