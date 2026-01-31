# Neuromorphic Inference Lab — Site

**Live site:** https://www.neuromorphicinference.com/  
**Systems (demos hub):** https://www.neuromorphicinference.com/demos/  
**Proof Ledger (evidence index):** https://www.neuromorphicinference.com/evidence/  
**Build provenance (commit/branch):** https://www.neuromorphicinference.com/api/build  

This repository contains the source for the Neuromorphic Inference Lab website: **static HTML pages + lightweight Cloudflare Pages Functions**.
The site is designed as an **applied Full-Stack Machine Learning Engineering portfolio**, where every claim is backed by **clickable proof**.

---

## What recruiters can verify in 60 seconds

1. **Systems**: each project is presented as an end-to-end system (data → features → training → artefacts → serving → monitoring-ready outputs).  
2. **Proof Ledger**: skill-to-proof mapping with stable anchors intended to be linked from a CV.  
3. **Build provenance**: the footer shows commit/branch to demonstrate traceability.

---

## Hero systems (the “front door”)

### 1) MV Grid Fault Risk Scoring Platform
**Live docs:** https://www.neuromorphicinference.com/demos/mv-grid-fault-risk/  
**API (live):** https://mv-grid-fault-risk-api.onrender.com/docs  
**Source:** https://github.com/nepryoon/mv-grid-fault-risk  

A production-first pipeline for medium-voltage fault risk inference:
- feature engineering + model training (tracked)
- artefact versioning
- model serving (API)
- demo UI for interactive scoring

Key keywords: CI/CD for ML, inference serving, model artefacts, pipeline automation, monitoring-ready outputs.

### 2) RAG Copilot (LLMOps)
**Live docs:** https://www.neuromorphicinference.com/demos/rag-copilot/  
**Source:** https://github.com/nepryoon/nil-rag-copilot  

A RAG chatbot built to be auditable and regression-tested:
- citations and retrieval transparency
- evaluation harness for quality regression
- guardrails for prompt injection / unsafe requests
- production-ready structure (API + containerisation)

Key keywords: RAG, LLMOps, evaluation harness, guardrails, citations.

### 3) Forecast Studio
**Live docs:** https://www.neuromorphicinference.com/demos/forecast-studio/  
**Source:** https://github.com/nepryoon/nil-forecast-studio  

A forecasting system designed to escape the “notebook trap”:
- data ingestion + validation
- backtesting and model comparison
- artefacts (reports) and scheduled runs
- dashboard-style presentation for decision-makers

Key keywords: time series, backtesting, reproducibility, artefacts, scheduling.

---

## Principles

- **Evidence-based competence**: no “skill listing” without clickable proof (live + code).
- **Production-first framing**: projects are described as systems, not papers.
- **Stable URLs**: `/demos/*` and `/evidence#*` are intended to be referenced from the CV.

---

## How the portfolio is structured

- `/` → positioning (Signal)
- `/demos/` → systems catalogue
- `/demos/<project>/` → live documentation (case study, architecture, verification path)
- `/evidence/` → Proof Ledger (skill-to-proof index)
- `/about/` → identity / narrative
- `/research/` → archive (intentionally secondary)

---

## Repo layout (high level)

- `index.html` → home
- `style.css` → shared styling
- `build-info.js` → fetches `/api/build` and populates footer provenance
- `demos/` → demo pages (live docs)
- `evidence/`, `about/`, `research/` → section pages
- `functions/api/build.js` → Cloudflare Pages Function returning build metadata as JSON

---

## Build provenance (commit + branch)

Cloudflare Pages provides build context (for example, branch and commit) at deploy time.
Because this information is not directly available to client-side scripts, the site uses:

- Function endpoint: `/api/build` (served by `functions/api/build.js`)
- Client script: `build-info.js` fetches `/api/build` and updates the footer

This provides a lightweight traceability signal engineers can audit.

---

## Local development

### Option A — Static-only preview (fastest)
Run with any static server:

- Python:
  - `python -m http.server 8080`
- Node:
  - `npx serve .`

Open: `http://localhost:8080`

Note: this does not run Pages Functions.

### Option B — Local dev with Pages Functions (recommended)
Use Cloudflare Wrangler to run static assets **and** Functions locally:

- `npx wrangler pages dev .`

This serves the site locally and runs Functions under `/functions`.

---

## Deployment (Cloudflare Pages)

This repo is connected to Cloudflare Pages (git-driven deploy).

Typical setup:
- Build command: none / empty (static)
- Output directory: root (this repository)

On each push to the production branch, Cloudflare Pages builds and deploys the site.

---

## Content conventions

- Each system page aims to be self-contained:
  - What it solves (problem + business impact)
  - Architecture (components + flow)
  - Verification path (how to reproduce / validate)
  - Links: live demo/docs + source repository
- The Proof Ledger maps skills → evidence anchors and should stay stable over time.

---

## Licence

Unless stated otherwise, content in this repository is licensed under the repository’s licence.
Project repositories may have different licences — see each project repo for details.
