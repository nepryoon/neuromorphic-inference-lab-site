variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "eu-south-1"
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
  default     = "102724112773"
}

variable "project_prefix" {
  description = "Project prefix for resource naming"
  type        = string
  default     = "nil"
}

variable "environment" {
  description = "Environment name (e.g., prod, staging, dev)"
  type        = string
  default     = "prod"
}

variable "inference_cpu" {
  description = "CPU units for inference task (1024 = 1 vCPU)"
  type        = number
  default     = 512
}

variable "inference_memory" {
  description = "Memory for inference task in MiB"
  type        = number
  default     = 1024
}

variable "rag_copilot_cpu" {
  description = "CPU units for RAG copilot task (1024 = 1 vCPU)"
  type        = number
  default     = 512
}

variable "rag_copilot_memory" {
  description = "Memory for RAG copilot task in MiB"
  type        = number
  default     = 1024
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "neuromorphic"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "niladmin"
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "grafana_admin_password" {
  description = "Grafana admin password"
  type        = string
  sensitive   = true
}

variable "domain_name" {
  description = "Domain name for API"
  type        = string
  default     = "api.neuromorphicinference.com"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones for subnets"
  type        = list(string)
  default     = ["eu-south-1a", "eu-south-1b"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT gateway for private subnets"
  type        = bool
  default     = true
}

variable "db_backup_retention_days" {
  description = "Number of days to retain database backups"
  type        = number
  default     = 7
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS in GB"
  type        = number
  default     = 20
}

variable "prometheus_version" {
  description = "Prometheus Docker image version"
  type        = string
  default     = "v2.53.0"
}

variable "grafana_version" {
  description = "Grafana Docker image version"
  type        = string
  default     = "11.1.0"
}

# Open Banking Service Configuration
variable "open_banking_cpu" {
  description = "CPU units for Open Banking task (1024 = 1 vCPU)"
  type        = number
  default     = 256
}

variable "open_banking_memory" {
  description = "Memory for Open Banking task in MiB"
  type        = number
  default     = 512
}

variable "open_banking_desired_count" {
  description = "Desired number of Open Banking service tasks"
  type        = number
  default     = 1
}

variable "open_banking_min_count" {
  description = "Minimum number of Open Banking service tasks for auto-scaling"
  type        = number
  default     = 1
}

variable "open_banking_max_count" {
  description = "Maximum number of Open Banking service tasks for auto-scaling"
  type        = number
  default     = 3
}

