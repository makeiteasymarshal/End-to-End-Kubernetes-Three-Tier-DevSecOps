# Troubleshooting Guide

## Common Issues & Resolutions

### 1. Backend Pods Fail Readiness Probe (`/health/ready` returns 503)
- **Cause**: Backend cannot reach PostgreSQL/RDS or `DATABASE_URL` secret is missing.
- **Check**:
  ```bash
  kubectl logs -n three-tier-app -l app=backend
  kubectl get secret db-credentials -n three-tier-app
  ```
- **Fix**: Verify RDS security group allows port `5432` from the EKS node security group and confirm `ExternalSecret` synced cleanly.

### 2. ALB Ingress Not Provisioning an External DNS Name
- **Cause**: AWS Load Balancer Controller is not installed or subnets lack `kubernetes.io/role/elb = 1` tag.
- **Check**:
  ```bash
  kubectl describe ingress three-tier-alb-ingress -n three-tier-app
  kubectl logs -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller
  ```

### 3. GitHub Actions OIDC `AssumeRoleWithWebIdentity` Fails
- **Cause**: `github_repository` variable in Terraform does not match the exact `owner/repo` string or `id-token: write` permission is missing in workflow YAML.
- **Fix**: Confirm `AWS_ROLE_ARN` secret and OIDC trust condition `repo:makeiteasymarshal/End-to-End-Kubernetes-Three-Tier-DevSecOps-Project:*`.
