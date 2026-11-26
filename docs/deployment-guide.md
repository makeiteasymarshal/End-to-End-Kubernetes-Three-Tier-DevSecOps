# Deployment Guide

## 1. Local Development (Zero AWS Cost)

```bash
cp .env.example .env
docker compose up --build
```
- Frontend: `http://localhost:8080`
- Backend API Docs: `http://localhost:8000/docs`
- Prometheus Metrics: `http://localhost:8000/metrics`

## 2. Provision AWS Infrastructure with Terraform

> **Cost Warning:** Provisioning EKS, NAT Gateway, and RDS incurs AWS charges beyond Free Tier limits. Review `terraform/terraform.tfvars.example` before applying.

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

## 3. Configure GitHub Actions Secrets & Variables

- **Secret `AWS_ROLE_ARN`**: Output `github_actions_role_arn` from Terraform.
- **Optional Variable `SONAR_HOST_URL`** & **Secret `SONAR_TOKEN`**: For SonarQube static analysis.

## 4. Deploy to Amazon EKS via Helm

```bash
aws eks update-kubeconfig --region us-east-1 --name three-tier-devsecops-dev-eks
helm upgrade --install three-tier-app ./helm/three-tier-app \
  --namespace three-tier-app \
  --create-namespace
```

## 5. Observability Setup (Prometheus, Grafana, CloudWatch)

1. Install `kube-prometheus-stack` in the `monitoring` namespace.
2. Apply `kubernetes/monitoring/prometheus-servicemonitor.yaml` and `kubernetes/monitoring/grafana-dashboard-configmap.yaml`.
3. Enable CloudWatch Container Insights add-on or Fluent Bit DaemonSet to ship pod logs to `/aws/containerinsights/<cluster>/application`.
