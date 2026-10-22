# AI Knowledge Copilot - Rollback Guide

## Overview

This guide provides instructions for rolling back deployments and recovering from failed releases in the AI Knowledge Copilot application.

---

## Rollback Strategies

The project supports multiple rollback strategies to ensure quick recovery from failed deployments.

### 1. Kubernetes Rolling Rollback

Kubernetes supports automatic rollback for deployments.

```bash
# View rollout history
kubectl rollout history deployment/ai-knowledge-copilot-backend -n ai-knowledge-copilot

# Roll back to previous version
kubectl rollout undo deployment/ai-knowledge-copilot-backend -n ai-knowledge-copilot


## Controlled Release Strategy

### Blue-Green Deployment

The CI/CD pipeline supports blue-green deployment for zero-downtime releases:

1. **Deploy new version** to staging environment
2. **Run smoke tests** against staging
3. **Switch traffic** to new version
4. **Monitor** for failures
5. **Keep old version** available for rollback

### Canary Deployment

For critical deployments, use canary deployment:

## Steps to Roll Back

### Step 1: Assess Damage

```bash
# Check current deployment status
kubectl get pods -n ai-knowledge-copilot
kubectl describe pods -n ai-knowledge-copilot

# Check logs for errors
kubectl logs -n ai-knowledge-copilot -l app=ai-knowledge-copilot --tail=100
```

### Step 2: Roll Back Deployment

```bash
# Choose rollback strategy:
# Option A: Kubernetes rollout undo (quickest)
kubectl rollout undo deployment/ai-knowledge-copilot-backend -n ai-knowledge-copilot

# Option B: Helm rollback (if using Helm)
helm history ai-knowledge-copilot -n ai-knowledge-copilot
helm rollback ai-knowledge-copilot <rev> -n ai-knowledge-copilot

# Option C: Redeploy with previous image tag
helm upgrade ai-knowledge-copilot helm/ai-knowledge-copilot \
  --namespace ai-knowledge-copilot \
  --set backend.image.tag=<previous-tag> \
  --wait
```


## Pre-Deployment Checks

Before deploying a new version:

1. **Run tests** locally
2. **Check image scan results**
3. **Review changelog**
4. **Verify dependencies** are up to date
5. **Plan rollback procedure** beforehand

---

## Rollback Checklist

- [ ] Inventory current deployment version
- [ ] Have rollback commands ready
- [ ] Check backup availability
- [ ] Verify data integrity
- [ ] Test rollback in non-production first
- [ ] Document rollback steps
- [ ] Notify stakeholders
- [ ] Execute rollback
- [ ] Verify application functionality
- [ ] Monitor for 24 hours
- [ ] Complete RCA (Root Cause Analysis)

---

## Known Limitations

1. **Manual Rollback**: Some manual steps are required for state management
2. **Stateful Components**: Database migrations require special handling
3. **Image Retention**: Old images should be retained for rollback
4. **Configuration Changes**: Changes to secrets require additional steps

---

## Education Tips

When rolling back:

1. **Always document** the rollback steps
2. **Verify** the environment is healthy after rollback
3. **Test** the system functionality
4. **Check** monitoring and alerts
5. **Notify** the team if there's an incident
6. **Document** the root cause and prevention measure

### Step 3: Verify Recovery

```bash
# Check pods are healthy
kubectl get pods -n ai-knowledge-copilot

# Verify health endpoint
kubectl exec -n ai-knowledge-copilot <pod-name> -- curl http://localhost:8000/health

# Check service endpoints
kubectl get svc -n ai-knowledge-copilot
```

### Step 4: Monitor Recovery

```bash
# Watch logs for errors
kubectl logs -f -n ai-knowledge-copilot -l app=ai-knowledge-copilot

# Check metrics in Azure Portal
# - Application Insights
# - Azure Monitor
```

### Step 5: Post-Recovery Actions

1. **Root Cause Analysis**: Investigate why the change failed
2. **Configuration Audit**: Verify secrets, env vars, connection strings
3. **Deployment Review**: Examine CI/CD logs for failures
4. **Update Documentation**: Document the issue and resolution

---

## Recovering From Specific Scenarios

### Scenario 1: "Pods Do Not Become Ready"

**Cause:** Configuration mismatch or missing secrets

**Recovery:**
1. Check the deployment logs
2. Verify ConfigMap/Secret are correct
3. Fix the configuration
4. Roll back to previous deployment
5. Recreate pods

### Scenario 2: "HTTP 502/503"

**Cause:** Backend service down or misconfigured

**Recovery:**
1. Check backend service status
2. Verify backend pod logs
3. Restart backend deployment
4. Check ingress/load balancer configuration

### Scenario 3: "Database Connection Failure"

**Cause:** Database unavailable or credentials changed

**Recovery:**
1. Verify database service is running
2. Check credentials in Key Vault
3. Restart pods to pick up new credentials
4. If credentials changed, update all config

### Scenario 4: "Bad Release Regression"

**Cause:** New version introduced a bug

**Recovery:**
1. Use `kubectl rollout undo`
2. Or use Helm rollback
3. Verify safety measures
4. Diagnose and fix root cause
5. Re-test before redeploying

1. Deploy to 10% of users
2. Monitor for errors
3. Gradually increase to 100%
4. Rollback immediately if issues detected

---

## Automatic Rollback Configuration

### Kubernetes Deployment

```yaml
# Add automatic rollback to Deployment
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 25%
      maxSurge: 25%
```

### Helm Values

Add to `values.yaml`:
```yaml
backend:
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
```

---

## Rollback Decision Matrix

| Issue Type | Recommended Action | Expected Time to Recover |
|------------|-------------------|--------------------------|
| Bad code release | Git revert + redeploy | 5-10 minutes |
| Configuration error | ConfigMap/Secret update | 2-5 minutes |
| Database connection failure | Restart pods / reconnect DB | 2-5 minutes |
| Out of memory | Scale up limits / increase resources | 5-10 minutes |
| Service degradation | Scale up replicas | 5-15 minutes |
| Security breach | Full redeployment + security review | 30-60 minutes |

# Roll back to specific revision
kubectl rollout undo deployment/ai-knowledge-copilot-backend --to-revision=3 -n ai-knowledge-copilot
```

### 2. Helm Rollback

When using Helm, use the `helm rollback` command.

```bash
# List releases and revisions
helm history ai-knowledge-copilot -n ai-knowledge-copilot

# Roll back to a previous revision
helm rollback ai-knowledge-copilot <revision-number> -n ai-knowledge-copilot

# Example
helm rollback ai-knowledge-copilot 2 -n ai-knowledge-copilot
```

### 3. Image Tag Rollback

Revert to a previous Docker image tag.

```bash
# Update image to previous tag
helm upgrade ai-knowledge-copilot helm/ai-knowledge-copilot \
  --namespace ai-knowledge-copilot \
  --set backend.image.tag=sha-abc123 \
  --wait
```

### 4. Full Deployment Recreation

In severe cases, recreate the entire deployment from scratch.

```bash
# Delete the deployment and config
kubectl delete deployment ai-knowledge-copilot-backend \
  -n ai-knowledge-copilot

# Reinstall from Helm
helm install ai-knowledge-copilot helm/ai-knowledge-copilot \
  --namespace ai-knowledge-copilot \
  --create-namespace \
  --set backend.image.tag=sha-abc123 \
  --wait
```
