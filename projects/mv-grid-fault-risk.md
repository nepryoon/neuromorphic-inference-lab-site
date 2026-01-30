---
title: "MV Grid Fault Risk Scoring Platform"
description: "End-to-end ML system for medium-voltage fault risk prediction with CI/CD for model deployment, inference serving, and monitoring-ready outputs."
---

# MV Grid Fault Risk Scoring Platform

Production-first, end-to-end Machine Learning system that predicts **medium-voltage grid fault risk** to prioritise preventive interventions and reduce unplanned outages.

**Core keywords:** Scalable ML Pipelines, Feature Engineering, Statistical Modelling, CI/CD for ML, Model Serving, Inference Scaling, Dockerization, MLflow Tracking, Automated Retraining (design pattern), Model Monitoring (drift-ready).

---

## Problem
Operational teams need a consistent way to identify high-risk assets/feeders early and allocate maintenance resources effectively.

## Solution
A full-stack ML workflow that delivers:
- Data pipeline (ingestion → validation → feature engineering → training table)
- Training with **MLflow** (metrics + artefacts)
- **FastAPI** model serving (online inference)
- Deployment-ready Docker image (cloud-native)

## Architecture (Data → Model → Production)
1. **Ingestion & data quality**: CSV → validated training table (Parquet)
2. **Feature engineering**: rolling fault windows (30/90/180 days), asset age, categorical metadata
3. **Model training**: baseline classifier + MLflow tracking (ROC-AUC / PR-AUC / F1)
4. **Serving**: FastAPI `/predict` endpoint returning probability + risk band
5. **MLOps hooks**: model versioning, reproducible builds, monitoring-ready outputs

## Live API
- Health: https://mv-grid-fault-risk-api.onrender.com/health  
- Docs (Swagger): https://mv-grid-fault-risk-api.onrender.com/docs  

## Demo
Use Swagger `/predict` or the interactive demo (coming next).

## Repository
https://github.com/nepryoon/mv-grid-fault-risk
