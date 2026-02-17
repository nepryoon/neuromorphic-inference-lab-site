.PHONY: help init plan apply destroy validate fmt clean

help: ## Show this help message
	@echo "Neuromorphic Inference Lab - Terraform Commands"
	@echo "================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

init: ## Initialize Terraform
	@echo "Initializing Terraform..."
	terraform init

validate: ## Validate Terraform configuration
	@echo "Validating Terraform configuration..."
	terraform validate

fmt: ## Format Terraform files
	@echo "Formatting Terraform files..."
	terraform fmt -recursive

plan: ## Create Terraform execution plan
	@echo "Creating Terraform plan..."
	terraform plan -out=tfplan

apply: ## Apply Terraform changes
	@echo "Applying Terraform changes..."
	terraform apply tfplan

apply-auto: ## Apply Terraform changes without confirmation
	@echo "Applying Terraform changes (auto-approve)..."
	terraform apply -auto-approve

destroy: ## Destroy Terraform infrastructure
	@echo "Destroying Terraform infrastructure..."
	terraform destroy

output: ## Show Terraform outputs
	@echo "Showing Terraform outputs..."
	terraform output

output-checklist: ## Show deployment checklist
	@echo "Showing deployment checklist..."
	terraform output -raw deployment_checklist

output-ecr: ## Show ECR repository URLs
	@echo "ECR Repository URLs:"
	@echo "==================="
	@terraform output -json | jq -r '.ecr_inference_url.value, .ecr_ingestion_url.value, .ecr_trainer_url.value, .ecr_rag_copilot_url.value'

output-alb: ## Show ALB DNS name
	@echo "ALB DNS Name (use as CNAME in Cloudflare):"
	@echo "==========================================="
	@terraform output -raw alb_dns_name

output-rds: ## Show RDS endpoint
	@echo "RDS Endpoint:"
	@echo "============="
	@terraform output -raw rds_endpoint

clean: ## Clean Terraform files
	@echo "Cleaning Terraform files..."
	rm -rf .terraform
	rm -f .terraform.lock.hcl
	rm -f tfplan
	rm -f terraform.tfstate
	rm -f terraform.tfstate.backup

state-list: ## List resources in Terraform state
	@echo "Listing Terraform state resources..."
	terraform state list

state-show: ## Show details of a specific resource (use: make state-show RESOURCE=<resource>)
	@if [ -z "$(RESOURCE)" ]; then \
		echo "Error: Please specify RESOURCE variable"; \
		echo "Usage: make state-show RESOURCE=aws_vpc.main"; \
		exit 1; \
	fi
	terraform state show $(RESOURCE)

import: ## Import existing resource (use: make import RESOURCE=<resource> ID=<id>)
	@if [ -z "$(RESOURCE)" ] || [ -z "$(ID)" ]; then \
		echo "Error: Please specify RESOURCE and ID variables"; \
		echo "Usage: make import RESOURCE=aws_vpc.main ID=vpc-123456"; \
		exit 1; \
	fi
	terraform import $(RESOURCE) $(ID)

graph: ## Generate Terraform dependency graph
	@echo "Generating Terraform dependency graph..."
	terraform graph | dot -Tpng > graph.png
	@echo "Graph saved to graph.png"

refresh: ## Refresh Terraform state
	@echo "Refreshing Terraform state..."
	terraform refresh

taint: ## Taint a resource for recreation (use: make taint RESOURCE=<resource>)
	@if [ -z "$(RESOURCE)" ]; then \
		echo "Error: Please specify RESOURCE variable"; \
		echo "Usage: make taint RESOURCE=aws_ecs_service.inference"; \
		exit 1; \
	fi
	terraform taint $(RESOURCE)

untaint: ## Untaint a resource (use: make untaint RESOURCE=<resource>)
	@if [ -z "$(RESOURCE)" ]; then \
		echo "Error: Please specify RESOURCE variable"; \
		echo "Usage: make untaint RESOURCE=aws_ecs_service.inference"; \
		exit 1; \
	fi
	terraform untaint $(RESOURCE)

# AWS Helper Commands
ecr-login: ## Login to ECR
	@echo "Logging in to ECR..."
	aws ecr get-login-password --region eu-south-1 | docker login --username AWS --password-stdin $$(terraform output -raw ecr_inference_url | cut -d/ -f1)

ecs-update-inference: ## Force update of inference service
	@echo "Forcing new deployment of inference service..."
	aws ecs update-service \
		--cluster $$(terraform output -raw ecs_cluster_name) \
		--service nil-inference-prod \
		--force-new-deployment \
		--region eu-south-1

ecs-update-rag: ## Force update of RAG copilot service
	@echo "Forcing new deployment of RAG copilot service..."
	aws ecs update-service \
		--cluster $$(terraform output -raw ecs_cluster_name) \
		--service nil-rag-copilot-prod \
		--force-new-deployment \
		--region eu-south-1

ecs-update-grafana: ## Force update of Grafana service
	@echo "Forcing new deployment of Grafana service..."
	aws ecs update-service \
		--cluster $$(terraform output -raw ecs_cluster_name) \
		--service nil-grafana-prod \
		--force-new-deployment \
		--region eu-south-1

ecs-update-prometheus: ## Force update of Prometheus service
	@echo "Forcing new deployment of Prometheus service..."
	aws ecs update-service \
		--cluster $$(terraform output -raw ecs_cluster_name) \
		--service nil-prometheus-prod \
		--force-new-deployment \
		--region eu-south-1

ecs-logs-inference: ## Tail logs for inference service
	@echo "Tailing logs for inference service..."
	aws logs tail /ecs/nil-prod --follow --filter-pattern "inference"

ecs-logs-rag: ## Tail logs for RAG copilot service
	@echo "Tailing logs for RAG copilot service..."
	aws logs tail /ecs/nil-prod --follow --filter-pattern "rag-copilot"

ecs-logs-grafana: ## Tail logs for Grafana service
	@echo "Tailing logs for Grafana service..."
	aws logs tail /ecs/nil-prod --follow --filter-pattern "grafana"

ecs-logs-prometheus: ## Tail logs for Prometheus service
	@echo "Tailing logs for Prometheus service..."
	aws logs tail /ecs/nil-prod --follow --filter-pattern "prometheus"
