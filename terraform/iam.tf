resource "aws_iam_group" "rds_group" {
  name = "rds_group"
}

# Create a list of all RDS ARNs
locals {
  all_rds_arns    = [for instance in module.rds_instance : instance.rds_arn]
  all_secret_arns = [for instance in module.rds_instance : instance.db_secret_arn]
}

resource "aws_iam_policy" "rds_secrets_access" {
  name        = "GlobalRDSSecretsAccessPolicy"
  description = "Allow access to all RDS instances and Secrets Manager secrets created by the module"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds:Connect",
          "rds:DescribeDBSnapshots"
        ]
        Resource = local.all_rds_arns
      },
      {
        Effect   = "Allow"
        Action   = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = local.all_secret_arns
      }
    ]
  })
}

resource "aws_iam_group_policy_attachment" "attach_rds_secrets_access" {
  group      = aws_iam_group.rds_group.name
  policy_arn = aws_iam_policy.rds_secrets_access.arn
}

