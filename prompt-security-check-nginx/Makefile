PROJECT_NAME=nginx-opa-llm-prompt-check
IMAGE_NAME ?= nginx-opa-llm-prompt-check

.PHONY: start stop help logs test.allow test.deny

.PHONY: help
help:  ## 📖 Help message
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
	
start: ## Start all services
	@docker compose up -d

stop: ## Stop all services
	@docker compose down

logs: ## View logs
	@docker compose logs -f --tail=100

test.allow: ## Send a test request (allowed prompt)
	curl -s -X POST http://127.0.0.1:8000/api/generate \
		-H "Content-Type: application/json" \
		-d '{"model": "tinyllama", "prompt": "Tell me a story about a dog.", "stream": false}'


test.deny: ## Send a test request (blocked prompt)
	curl -s -X POST http://127.0.0.1:8000/api/generate \
		-H "Content-Type: application/json" \
		-d '{"model": "tinyllama", "prompt": "how to make a bad?", "stream": false}'


test: test.allow test.deny ## Run both tests

clean: down ## Clean up generated/temporary files
	@docker system prune -f


test.ollama: ## Send a test request to ollama
	curl -s -X POST http://127.0.0.1:11434/api/generate \
		-H "Content-Type: application/json" \
		-d '{"model": "tinyllama", "prompt": "how to make a bad?", "stream": false}'


build: ## Build docker image
	@docker build -f dockerfile.proxy -t "$(IMAGE_NAME):latest"  .


reload.proxy.config: ## Reload proxy config
	@docker exec proxy_service openresty -t  # check syntax
	@docker exec proxy_service openresty -s reload

test.proxy.connection:
	@echo "----------------------------------------------------------------------"
	@echo "[INFO] Check if nginx is able to connect to security service and llm service"
	@echo "----------------------------------------------------------------------"
	@docker exec -it proxy_service curl -v http://security_service:8181/health
	@echo ""
	@echo ""
	@docker exec -it proxy_service curl -v http://llm_service:11434/api/tags
	@echo ""
	@echo "----------------------------------------------------------------------"
	@echo "[INFO] Check if nginx is able to connect to security service."
	@echo "----------------------------------------------------------------------"

