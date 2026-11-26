output "vpc_id" {
  description = "Custom VPC ID"
  value       = module.vpc.vpc_id
}

output "eks_cluster_name" {
  description = "Amazon EKS cluster name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "Amazon EKS API server endpoint"
  value       = module.eks.cluster_endpoint
}

output "eks_oidc_provider_arn" {
  description = "OIDC provider ARN for EKS IRSA"
  value       = module.eks.oidc_provider_arn
}

output "ecr_frontend_repository_url" {
  description = "Amazon ECR repository URL for frontend"
  value       = module.ecr.frontend_repository_url
}

output "ecr_backend_repository_url" {
  description = "Amazon ECR repository URL for backend"
  value       = module.ecr.backend_repository_url
}

output "github_actions_role_arn" {
  description = "IAM Role ARN assumed by GitHub Actions via OIDC"
  value       = module.iam.github_actions_role_arn
}

output "rds_endpoint" {
  description = "Amazon RDS PostgreSQL endpoint"
  value       = module.rds.db_endpoint
}

output "rds_secret_arn" {
  description = "AWS Secrets Manager ARN storing RDS credentials"
  value       = module.rds.db_secret_arn
}
