# Architecture Overview

## Three-Tier AWS & Kubernetes Architecture

```mermaid
flowchart TB
    User[End User / Browser] --> ALB[AWS Application Load Balancer<br/>Public Subnets]
    ALB -->|/ and static assets| FE[Frontend Pods<br/>React + Nginx :8080<br/>Private App Subnets]
    ALB -->|/api/* and /health/*| BE[Backend Pods<br/>FastAPI :8000<br/>Private App Subnets]
    FE -->|/api proxy| BE
    BE -->|PostgreSQL :5432| RDS[(Amazon RDS PostgreSQL<br/>Private DB Subnets)]
    BE -.->|Credentials via IRSA| SM[AWS Secrets Manager]
    EKS[Amazon EKS Control Plane] -.->|Control Plane Logs| CW[AWS CloudWatch]
    Prom[Prometheus] -->|Scrape /metrics| BE
    Graf[Grafana] -->|Query| Prom
```

## Network Segmentation

1. **Public Subnets (`10.0.1.0/24`, `10.0.2.0/24`)**: Host the internet-facing AWS Application Load Balancer and NAT Gateway.
2. **Private Application Subnets (`10.0.11.0/24`, `10.0.12.0/24`)**: Host Amazon EKS worker nodes and application pods (React/Nginx + FastAPI). Outbound internet access routes through the NAT Gateway.
3. **Private Database Subnets (`10.0.21.0/24`, `10.0.22.0/24`)**: Host Amazon RDS PostgreSQL with `publicly_accessible = false` and no internet route.
