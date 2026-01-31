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

## What recruiters can verify in 60 seconds

1. **End-to-end systems thinking**  
   Each project is framed as a system (data → features → training → artefacts → serving → evaluation → ops).

2. **Evidence-based competence (ATS-friendly)**  
   The Proof Ledger maps “skills” to stable anchors intended to be linked from a CV.

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

- https://github.com/nepryoon/mv-grid-fault-risk
- https://github.com/nepryoon/nil-rag-copilot
- https://github.com/nepryoon/nil-forecast-studio
- https://github.com/nepryoon/edgepulse

(See `/demos/` for the authoritative list.)

---

## Licence

Add a `LICENSE` file if you want explicit reuse terms for the site content.
(MIT is common for code; content may require a separate policy.)

---

## Contact

GitHub: https://github.com/nepryoon  
Website: https://www.neuromorphicinference.com
