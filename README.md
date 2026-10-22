# AI Knowledge Copilot - DevOps Capstone Project

## Project Overview

Build, deploy, automate, secure, monitor, and operate an AI-enabled knowledge assistant on Microsoft Azure. The application allows internal users to upload approved documents and ask natural language questions, receiving grounded answers sourced from the knowledge base.

## Repository Structure

```
project/
├── frontend/             # React/Next.js frontend
├── backend/              # FastAPI backend with RAG
├── terraform/            # Azure infrastructure (Terraform)
│   ├── modules/          # Reusable modules
│   └── environments/     # dev/staging/prod
├── helm/                 # Helm charts
├── kubernetes/           # K8s manifests
├── tests/                # Test suites
├── docs/                 # Documentation
├── .github/workflows/    # CI/CD pipelines
├── docker-compose.yml    # Local development
├── .dockerignore
└── README.md
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| AI/RAG | Azure OpenAI + LangChain |
| Vector Store | Azure AI Search (or pgvector) |
| Database | Azure PostgreSQL |
| Storage | Azure Blob Storage |
| Container Registry | Azure Container Registry |
| Kubernetes | Azure Kubernetes Service |
| App Service | Azure App Service |
| IaC | Terraform |
| CI/CD | GitHub Actions |
| Monitoring | Azure Monitor + Application Insights |

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.11+
- Terraform 1.5+
- Docker Desktop
- Azure CLI

### Local Development

1. Clone the repository
2. Configure environment variables (see `.env.example` files)
3. Start local services:
   ```bash
   docker-compose up -d
   ```
4. Install and run backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn src.main:app --reload
   ```
5. Install and run frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full architecture diagram and explanation.

## Project Components

### 1. Frontend
- React + Vite
- Document upload/selection
- Chat interface
- Configurable API endpoint via environment variable

### 2. Backend
- FastAPI REST API
- Document ingestion workflow
- Question/answer endpoint with RAG
- Structured logging
- Input validation

### 3. Terraform Modules
Reusable modules for:
- Resource Group
- Networking (VNet, Subnets, NSG)
- Azure Container Registry
- AKS (Kubernetes)
- App Service
- Database (PostgreSQL)
- Storage (Blob Storage)
- Key Vault
- Monitoring (Application Insights)

### 4. Helm Chart
Environment-specific values for AKS deployment.

### 5. CI/CD Pipeline
- GitHub Actions workflow
- Build → Test → Scan → Push → Deploy
- Support for both AKS and App Service

## Documentation

- [Architecture](docs/architecture.md)
- [Deployment](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Rollback](docs/rollback.md)

## Azure Resources to Monitor

See the final section of this README for guidance on where to find each resource in the Azure Portal.

## License

MIT
