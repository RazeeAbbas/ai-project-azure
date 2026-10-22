# AI Knowledge Copilot — Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USERS (Browser)                          │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ HTTPS
              ┌───────────────────▼───────────────────┐
              │          Azure Load Balancer            │
              │       (AKS Ingress / App Service)       │
              └───────────────────┬───────────────────┘
                                  │
          ┌───────────────────────▼──────────────────────────┐
          │                  Frontend Layer                    │
          │          React SPA (Nginx, port 80)               │
          │    AKS Deployment + App Service (Linux)            │
          └───────────────────────┬──────────────────────────┘
                                  │ REST API /api/*
          ┌───────────────────────▼──────────────────────────┐
          │                  Backend Layer                     │
          │            FastAPI (Python, port 8000)             │
          │    AKS Deployment + App Service (Linux)            │
          └──┬─────────┬──────────┬────────────┬─────────────┘
             │         │          │             │
    ┌────────▼──┐ ┌────▼────┐ ┌──▼──────┐ ┌───▼─────────┐
    │  Azure    │ │ Azure   │ │ Azure   │ │   Redis     │
    │ OpenAI    │ │   AI    │ │  Blob   │ │  (Cache)    │
    │ (GPT-4o)  │ │ Search  │ │ Storage │ │             │
    │Embeddings │ │(Vectors)│ │  Docs   │ │             │
    └───────────┘ └─────────┘ └─────────┘ └─────────────┘
                       │
          ┌────────────▼───────────┐
          │  Azure PostgreSQL       │
          │  Flexible Server       │
          │  (Document metadata)   │
          └────────────────────────┘

Infrastructure Layer:
  ┌─────────────────────────────────────────┐
  │           Terraform Modules              │
  │  resource-group / networking / acr      │
  │  aks / app-service / database           │
  │  storage / key-vault / monitoring       │
  └─────────────────────────────────────────┘

Delivery Layer:
  ┌─────────────────────────────────────────┐
  │         GitHub Actions CI/CD             │
  │  test → build → scan → push → deploy   │
  └─────────────────────────────────────────┘

Observability:
  ┌─────────────────────────────────────────┐
  │      Azure Monitor + App Insights        │
  │   Log Analytics Workspace + Dashboards   │
  └─────────────────────────────────────────┘
```

## RAG Pipeline

```
User Question
     │
     ▼
[Backend /api/questions]
     │
     ├─► Embedding Service (Azure OpenAI ada-002)
     │         │
     │         ▼
     │   [Question Vector]
     │         │
     ├─► Vector Search (Azure AI Search)
     │         │
     │         ▼
     │   [Top-K Chunks + Scores]
     │         │
     ├─► Context Assembly
     │         │
     │         ▼
     │   [Grounded Prompt]
     │         │
     └─► Azure OpenAI GPT-4o-mini
               │
               ▼
         [Grounded Answer + Sources]
               │
               ▼
         Response to User
```

## Deployment Environments

| Environment | AKS Nodes | DB SKU         | App Service SKU | ACR SKU  |
|-------------|-----------|----------------|-----------------|----------|
| Dev         | 1×B2s     | B_Standard_B1ms| B1              | Basic    |
| Staging     | 2×B2s     | B_Standard_B1ms| B2              | Standard |
| Prod        | 3+×D2ds   | GP_D2ds_v4     | P1v2            | Premium  |

## AKS vs App Service — Key Differences

| Aspect         | AKS                          | App Service                  |
|----------------|------------------------------|------------------------------|
| Deployment     | Kubernetes manifests / Helm  | Docker container via az CLI  |
| Scaling        | HPA + cluster autoscaler     | Auto-scale rules             |
| Networking     | VNet, Ingress controller     | Managed by Azure             |
| Complexity     | Higher (K8s knowledge)       | Lower (PaaS managed)         |
| Cost           | VM-based (pay for nodes)     | Plan-based (more predictable)|
| Blue/Green     | Manual with Helm             | Deployment slots (built-in)  |
| Config         | ConfigMaps + Secrets         | App Settings + Key Vault ref |
