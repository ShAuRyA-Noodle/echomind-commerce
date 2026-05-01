# Echomind Commerce - developer Makefile
#
# Run `make help` for the full target table.

SHELL := /bin/bash
COMPOSE ?= docker compose
BACKEND_SVC ?= backend
FRONTEND_SVC ?= frontend
BACKEND_PORT ?= 8000

.DEFAULT_GOAL := help

.PHONY: help dev build down logs backend-shell frontend-shell health \
        seed-shopify neo4j-init test lint fmt clean

help: ## Print all targets (see Makefile.help)
	@if [ -f Makefile.help ]; then cat Makefile.help; else \
	  awk 'BEGIN{FS=":.*##"; printf "Targets:\n"} /^[a-zA-Z_-]+:.*##/ {printf "  %-18s %s\n",$$1,$$2}' $(MAKEFILE_LIST); \
	fi

dev: ## Start full stack (backend + frontend) with hot reload
	$(COMPOSE) up

build: ## Build all docker images
	$(COMPOSE) build

down: ## Stop and remove containers, networks
	$(COMPOSE) down

logs: ## Tail logs for all services
	$(COMPOSE) logs -f

backend-shell: ## Exec into running backend container
	$(COMPOSE) exec $(BACKEND_SVC) /bin/bash

frontend-shell: ## Exec into running frontend container
	$(COMPOSE) exec $(FRONTEND_SVC) /bin/sh

health: ## Curl backend /health endpoint
	@curl -fsS http://localhost:$(BACKEND_PORT)/health || \
	  (echo "backend not reachable on :$(BACKEND_PORT)" && exit 1)

seed-shopify: ## Push seeded products into the dev Shopify store
	$(COMPOSE) exec $(BACKEND_SVC) python scripts/import_to_shopify.py

neo4j-init: ## Apply Cypher schema (constraints + indexes) from backend/graph/schema.py
	$(COMPOSE) exec $(BACKEND_SVC) python -m graph.schema

test: ## Run backend pytest suite
	$(COMPOSE) exec $(BACKEND_SVC) pytest -q

lint: ## Lint Python (ruff) + frontend (eslint)
	$(COMPOSE) exec $(BACKEND_SVC) ruff check .
	$(COMPOSE) exec $(FRONTEND_SVC) npm run lint

fmt: ## Format Python (ruff format) + frontend (prettier)
	$(COMPOSE) exec $(BACKEND_SVC) ruff format .
	$(COMPOSE) exec $(FRONTEND_SVC) npx prettier --write .

clean: ## Remove containers, volumes, build cache
	$(COMPOSE) down -v --remove-orphans
