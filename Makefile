# ------------------------------------------ #
# AI Knowledge Copilot - Root Makefile        #
# ------------------------------------------ #

.PHONY: help setup backend frontend docker-build docker-push terraform-validate terraform-apply terraform-destroy

help: ## Show this help message
	@echo "AI Knowledge Copilot - DevOps Capstone"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

setup: ## Install all dependencies (backend and frontend)
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Setup complete!"

backend: ## Run backend locally
	cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

frontend: ## Run frontend locally
	cd frontend && npm run dev

docker-build: ## Build all Docker images
	@echo "Building backend image..."
	docker build -t ai-knowledge-copilot-backend:latest backend
	@echo "Building frontend image..."
	docker build -t ai-knowledge-copilot-frontend:latest frontend
	@echo "Docker images built!"

docker-push: ## Push images to registry (requires auth)
	docker push ai-knowledge-copilot-backend:latest
	docker push ai-knowledge-copilot-frontend:latest

terraform-init: ## Initialize Terraform
	cd terraform && terraform init

terraform-validate: ## Validate Terraform configuration
	cd terraform && terraform validate

terraform-plan: ## Plan Terraform changes
	cd terraform && terraform plan

terraform-apply: ## Apply Terraform changes
	cd terraform && terraform apply -auto-approve

terraform-destroy: ## Destroy Terraform-managed resources
	cd terraform && terraform destroy -auto-approve

test: ## Run all tests
	@echo "Running backend tests..."
	cd backend && pytest tests/ -v
	@echo "Running frontend tests..."
	cd frontend && npx vitest run

helm-lint: ## Lint Helm chart
	helm lint helm/ai-knowledge-copilot

helm-install: ## Install Helm chart locally
	helm install ai-knowledge-copilot helm/ai-knowledge-copilot --namespace ai-knowledge-copilot --create-namespace

helm-uninstall: ## Uninstall Helm chart
	helm uninstall ai-knowledge-copilot --namespace ai-knowledge-copilot

clean: ## Clean build artifacts
	rm -rf backend/.venv
	rm -rf frontend/node_modules
	rm -rf .terraform
	rm -rf terraform/**/.terraform
	rm -f terraform/**/*.tfstate
	rm -f terraform/**/*.tfstate.*
