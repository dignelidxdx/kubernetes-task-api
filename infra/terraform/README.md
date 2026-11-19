# Terraform for EKS capacity

This configuration manages only the existing managed node group
`task-api-workers-v2` in the `task-api-eks` cluster in `us-east-2`.
It does not declare or create a cluster, VPC, roles, subnets, or another node group.

The original resources were created with eksctl/CloudFormation. Therefore, the
first step is to import the group into local Terraform state and review the plan.
The state file contains infrastructure identifiers and must not be committed or
shared without an appropriate backend and controls.

## Safe workflow

From `infra/terraform/`:

```powershell
terraform init
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
```

Before planning, import the existing group:

```powershell
terraform import aws_eks_node_group.workers task-api-eks:task-api-workers-v2
```

Confirm that the plan only adjusts `scaling_config` to minimum 1, desired 3,
and maximum 3. `apply` is the final advanced step: it requires reviewing the
plan and credentials for account `647870083089`. It must not run automatically
from this repository.

If `terraform plan` proposes creating or replacing the group, or touching the
cluster, stop and review the imported state and credentials before applying.
