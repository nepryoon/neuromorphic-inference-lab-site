# Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INTERNET (Public)                               │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                   ┌───────────────┴───────────────┐
                   │      Cloudflare DNS           │
                   │  api.neuromorphicinference    │
                   │          .com                 │
                   └───────────────┬───────────────┘
                                   │ HTTPS (443)
                                   │
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AWS VPC (10.0.0.0/16)                               │
│  Region: eu-south-1 (Milano)                                                │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                       PUBLIC SUBNETS                                │    │
│  │  ┌─────────────────────┐           ┌─────────────────────┐         │    │
│  │  │ Public Subnet 1     │           │ Public Subnet 2     │         │    │
│  │  │ 10.0.0.0/24         │           │ 10.0.1.0/24         │         │    │
│  │  │ AZ: eu-south-1a     │           │ AZ: eu-south-1b     │         │    │
│  │  │                     │           │                     │         │    │
│  │  │  ┌───────────────┐  │           │  ┌───────────────┐  │         │    │
│  │  │  │               │  │           │  │               │  │         │    │
│  │  │  │  Application  │──┼───────────┼──│  Application  │  │         │    │
│  │  │  │      Load     │  │           │  │      Load     │  │         │    │
│  │  │  │   Balancer    │  │           │  │   Balancer    │  │         │    │
│  │  │  │   (ALB)       │  │           │  │   (ALB)       │  │         │    │
│  │  │  │               │  │           │  │               │  │         │    │
│  │  │  └───────┬───────┘  │           │  └───────────────┘  │         │    │
│  │  │          │          │           │                     │         │    │
│  │  │  ┌───────▼───────┐  │           │                     │         │    │
│  │  │  │  NAT Gateway  │  │           │                     │         │    │
│  │  │  └───────────────┘  │           │                     │         │    │
│  │  └─────────────────────┘           └─────────────────────┘         │    │
│  └────────────────┬───────────────────────────┬────────────────────────┘    │
│                   │                           │                             │
│       ┌───────────▼───────────────────────────▼───────────┐                 │
│       │            Internet Gateway                       │                 │
│       └───────────────────────────────────────────────────┘                 │
│                                                                              │
│  Path-based Routing (HTTPS):                                                │
│    /predict, /health, /metrics  →  Inference Service                        │
│    /rag, /ask                   →  RAG Copilot Service                      │
│    /grafana                     →  Grafana                                  │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                       PRIVATE SUBNETS                               │    │
│  │  ┌─────────────────────┐           ┌─────────────────────┐         │    │
│  │  │ Private Subnet 1    │           │ Private Subnet 2    │         │    │
│  │  │ 10.0.10.0/24        │           │ 10.0.11.0/24        │         │    │
│  │  │ AZ: eu-south-1a     │           │ AZ: eu-south-1b     │         │    │
│  │  │                     │           │                     │         │    │
│  │  │  ┌──────────────┐   │           │   ┌──────────────┐  │         │    │
│  │  │  │ ECS Fargate  │   │           │   │ ECS Fargate  │  │         │    │
│  │  │  ├──────────────┤   │           │   ├──────────────┤  │         │    │
│  │  │  │ Inference    │   │           │   │ Inference    │  │         │    │
│  │  │  │ Service      │   │           │   │ Service      │  │         │    │
│  │  │  │ Port: 8000   │   │           │   │ Port: 8000   │  │         │    │
│  │  │  └──────┬───────┘   │           │   └──────────────┘  │         │    │
│  │  │         │           │           │                     │         │    │
│  │  │  ┌──────▼───────┐   │           │   ┌──────────────┐  │         │    │
│  │  │  │ RAG Copilot  │   │           │   │ RAG Copilot  │  │         │    │
│  │  │  │ Service      │   │           │   │ Service      │  │         │    │
│  │  │  │ Port: 8000   │   │           │   │ Port: 8000   │  │         │    │
│  │  │  └──────┬───────┘   │           │   └──────────────┘  │         │    │
│  │  │         │           │           │                     │         │    │
│  │  │  ┌──────▼───────┐   │           │   ┌──────────────┐  │         │    │
│  │  │  │ Prometheus   │   │           │   │ Prometheus   │  │         │    │
│  │  │  │ v2.53.0      │   │           │   │ v2.53.0      │  │         │    │
│  │  │  │ Port: 9090   │   │           │   │ Port: 9090   │  │         │    │
│  │  │  └──────┬───────┘   │           │   └──────────────┘  │         │    │
│  │  │         │           │           │                     │         │    │
│  │  │  ┌──────▼───────┐   │           │   ┌──────────────┐  │         │    │
│  │  │  │ Grafana      │   │           │   │ Grafana      │  │         │    │
│  │  │  │ v11.1.0      │   │           │   │ v11.1.0      │  │         │    │
│  │  │  │ Port: 3000   │   │           │   │ Port: 3000   │  │         │    │
│  │  │  └──────┬───────┘   │           │   └──────────────┘  │         │    │
│  │  │         │           │           │         │           │         │    │
│  │  │         │           │           │         │           │         │    │
│  │  │  ┌──────▼───────────┴───────────┴─────────▼──────┐    │         │    │
│  │  │  │           RDS PostgreSQL 16                    │    │         │    │
│  │  │  │           db.t3.micro                          │    │         │    │
│  │  │  │           Storage: 20GB gp3 (encrypted)        │    │         │    │
│  │  │  │           Port: 5432                           │    │         │    │
│  │  │  │           Multi-AZ: No (single instance)       │    │         │    │
│  │  │  └────────────────────────────────────────────────┘    │         │    │
│  │  │                                                         │         │    │
│  │  │  ┌─────────────────────────────────────────────────┐   │         │    │
│  │  │  │              EFS File Systems                    │   │         │    │
│  │  │  │  - Prometheus data (encrypted)                  │   │         │    │
│  │  │  │  - Grafana data (encrypted)                     │   │         │    │
│  │  │  └─────────────────────────────────────────────────┘   │         │    │
│  │  │                                                         │         │    │
│  │  └─────────────────────┘           └─────────────────────┘         │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │               Service Discovery (AWS Cloud Map)                     │    │
│  │                 Namespace: nil.local                                │    │
│  │    - prometheus.nil.local:9090                                      │    │
│  │    - grafana.nil.local:3000                                         │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                     ECR Repositories (Container Registry)                    │
│  - nil/inference      (Inference service images)                            │
│  - nil/ingestion      (Data ingestion service images)                       │
│  - nil/trainer        (Model training service images)                       │
│  - nil/rag-copilot    (RAG copilot service images)                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                AWS Systems Manager Parameter Store (Secrets)                 │
│  - /nil/prod/db_password            (Database password - encrypted)         │
│  - /nil/prod/grafana_admin_password (Grafana password - encrypted)          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         CloudWatch Logs                                      │
│  Log Group: /ecs/nil-prod                                                   │
│    - inference/*      (Inference service logs)                              │
│    - rag-copilot/*    (RAG copilot service logs)                            │
│    - prometheus/*     (Prometheus logs)                                     │
│    - grafana/*        (Grafana logs)                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        Security Groups                                       │
│  1. ALB SG         - Inbound: 80, 443 from 0.0.0.0/0                       │
│  2. ECS Tasks SG   - Inbound: 8000 from ALB SG                              │
│  3. RDS SG         - Inbound: 5432 from ECS Tasks SG                        │
│  4. Monitoring SG  - Inbound: 9090, 3000 from self & ALB SG                 │
└─────────────────────────────────────────────────────────────────────────────┘

═════════════════════════════════════════════════════════════════════════════

Key Features:
─────────────
✓ Multi-AZ deployment across 2 availability zones
✓ High availability with ALB health checks
✓ Auto-scaling ready (configured but not yet enabled)
✓ Container Insights enabled for ECS monitoring
✓ Encrypted data at rest (RDS, EFS) and in transit (TLS/HTTPS)
✓ Private subnets for ECS and RDS (enhanced security)
✓ NAT Gateway for outbound internet access from private subnets
✓ Service Discovery for internal service communication
✓ CloudWatch Logs with 7-day retention
✓ Performance Insights enabled for RDS
✓ Automated daily backups (7-day retention)
✓ ACM-managed SSL certificate with auto-renewal
✓ Path-based routing for multiple services on single domain

Cost Optimization:
──────────────────
• Single NAT Gateway (can be disabled when not needed)
• t3.micro RDS instance (can scale up as needed)
• Fargate Spot pricing compatible (not yet configured)
• 7-day log retention (reduces storage costs)
• EFS lifecycle policy (transition to IA after 30 days)

Security:
─────────
• All secrets in AWS Systems Manager Parameter Store
• Security groups follow principle of least privilege
• RDS and ECS tasks in private subnets (no direct internet access)
• All data encrypted at rest and in transit
• IAM roles with minimal required permissions
• VPC flow logs ready (to be enabled)
• CloudTrail ready (to be enabled)
```
