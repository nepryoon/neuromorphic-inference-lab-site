# Neuromorphic Inference Lab — Site

**Live:** https://www.neuromorphicinference.com/  
**Systems hub:** https://www.neuromorphicinference.com/demos/  
**Proof Ledger:** https://www.neuromorphicinference.com/evidence/  
**Build provenance (commit/branch):** https://www.neuromorphicinference.com/api/build

This repository contains the source for the Neuromorphic Inference Lab website:
**static HTML + lightweight Cloudflare Pages Functions**.

The site is intentionally designed as an **applied Full-Stack Machine Learning Engineering portfolio**:
every claim is backed by **clickable proof** (live docs + source code).

---

## Quick verification

1. **End-to-end systems thinking**  
   Each project is framed as a system (data → features → training → artefacts → serving → evaluation → ops).

2. **Evidence-based competence**  
   The Proof Ledger maps “skills” to stable anchors for direct linking.

3. **Traceability / provenance**  
   Footer build provenance shows commit + branch from `/api/build`.

---

## Hero systems (the “front door”)

### 1) MV Grid Fault Risk Scoring Platform
**Live docs:** https://www.neuromorphicinference.com/demos/mv-grid-fault-risk/  
**API docs:** https://mv-grid-fault-risk-api.onrender.com/docs  
**Source:** https://github.com/nepryoon/mv-grid-fault-risk

Production-first fault risk inference for medium-voltage networks:
- feature engineering + tracked training
- artefact versioning and releases
- model serving via API
- demo UI for interactive scoring
- monitoring-ready outputs (structured, consistent)

Keywords: CI/CD for ML, model serving, inference scaling, artefact lineage, automated retraining (pattern-ready).

### 2) RAG Copilot (LLMOps)
**Live docs:** https://www.neuromorphicinference.com/demos/rag-copilot/  
**Source:** https://github.com/nepryoon/nil-rag-copilot

RAG copilot built for auditability and regression safety:
- retrieval traceability + citations
- evaluation harness for quality regression
- guardrails for prompt injection and unsafe requests
- production-friendly layout (API + containerisation patterns)

Keywords: RAG, LLMOps, evaluation harness, guardrails, citations, observability.

### 3) Forecast Studio
**Live docs:** https://www.neuromorphicinference.com/demos/forecast-studio/  
**Source:** https://github.com/nepryoon/nil-forecast-studio

Forecasting system designed to escape the “notebook trap”:
- ingestion + validation
- backtesting and model comparison
- reproducible artefacts and reports
- stakeholder-facing memo output

Keywords: time series, backtesting, reproducibility, artefacts, scheduling.

---

## Principles

- **Evidence-based competence**: no “skill listing” without clickable proof (live + code).
- **Production-first framing**: projects are described as systems, not papers.
- **Stable URLs**: `/demos/*` and `/evidence#*` are intended for direct CV links.
- **Fast scanning**: each page prioritises clarity for technical screening.

---

## Site structure

- `/` → positioning (“Signal”)
- `/demos/` → systems catalogue (cards + links)
- `/demos/<project>/` → live documentation (case study / verification path)
- `/evidence/` → Proof Ledger (skill → proof mapping)
- `/about/` → identity / narrative
- `/research/` → archive (intentionally secondary)

---

## Repo layout (high level)

- `index.html` → home
- `style.css` → shared styling
- `build-info.js` → populates footer provenance by calling `/api/build`
- `demos/` → systems pages
- `evidence/`, `about/`, `research/` → section pages
- `functions/api/build.js` → Cloudflare Pages Function returning build metadata as JSON
- `infra/terraform/` → **AWS infrastructure code (Terraform)** for hosting the complete ML stack

---

## Build provenance (commit + branch)

Cloudflare Pages exposes build information as environment variables (e.g., commit SHA, branch).
Because these variables are not directly available in the browser, the site uses:

- Function endpoint: `/api/build` (served by `functions/api/build.js`)
- Client script: `build-info.js` fetches `/api/build` and updates the footer

This provides a lightweight traceability signal engineers can audit.

---

## Local development

### Option A — Static preview (fastest)
This site is static HTML. Use any static server:

- Python: `python -m http.server 8080`
- Node: `npx serve .`

Open: http://localhost:8080

### Sovereign AI demo destination

The homepage hero, responsive navigation, and Systems catalogue link to the Enterprise
Sovereign AI Decision Matrix. The public destination defaults to
`https://matrix.neuromorphicinference.com` and can be overridden for preview or staging
deployments with:

```bash
NEXT_PUBLIC_SOVEREIGN_MATRIX_URL=https://matrix-preview.example.com
```

Set the variable in Cloudflare Pages for deployed environments, or copy `.env.example`
to `.dev.vars` when using Wrangler locally. Overrides must be HTTPS URLs without embedded
credentials; invalid values safely use the production default. To verify locally, run
`npx wrangler pages dev .`, open `http://localhost:8788`, and inspect the “Launch Sovereign
AI Demo” link. A plain static server uses the production default because Pages Functions
are not available.

> Note: Cloudflare Pages Functions won’t run in a plain static server.

### Option B — With Pages Functions (recommended)
Run static + Functions locally using Wrangler:

- `npx wrangler pages dev .`

---

## Deployment (Cloudflare Pages)

This repo is connected to Cloudflare Pages (git-driven deploy).

Typical setup:
- Build command: none / empty (static)
- Output directory: `/` (repo root)
- Functions directory: `functions/` (auto-detected)

After pushing to `main`, Cloudflare Pages deploys automatically.

**📖 Developer Guides:**
- **[DEVELOPER_WORKFLOW.md](DEVELOPER_WORKFLOW.md)** - Step-by-step guide for deploying HTML changes
- **[DEPLOYMENT_ANALYSIS.md](DEPLOYMENT_ANALYSIS.md)** - Technical analysis of build, deployment, and caching

---

## Adding a new system (standard workflow)

1. Create a live docs page:
   - `/demos/<slug>/index.html`

2. Link the code repository (or create a new repo)

3. Update:
   - `/demos/index.html` (add a project card with Live/Docs + Source)
   - `/evidence/index.html` (add proofs for skills demonstrated)

4. Enforce bidirectional links:
   - Demo page → GitHub repo
   - GitHub README → live docs page + Proof Ledger

---

## Related repositories (code)

### Core Systems
- **MV Grid Fault Risk:** https://github.com/nepryoon/mv-grid-fault-risk
- **RAG Copilot (LLMOps):** https://github.com/nepryoon/nil-rag-copilot
- **Forecast Studio:** https://github.com/nepryoon/nil-forecast-studio
- **Centrico LiveLab (MLOps):** https://github.com/nepryoon/centrico-livelab-mlops

### Additional Microservices
- **Open Banking Transaction Enrichment:** https://github.com/nepryoon/open-banking-transaction-enrichment
- **Visual Inspector:** https://github.com/nepryoon/nil-visual-inspector
- **Tabular Risk:** https://github.com/nepryoon/nil-tabular-risk
- **EdgePulse:** https://github.com/nepryoon/edgepulse
- **Infrastructure Templates:** https://github.com/nepryoon/nil-infra-template

(See `/demos/` for the authoritative list with live demos.)

---

## Monitoring & Observability

The platform includes a complete monitoring stack with Prometheus and Grafana.

### Dashboard

Grafana is auto-provisioned with a pre-built ML dashboard at startup:
- **Model F1 Score** — current quality gate metric
- **Predictions/min** — throughput
- **P95 Latency** — inference performance
- **Prediction Score Distribution** — heatmap for drift detection
- **Predictions by Class** — class balance over time

Access: http://localhost:3000 (admin / centrico)

Prediction history is logged to the `prediction_log` table.

### Quick Start

```bash
docker compose -f docker-compose.monitoring.yml up --build
```

The stack includes:
- **Inference API** with Prometheus metrics at `/metrics`
- **Prometheus** scraping metrics every 10s
- **Grafana** with pre-configured dashboards and datasources
- **PostgreSQL** for prediction logging

---

## AWS Infrastructure (Terraform)

Complete Terraform configuration for deploying the full Neuromorphic Inference Lab stack on AWS:

📍 **Location:** `infra/terraform/`

### What's Included

- **VPC & Networking:** Multi-AZ setup with public/private subnets
- **ECS Fargate:** Container orchestration with 4 services (inference, RAG, Prometheus, Grafana)
- **ECR:** Container registries for all services
- **ALB:** HTTPS load balancing with path-based routing
- **RDS:** PostgreSQL 16 database with encryption
- **Monitoring:** Prometheus + Grafana with persistent storage
- **Security:** IAM roles, security groups, secrets management

### Quick Start

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your configuration
terraform init
terraform plan
terraform apply
```

📚 **Documentation:**
- [README.md](infra/terraform/README.md) - Overview and quick start
- [DEPLOYMENT_GUIDE.md](infra/terraform/DEPLOYMENT_GUIDE.md) - Step-by-step deployment
- [ARCHITECTURE.md](infra/terraform/ARCHITECTURE.md) - Visual architecture diagram
- [QUICK_REFERENCE.md](infra/terraform/QUICK_REFERENCE.md) - Command cheat sheet

**Region:** eu-south-1 (Milano)  
**Estimated Cost:** ~$120-170/month  
**Resources:** ~60 AWS resources

---

## Licence

Add a `LICENSE` file if you want explicit reuse terms for the site content.
(MIT is common for code; content may require a separate policy.)

---

## Contact

GitHub: https://github.com/nepryoon  
Website: https://www.neuromorphicinference.com
