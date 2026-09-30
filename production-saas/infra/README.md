# AWS Deployment Blueprint

This repository includes an application-ready deployment shape without pretending that cloud resources exist before you provision them.

## Recommended resources
1. ECR repositories for `web` and `api`.
2. ECS/Fargate cluster and services behind an Application Load Balancer.
3. RDS PostgreSQL Multi-AZ in private subnets.
4. ElastiCache Redis in private subnets.
5. CloudFront + Route 53 + ACM for the public domain.
6. Secrets Manager/SSM for JWT and Stripe secrets.
7. CloudWatch/OTel destination for logs, metrics and traces.
8. GitHub OIDC IAM role restricted to this repository/branch.

## GitHub deployment variables/secrets
- `AWS_ROLE_ARN`
- `AWS_REGION`
- `ECR_API_REPOSITORY`
- `ECR_WEB_REPOSITORY`
- `ECS_CLUSTER`
- `ECS_API_SERVICE`
- `ECS_WEB_SERVICE`

Use Terraform/CDK in a follow-up iteration if you want the portfolio to emphasize infrastructure-as-code. Never commit AWS keys.
