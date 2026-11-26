module "vpc" {
  source = "./modules/vpc"

  name_prefix        = local.name_prefix
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  cluster_name       = "${local.name_prefix}-eks"
  enable_nat_gateway = var.enable_nat_gateway
}

module "security_groups" {
  source = "./modules/security-groups"

  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
  vpc_cidr    = var.vpc_cidr
}

module "ecr" {
  source = "./modules/ecr"

  name_prefix = local.name_prefix
}

module "iam" {
  source = "./modules/iam"

  name_prefix       = local.name_prefix
  github_repository = var.github_repository
  ecr_repo_arns     = [module.ecr.frontend_repository_arn, module.ecr.backend_repository_arn]
}

module "eks" {
  source = "./modules/eks"

  name_prefix            = local.name_prefix
  cluster_version        = var.eks_cluster_version
  vpc_id                 = module.vpc.vpc_id
  private_app_subnet_ids = module.vpc.private_app_subnet_ids
  eks_cluster_role_arn   = module.iam.eks_cluster_role_arn
  eks_node_role_arn      = module.iam.eks_node_role_arn
  eks_node_sg_id         = module.security_groups.eks_node_sg_id
  node_instance_types    = var.eks_node_instance_types
  desired_size           = var.eks_desired_size
  min_size               = var.eks_min_size
  max_size               = var.eks_max_size
}

module "rds" {
  source = "./modules/rds"

  name_prefix           = local.name_prefix
  private_db_subnet_ids = module.vpc.private_db_subnet_ids
  rds_security_group_id = module.security_groups.rds_sg_id
  db_instance_class     = var.db_instance_class
  db_name               = var.db_name
  db_username           = var.db_username
}
