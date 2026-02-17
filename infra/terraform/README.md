# Neuromorphic Inference Lab - AWS Infrastructure

This directory contains Terraform configuration for deploying the Neuromorphic Inference Lab stack on AWS.

## Architecture Overview

The infrastructure consists of:

- **VPC** with public and private subnets across 2 availability zones
- **ECS Fargate** cluster for containerized services
- **Application Load Balancer** for HTTPS routing
- **RDS PostgreSQL 16** database
- **EFS** for persistent storage (Prometheus & Grafana)
- **Service Discovery** (AWS Cloud Map) for internal service communication
- **ECR** repositories for Docker images

## Services

1. **Inference Service** - FastAPI application for ML inference
2. **RAG Copilot** - RAG-based AI assistant
3. **Ingestion Service** - Data ingestion pipeline
4. **Trainer Service** - Model training pipeline
5. **Prometheus** - Metrics collection
6. **Grafana** - Monitoring dashboards

## Prerequisites

1. **AWS CLI** configured with credentials for account `102724112773`
2. **Terraform** >= 1.0
3. **S3 Bucket** for state: `neuromorphic-tfstate-102724112773`
4. **Domain** configured in Cloudflare: `api.neuromorphicinference.com`

## Quick Start

### 1. Create S3 Backend (one-time setup)

```bash
aws s3api create-bucket \
  --bucket neuromorphic-tfstate-102724112773 \
  --region eu-south-1 \
  --create-bucket-configuration LocationConstraint=eu-south-1

aws s3api put-bucket-versioning \
  --bucket neuromorphic-tfstate-102724112773 \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket neuromorphic-tfstate-102724112773 \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

### 2. Create terraform.tfvars

Create a `terraform.tfvars` file (not committed to git):

```hcl
aws_region     = "eu-south-1"
aws_account_id = "102724112773"
project_prefix = "nil"
environment    = "prod"

# Database
db_name     = "neuromorphic"
db_username = "niladmin"
db_password = "CHANGE_ME_SECURE_PASSWORD"

# Monitoring
grafana_admin_password = "CHANGE_ME_SECURE_PASSWORD"

# Domain
domain_name = "api.neuromorphicinference.com"
```

### 3. Initialize Terraform

```bash
cd infra/terraform
terraform init
```

### 4. Plan and Apply

```bash
# Review the plan
terraform plan -out=tfplan

# Apply the infrastructure
terraform apply tfplan
```

### 5. Complete Setup

After `terraform apply` completes, follow the deployment checklist in the output:

```bash
terraform output deployment_checklist
```

## Post-Deployment Steps

### DNS Configuration (Cloudflare)

1. Add ACM certificate validation records:
   ```bash
   terraform output acm_certificate_validation_records
   ```

2. Add CNAME record for API:
   ```
   Name: api
   Type: CNAME
   Value: <alb_dns_name from output>
   ```

### Build and Push Docker Images

```bash
# Get ECR login
aws ecr get-login-password --region eu-south-1 | docker login --username AWS --password-stdin <ECR_URL>

# Build and push inference service
docker build -t <ecr_inference_url>:latest ./inference
docker push <ecr_inference_url>:latest

# Build and push RAG copilot
docker build -t <ecr_rag_copilot_url>:latest ./rag-copilot
docker push <ecr_rag_copilot_url>:latest

# Build and push other services...
```

### Force ECS Service Update

After pushing images:

```bash
aws ecs update-service \
  --cluster nil-cluster-prod \
  --service nil-inference-prod \
  --force-new-deployment \
  --region eu-south-1
```

## Infrastructure Details

### Networking

- **VPC CIDR**: 10.0.0.0/16
- **Public Subnets**: 10.0.0.0/24, 10.0.1.0/24 (ALB)
- **Private Subnets**: 10.0.10.0/24, 10.0.11.0/24 (ECS, RDS)
- **NAT Gateway**: Single NAT in first public subnet

### ECS Configuration

- **Platform**: Fargate
- **Container Insights**: Enabled
- **Log Retention**: 7 days

**Inference Task:**
- CPU: 512 (0.5 vCPU)
- Memory: 1024 MiB
- Port: 8000
- Health Check: `/health`

**RAG Copilot Task:**
- CPU: 512 (0.5 vCPU)
- Memory: 1024 MiB
- Port: 8000
- Health Check: `/health`

### ALB Routing

- **HTTP (80)**: Redirects to HTTPS
- **HTTPS (443)**: Path-based routing:
  - `/predict`, `/health`, `/version`, `/metrics` → Inference
  - `/rag`, `/ask` → RAG Copilot
  - `/grafana` → Grafana

### RDS Configuration

- **Engine**: PostgreSQL 16
- **Instance**: db.t3.micro
- **Storage**: 20GB gp3 (encrypted)
- **Backups**: 7 days retention
- **Performance Insights**: Enabled

### Monitoring

- **Prometheus**: v2.53.0, EFS-backed
- **Grafana**: v11.1.0, EFS-backed, PostgreSQL backend
- **Service Discovery**: nil.local namespace

## Cost Estimation

Approximate monthly costs (eu-south-1):

- **VPC**: $0 (NAT Gateway: ~$32)
- **ECS Fargate**: ~$50-100 (depending on task count)
- **ALB**: ~$22
- **RDS db.t3.micro**: ~$15
- **EFS**: ~$0.30/GB
- **Data Transfer**: Variable

**Total**: ~$120-170/month (excluding data transfer)

## Maintenance

### Update Service Images

```bash
# Update task definition with new image
aws ecs update-service \
  --cluster <cluster-name> \
  --service <service-name> \
  --force-new-deployment
```

### Scale Services

```bash
aws ecs update-service \
  --cluster <cluster-name> \
  --service <service-name> \
  --desired-count 2
```

### Database Backups

Automated backups are enabled with 7-day retention. Manual snapshot:

```bash
aws rds create-db-snapshot \
  --db-instance-identifier nil-db-prod \
  --db-snapshot-identifier nil-manual-snapshot-$(date +%Y%m%d)
```

## Troubleshooting

### ECS Tasks Not Starting

1. Check CloudWatch logs:
   ```bash
   aws logs tail /ecs/nil-prod --follow
   ```

2. Verify security groups allow traffic

3. Check ECR image exists:
   ```bash
   aws ecr describe-images --repository-name nil/inference
   ```

### Database Connection Issues

1. Verify security group allows port 5432 from ECS security group
2. Check RDS instance is available
3. Verify database credentials in SSM Parameter Store

### ALB Health Check Failures

1. Verify containers are listening on port 8000
2. Check health check endpoint returns 200
3. Review target group settings

## Security

### Secrets Management

All sensitive values are stored in AWS Systems Manager Parameter Store:
- Database password: `/${project_prefix}/${environment}/db_password`
- Grafana password: `/${project_prefix}/${environment}/grafana_admin_password`

### Network Security

- ECS tasks run in private subnets (no public IPs)
- RDS is not publicly accessible
- Security groups follow principle of least privilege
- All data encrypted at rest (RDS, EFS)
- All data encrypted in transit (TLS)

### IAM

- ECS execution role: Pull images, read secrets
- ECS task role: Write CloudWatch logs
- Principle of least privilege applied

## Cleanup

To destroy all infrastructure:

```bash
# Review what will be destroyed
terraform plan -destroy

# Destroy (requires confirmation)
terraform destroy
```

**Warning**: This will delete:
- All ECS services and tasks
- RDS database (final snapshot will be created)
- ALB and target groups
- VPC and all networking
- EFS file systems
- ECR repositories (images will be deleted)

## Support

For issues or questions:
- GitHub: https://github.com/nepryoon
- Website: https://www.neuromorphicinference.com

## License

See repository root for license information.
