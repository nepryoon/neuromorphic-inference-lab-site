# EHD Simulations — Can LLM Agents Care About the World?

<img src="https://img.shields.io/badge/python-3.10%2B-blue">

Reproducible simulation code for the paper:

> **Can LLM Agents Care About the World? World-Directed Welfare
> and Exocentric Homeostatic Deliberation**
> Luca Lillo — University of Liverpool, 2026
> *arXiv preprint — under submission*

Paper evidence memo: https://www.neuromorphicinference.com/evidence/

## Figures produced

| File | Description |
|------|-------------|
| `figures/fig_convergence` | Proposition 4 — Robbins–Monro convergence of the mean recalibration rule. 50 independent trajectories converging to μ*(a)=0.35 from initial estimate 0.60. |
| `figures/fig_ranking_divergence` | Proposition 5 (ii) — Action-ranking divergence between EHD and single-step EFE. Equal means, differing variances produce identical EHD pragmatic scores but different EFE KL scores. |
| `figures/fig_welfare_trajectory` | Section 7 — 24-month EHD welfare simulation on AMR-style monitoring task. Exocentric trigger fires at W_ext < θ_ext = 0.45 despite satisfactory endocentric state. |

## Usage
```bash
pip install -r requirements.txt
python ehd_simulations.py
```

Figures are saved as PDF and PNG in `./figures/`.

## Citation
```bibtex
@misc{lillo2026ehd,
  author = {Luca Lillo},
  title  = {Can {LLM} Agents Care About the World?
             World-Directed Welfare and Exocentric
             Homeostatic Deliberation},
  year   = {2026},
  note   = {arXiv preprint, under submission}
}
```

## Licence
MIT
