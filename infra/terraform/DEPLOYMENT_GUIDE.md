# Deployment Guide - Neuromorphic Inference Lab on AWS

This guide walks you through deploying the complete Neuromorphic Inference Lab infrastructure on AWS using Terraform.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Infrastructure Deployment](#infrastructure-deployment)
4. [DNS Configuration](#dns-configuration)
5. [Container Deployment](#container-deployment)
6. [Monitoring Setup](#monitoring-setup)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **AWS CLI** v2.x or higher
- **Terraform** v1.0 or higher
- **Docker** v20.x or higher
- **jq** (for JSON processing)

### AWS Account Setup

- **Account ID**: 102724112773 (nepryoon)
- **Region**: eu-south-1 (Milano)
- **IAM Permissions**: Administrator access or equivalent permissions for:
  - VPC, EC2, ECS, ECR
  - RDS, ALB, ACM
  - CloudWatch, Systems Manager
  - IAM roles and policies

### Domain Setup

- Domain managed in Cloudflare: `neuromorphicinference.com`
- Subdomain to configure: `api.neuromorphicinference.com`

---

## Initial Setup

### 1. Configure AWS CLI

```bash
aws configure
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]
# Default region name: eu-south-1
# Default output format: json
```

Verify access:

```bash
aws sts get-caller-identity
# Should show account 102724112773
```

### 2. Create S3 Backend for Terraform State

```bash
# Create S3 bucket
aws s3api create-bucket \
  --bucket neuromorphic-tfstate-102724112773 \
  --region eu-south-1 \
  --create-bucket-configuration LocationConstraint=eu-south-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket neuromorphic-tfstate-102724112773 \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket neuromorphic-tfstate-102724112773 \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Block public access
aws s3api put-public-access-block \
  --bucket neuromorphic-tfstate-102724112773 \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### 3. Generate Secure Passwords

```bash
# Generate database password
DB_PASSWORD=$(openssl rand -base64 32)
echo "Database Password: $DB_PASSWORD"

# Generate Grafana admin password
GRAFANA_PASSWORD=$(openssl rand -base64 32)
echo "Grafana Password: $GRAFANA_PASSWORD"

# Save these securely (e.g., in a password manager)
```

### 4. Create terraform.tfvars

```bash
cd infra/terraform

# Copy example file
cp terraform.tfvars.example terraform.tfvars

# Edit with your favorite editor
nano terraform.tfvars
```

Update the passwords:

```hcl
db_password            = "YOUR_SECURE_DB_PASSWORD"
grafana_admin_password = "YOUR_SECURE_GRAFANA_PASSWORD"
```

---

## Infrastructure Deployment

### 1. Initialize Terraform

```bash
cd infra/terraform

# Initialize (downloads providers)
terraform init

# Or using Makefile
make init
```

Expected output:
```
Terraform has been successfully initialized!
```

### 2. Validate Configuration

```bash
# Validate syntax
terraform validate

# Format files
terraform fmt -recursive

# Or using Makefile
make validate
make fmt
```

### 3. Plan Infrastructure

```bash
# Create execution plan
terraform plan -out=tfplan

# Or using Makefile
make plan
```

Review the plan carefully. It should create:
- 1 VPC with subnets, gateways, and route tables
- 1 ECS cluster with 4 services
- 4 ECR repositories
- 1 Application Load Balancer with target groups
- 1 RDS PostgreSQL instance
- 2 EFS file systems
- Security groups and IAM roles
- Service discovery namespace

### 4. Apply Infrastructure

```bash
# Apply the plan
terraform apply tfplan

# Or auto-approve (use with caution)
terraform apply -auto-approve

# Or using Makefile
make apply
```

**Duration**: ~15-20 minutes

**Note**: RDS instance creation takes the longest (~10-15 minutes)

### 5. Save Important Outputs

```bash
# View all outputs
terraform output

# Save outputs to file
terraform output -json > outputs.json

# View deployment checklist
terraform output -raw deployment_checklist
```

---

## DNS Configuration

### 1. Get ACM Certificate Validation Records

```bash
# Get validation records
terraform output acm_certificate_validation_records

# Or
terraform output -json | jq -r '.acm_certificate_validation_records.value'
```

### 2. Add DNS Records in Cloudflare

#### A. Certificate Validation (CNAME)

Log in to Cloudflare → Select domain → DNS → Add record

For each validation record:
```
Type: CNAME
Name: [from terraform output]
Target: [from terraform output]
TTL: Auto
Proxy status: DNS only (grey cloud)
```

#### B. API Subdomain (CNAME)

```
Type: CNAME
Name: api
Target: [ALB DNS name from terraform output]
TTL: Auto
Proxy status: DNS only (grey cloud)
```

Get ALB DNS name:
```bash
terraform output -raw alb_dns_name
# Or
make output-alb
```

### 3. Wait for Certificate Validation

```bash
# Check certificate status
aws acm describe-certificate \
  --certificate-arn $(terraform output -json | jq -r '.acm_certificate_arn.value') \
  --region eu-south-1 \
  --query 'Certificate.Status'
```

Status should change from `PENDING_VALIDATION` to `ISSUED` (usually 1-5 minutes).

---

## Container Deployment

### 1. Prepare Docker Images

Ensure you have Dockerfiles for each service:
- `./inference/Dockerfile`
- `./ingestion/Dockerfile`
- `./trainer/Dockerfile`
- `./rag-copilot/Dockerfile`

### 2. Login to ECR

```bash
# Get ECR login command
aws ecr get-login-password --region eu-south-1 | \
  docker login --username AWS --password-stdin \
  $(terraform output -raw ecr_inference_url | cut -d/ -f1)

# Or using Makefile
make ecr-login
```

### 3. Build and Push Images

#### Inference Service

```bash
# Get repository URL
INFERENCE_REPO=$(terraform output -raw ecr_inference_url)

# Build
docker build -t $INFERENCE_REPO:latest ./inference

# Tag with version
docker tag $INFERENCE_REPO:latest $INFERENCE_REPO:v1.0.0

# Push both tags
docker push $INFERENCE_REPO:latest
docker push $INFERENCE_REPO:v1.0.0
```

#### RAG Copilot Service

```bash
RAG_REPO=$(terraform output -raw ecr_rag_copilot_url)
docker build -t $RAG_REPO:latest ./rag-copilot
docker tag $RAG_REPO:latest $RAG_REPO:v1.0.0
docker push $RAG_REPO:latest
docker push $RAG_REPO:v1.0.0
```

#### Ingestion Service

```bash
INGESTION_REPO=$(terraform output -raw ecr_ingestion_url)
docker build -t $INGESTION_REPO:latest ./ingestion
docker tag $INGESTION_REPO:latest $INGESTION_REPO:v1.0.0
docker push $INGESTION_REPO:latest
docker push $INGESTION_REPO:v1.0.0
```

#### Trainer Service

```bash
TRAINER_REPO=$(terraform output -raw ecr_trainer_url)
docker build -t $TRAINER_REPO:latest ./trainer
docker tag $TRAINER_REPO:latest $TRAINER_REPO:v1.0.0
docker push $TRAINER_REPO:latest
docker push $TRAINER_REPO:v1.0.0
```

### 4. Force Service Updates

After pushing images, force ECS to deploy them:

```bash
# Get cluster name
CLUSTER=$(terraform output -raw ecs_cluster_name)

# Update inference service
aws ecs update-service \
  --cluster $CLUSTER \
  --service nil-inference-prod \
  --force-new-deployment \
  --region eu-south-1

# Update RAG copilot service
aws ecs update-service \
  --cluster $CLUSTER \
  --service nil-rag-copilot-prod \
  --force-new-deployment \
  --region eu-south-1

# Update Prometheus
aws ecs update-service \
  --cluster $CLUSTER \
  --service nil-prometheus-prod \
  --force-new-deployment \
  --region eu-south-1

# Update Grafana
aws ecs update-service \
  --cluster $CLUSTER \
  --service nil-grafana-prod \
  --force-new-deployment \
  --region eu-south-1

# Or using Makefile
make ecs-update-inference
make ecs-update-rag
make ecs-update-prometheus
make ecs-update-grafana
```

### 5. Monitor Deployment

```bash
# Watch service status
aws ecs describe-services \
  --cluster $CLUSTER \
  --services nil-inference-prod \
  --query 'services[0].deployments' \
  --region eu-south-1

# Or tail logs
aws logs tail /ecs/nil-prod --follow --filter-pattern "inference"

# Or using Makefile
make ecs-logs-inference
```

---

## Monitoring Setup

### 1. Access Grafana

```bash
# Get Grafana URL
terraform output -raw grafana_url
# https://api.neuromorphicinference.com/grafana
```

Login credentials:
- Username: `admin`
- Password: [from terraform.tfvars `grafana_admin_password`]

### 2. Add Prometheus Data Source

In Grafana:

1. Go to **Configuration** → **Data Sources**
2. Click **Add data source**
3. Select **Prometheus**
4. Configure:
   ```
   Name: Prometheus
   URL: http://prometheus.nil.local:9090
   Access: Server (default)
   ```
5. Click **Save & Test**

### 3. Import Dashboards

Import pre-built dashboards:

#### ECS Dashboard
- Dashboard ID: 551 (AWS ECS)
- Data source: Prometheus

#### RDS Dashboard
- Dashboard ID: 707 (RDS)
- Data source: Prometheus

#### ALB Dashboard
- Dashboard ID: 8466 (AWS ALB)
- Data source: Prometheus

### 4. Configure Alerts (Optional)

Set up alerts for:
- High CPU/Memory usage
- Failed health checks
- Database connection errors
- High latency

---

## Verification

### 1. Check Infrastructure

```bash
# List all resources
terraform state list

# Check specific resources
terraform state show aws_lb.main
terraform state show aws_db_instance.main
```

### 2. Test API Endpoints

```bash
# Health check
curl https://api.neuromorphicinference.com/health

# Version
curl https://api.neuromorphicinference.com/version

# Inference (POST request)
curl -X POST https://api.neuromorphicinference.com/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "test"}'

# RAG
curl https://api.neuromorphicinference.com/rag/health

# Grafana
curl https://api.neuromorphicinference.com/grafana/api/health
```

### 3. Check CloudWatch Logs

```bash
# List log streams
aws logs describe-log-streams \
  --log-group-name /ecs/nil-prod \
  --region eu-south-1

# Tail logs
aws logs tail /ecs/nil-prod --follow
```

### 4. Verify Database Connectivity

```bash
# Get RDS endpoint
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)

# Install PostgreSQL client (if not installed)
sudo apt-get install postgresql-client -y

# Connect (requires bastion host or VPN)
psql -h $RDS_ENDPOINT -U niladmin -d neuromorphic
```

**Note**: RDS is in private subnet. You'll need a bastion host or VPN to connect directly.

---

## Troubleshooting

### Issue: Terraform Apply Fails

**Solution**:
1. Read error message carefully
2. Check AWS service limits
3. Verify IAM permissions
4. Ensure S3 backend bucket exists
5. Run `terraform plan` to diagnose

### Issue: ECS Tasks Not Starting

**Symptoms**: Tasks stuck in PENDING or immediately fail

**Solutions**:
1. Check CloudWatch logs:
   ```bash
   aws logs tail /ecs/nil-prod --follow
   ```

2. Verify image exists in ECR:
   ```bash
   aws ecr describe-images \
     --repository-name nil/inference \
     --region eu-south-1
   ```

3. Check security groups allow outbound internet (for pulling images)

4. Verify execution role has ECR pull permissions

### Issue: Certificate Validation Stuck

**Symptoms**: Certificate remains in PENDING_VALIDATION

**Solutions**:
1. Verify DNS records are added correctly in Cloudflare
2. Ensure CNAME records are set to "DNS only" (not proxied)
3. Wait 5-10 minutes for DNS propagation
4. Check DNS with:
   ```bash
   dig [validation-record-name]
   ```

### Issue: Health Checks Failing

**Symptoms**: Target groups show unhealthy targets

**Solutions**:
1. Verify application is listening on correct port (8000 or 3000)
2. Check health check endpoint returns 200 status
3. Ensure security groups allow ALB → ECS communication
4. Review application logs for errors
5. Test health check endpoint directly (if accessible)

### Issue: Cannot Connect to RDS

**Symptoms**: Connection timeout or refused

**Solutions**:
1. Verify RDS security group allows port 5432 from ECS SG
2. Check RDS instance is in "available" state
3. Ensure applications are in same VPC
4. Use bastion host for testing connection
5. Verify database credentials in SSM Parameter Store

### Issue: Grafana Shows "Bad Gateway"

**Symptoms**: 502 error when accessing /grafana

**Solutions**:
1. Check Grafana task is running:
   ```bash
   aws ecs list-tasks --cluster nil-cluster-prod --service-name nil-grafana-prod
   ```
2. Verify target group health checks
3. Check Grafana logs
4. Ensure EFS mount succeeded
5. Verify database connection (Grafana uses PostgreSQL backend)

### Issue: High Costs

**Solutions**:
1. Stop NAT Gateway when not needed:
   ```bash
   # In terraform.tfvars, set:
   enable_nat_gateway = false
   terraform apply
   ```

2. Scale down ECS tasks to 0 when idle:
   ```bash
   aws ecs update-service \
     --cluster nil-cluster-prod \
     --service nil-inference-prod \
     --desired-count 0
   ```

3. Stop RDS instance (note: will still incur storage costs):
   ```bash
   aws rds stop-db-instance --db-instance-identifier nil-db-prod
   ```

---

## Cleanup

To destroy all infrastructure:

```bash
# Review what will be destroyed
terraform plan -destroy

# Destroy (will prompt for confirmation)
terraform destroy

# Or using Makefile
make destroy
```

**Warning**: This will delete:
- All ECS services and tasks
- RDS database (final snapshot will be created)
- ALB and networking
- EFS file systems
- ECR repositories and images

**Note**: The S3 state bucket must be manually deleted:

```bash
# Empty bucket first
aws s3 rm s3://neuromorphic-tfstate-102724112773 --recursive

# Delete bucket
aws s3api delete-bucket \
  --bucket neuromorphic-tfstate-102724112773 \
  --region eu-south-1
```

---

## Next Steps

After successful deployment:

1. **Set up CI/CD**: Automate Docker image builds and deployments
2. **Configure backups**: Set up automated RDS snapshots and EFS backups
3. **Enable monitoring**: Set up CloudWatch alarms and Grafana alerts
4. **Implement auto-scaling**: Configure ECS service auto-scaling based on metrics
5. **Harden security**: Review security groups, enable GuardDuty, set up CloudTrail
6. **Document runbooks**: Create operational procedures for common tasks

---

## Support

For issues or questions:
- GitHub: https://github.com/nepryoon
- Website: https://www.neuromorphicinference.com

## References

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
