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

.PHONY: docs-offline-nav
docs-offline-nav:
	echo "INHERIT: mkdocs-offline.yml" > mkdocs-nav-offline.yml
	grep -v "\- \"*[Bb]log" mkdocs-nav.yml >> mkdocs-nav-offline.yml

.PHONY: docs-online-nav
docs-online-nav:
	echo "INHERIT: mkdocs-online.yml" > mkdocs-nav-online.yml
	cat mkdocs-nav.yml >> mkdocs-nav-online.yml

.PHONY: docs-serve
docs-serve: clean-screenshot-cache docs-online-nav
	$(run) mkdocs serve --config-file mkdocs-nav-online.yml
	rm -f mkdocs-nav-online.yml

.PHONY: docs-serve-offline
docs-serve-offline: clean-screenshot-cache docs-offline-nav
	$(run) mkdocs serve --config-file mkdocs-nav-offline.yml
	rm -f mkdocs-nav-offline.yml

.PHONY: docs-build
docs-build: docs-online-nav
	$(run) mkdocs build --config-file mkdocs-nav-online.yml
	rm -f mkdocs-nav-online.yml

.PHONY: docs-build-offline
docs-build-offline: docs-offline-nav
	$(run) mkdocs build --config-file mkdocs-nav-offline.yml
	rm -f mkdocs-nav-offline.yml

.PHONY: clean-offline-docs
clean-offline-docs:
	rm -rf docs-offline

.PHONY: docs-deploy
docs-deploy: clean-screenshot-cache docs-online-nav
	$(run) mkdocs gh-deploy --config-file mkdocs-nav-online.yml
	rm -f mkdocs-nav-online.yml

.PHONY: faq
faq:
	$(run) faqtory build

.PHONY: build
build: docs-build-offline
	poetry build

.PHONY: clean
clean: clean-screenshot-cache clean-offline-docs

.PHONY: setup
setup:
	poetry install

.PHONY: update
update:
	poetry update

.PHONY: install-pre-commit
install-pre-commit:
	$(run) pre-commit install
