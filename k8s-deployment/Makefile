SOURCE_DIR := "../restapi-auth-opa-integration"
MICROSERVICE_IMAGE_NAME := restapi-auth-opa-integration-microservice
CLUSTER_NAME=microservice-opa-integration
CONFIG_FILE=k3d-config.yaml
DEFAULT_REG=localhost:5000

IMAGE_NAME=$(DEFAULT_REG)/$(MICROSERVICE_IMAGE_NAME)
DOCKER_NETWORK := k3d-$(CLUSTER_NAME)

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "\n\033[1;33mAvailable commands:\033[0m" \
	    && awk -F ':.*## ' '/^[a-zA-Z0-9_.-]+:.*## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) \
	    | sort && echo ""

.PHONY: create.network
create.network: ## Create a K3d network
	@echo "[INFO] Creating docker network $(DOCKER_NETWORK)."
	docker network create $(DOCKER_NETWORK) || true

.PHONY: delete.network
delete.network: ## Delete a K3d network
	@docker network rm $(DOCKER_NETWORK) || true

.PHONY: start.registry
start.registry: ## Start Docker registry using Compose
	@echo "[INFO] Registry for docker images - Starting."
	@DOCKER_NETWORK=$(DOCKER_NETWORK) docker compose up -d 
	@echo "[INFO]  Registry for docker images - Started ."

.PHONY: stop.registry
stop.registry: ## Stop Docker registry
	@echo "[INFO] Registry for docker images - Shutdown initiated."
	@DOCKER_NETWORK=$(DOCKER_NETWORK) docker compose down
	@echo "[INFO] Registry for docker images - Shutdown complete."

.PHONY: build
create.cluster: ## Create K3d cluster with custom registry
	@echo "[INFO] K3d Cluster $(CLUSTER_NAME) - Creation started."
	@DOCKER_NETWORK=$(DOCKER_NETWORK) k3d cluster create --config $(CONFIG_FILE)
	@echo "[INFO] K3d Cluster $(CLUSTER_NAME) - Creation Completed."

.PHONY: init
init.cluster: create.network start.registry create.cluster ## Initialize the cluster

.PHONY: delete.cluster
delete.cluster: ## Delete the k3d cluster
	@echo "[INFO] K3d Cluster $(CLUSTER_NAME) - Deletion started."
	@k3d cluster delete $(CLUSTER_NAME)
	@echo "[INFO] K3d Cluster $(CLUSTER_NAME) - Deletion Completed."

.PHONY: get.nodes
get.nodes: ## List Kubernetes nodes
	kubectl get nodes -o wide

.PHONY: describe.cluster
describe.cluster: ## Describe the k3d cluster
	k3d cluster list $(CLUSTER_NAME)

.PHONY: build
build: ## Build Python and Rego policies
	cd $(SOURCE_DIR) && make  build

build.push: build ## Build, push nginx image
	docker tag $(MICROSERVICE_IMAGE_NAME):latest $(IMAGE_NAME):0.1.0
	docker push $(IMAGE_NAME)

.PHONY: start.localstack
start.localstack:  ## Start localstack service for S3
	cd $(SOURCE_DIR) && DOCKER_NETWORK=$(DOCKER_NETWORK) make  start.localstack

.PHONY: stop.localstack
stop.localstack:
	cd $(SOURCE_DIR) && make  stop.localstack

.PHONY: deploy.rego
deploy.rego:  ## Deploy the policy to S3 bucket
	cd $(SOURCE_DIR) ; DOCKER_NETWORK=$(DOCKER_NETWORK) make  deploy.rego deploy.rego.validate

deploy.microservice: ## Deploy microservice 
	helm install restapi-opa restapi-opa --namespace restapi-opa --create-namespace

undeploy.microservice: ## Uninstall microservice 
	helm uninstall restapi-opa --namespace restapi-opa || true
	kubectl delete namespace restapi-opa --ignore-not-found

test.deployment: ## Test if application is deployed
	curl --fail http://localhost:8080 || echo "Microservices not reachable"

test.rego.integration: ## Test an OPA auhtorized API endpoint
	cd $(SOURCE_DIR) && make test.rego.integration

test: test.deployment test.rego.integration ## Perform test of the deployment


deploy.view: ## View  pods, svc, deployment
	kubectl get configmap,pods,svc,deployment,replicaset,hpa -n restapi-opa
	
delete.cluster: undeploy.microservice stop.registry delete.cluster delete.network ## Cleanup resource created during the session.