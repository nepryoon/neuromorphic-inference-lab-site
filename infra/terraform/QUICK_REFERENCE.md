# Quick Reference - Terraform Commands

## Essential Commands

```bash
# Initialize
make init

# Plan changes
make plan

# Apply changes
make apply

# Show outputs
make output

# Show deployment checklist
make output-checklist
```

## Container Operations

```bash
# Login to ECR
make ecr-login

# Show ECR URLs
make output-ecr

# Update services (after pushing new images)
make ecs-update-inference
make ecs-update-rag
make ecs-update-grafana
make ecs-update-prometheus
```

## Monitoring

```bash
# View logs
make ecs-logs-inference
make ecs-logs-rag
make ecs-logs-grafana
make ecs-logs-prometheus

# Get Grafana URL
terraform output -raw grafana_url
```

## DNS & Network

```bash
# Get ALB DNS (for Cloudflare CNAME)
make output-alb

# Get certificate validation records
terraform output acm_certificate_validation_records
```

## Database

```bash
# Get RDS endpoint
make output-rds

# Get database credentials
terraform output -raw rds_endpoint
# Username: niladmin
# Password: (from terraform.tfvars)
# Database: neuromorphic
```

## State Management

```bash
# List all resources
make state-list

# Show specific resource
make state-show RESOURCE=aws_vpc.main

# Refresh state
make refresh
```

## Troubleshooting

```bash
# Validate configuration
make validate

# Format files
make fmt

# Check CloudWatch logs
aws logs tail /ecs/nil-prod --follow --region eu-south-1

# Describe ECS service
aws ecs describe-services \
  --cluster nil-cluster-prod \
  --services nil-inference-prod \
  --region eu-south-1

# Check ACM certificate status
aws acm describe-certificate \
  --certificate-arn $(terraform output -json | jq -r '.acm_certificate_arn.value') \
  --region eu-south-1

# List ECS tasks
aws ecs list-tasks \
  --cluster nil-cluster-prod \
  --service-name nil-inference-prod \
  --region eu-south-1
```

## Cleanup

```bash
# Destroy infrastructure
make destroy

# Clean local files
make clean
```

## Important URLs

After deployment:
- API Base: https://api.neuromorphicinference.com
- Inference: https://api.neuromorphicinference.com/predict
- RAG: https://api.neuromorphicinference.com/rag
- Grafana: https://api.neuromorphicinference.com/grafana
- Health: https://api.neuromorphicinference.com/health

## File Structure

```
infra/terraform/
├── main.tf                  # VPC, networking
├── variables.tf             # Input variables
├── ecs.tf                   # ECS cluster, tasks, services, ECR
├── alb.tf                   # Load balancer, routing
├── rds.tf                   # PostgreSQL database
├── monitoring.tf            # Prometheus, Grafana
├── outputs.tf               # Output values
├── terraform.tfvars         # Variable values (not committed)
├── terraform.tfvars.example # Example variable values
├── .gitignore              # Git ignore patterns
├── README.md               # Main documentation
├── DEPLOYMENT_GUIDE.md     # Detailed deployment guide
├── Makefile                # Helper commands
└── QUICK_REFERENCE.md      # This file
```

## Resource Naming Convention

Format: `{project_prefix}-{resource}-{environment}`

Examples:
- VPC: `nil-vpc-prod`
- ECS Cluster: `nil-cluster-prod`
- ALB: `nil-alb-prod`
- RDS: `nil-db-prod`
- ECR: `nil/inference`, `nil/rag-copilot`

## AWS Resources Created

- **VPC**: 1
- **Subnets**: 4 (2 public, 2 private)
- **Internet Gateway**: 1
- **NAT Gateway**: 1
- **Route Tables**: 2
- **Security Groups**: 4 (ALB, ECS, RDS, Monitoring)
- **ECS Cluster**: 1
- **ECS Services**: 4 (Inference, RAG, Prometheus, Grafana)
- **ECR Repositories**: 4
- **ALB**: 1
- **Target Groups**: 3
- **ACM Certificate**: 1
- **RDS Instance**: 1 (PostgreSQL 16)
- **EFS File Systems**: 2 (Prometheus, Grafana)
- **Service Discovery Namespace**: 1
- **CloudWatch Log Group**: 1
- **IAM Roles**: 2 (Execution, Task)
- **SSM Parameters**: 2 (DB password, Grafana password)

Total: ~40 resources

## Cost Estimate (Monthly)

- NAT Gateway: ~$32
- ECS Fargate: ~$50-100
- ALB: ~$22
- RDS db.t3.micro: ~$15
- EFS: ~$0.30/GB
- **Total**: ~$120-170/month

## Security Checklist

- [x] All data encrypted at rest (RDS, EFS)
- [x] All data encrypted in transit (TLS)
- [x] RDS in private subnet
- [x] ECS tasks in private subnet
- [x] Secrets in SSM Parameter Store
- [x] Minimum security group rules
- [x] IAM least privilege
- [ ] Enable CloudTrail (manual)
- [ ] Enable GuardDuty (manual)
- [ ] Enable VPC Flow Logs (manual)

## Common Issues & Solutions

### Certificate Validation Stuck
→ Check DNS records in Cloudflare, ensure "DNS only" mode

### Tasks Not Starting
→ Check CloudWatch logs, verify ECR image exists

### 502 Bad Gateway
→ Check target group health, verify security groups

### High Costs
→ Scale down to 0 tasks when not needed, disable NAT gateway

### Database Connection Failed
→ Verify security group rules, check credentials in SSM
