variable "aws_region" {
  description = "AWS region where the existing EKS cluster is deployed."
  type        = string
  default     = "us-east-2"
}

variable "aws_account_id" {
  description = "Expected AWS account ID; used as a safety precondition."
  type        = string
  default     = "647870083089"
}

variable "cluster_name" {
  description = "Existing EKS cluster name."
  type        = string
  default     = "task-api-eks"
}

variable "node_group_name" {
  description = "Existing EKS managed node group name."
  type        = string
  default     = "task-api-workers-v2"
}

variable "min_size" {
  description = "Minimum node count for the existing node group."
  type        = number
  default     = 1
}

variable "desired_size" {
  description = "Desired node count for the existing node group."
  type        = number
  default     = 3
}

variable "max_size" {
  description = "Maximum node count for the existing node group."
  type        = number
  default     = 3
}
