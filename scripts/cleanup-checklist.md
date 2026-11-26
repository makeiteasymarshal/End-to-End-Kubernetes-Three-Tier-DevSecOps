# AWS Cleanup Checklist (Cost Protection)

Always tear down resources in reverse dependency order to avoid orphaned billable assets:

1. **Delete Kubernetes Ingress & Workloads** (removes AWS ALB provisioned by Load Balancer Controller):
   ```bash
   helm uninstall three-tier-app -n three-tier-app
   kubectl delete namespace three-tier-app
   ```
2. **Verify Load Balancers & Target Groups are deleted** in the AWS EC2 Console.
3. **Empty ECR Repositories** (if `force_delete` is not enabled):
   - Delete images in `three-tier-devsecops-dev-frontend` and `three-tier-devsecops-dev-backend`.
4. **Destroy Terraform Infrastructure**:
   ```bash
   cd terraform
   terraform destroy
   ```
5. **Confirm Zero Remaining Billable Resources**:
   - NAT Gateways & Elastic IPs
   - EKS Cluster & EC2 Worker Nodes
   - RDS PostgreSQL Instances & Snapshots
   - EBS Volumes
