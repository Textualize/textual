run := poetry run

.PHONY: test
test:
	$(run) pytest --cov-report term-missing --cov=textual tests/ -vv

.PHONY: unit-test
unit-test:
	$(run) pytest --cov-report term-missing --cov=textual tests/ -vv -m "not integration_test"

.PHONY: test-snapshot-update
test-snapshot-update:
	$(run) pytest --cov-report term-missing --cov=textual tests/ -vv --snapshot-update

.PHONY: typecheck
typecheck:
	$(run) mypy src/textual

.PHONY: format
format:
	$(run) black src

.PHONY: format-check
format-check:
	$(run) black --check src

.PHONY: clean-screenshot-cache
clean-screenshot-cache:
	rm -rf .screenshot_cache

.PHONY: docs-serve
docs-serve: clean-screenshot-cache
	$(run) mkdocs serve --config-file mkdocs-online.yml

.PHONY: docs-build
docs-build:
	$(run) mkdocs build --config-file mkdocs-online.yml

.PHONY: docs-build-offline
docs-build-offline:
	$(run) mkdocs build --config-file mkdocs-offline.yml

.PHONY: clean-offline-docs
clean-offline-docs:
	rm -rf docs-offline

.PHONY: docs-deploy
docs-deploy: clean-screenshot-cache
	$(run) mkdocs gh-deploy

.PHONY: build
build: docs-build-offline
	poetry build

.PHONY: clean
clean: clean-screenshot-cache clean-offline-docs
