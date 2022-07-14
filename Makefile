test:
	pytest --cov-report term-missing --cov=textual tests/ -vv
unit-test:
	pytest --cov-report term-missing --cov=textual tests/ -vv -m "not integration_test"
typecheck:
	mypy src/textual
format:
	black src
format-check:
	black --check src
docs-serve:
	mkdocs serve
docs-build:
	mkdocs build
