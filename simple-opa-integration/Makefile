.DEFAULT_GOAL := help
PROJECT_DESCRIPTION = "Simple OPA Integration"
PROJECT_NAME = "Second-microservice"
VENV = .venv
POETRY = poetry
PIP = pip
POETRY_CONF=$(shell echo $(HOME))
UNAME_S := $(shell uname -s)
PIP_CONF_USER := $(addsuffix /.config/pip/pip.conf,$(HOME))
PIP_CONF_USER_OLD := $(addsuffix /.pip/pip.conf,$(HOME))
PIP_CONF_GLOBAL := $(addsuffix /Library/Application Support/pip/pip.conf,$(HOME))
DOCKERFILE ?= dockerfile
IMAGE_NAME ?= "simple-opa-integration:latest"

ifeq ($(UNAME_S),Linux)
	POETRY_AUTH_CONF := $(addsuffix /auth.toml,$(POETRY_HOME))
endif
ifeq ($(UNAME_S),Darwin)
	POETRY_AUTH_CONF := $(addsuffix /auth.toml,$(POETRY_HOME))
endif

help:  ## Help message
	@echo ""
	@echo "\033[1;33mAvailable commands:\033[0m"
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

.PHONY: init
init: ## Initialize the Poetry development environment
	@echo "[Info] $(PROJECT_DESCRIPTION) Initialization of development Environment - Started"
	$(eval PYTHON_VERSION=$(shell pyenv versions --bare --skip-aliases --skip-envs | grep 3.12 | sort | tail -1))
	@echo "Python Version : $(PYTHON_VERSION)"
	@pyenv local $(PYTHON_VERSION)
	@$(POETRY) config virtualenvs.in-project true && \
		$(POETRY) config installer.max-workers 10 && \
		$(POETRY) run pip install  --upgrade pip setuptools wheel && \
		$(POETRY) install --no-root
	@echo "[Info] $(PROJECT_DESCRIPTION) Initialization of development Environment - Completed"

.PHONY: cleanup
cleanup: ## Cleanup the developmenet environment temporary files
	@find . \( \
		-name "__pycache__" -o \
		-name "*.pyc" -o \
		-name "*.pyo" -o \
		-name ".DS_Store" -o \
		-name ".mypy_cache" -o \
		-name ".pytest_cache" -o \
		-name ".coverage" -o \
		-name "coverage.xml" -o \
		-name "htmlcov" -o \
		-name "test-results" \
	\) -exec rm -rf {} +
	@rm -rf build/ .tox

.PHONY: format
format:  ## Format code using Ruff (Black-compatible)
	@poetry run ruff format .

.PHONY: lint
lint:  dockerfile_lint ## Run static analysis with Ruff and Mypy
	@poetry run ruff check .
	@poetry run mypy basic_opa_integration

.PHONY: test
test:  ## Run tests with Pytest and show coverage
	@poetry run pytest

.PHONY: validate_policy
validate_policy: ## Validate Rego Policies
	@docker run --rm -v $(PWD):/app openpolicyagent/opa:latest eval -d /app/policies  'data.simple.authz'
	@docker run --rm -v $(PWD):/app openpolicyagent/opa:latest check /app/policies

.PHONY: infra_init
infra_init: ## Create the infrastructure
	@docker network create app || true

.PHONY: infra_cleanup
infra_cleanup: ## Cleanup the infrastructure
	@docker network remove app

.PHONY: authz_start
authz_start: ## Start Authorization Service(Open Policy Agent)
	@docker compose --profile authz up -d

.PHONY: authz_stop
authz_stop: ## Stop Authorization Service(Open Policy Agent)
	@docker compose --profile authz down

.PHONY: app_start
app_start: ## Start App
	@docker compose --profile app up -d

.PHONY: app_stop
app_stop: ## Stop App
	@docker compose --profile app down

.PHONY: start
start: authz_start app_start  ## Start Authorization Services and Application

.PHONY: stop
stop: authz_stop app_stop  ## Start Authorization Services and Application


.PHONY: dockerfile-lint
dockerfile_lint: ## Run lint for dockerfile
	@docker run --rm -i hadolint/hadolint < $(DOCKERFILE)

docker_build: ## Build application docker image
	@docker build -f dockerfile -t $(IMAGE_NAME)  .

