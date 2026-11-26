#!/usr/bin/env bash
set -euo pipefail

echo "=== Running Python Unit & Integration Tests ==="
python3 -m unittest discover -s tests -p "test_*.py" -v

echo "=== Validating YAML files ==="
python3 - << 'EOF'
import glob, yaml
for path in glob.glob("kubernetes/**/*.yaml", recursive=True) + glob.glob(".github/workflows/*.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        list(yaml.safe_load_all(f))
    print(f"OK: {path}")
EOF

if command -v terraform >/dev/null 2>&1; then
  echo "=== Terraform fmt & validate ==="
  terraform -chdir=terraform fmt -check -recursive
  terraform -chdir=terraform init -backend=false
  terraform -chdir=terraform validate
else
  echo "SKIP: terraform not installed"
fi

if command -v helm >/dev/null 2>&1; then
  echo "=== Helm lint ==="
  helm lint helm/three-tier-app
else
  echo "SKIP: helm not installed"
fi
