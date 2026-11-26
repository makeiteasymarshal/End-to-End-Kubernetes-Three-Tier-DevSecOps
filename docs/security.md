# Security & DevSecOps Architecture

## Key Security Controls

1. **Keyless CI/CD Authentication (GitHub OIDC)**:
   - GitHub Actions assumes an IAM Role via `sts:AssumeRoleWithWebIdentity` scoped strictly to `repo:makeiteasymarshal/End-to-End-Kubernetes-Three-Tier-DevSecOps-Project:*`.
   - Zero long-lived AWS Access Keys are stored in GitHub.
2. **Container & Pod Hardening**:
   - Multi-stage Dockerfiles run as non-root users (`UID 10001` for FastAPI, `nginx` for frontend).
   - Kubernetes Namespace enforces Pod Security Standards (`restricted`), `allowPrivilegeEscalation: false`, and `capabilities.drop: ["ALL"]`.
3. **Secrets Management**:
   - RDS master password is generated dynamically via Terraform `random_password` and stored in AWS Secrets Manager.
   - External Secrets Operator syncs credentials into Kubernetes Secrets via IRSA.
4. **Shift-Left Scanning**:
   - **Trivy Filesystem Scan**: Detects CVEs, hardcoded secrets, and Terraform/Kubernetes misconfigurations.
   - **Trivy Image Scan**: Blocks `CRITICAL` vulnerabilities before ECR push.
   - **SonarQube**: Static code quality and security hotspot analysis.
   - **Amazon ECR**: `scan_on_push = true`, AES-256 encryption, and `IMMUTABLE` image tags.
