$ErrorActionPreference = "Stop"

Write-Host "=== Building Local Docker Images ===" -ForegroundColor Cyan
docker build -f docker/backend.Dockerfile -t three-tier-backend:local .
docker build -f docker/frontend.Dockerfile -t three-tier-frontend:local .

Write-Host "=== Build Complete ===" -ForegroundColor Green
Write-Host "Run 'docker compose up' to start the local 3-tier stack."
