test:
	pytest --cov-report term-missing --cov=textual tests/ -vv
typecheck:
	mypy src/textual --strict
format:
	black src
format-check:
	black --check .
