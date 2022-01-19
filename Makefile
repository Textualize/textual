test:
	pytest --cov-report term-missing --cov=textual tests/ -vv
typecheck:
	mypy src/textual
format:
	black src
format-check:
	black --check src
