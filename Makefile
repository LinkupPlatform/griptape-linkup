.PHONY: install
install: ## Install all dependencies.
	@make install/all

.PHONY: install/core
install/core: ## Install core dependencies.
	@uv sync --no-default-groups

.PHONY: install/all
install/all: ## Install all dependencies.
	@uv sync --all-groups
	@uv run pre-commit install

.PHONY: install/dev
install/dev: ## Install dev dependencies.
	@uv sync --no-default-groups --group dev

.PHONY: install/test
install/test: ## Install test dependencies.
	@uv sync --no-default-groups --group test

.PHONY: test  ## Run all tests.
test: test/unit

.PHONY: test/unit
test/unit: ## Run unit tests.
	@uv run pytest tests/unit

.PHONY: test/unit/%
test/unit/%: ## Run specific unit tests.
	@uv run pytest tests/unit -k $*

.PHONY: lint
lint: ## Lint project.
	@uv run ruff check --fix

.PHONY: format
format: ## Format project.
	@uv run ruff format

.PHONY: check
check: check/format check/lint check/types check/spell ## Run all checks.

.PHONY: check/format
check/format:
	@uv run ruff format --check

.PHONY: check/lint
check/lint:
	@uv run ruff check

.PHONY: check/types
check/types:
	@uv run pyright griptape

.PHONY: check/spell
check/spell:
	@uv run typos

.PHONY: build
build: ## Build sdist and wheel.
	@uv build

.DEFAULT_GOAL := help
.PHONY: help
help: ## Print Makefile help text.
	@# Matches targets with a comment in the format <target>: ## <comment>
	@# then formats help output using these values.
	@grep -E '^[a-zA-Z_\/-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; \
		{printf "\033[36m%-12s\033[0m%s\n", $$1, $$2}'
