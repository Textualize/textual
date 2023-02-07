.PHONY: test
test:
	pytest --cov-report term-missing --cov=textual tests/ -vv

.PHONY: unit-test
unit-test:
	pytest --cov-report term-missing --cov=textual tests/ -vv -m "not integration_test"

.PHONY: test-snapshot-update
test-snapshot-update:
	pytest --cov-report term-missing --cov=textual tests/ -vv --snapshot-update

.PHONY: typecheck
typecheck:
	mypy src/textual

.PHONY: format
format:
	black src

.PHONY: format-check
format-check:
	black --check src

.PHONY: clean-screenshot-cache
clean-screenshot-cache:
	rm -rf .screenshot_cache

.PHONY: docs-serve
docs-serve: clean-screenshot-cache
	mkdocs serve --config-file mkdocs-online.yml

.PHONY: docs-build
docs-build:
	mkdocs build --config-file mkdocs-online.yml

.PHONY: docs-build-offline
docs-build-offline:
	mkdocs build --config-file mkdocs-offline.yml

.PHONY: docs-deploy
docs-deploy: clean-screenshot-cache
	mkdocs gh-deploy
