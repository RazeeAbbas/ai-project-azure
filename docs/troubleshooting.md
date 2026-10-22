# AI Knowledge Copilot - Troubleshooting Guide

## Overview

This guide provides troubleshooting steps for common issues with the AI Knowledge Copilot application.

---

## Application/Backend Issues

### 1. Health Check Fails

**Symptoms:**
- `/health` endpoint returns 503
- "database" or "azure_openai" check shows error

**Investigation:**
```bash
# Check backend pod logs
kubectl logs -n ai-knowledge-copilot -l app=ai-knowledge-copilot --tail=100

# Check service status
kubectl get pods -n ai-knowledge-copilot -o wide
kubectl describe pod <pod-name> -n ai-knowledge-copilot

### 2. Question/Answer Not Working

**Symptoms:**
- /api/questions endpoint returns error
- Hmm says "knowledge base empty" repeatedly

**Steps:**
1. Verify document ingestion completed
2. Check vector database has data
3. Verify OpenAI embedding model is available
4. Check API logs for processing errors

**Commands:**
```bash
# Check ingestion status
kubectl logs -n ai-knowledge-copilot -l app=ai-knowledge-copilot | grep -i ingest

# Check vector database
kubectl logs -n ai-knowledge-copilot <vector-db-container> | grep -i index

# Query the API
curl -X POST https://<backend-url>/api/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?"}'
```

---

## Database Issues

### 2. Container Crashes

**Symptoms:**
- `CrashLoopBackOff` state
- Exit code 1 or 137

**Investigation:**
```bash
# View recent logs
kubectl logs <pod-name> -n ai-knowledge-copilot --previous

# Check exit codes
kubectl describe pod <pod-name> | grep -i exit
```

**Common Solutions:**
- Missing environment variables
- Incorrect configuration
- Out of memory → Increase limit
- Missing dependencies

---

## Network Issues

### 1. Frontend Cannot Reach Backend

**Symptoms:**
- Chat not working
- API errors in console

**Diagnosis:**
```bash
# Check service connectivity
kubectl get svc -n ai-knowledge-copilot

# Test connection
kubectl run -it --rm --image=curlimages/curl curl-test -- curl -v http://backend-service:8000/health

# Check DNS
kubectl get endpoints -n ai-knowledge-copilot
```

**Solutions:**
- Verify service selector matches deployment
- Check environment variable (VITE_API_BASE_URL)
- Review NetworkPolicies

### 2. Ingress/Session Issues

**Symptoms:**
- 502/503 errors
- Ingress path not working

**Diagnosis:**
```bash
kubectl get ingress -A
kubectl describe ingress <ingress-name>
```

**Solutions:**
- Verify host/path configuration
- Check TLS certificate
- Review backend service status

---

## Azure Resource Issues

### 1. Terraform Deployment Failures

**Symptoms:**
- Plan fails
- Apply fails with errors

**Common Issues:**

| Error | Solution |
|-------|----------|
| "Resource group not found" | Use correct subscription |
| "Permission denied" | Grant required role assignments |
| "East US not available" | Use region with availability |
| "State lock" | Wait for manual lock release |

**Commands:**
```bash
# Check terraform state
terraform state list
terraform output

# Review detailed logs
terraform apply -debug
```

### 2. Azure Container Registry Issues

**Symptoms:**
- Image pull failures
- Docker login failed

**Diagnosis:**
```bash
# Login to ACR
az acr login --name aicopi01dev

# List repositories
az acr repository list --name aicopi01dev --output table

# Pull image manually
docker pull aicopi01dev.azurecr.io/ai-knowledge-copilot-backend:latest
```

### 3. AKS Issues

**Symptoms:**
- Nodes not ready
- Cluster unreachable

**Diagnosis:**
```bash
# Check nodes
az aks get-credentials --resource-group ai-knowledge-copilot-dev-rg --name aikacopilot-aks-dev
kubectl get nodes

# Check cluster events
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

---

## Monitoring & Logging

### 1. Application Logs Not Showing

**Symptoms:**
- No logs in Azure Monitor
- Logs not visible in Application Insights

**Solutions:**
- Verify instrumentation key is configured
- Check log level (set to DEBUG for development)
- Review logging configuration

### 2. Missing Metrics

**Symptoms:**
- Dashboard shows no data
- Alerts not triggering

**Solutions:**
- Check metric dimensions
- Verify Application Insights connections
- Review API limits

---

## Recovery Actions

### 1. Restart a Deployment

```bash
# Restart backend
kubectl rollout restart deployment/ai-knowledge-copilot-backend -n ai-knowledge-copilot

# Restart frontend
kubectl rollout restart deployment/ai-knowledge-copilot-frontend -n ai-knowledge-copilot
```

### 2. Roll Back Deployment

```bash
# Helm rollback (enterprise)
helm rollback ai-knowledge-copilot <revision> -n ai-knowledge-copilot

# Kubernetes rollback
kubectl rollout undo deployment/ai-knowledge-copilot-backend -n ai-knowledge-copilot
```

### 3. Recreate Pods

```bash
# Delete pods to force recreation
kubectl delete pod -l app=ai-knowledge-copilot -n ai-knowledge-copilot
```

---

## When to Contact Support

- Azure subscription exhausted (quotas)
- Critical security vulnerabilities
- Data loss or corruption
- Failed production deployments requiring manual intervention

For additional support:
- Azure Support: https://azure.microsoft.com/support
- Terraform documentation: https://developer.hashicorp.com/terraform/docs
- AKS FAQs: https://learn.microsoft.com/azure/aks/faqs


### 1. Backend Cannot Connect to Database

**Symptoms:**
- Connection refused errors
- "timeout" in logs

**Diagnosis:**
```bash
# Test database connectivity
kubectl get pods -n ai-knowledge-copilot
kubectl exec -n ai-knowledge-copilot <backend-pod> -- nc -zv <db-host> 5432

# Check connection string
kubectl get configmap ai-kc-backend-config -n ai-knowledge-copilot -o yaml | grep DATABASE_URL
```

**Solutions:**
1. Verify PostgreSQL server is running
2. Check firewall rules allow connection from AKS
3. Verify credentials in config
4. Check database service is healthy

### 2. Database Slow Performance

**Symptoms:**
- Query timeouts
- High latency

**Investigation:**
- Check database metrics in Azure Portal
- Connection count
- Query performance

**Solutions:**
- Scale up database tier
- Add indexes
- Tune connection pool settings

---

## Container/Container Issues

### 1. Pods Not Becoming Ready

**Symptoms:**
- `READY` status shows 0/1 or 0/2
- Pods in `Pending` or `CrashLoopBackOff`

**Diagnosis:**
```bash
# Check pod status
kubectl get pods -n ai-knowledge-copilot

# Describe pod for events
kubectl describe pod <pod-name> -n ai-knowledge-copilot

# Check resource limits
kubectl get pods -n ai-knowledge-copilot -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.containers[0].resources}{"\n"}{end}'
```

**Common Causes:**
- Resource limits too low → Increase requests/limits
- Image not found → Check image name and pull secret
- Health check failing → Review liveness probe configuration


# Test endpoints
kubectl exec -n ai-knowledge-copilot <pod-name> -- curl http://localhost:8000/health
```

**Common Causes & Solutions:**

| Issue | Solution |
|-------|----------|
| Missing environment variables | Check ConfigMap/Secret mounted correctly |
| Database connection failure | Verify connection string, DB is running |
| OpenAI authentication failure | Check API key, region, deployment name |
| Missing index | Run vector database initialization |
