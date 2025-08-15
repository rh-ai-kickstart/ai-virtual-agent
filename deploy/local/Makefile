# AI Virtual Agent - Local Development Makefile
# Run `make help` to see available targets.

.PHONY: help dev backend frontend llamastack stop dev-deps backend-deps frontend-deps \
        build-frontend lint lint-backend lint-frontend test test-unit test-int \
        compose-up compose-down dev-compose-up dev-compose-down dev-compose-restart \
        dev-compose-logs dev-compose-build dev-compose-status image-build

# -----------------------------------------------------------------------------
# Helper
# -----------------------------------------------------------------------------
help: ## Show help for local development targets
	@echo "AI Virtual Agent - Local Development Commands"
	@echo "============================================="
	@echo ""
	@echo "🚀 Development Commands:"
	@grep -E '^(dev|backend|frontend|llamastack|stop):.*?## ' $(MAKEFILE_LIST) | \
		sed -e 's/^/  /' -e 's/:.*## / - /'
	@echo ""
	@echo "📦 Dependencies & Setup:"
	@grep -E '^(dev-deps|backend-deps|frontend-deps):.*?## ' $(MAKEFILE_LIST) | \
		sed -e 's/^/  /' -e 's/:.*## / - /'
	@echo ""
	@echo "🔨 Build Commands:"
	@grep -E '^(build-frontend):.*?## ' $(MAKEFILE_LIST) | \
		sed -e 's/^/  /' -e 's/:.*## / - /'
	@echo ""
	@echo "🧪 Testing & Quality:"
	@grep -E '^(test|test-unit|test-int|lint|lint-backend|lint-frontend):.*?## ' $(MAKEFILE_LIST) | \
		sed -e 's/^/  /' -e 's/:.*## / - /'
	@echo ""
	@echo "🐳 Container Commands:"
	@grep -E '^(compose-up|compose-down|image-build):.*?## ' $(MAKEFILE_LIST) | \
		sed -e 's/^/  /' -e 's/:.*## / - /'
	@echo ""
	@echo "🔧 Development Container Commands:"
	@grep -E '^(dev-compose-up|dev-compose-down|dev-compose-restart|dev-compose-logs|dev-compose-build|dev-compose-status):.*?## ' $(MAKEFILE_LIST) | \
		sed -e 's/^/  /' -e 's/:.*## / - /'

# -----------------------------------------------------------------------------
# Development (runs local_dev scripts)
# -----------------------------------------------------------------------------

# Start backend, frontend, and LlamaStack (detached)
dev: ## Run backend, frontend, and LlamaStack together
	./dev/run_local.sh

backend: ## Run backend dev server with hot-reload (uvicorn)
	./dev/local_backend.sh

frontend: ## Run frontend Vite dev server
	./dev/local_frontend.sh

llamastack: ## Run local LlamaStack server (for dev)
	./dev/local_llamastack.sh

stop: ## Stop all dev services started via ./dev scripts
	./dev/stop_local.sh

# -----------------------------------------------------------------------------
# Build helpers (build without installing)
# -----------------------------------------------------------------------------
build-frontend: ## Build frontend application for production
	cd ../../frontend && npm run build

# -----------------------------------------------------------------------------
# Installation helpers
# -----------------------------------------------------------------------------
dev-deps: backend-deps frontend-deps ## Install backend & frontend development dependencies

backend-deps: ## Create Python venv and install backend requirements
	cd ../../ && python -m venv venv && . venv/bin/activate && pip install -r backend/requirements.txt

frontend-deps: ## Install Node dependencies
	cd ../../frontend && npm install

# -----------------------------------------------------------------------------
# Quality & Tests
# -----------------------------------------------------------------------------
lint-backend: ## Run backend linters (pre-commit)
	cd ../../backend && pre-commit run --all-files --show-diff-on-failure || true

lint-frontend: ## Run frontend linters (eslint & prettier)
	cd ../../frontend && npm run lint

lint: lint-backend lint-frontend ## Run all linters

test-unit: ## Run unit tests only
	cd ../../ && ./scripts/ci/run_tests.sh --unit

test-int: ## Run integration tests only
	cd ../../ && ./scripts/ci/run_tests.sh --integration

test-all: ## Run all tests (unit + integration)
	cd ../../ && ./scripts/ci/run_tests.sh --all

test: lint test-all ## Run full test & lint suite

# -----------------------------------------------------------------------------
# Container / Compose helpers
# -----------------------------------------------------------------------------
compose-up: ## Start services with podman/docker compose
	cd ../../ && podman compose --file compose.yaml up -d

compose-down: ## Stop compose services
	cd ../../ && podman compose --file compose.yaml down

image-build: ## Build application container image
	cd ../../ && podman build -t ai-virtual-agent:dev .

dev-compose-up: ## Start development services with podman compose (uses .env and compose.dev.yaml)
	./dev/start-dev.sh

dev-compose-down: ## Stop development services
	./dev/stop-dev.sh

dev-compose-restart: ## Restart development services
	cd ../../ && podman compose -f deploy/local/compose.dev.yaml restart

dev-compose-logs: ## View logs from development services
	cd ../../ && podman compose -f deploy/local/compose.dev.yaml logs -f

dev-compose-build: ## Rebuild and start development services
	cd ../../ && podman compose -f deploy/local/compose.dev.yaml up --build -d

dev-compose-status: ## Show status of development services
	cd ../../ && podman compose -f deploy/local/compose.dev.yaml ps