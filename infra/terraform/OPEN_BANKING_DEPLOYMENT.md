# Open Banking Transaction Enrichment - Deployment Guide

This guide provides step-by-step instructions for deploying the Open Banking Transaction Enrichment microservice to AWS using Terraform.

## Overview

The Open Banking service is deployed as a containerized application on AWS ECS Fargate with:
- Auto-scaling based on CPU and memory utilization
- Health checks and monitoring
- Integration with the main ALB for routing
- CloudWatch logging and alarms

## Prerequisites

1. **Terraform** >= 1.0 installed
2. **Docker** installed for building container images
3. **AWS CLI** configured with credentials for account `102724112773`
4. **Open Banking repository** cloned locally: `https://github.com/nepryoon/open-banking-transaction-enrichment`

## Architecture

```
Internet → Cloudflare → ALB → ECS Fargate (Open Banking Service)
                                    ↓
                            CloudWatch Logs & Metrics
```

### Service Specifications

- **CPU**: 256 units (0.25 vCPU) - configurable
- **Memory**: 512 MiB - configurable
- **Desired Count**: 1 task
- **Auto-scaling**: 1-3 tasks based on CPU/Memory utilization (70% threshold)
- **Port**: 8000
- **Health Check**: `/health` endpoint

## Deployment Steps

### Step 1: Build the Docker Image

Navigate to the Open Banking repository and build the Docker image:

```bash
cd /path/to/open-banking-transaction-enrichment

# Build the Docker image
docker build -t open-banking:latest .

# Test locally (optional)
docker run -p 8000:8000 open-banking:latest
curl http://localhost:8000/health
```

### Step 2: Push Image to ECR

Get the ECR repository URL from Terraform output:

```bash
cd /path/to/neuromorphic-inference-lab-site/infra/terraform
terraform output ecr_open_banking_url
```

Authenticate Docker to ECR and push the image:

```bash
# Get ECR login token
aws ecr get-login-password --region eu-south-1 | \
  docker login --username AWS --password-stdin \
  102724112773.dkr.ecr.eu-south-1.amazonaws.com

# Tag the image
docker tag open-banking:latest \
  102724112773.dkr.ecr.eu-south-1.amazonaws.com/nil/open-banking:latest

# Push to ECR
docker push 102724112773.dkr.ecr.eu-south-1.amazonaws.com/nil/open-banking:latest
```

### Step 3: Deploy with Terraform

Apply the Terraform configuration (if not already done):

```bash
cd /path/to/neuromorphic-inference-lab-site/infra/terraform

# Initialize Terraform (if not done)
terraform init

# Plan the deployment
terraform plan -out=tfplan

# Apply the changes
terraform apply tfplan
```

### Step 4: Verify Deployment

Check the ECS service status:

```bash
# Check ECS service
aws ecs describe-services \
  --cluster nil-cluster-prod \
  --services nil-open-banking-prod \
  --region eu-south-1

# Check running tasks
aws ecs list-tasks \
  --cluster nil-cluster-prod \
  --service-name nil-open-banking-prod \
  --region eu-south-1

# View logs
aws logs tail /ecs/nil-prod --follow \
  --filter-pattern "open-banking" \
  --region eu-south-1
```

### Step 5: Test the Service

Once deployed, test the service through the ALB:

```bash
# Health check
curl https://api.neuromorphicinference.com/open-banking/health

# Test transaction enrichment
curl -X POST https://api.neuromorphicinference.com/transactions/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "description": "POS 4839 STARBUCKS COFFEE MILANO 02/11 IT"
  }'
```

Expected response:
```json
{
  "merchant": "Starbucks Coffee Milano",
  "category": "Food",
  "signals": ["Standard Transaction"],
  "confidence": 0.95
}
```

## Configuration

### Scaling Configuration

To adjust auto-scaling parameters, update `variables.tf`:

```hcl
variable "open_banking_desired_count" {
  default = 2  # Increase desired count
}

variable "open_banking_max_count" {
  default = 5  # Increase max count
}
```

Then apply:

```bash
terraform apply
```

### Resource Allocation

To adjust CPU/Memory:

```hcl
variable "open_banking_cpu" {
  default = 512  # 0.5 vCPU
}

variable "open_banking_memory" {
  default = 1024  # 1 GB
}
```

## Monitoring

### CloudWatch Metrics

Monitor the service in CloudWatch:

1. **ECS Service Metrics**:
   - Navigate to CloudWatch → Metrics → ECS
   - Select cluster: `nil-cluster-prod`
   - Select service: `nil-open-banking-prod`

2. **Key Metrics**:
   - `CPUUtilization`: Should stay below 70%
   - `MemoryUtilization`: Should stay below 70%
   - `TargetResponseTime`: Latency metrics

### CloudWatch Alarms

Alarms are automatically created:
- `nil-open-banking-cpu-prod`: Alerts when CPU > 80%
- `nil-open-banking-memory-prod`: Alerts when memory > 80%

### Logs

View service logs:

```bash
# Via AWS CLI
aws logs tail /ecs/nil-prod \
  --filter-pattern "open-banking" \
  --follow \
  --region eu-south-1

# Via AWS Console
# Navigate to CloudWatch → Log Groups → /ecs/nil-prod
# Filter by "open-banking"
```

## Troubleshooting

### Service Not Starting

Check ECS task events:

```bash
aws ecs describe-services \
  --cluster nil-cluster-prod \
  --services nil-open-banking-prod \
  --region eu-south-1 \
  --query 'services[0].events[:5]'
```

### Health Check Failing

Check task logs:

```bash
# Get task ID
TASK_ID=$(aws ecs list-tasks \
  --cluster nil-cluster-prod \
  --service-name nil-open-banking-prod \
  --region eu-south-1 \
  --query 'taskArns[0]' \
  --output text | cut -d'/' -f3)

# View task logs
aws logs get-log-events \
  --log-group-name /ecs/nil-prod \
  --log-stream-name "open-banking/open-banking/${TASK_ID}" \
  --region eu-south-1
```

### High CPU/Memory Usage

1. Check metrics in CloudWatch
2. Review application logs for errors
3. Consider increasing task size:

```hcl
# In variables.tf
variable "open_banking_cpu" {
  default = 512  # Increase from 256
}

variable "open_banking_memory" {
  default = 1024  # Increase from 512
}
```

Then apply:

```bash
terraform apply
```

## Rolling Updates

To deploy a new version:

```bash
# Build and push new image
docker build -t open-banking:v2 .
docker tag open-banking:v2 \
  102724112773.dkr.ecr.eu-south-1.amazonaws.com/nil/open-banking:latest
docker push 102724112773.dkr.ecr.eu-south-1.amazonaws.com/nil/open-banking:latest

# Force new deployment
aws ecs update-service \
  --cluster nil-cluster-prod \
  --service nil-open-banking-prod \
  --force-new-deployment \
  --region eu-south-1
```

## Cost Estimation

Monthly cost for Open Banking service (1 task, 0.25 vCPU, 512 MB):

- **ECS Fargate**: ~$12/month
  - CPU: 0.25 vCPU * $0.04048/vCPU/hour * 730 hours = ~$7.40
  - Memory: 0.5 GB * $0.004445/GB/hour * 730 hours = ~$1.62
- **Data Transfer**: ~$2-5/month (varies with usage)
- **CloudWatch Logs**: ~$1-3/month
- **ALB (shared)**: Included in main infrastructure

**Total**: ~$15-20/month per task

## Security

### IAM Permissions

The service has these permissions:
- CloudWatch Logs: Write logs
- SSM Parameters: Read application configuration
- Secrets Manager: Read sensitive data (if needed)

### Network Security

- Service runs in **private subnets** (no public IP)
- Traffic flows through ALB in public subnets
- Security group allows inbound traffic only from ALB
- Outbound traffic allowed for AWS service endpoints

## Next Steps

1. **Set up CI/CD**: Automate Docker image builds and deployments
2. **Add monitoring dashboards**: Create Grafana dashboards for service metrics
3. **Implement caching**: Add Redis for caching enrichment results
4. **Add API authentication**: Implement API key validation
5. **Performance testing**: Load test the service

## Support

For issues or questions:
- GitHub: https://github.com/nepryoon/open-banking-transaction-enrichment
- Main site: https://www.neuromorphicinference.com/demos/open-banking-enrichment/
