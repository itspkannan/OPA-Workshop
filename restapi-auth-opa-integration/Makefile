.DEFAULT_GOAL := help
PROJECT_DESCRIPTION = "RestAPI Auth OPA Integration"
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
IMAGE_NAME ?= "restapi-auth-opa-integration-microservice:latest"
AUTHZ_PROFILE ?= authz-v1
OPA_IMAGE ?= openpolicyagent/opa:latest
POLICY_BUNDLE_DIST ?=bundle.tar.gz
DOCKER_NETWORK ?= app


ifeq ($(UNAME_S),Linux)
	POETRY_AUTH_CONF := $(addsuffix /auth.toml,$(POETRY_HOME))
endif
ifeq ($(UNAME_S),Darwin)
	POETRY_AUTH_CONF := $(addsuffix /auth.toml,$(POETRY_HOME))
endif

help:  ## Help message
	@echo ""
	@echo "\033[1;33mAvailable commands:\033[0m" && \
	awk -F ':.*?## ' '/^[a-zA-Z0-9_.-]+:.*## / { \
		cmds[$$1] = $$2; \
		if (length($$1) > max_len) max_len = length($$1); \
	} \
	END { \
		for (cmd in cmds) { \
			printf "  \033[36m%-" max_len "s\033[0m %s\n", cmd, cmds[cmd]; \
		} \
	}' $(MAKEFILE_LIST) | sort
	@echo ""


.PHONY: init.python
init.python: ## Initialize the Poetry development environment
	@echo "[Info] $(PROJECT_DESCRIPTION) Initialization of development Environment - Started"
	$(eval PYTHON_VERSION=$(shell pyenv versions --bare --skip-aliases --skip-envs | grep 3.12 | sort | tail -1))
	@echo "Python Version : $(PYTHON_VERSION)"
	@pyenv local $(PYTHON_VERSION)
	@$(POETRY) config virtualenvs.in-project true && \
		$(POETRY) config installer.max-workers 10 && \
		$(POETRY) run pip install  --upgrade pip setuptools wheel && \
		$(POETRY) install --no-root
	@echo "[Info] $(PROJECT_DESCRIPTION) Initialization of development Environment - Completed"

.PHONY: clean.python
clean.python: ## Cleanup the development environment temporary files
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

.PHONY: format.python
format.python:  ## Format code using Ruff (Black-compatible)
	@poetry run ruff format .

.PHONY: lint.python
lint.python:   ## Run static analysis with Ruff and Mypy
	@poetry run ruff check .
	@poetry run mypy basic_opa_integration

.PHONY: python.test
test.python:  ## Run tests with Pytest and show coverage
	@echo "[INFO] Started unit test of python code"
	@poetry run pytest
	@echo "[INFO] Completed unit test of python code"

.PHONY: policy.check
policy.check: ## Run OPA check on Policies
	@docker run --rm -v $(PWD)/deployment/authz:/authz $(OPA_IMAGE) check /authz/policies

.PHONY: policy.eval
policy.eval: ## Evaluate the Rego Policies
	@docker run --rm -v $(PWD)/deployment/authz:/authz $(OPA_IMAGE) eval -d /authz/policies  'data.simple.authz'

.PHONY: test.rego.integration
test.rego.integration: ## Test the policy against a valid input using JWT token
	@echo "[INFO] Started integration test of Rego Policies"
	@docker run --network $(DOCKER_NETWORK) --rm -v $(PWD)/scripts:/app -w /app python:3.12-slim \
		sh -c "pip install --no-cache-dir pyjwt >/dev/null && python3 validate_policy.py"
	@echo "[INFO] Completed integration test of Rego Policies"

.PHONY: test.rego
test.rego: ## Unit test of rego policies with mocking of data
	@echo "[INFO] Started unit test of Rego Policies"
	@docker run --rm  -v "$(PWD)/src/main/rego:/policies" -e JWT_ISSUER=pki.example.com \
      -e JWT_TOKEN_SIGN_SECRET=secret123 \
	 -v "$(PWD)/src/test/rego:/test-policies" $(OPA_IMAGE) test -v /policies /test-policies
	@echo "[INFO] Completed unit test of Rego Policies"

.PHONY: clean.rego
clean.rego:  ## Cleanup policies build folder
	@rm -rf $(PWD)/dist/authz || true

.PHONY: build.rego
build.rego: clean.rego ## Build policies into a gzipped file
	@mkdir -p $(PWD)/dist/authz
	@docker run --rm -v $(PWD)/src/main/rego:/authz/src/main/rego/ -v $(PWD)/dist/authz:/authz/dist -w /authz $(OPA_IMAGE) build -o dist/$(POLICY_BUNDLE_DIST) src/main/rego/

build.python: ## Build python source
	@poetry build --output dist/app

.PHONY: init.infra
init.infra: ## Create the infrastructure
	@docker network create app || true

.PHONY: infra.cleanup
infra.cleanup: ## Cleanup the infrastructure
	@docker network remove app

.PHONY: start.authz
start.authz: ## Start Authorization Service (Open Policy Agent)
	docker compose --profile $(AUTHZ_PROFILE) up -d

.PHONY: stop.authz
stop.authz: ## Stop Authorization Service (Open Policy Agent)
	@docker compose --profile $(AUTHZ_PROFILE) down

.PHONY: logs.authz
logs.authz: ## View logs of Authorization Service (Open Policy Agent)
	@docker compose --profile $(AUTHZ_PROFILE) logs

.PHONY: start.app
start.app: ## Start App
	@docker compose --profile app up -d

.PHONY: stop.app
stop.app: ## Stop App
	@docker compose --profile app down

.PHONY: logs.app
logs.app: ## View application logs
	@docker compose --profile app logs

.PHONY: lint.dockerfile
lint.dockerfile: ## Run lint for dockerfile
	@docker run --rm -i hadolint/hadolint < $(DOCKERFILE)

build.docker: ## Build application docker image
	@docker build -f dockerfile -t $(IMAGE_NAME)  .

.PHONY: docker.image.describe
docker.image.describe: ## View Application docker image view
	@dive $(IMAGE_NAME)

.PHONY: runtime.view
runtime.view:  ## view the active docker container
	@docker container ls

.PHONY: token.generate
token.generate:  ## Generate a mock JWT token 
	@docker run --rm -v $(PWD)/scripts:/app -w /app python:3.12-slim \
	    sh -c "pip install --no-cache-dir pyjwt && python3 generate_token.py"

.PHONY: start.localstack
start.localstack:  ## Start localstack service for S3
	@echo ""
	@echo "[INFO] Starting localstack Service "
	@echo ""
	@docker compose --profile authz-v3 up -d aws-mock-service

.PHONY: stop.localstack
stop.localstack:  ## Stop localstack service
	@echo ""
	@echo "[INFO] Stopping localstack Service "
	@echo ""
	@docker compose --profile authz-v3 down aws-mock-service

.PHONY: deploy.rego
deploy.rego:  ## Deploy the policy to S3 bucket
	@echo ""
	@echo "[INFO] Deploying $(POLICY_BUNDLE_DIST) to S3 Bucket "
	@echo ""
	@echo "🪣 Creating bucket ..."
	@docker run --rm --network $(DOCKER_NETWORK) \
	  -e AWS_ACCESS_KEY_ID=test -e AWS_SECRET_ACCESS_KEY=test \
	  -e AWS_REGION=us-west-1 -e AWS_DEFAULT_REGION=us-west-1 \
	  amazon/aws-cli \
	  s3 mb s3://simple-app --endpoint-url http://aws-mock-service:4566 || true

	@echo "📦 Uploading $(POLICY_BUNDLE_DIST) to s3://simple-app..."
	@docker run --rm --network $(DOCKER_NETWORK) \
	  -v $(PWD)/dist/authz:/authz \
	  -e AWS_ACCESS_KEY_ID=test -e AWS_SECRET_ACCESS_KEY=test \
	  -e AWS_REGION=us-west-1 -e AWS_DEFAULT_REGION=us-west-1 \
	  amazon/aws-cli \
	  s3 cp /authz/$(POLICY_BUNDLE_DIST) s3://simple-app/authz/$(POLICY_BUNDLE_DIST) \
	  --endpoint-url http://aws-mock-service:4566 \
	  --content-type application/gzip

.PHONY: deploy.rego.validate
deploy.rego.validate: ## Validate rego policy deployment to S3
	@echo ""
	@echo "[INFO] Validate deployment of $(POLICY_BUNDLE_DIST) to S3 Bucket "
	@echo ""
	@docker run --rm --network $(DOCKER_NETWORK) \
	-e AWS_ACCESS_KEY_ID=test -e AWS_SECRET_ACCESS_KEY=test \
	-e AWS_REGION=us-west-1 -e AWS_DEFAULT_REGION=us-west-1 \
	amazon/aws-cli s3 ls s3://simple-app/authz/$(POLICY_BUNDLE_DIST) --endpoint-url http://host.docker.internal:4566


.PHONY: build
build: build.python build.rego build.docker ## Build Python and Rego policies

.PHONY: test
test: test.python test.rego ## Run tests for Rego and Python src code

.PHONY: lint
lint: lint.python  lint.dockerfile ## Run static analysis on Python, Rego and Dockerfile
	@poetry run ruff check .
	@poetry run mypy basic_opa_integration

.PHONY: start
start: start.authz start.app  ## Start Authorization Services and Application

.PHONY: stop
stop: stop.authz stop.app  ## Stop Authorization Services and Application

.PHONY: clean.docker
clean.docker: ## Remove docker related files created for project, any network, images, volume
	@echo "[INFO] Removing docker images built for the project"
	@docker rmi $(IMAGE_NAME) 

.PHONY: clean
clean: clean.python clean.rego clean.docker ## Cleanup all generated files

.PHONY: bootstrap
bootstrap: init.infra init.python build ## Bootstrap environment