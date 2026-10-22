# AI Knowledge Copilot - Deployment Guide

## Overview

This guide provides instructions for deploying the AI Knowledge Copilot application to Azure.

## Prerequisites

### Step 2: Terraform Deployment

```bash
# Initialize Terraform
cd terraform
terraform init

# Select environment (dev, staging, or prod)
cd environments/dev

# Review variables
cat variables.tf

# Create tfvars file (if not exists)
cp terraform.tfvars.example terraform.tfvars

### Step 5: Access the Application

```bash
# Get frontend service endpoint
az aks get-credentials --resource-group ai-knowledge-copilot-dev-rg --name aikacopilot-aks-dev
kubectl get svc ai-knowledge-copilot-frontend -n ai-knowledge-copilot

# Access the application via browser
# Open the external IP or use port-forwarding
kubectl port-forward svc/ai-knowledge-copilot-frontend 5173:80 -n ai-knowledge-copilot
```

---

## Deployment Option 2: Azure App Service

### Step 1: Terraform Deployment (App Service Module)

```bash

### Step 4: Configure App Settings

```bash
# Set Key Vault reference
az webapp config appsettings set --name aicopilotappservice-dev \
  --resource-group ai-knowledge-copilot-dev-rg \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://YOUR-OPENAI.resource.azure.com/" \
    AZURE_OPENAI_API_KEY="@Microsoft.KeyVault(SecretUri=https://aicopi01kvdev.vault.azure.net/secrets/AZURE_OPENAI_API_KEY/...)"

# Add database connection string
az webapp config appsettings set --name aicopilotappservice-dev \
  --resource-group ai-knowledge-copilot-dev-rg \
  --settings DATABASE_URL="@Microsoft.KeyVault(SecretUri=https://aicopi01kvdev.vault.azure.net/secrets/DATABASE_URL/...)"

# Enable Managed Identity and assign roles
az webapp identity assign --name aicopilotappservice-dev --resource-group ai-knowledge-copilot-dev-rg
```

---

## Configuration Management

### Environment Variables

| Environment | Source | Notes |
|-------------|--------|-------|
| Backend | ConfigMap + Secret | Azure Key Vault secrets mounted in AKS |
| Frontend | ConfigMap | API URL and environment settings |
| Terraform | tfvars files | Never commit secrets |

### Secrets Management

1. **Azure Key Vault**: Primary secrets storage
2. **GitHub Secrets**: CI/CD secrets
3. **Azure Key Vault for AKS**: Access via managed identity

### Deployment Keys to Azure Key Vault

```bash
# Create a Key Vault
az keyvault create --name "aicopi01kvdev" --resource-group "ai-knowledge-copilot-dev-rg" --location "East US"

# Add secrets (in production, use secure generation)
az keyvault secret set --vault-name "aicopi01kvdev" --name "AZURE_OPENAI_API_KEY" --value "your-key-value"

# Grant AKS access to Key Vault
az role assignment create --assignee <AKS_OBJECT_ID> --role "Key Vault Secrets User" --scope "/subscriptions/.../resourceGroups/ai-knowledge-copilot-dev-rg/providers/Microsoft.KeyVault/vaults/aicopi01kvdev"
```

---

## Accessing the Application

### AKS

```bash
# Port forward for local testing
kubectl port-forward svc/ai-knowledge-copilot-frontend 5173:80 -n ai-knowledge-copilot

# View logs
kubectl logs -n ai-knowledge-copilot -l app=ai-knowledge-copilot --tail=100

# Get pods
kubectl get pods -n ai-knowledge-copilot -o wide

# Scale deployment
kubectl scale deployment/ai-knowledge-copilot-backend --replicas=5 -n ai-knowledge-copilot
```

### App Service

```bash
# Get URL
az webapp show --name aicopilotappservice-dev --resource-group ai-knowledge-copilot-dev-rg --query "defaultHostName" -o tsv

# View logs
az webapp log tail --name aicopilotappservice-dev --resource-group ai-knowledge-copilot-dev-rg

# Restart
az webapp restart --name aicopilotappservice-dev --resource-group ai-knowledge-copilot-dev-rg
```

---

## Verification Checklist

- [ ] Terraform infrastructure deployed successfully
- [ ] Container images built and pushed to ACR
- [ ] AKS cluster deployed with applications running
- [ ] Frontend accessible via browser
- [ ] Backend API responds at /health
- [ ] Document upload works end-to-end
- [ ] Question/answer functionality works
- [ ] Monitoring enabled and accessible
- [ ] Secrets properly managed
- [ ] Security scan passed

# Initialize Terraform
cd terraform
terraform init

# Select environment
cd environments/dev

# Apply deployment (includes App Service)
terraform apply -var="enable_app_service=true"

# Save outputs
terraform output > terraform-outputs-appservice.json
```

### Step 2: Deploy Application

```bash
# Use Azure App Service deploy via GitHub Actions
# OR manually deploy using Az CLI

# Login to Azure
az login

# Deploy via Azure CLI
az webapp deploy --src-path ./backend --name aicopilotappservice-dev --resource-group ai-knowledge-copilot-dev-rg

# OR use Azure App Service with Docker
az webapp create --name aicopilotappservice-dev \
  --resource-group ai-knowledge-copilot-dev-rg \
  --plan aicopilot-asp-dev \
  --deployment-container-image-name aicopi01dev.azurecr.io/ai-knowledge-copilot-backend:latest
```

### Step 3: Configure App Settings

```bash
# Get the resource ID for the App Service
APP_SERVICE_ID=$(az appservice list --query "[?name=='aicopilotappservice-dev'].id" -o tsv)

# Set app settings
az webapp config appsettings set --name aicopilotappservice-dev \
  --resource-group ai-knowledge-copilot-dev-rg \
  --settings \
    AZURE_OPENAI_ENDPOINT=https://YOUR-OPENAI.resource.azure.com/ \
    AZURE_OPENAI_API_KEY=your-api-key \
    DATABASE_URL=postgresql://user:pass@host:5432/dbname \
    AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
```


# Edit terraform.tfvars with your values
# - location
# - resource names
# - database admin password (generate a secure one)
# - common tags

# Validate configuration
terraform validate

# Plan deployment
terraform plan -out=tfplan

# Apply deployment
terraform apply tfplan

# Save state
terraform output > terraform-outputs.json
```

### Step 3: Docker Image Build and Push

```bash
# Login to Azure Container Registry
az acr login --name aicopi01dev

# Build backend image
docker build -t ai-knowledge-copilot-backend:latest backend
docker tag ai-knowledge-copilot-backend:latest aicopi01dev.azurecr.io/ai-knowledge-copilot-backend:latest
docker push aicopi01dev.azurecr.io/ai-knowledge-copilot-backend:latest

# Build frontend image
docker build -t ai-knowledge-copilot-frontend:latest frontend
docker tag ai-knowledge-copilot-frontend:latest aicopi01dev.azurecr.io/ai-knowledge-copilot-frontend:latest
docker push aicopi01dev.azurecr.io/ai-knowledge-copilot-frontend:latest
```

### Step 4: Helm Deployment

```bash
# Create config values for your environment
cp helm/ai-knowledge-copilot/values.yaml helm/ai-knowledge-copilot/values-dev.yaml

# Edit values-dev.yaml with your settings:
# - backend.image.repository
# - backend.image.tag
# - backend.envSecrets
# - frontend.apiUrl
# - namespace

# Deploy to AKS
helm upgrade --install ai-knowledge-copilot helm/ai-knowledge-copilot \
  --namespace ai-knowledge-copilot \
  --create-namespace \
  --values helm/ai-knowledge-copilot/values-dev.yaml \
  --wait

# Verify deployment
kubectl get pods -n ai-knowledge-copilot
kubectl get services -n ai-knowledge-copilot
```


1. **Azure Subscription**: With an active subscription
2. **Azure CLI**: Installed and configured
3. **Terraform**: Version 1.5+ installed
4. **Azure Credentials**: Service principal or managed identity
5. **Docker**: Installed (for building images locally)
6. **Helm**: Version 3.14+ installed
7. **Kubernetes CLI (kubectl)**: Installed

## Deployment Options

The application supports two deployment options:
1. **AKS (Azure Kubernetes Service)** - Recommended for production
2. **Azure App Service** - Alternative for simpler deployments

---

## Deployment Option 1: AKS

### Step 1: Prerequisites

Ensure you have the required Azure resources created using Terraform:

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "bccd0532-eb8d-447b-b3d3-bdb802e4adcb"
```
