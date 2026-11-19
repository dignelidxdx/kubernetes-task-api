data "aws_caller_identity" "current" {}

data "aws_eks_node_group" "existing" {
  cluster_name    = var.cluster_name
  node_group_name = var.node_group_name
}

resource "aws_eks_node_group" "workers" {
  cluster_name    = var.cluster_name
  node_group_name = var.node_group_name
  node_role_arn   = data.aws_eks_node_group.existing.node_role_arn
  subnet_ids      = data.aws_eks_node_group.existing.subnet_ids

  ami_type       = data.aws_eks_node_group.existing.ami_type
  capacity_type  = data.aws_eks_node_group.existing.capacity_type
  disk_size      = data.aws_eks_node_group.existing.disk_size
  instance_types = data.aws_eks_node_group.existing.instance_types

  scaling_config {
    min_size     = var.min_size
    desired_size = var.desired_size
    max_size     = var.max_size
  }

  lifecycle {
    precondition {
      condition     = data.aws_caller_identity.current.account_id == var.aws_account_id
      error_message = "Refusing to manage the node group outside the expected AWS account."
    }

    # eksctl/CloudFormation remains authoritative for settings not managed here.
    ignore_changes = [
      labels,
      taint,
      update_config,
      launch_template,
      release_version,
      version,
    ]
  }
}
