resource "aws_cloudwatch_log_group" "eks" {
  name              = "/aws/eks/${var.name_prefix}-eks/cluster"
  retention_in_days = 7
}

resource "aws_eks_cluster" "this" {
  name     = "${var.name_prefix}-eks"
  version  = var.cluster_version
  role_arn = var.eks_cluster_role_arn

  vpc_config {
    subnet_ids              = var.private_app_subnet_ids
    security_group_ids      = [var.eks_node_sg_id]
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator"]

  depends_on = [aws_cloudwatch_log_group.eks]
}

data "tls_certificate" "eks_oidc" {
  url = aws_eks_cluster.this.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "eks" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks_oidc.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.this.identity[0].oidc[0].issuer
}

resource "aws_eks_node_group" "this" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "${var.name_prefix}-ng"
  node_role_arn   = var.eks_node_role_arn
  subnet_ids      = var.private_app_subnet_ids
  instance_types  = var.node_instance_types
  capacity_type   = "ON_DEMAND"

  scaling_config {
    desired_size = var.desired_size
    min_size     = var.min_size
    max_size     = var.max_size
  }

  update_config {
    max_unavailable = 1
  }
}

resource "aws_eks_addon" "vpc_cni" {
  cluster_name = aws_eks_cluster.this.name
  addon_name   = "vpc-cni"
}

resource "aws_eks_addon" "coredns" {
  cluster_name = aws_eks_cluster.this.name
  addon_name   = "coredns"
  depends_on   = [aws_eks_node_group.this]
}

resource "aws_eks_addon" "kube_proxy" {
  cluster_name = aws_eks_cluster.this.name
  addon_name   = "kube-proxy"
}
