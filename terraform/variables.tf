variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project identifier used in resource naming"
  type        = string
  default     = "three-tier-devsecops"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the custom VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of Availability Zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "eks_cluster_version" {
  description = "Kubernetes version for Amazon EKS"
  type        = string
  default     = "1.33"
}

variable "eks_node_instance_types" {
  description = "EC2 instance types for EKS managed node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "eks_desired_size" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 2
}

variable "eks_min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}

variable "eks_max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 3
}

variable "db_instance_class" {
  description = "RDS PostgreSQL instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "Initial PostgreSQL database name"
  type        = string
  default     = "threetierdb"
}

variable "db_username" {
  description = "Master username for Amazon RDS PostgreSQL"
  type        = string
  default     = "appadmin"
}

variable "github_repository" {
  description = "GitHub repository in owner/repo format for OIDC trust policy"
  type        = string
  default     = "makeiteasymarshal/End-to-End-Kubernetes-Three-Tier-DevSecOps"
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets (set false only for offline cost tests)"
  type        = bool
  default     = true
}
