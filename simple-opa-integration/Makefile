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
AUTHZ_PROFILE ?= authz-v1
OPA_IMAGE ?= openpolicyagent/opa:latest
POLICY_BUNDLE_DIST ?=bundle.tar.gz
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

.PHONY: policy_check
policy_check: ## Run OPA check on Policies
	@docker run --rm -v $(PWD)/deployment/authz:/authz $(OPA_IMAGE) check /authz/policies

.PHONY: policy_eval
policy_eval: ## Evaluate the Rego Policies
	@docker run --rm -v $(PWD)/deployment/authz:/authz $(OPA_IMAGE) eval -d /authz/policies  'data.simple.authz'

.PHONY: policy_test
policy_test: ## Test the policy against a valid input using JWT token
	@docker run --network app --rm -v $(PWD)/scripts:/app -w /app python:3.12-slim \
		sh -c "pip install --no-cache-dir pyjwt >/dev/null && python3 validate_policy.py"

.PHONY: policy_build
policy_build:  ## Build policies into a gzipped file
	@rm -rf $(PWD)/deployment/authz/dist
	@mkdir -p $(PWD)/deployment/authz/dist
	@docker run --rm -v $(PWD)/deployment/authz:/authz -w /authz $(OPA_IMAGE) build -o dist/$(POLICY_BUNDLE_DIST) policies/

.PHONY: infra_init
infra_init: ## Create the infrastructure
	@docker network create app || true

.PHONY: infra_cleanup
infra_cleanup: ## Cleanup the infrastructure
	@docker network remove app

.PHONY: authz_start
authz_start: ## Start Authorization Service (Open Policy Agent)
	docker compose --profile $(AUTHZ_PROFILE) up -d

.PHONY: authz_stop
authz_stop: ## Stop Authorization Service (Open Policy Agent)
	@docker compose --profile $(AUTHZ_PROFILE) down

.PHONY: authz_logs
authz_logs: ## View logs of Authorization Service (Open Policy Agent)
	@docker compose --profile $(AUTHZ_PROFILE) logs

.PHONY: app_start
app_start: ## Start App
	@docker compose --profile app up -d

.PHONY: app_stop
app_stop: ## Stop App
	@docker compose --profile app down

.PHONY: app_logs
app_logs: ## View application logs
	@docker compose --profile app logs

.PHONY: start
start: authz_start app_start  ## Start Authorization Services and Application

.PHONY: stop
stop: authz_stop app_stop  ## Start Authorization Services and Application


.PHONY: dockerfile-lint
dockerfile_lint: ## Run lint for dockerfile
	@docker run --rm -i hadolint/hadolint < $(DOCKERFILE)

docker_build: ## Build application docker image
	@docker build -f dockerfile -t $(IMAGE_NAME)  .

.PHONY: docker_image_view
docker_image_view: ## View Application docker image view
	@dive $(IMAGE_NAME)

.PHONY: runtime_view
runtime_view:  ## view the active docker container
	@docker container ls

.PHONY: generate_token
generate_token:  ## Generate a mock JWT token using Docker CLI
	@docker run --rm -v $(PWD)/scripts:/app -w /app python:3.12-slim \
	    sh -c "pip install --no-cache-dir pyjwt && python3 generate_token.py"

.PHONY: localstack_start
localstack_start:  ## Start localstack service for S3
	@echo ""
	@echo "[INFO] Starting localstack Service "
	@echo ""
	@docker compose --profile authz-s3 up -d aws-mock-service

.PHONY: localstack_stop
localstack_stop:  ## Stop localstack service
	@echo ""
	@echo "[INFO] Stopping localstack Service "
	@echo ""
	@docker compose --profile authz-s3 down aws-mock-service

.PHONY: s3_deploy
s3_deploy:  ## Deploy the policy to S3 bucket
	@echo ""
	@echo "[INFO] Deploying $(POLICY_BUNDLE_DIST) to S3 Bucket "
	@echo ""
	@echo "🪣 Creating bucket ..."
	@docker run --rm --network app \
	  -e AWS_ACCESS_KEY_ID=test -e AWS_SECRET_ACCESS_KEY=test \
	  -e AWS_REGION=us-west-1 -e AWS_DEFAULT_REGION=us-west-1 \
	  amazon/aws-cli \
	  s3 mb s3://simple-app --endpoint-url http://aws-mock-service:4566 || true

	@echo "📦 Uploading $(POLICY_BUNDLE_DIST) to s3://simple-app..."
	@docker run --rm --network app \
	  -v $(PWD)/deployment/authz/dist:/authz \
	  -e AWS_ACCESS_KEY_ID=test -e AWS_SECRET_ACCESS_KEY=test \
	  -e AWS_REGION=us-west-1 -e AWS_DEFAULT_REGION=us-west-1 \
	  amazon/aws-cli \
	  s3 cp /authz/$(POLICY_BUNDLE_DIST) s3://simple-app/authz/$(POLICY_BUNDLE_DIST) \
	  --endpoint-url http://aws-mock-service:4566 \
	  --content-type application/gzip


s3_deploy_check:
	@echo ""
	@echo "[INFO] Validate deployment of $(POLICY_BUNDLE_DIST) to S3 Bucket "
	@echo ""
	@docker run --rm --network app \
	-e AWS_ACCESS_KEY_ID=test -e AWS_SECRET_ACCESS_KEY=test \
	-e AWS_REGION=us-west-1 -e AWS_DEFAULT_REGION=us-west-1 \
	amazon/aws-cli s3 ls s3://simple-app/authz/$(POLICY_BUNDLE_DIST) --endpoint-url http://host.docker.internal:4566