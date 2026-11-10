# Azure Resource Verification Guide

This guide shows where to find every resource in the Azure Portal, how to verify containers/images are working, and what to look for to confirm your AI Knowledge Copilot is running correctly.

## Prerequisites

- **Tenant ID**: `8d803e1b-28bd-437c-aac9-8eeefe2b29ab`
- **Subscription ID**: `bccd0532-eb8d-447b-b3d3-bdb802e4adcb`
- **Resource Group**: `aicopilot-dev-rg` (created by Terraform)

## 1. Azure Container Registry (ACR) — Container Images

### Portal Location
1. Go to **https://portal.azure.com**
2. Sign in with your tenant
3. Select subscription: `bccd0532-eb8d-447b-b3d3-bdb802e4adcb`
4. Navigate to: **Containers** → **Container registries**
5. Click your registry (name pattern: `aicopdev<random>acr`)

### How to Verify Images
1. Open the Container Registry resource
2. Click **Repositories** in the left menu
3. You should see:
   - `ai-knowledge-copilot-backend`
   - `ai-knowledge-copilot-frontend`
4. Click a repository → **Tags** to see image versions (format: `20261023-<sha>`)

### Via Azure CLI
```bash
az login --tenant 8d803e1b-28bd-437c-aac9-8eeefe2b29ab
az acr repository list --name <your-acr-name> --output table
az acr repository show-tags --name <your-acr-name> --repository ai-knowledge-copilot-backend
```

## 2. Azure Kubernetes Service (AKS) — Verify Deployment

### Portal Location
1. Navigate to: **Kubernetes services** → Click your AKS cluster (`aks-copilot-dev-*`)
2. Check **Overview** blade:
   - **Provisioning state**: Should be "Succeeded"
   - **Node count** and **VM size**
   - **FQDN**: The cluster endpoint

### How to Verify Pods are Running
1. Click **Workloads** → **Containers** in left menu
2. Namespace: `ai-knowledge-copilot`
3. You should see:
   - `ai-knowledge-copilot-backend` pods (**Running**, **1/1 Ready**)
   - `ai-knowledge-copilot-frontend` pods (**Running**, **1/1 Ready**)
4. Click on a pod → **Containers** tab to see image and status

### Via kubectl
```bash
az aks get-credentials --resource-group aicopilot-dev-rg --name aks-copilot-dev-* --overwrite-existing
kubectl get pods -n ai-knowledge-copilot
kubectl get services -n ai-knowledge-copilot
kubectl get ingress -n ai-knowledge-copilot
```

### Expected Output
```
NAME                                     READY   STATUS    RESTARTS   AGE
ai-knowledge-copilot-backend-<hash>      1/1     Running   0          5m
ai-knowledge-copilot-frontend-<hash>     1/1     Running   0          5m
```


## 3. Azure App Service — Verify Deployment

### Portal Location
1. Navigate to: **App Services** → Click your web app (`aicopilot-dev-app`)
2. Check **Overview** blade:
   - **Status**: Should be "Running"
   - **Default domain**: `https://aicopilot-dev-app.azurewebsites.net`

### Verify Health Endpoint
Open in browser:
```
https://aicopilot-dev-app.azurewebsites.net/health
```

Expected response:
```json
{"status": "healthy", "service": "ai-knowledge-copilot", "version": "1.0.0"}
```

## 4. Azure PostgreSQL — Verify Database

### Portal Location
1. Navigate to: **Azure Database for PostgreSQL flexible servers**
2. Click your server (`aicopilot-dev-psql`)
3. **Server status**: Should be "Ready"

### Verify Connectivity
```bash
az postgres flexible-server connect \
  --name aicopilot-dev-psql \
  --admin-user copilotadmin \
  --database aikcopilot
```

## 5. Azure Blob Storage — Verify Document Storage

### Portal Location
1. Navigate to: **Storage accounts** → Click your storage account (`aicopdev<random>sa`)
2. Click **Containers** → Container: `documents` (access level: Private)
3. Upload a test document via the frontend UI
4. Refresh → You should see the uploaded `.bin` file

## 6. Azure Key Vault — Verify Secret Management

### Portal Location
1. Navigate to: **Key vaults** → Click your vault (`aicopdev<random>kv`)
2. Click **Secrets** in left menu
3. Verify secrets exist: AZURE-OPENAI-ENDPOINT, DATABASE-URL, etc.

## 7. Azure Monitor / Application Insights — Verify Monitoring

### Portal Location
1. Navigate to: **Monitor** → **Application Insights** → Click your resource (`aicopilot-dev-ai`)
2. Click **Overview** → Check connection string
3. Click **Metrics** → Select `Server requests` to verify traffic

### Create Dashboard
Navigate to: **Monitor** → **Dashboards** → **Create**
Add tiles for: AKS CPU/Memory, App Service 4xx/5xx, App Insights requests

## Quick Verification Checklist

| Resource | Portal Path | Healthy Indicator |
|----------|-------------|-------------------|
| ACR | Container registries → `<name>` | Backend + frontend repos with tags |
| AKS | Kubernetes services → `<name>` | Pods Running, 1/1 Ready |
| App Service | App Services → `<name>` | Status: Running, health endpoint 200 |
| PostgreSQL | Azure Database for PostgreSQL → `<name>` | Server status: Ready |
| Blob Storage | Storage accounts → `<name>` | Container `documents` exists |
| Key Vault | Key vaults → `<name>` | Secrets listed |
| App Insights | Monitor → Application Insights → `<name>` | Metrics flowing |

## Azure Tenant & Subscription Details

| Setting | Value |
|---------|-------|
| Tenant ID | `8d803e1b-28bd-437c-aac9-8eeefe2b29ab` |
| Subscription ID | `bccd0532-eb8d-447b-b3d3-bdb802e4adcb` |
| Resource Group | `aicopilot-dev-rg` |
| Location | East US / Central US (AKS) |

## Common Issues

**Backend Returns 502**: Check `kubectl get pods -n ai-knowledge-copilot`, verify readiness probe path is `/health`

**File Upload Fails**: Verify storage container name is `documents`, check connection string in secrets

**Image Not Found in ACR**: Verify CI/CD pushed images, check image tag format matches deployment

