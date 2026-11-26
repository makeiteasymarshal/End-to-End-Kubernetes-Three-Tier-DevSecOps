$ErrorActionPreference = "Stop"

Write-Host "=== Running Python Unit & Integration Tests ===" -ForegroundColor Cyan
python -m unittest discover -s tests -p "test_*.py" -v

if (Get-Command terraform -ErrorAction SilentlyContinue) {
    Write-Host "=== Terraform fmt & validate ===" -ForegroundColor Cyan
    terraform -chdir=terraform fmt -check -recursive
    terraform -chdir=terraform init -backend=false
    terraform -chdir=terraform validate
} else {
    Write-Warning "terraform CLI not found. Skipping Terraform checks."
}

if (Get-Command helm -ErrorAction SilentlyContinue) {
    Write-Host "=== Helm lint ===" -ForegroundColor Cyan
    helm lint helm/three-tier-app
} else {
    Write-Warning "helm CLI not found. Skipping Helm lint."
}

if (Get-Command kubectl -ErrorAction SilentlyContinue) {
    Write-Host "=== Kubectl client dry-run ===" -ForegroundColor Cyan
    kubectl apply --dry-run=client -R -f kubernetes/
} else {
    Write-Warning "kubectl CLI not found. Skipping Kubernetes dry-run."
}
