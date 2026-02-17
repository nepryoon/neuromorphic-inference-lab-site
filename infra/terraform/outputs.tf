# VPC Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

# ALB Outputs
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer (use as CNAME in Cloudflare)"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Hosted zone ID of the Application Load Balancer"
  value       = aws_lb.main.zone_id
}

# ACM Certificate Outputs
output "acm_certificate_arn" {
  description = "ARN of the ACM certificate"
  value       = aws_acm_certificate.main.arn
}

output "acm_certificate_validation_records" {
  description = "DNS validation records for ACM certificate (add these to Cloudflare)"
  value = {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name  = dvo.resource_record_name
      type  = dvo.resource_record_type
      value = dvo.resource_record_value
    }
  }
}

# RDS Outputs
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
}

output "rds_address" {
  description = "RDS instance address"
  value       = aws_db_instance.main.address
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

# ECR Repository URLs
output "ecr_inference_url" {
  description = "ECR repository URL for inference service"
  value       = aws_ecr_repository.inference.repository_url
}

output "ecr_ingestion_url" {
  description = "ECR repository URL for ingestion service"
  value       = aws_ecr_repository.ingestion.repository_url
}

output "ecr_trainer_url" {
  description = "ECR repository URL for trainer service"
  value       = aws_ecr_repository.trainer.repository_url
}

output "ecr_rag_copilot_url" {
  description = "ECR repository URL for RAG copilot service"
  value       = aws_ecr_repository.rag_copilot.repository_url
}

output "ecr_open_banking_url" {
  description = "ECR repository URL for Open Banking service"
  value       = aws_ecr_repository.open_banking.repository_url
}

# ECS Outputs
output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ECS cluster ARN"
  value       = aws_ecs_cluster.main.arn
}

# Service Discovery Outputs
output "service_discovery_namespace" {
  description = "Service discovery namespace"
  value       = aws_service_discovery_private_dns_namespace.main.name
}

output "prometheus_service_discovery_name" {
  description = "Prometheus service discovery DNS name"
  value       = "${aws_service_discovery_service.prometheus.name}.${aws_service_discovery_private_dns_namespace.main.name}"
}

output "grafana_service_discovery_name" {
  description = "Grafana service discovery DNS name"
  value       = "${aws_service_discovery_service.grafana.name}.${aws_service_discovery_private_dns_namespace.main.name}"
}

# Monitoring URLs
output "grafana_url" {
  description = "Grafana URL (after certificate validation and DNS setup)"
  value       = "https://${var.domain_name}/grafana"
}

output "prometheus_internal_url" {
  description = "Prometheus internal URL (accessible within VPC)"
  value       = "http://${aws_service_discovery_service.prometheus.name}.${aws_service_discovery_private_dns_namespace.main.name}:9090"
}

# Deployment Checklist
output "deployment_checklist" {
  description = "Post-deployment steps checklist"
  value       = <<-EOT
  
  ═══════════════════════════════════════════════════════════════════════
  DEPLOYMENT CHECKLIST - Neuromorphic Inference Lab on AWS
  ═══════════════════════════════════════════════════════════════════════
  
  1. DNS Configuration in Cloudflare:
     ────────────────────────────────────────────────────────────────────
     a) Add ACM certificate validation records:
        ${join("\n        ", [for dvo in aws_acm_certificate.main.domain_validation_options : "Name: ${dvo.resource_record_name}\n        Type: ${dvo.resource_record_type}\n        Value: ${dvo.resource_record_value}"])}
     
     b) Add CNAME record:
        Name: api.neuromorphicinference.com
        Type: CNAME
        Value: ${aws_lb.main.dns_name}
        TTL: Auto
  
  2. Container Images:
     ────────────────────────────────────────────────────────────────────
     Build and push Docker images to ECR repositories:
     
     a) Inference service:
        aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.inference.repository_url}
        docker build -t ${aws_ecr_repository.inference.repository_url}:latest ./inference
        docker push ${aws_ecr_repository.inference.repository_url}:latest
     
     b) Ingestion service:
        docker build -t ${aws_ecr_repository.ingestion.repository_url}:latest ./ingestion
        docker push ${aws_ecr_repository.ingestion.repository_url}:latest
     
     c) Trainer service:
        docker build -t ${aws_ecr_repository.trainer.repository_url}:latest ./trainer
        docker push ${aws_ecr_repository.trainer.repository_url}:latest
     
     d) RAG Copilot service:
        docker build -t ${aws_ecr_repository.rag_copilot.repository_url}:latest ./rag-copilot
        docker push ${aws_ecr_repository.rag_copilot.repository_url}:latest
  
  3. Database Setup:
     ────────────────────────────────────────────────────────────────────
     a) Connect to RDS instance:
        Endpoint: ${aws_db_instance.main.endpoint}
        Database: ${var.db_name}
        Username: ${var.db_username}
     
     b) Run database migrations for each service
     
     c) Create necessary schemas and seed data
  
  4. ECS Service Updates:
     ────────────────────────────────────────────────────────────────────
     After pushing container images, force new deployments:
     
     aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.inference.name} --force-new-deployment --region ${var.aws_region}
     aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.rag_copilot.name} --force-new-deployment --region ${var.aws_region}
     aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.prometheus.name} --force-new-deployment --region ${var.aws_region}
     aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.grafana.name} --force-new-deployment --region ${var.aws_region}
  
  5. Monitoring Setup:
     ────────────────────────────────────────────────────────────────────
     a) Access Grafana:
        URL: ${var.domain_name}/grafana
        Username: admin
        Password: (from SSM parameter)
     
     b) Configure Prometheus data source in Grafana:
        URL: http://${aws_service_discovery_service.prometheus.name}.${aws_service_discovery_private_dns_namespace.main.name}:9090
     
     c) Import dashboards for:
        - ECS task metrics
        - RDS performance
        - ALB metrics
        - Application-specific metrics
  
  6. Verification:
     ────────────────────────────────────────────────────────────────────
     Test endpoints:
     - https://${var.domain_name}/health
     - https://${var.domain_name}/version
     - https://${var.domain_name}/predict
     - https://${var.domain_name}/rag
     - https://${var.domain_name}/grafana
  
  7. Security:
     ────────────────────────────────────────────────────────────────────
     a) Rotate SSM parameters regularly
     b) Enable AWS CloudTrail for audit logging
     c) Set up AWS GuardDuty for threat detection
     d) Review security group rules
     e) Enable VPC Flow Logs
  
  ═══════════════════════════════════════════════════════════════════════
  EOT
}
