"""
Simulation code for:
  Can LLM Agents Care About the World?
  Exocentric Homeostatic Deliberation (EHD)

Author : Luca Lillo, University of Liverpool, 2026
Purpose: Reproduce Figures for Propositions 4, 5 and Section 7.
Usage  : python ehd_simulations.py
Output : figures/fig_convergence.{pdf,png}
         figures/fig_ranking_divergence.{pdf,png}
         figures/fig_welfare_trajectory.{pdf,png}
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

# Global settings
np.random.seed(42)
os.makedirs("figures", exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

NAVY   = "#1B3A6B"
PLUM   = "#7B2D8B"
GREEN  = "#2E7D32"
GOLD   = "#DAA520"
RED    = "#B71C1C"
GRAY   = "#757575"


# ------------------------------------------------------------------ #
# FIGURE 1 — Proposition 4: Robbins-Monro convergence
# ------------------------------------------------------------------ #
def generate_fig1():
    mu_star = 0.35
    mu_0    = 0.60
    sigma_obs = 0.05
    K = 200
    N = 50

    trajectories = np.zeros((N, K + 1))
    for n in range(N):
        mu = mu_0
        trajectories[n, 0] = mu
        for k in range(1, K + 1):
            kappa = 0.5 / (k ** 0.75)
            obs   = np.random.normal(mu_star, sigma_obs)
            mu    = mu + kappa * (obs - mu)
            trajectories[n, k] = mu

    ks       = np.arange(K + 1)
    mean_tr  = trajectories.mean(axis=0)
    p10      = np.percentile(trajectories, 10, axis=0)
    p90      = np.percentile(trajectories, 90, axis=0)

    fig, ax = plt.subplots(figsize=(6.5, 4))

    for n in range(N):
        ax.plot(ks, trajectories[n], color=NAVY, alpha=0.12, lw=0.7)

    ax.fill_between(ks, p10, p90, color=NAVY, alpha=0.18,
                    label="10th–90th percentile")
    ax.plot(ks, mean_tr, color=NAVY, lw=2.0,
            label=r"Mean trajectory")
    ax.axhline(mu_star, color=GREEN, lw=1.6, ls="--",
               label=r"True interventional mean $\mu^*(a)=0.35$")
    ax.axhline(mu_0, color=RED, lw=1.2, ls="--", alpha=0.6,
               label=r"Initial estimate $\mu_{\theta_0}(a)=0.60$")

    ax.set_xlabel(r"Visit count $k$")
    ax.set_ylabel(r"Mean estimate $\mu_{\theta_k}(a)$")
    ax.set_title("Convergence of recalibration rule (Proposition 4)")
    ax.legend(fontsize=9, frameon=False, loc="upper right")

    fig.tight_layout()
    fig.savefig("figures/fig_convergence.pdf", dpi=300)
    fig.savefig("figures/fig_convergence.png", dpi=300)
    plt.close(fig)
    print("fig_convergence saved.")


# ------------------------------------------------------------------ #
# FIGURE 2 — Proposition 5(ii): ranking divergence EHD vs EFE
# ------------------------------------------------------------------ #
def generate_fig2():
    mu_star    = 0.50
    sigma_star = 0.03
    sigma2_a   = 0.02
    mu_a = mu_b = 0.45

    sigma2_b_vals  = np.linspace(0.02, 0.15, 100)
    delta_sigma2   = sigma2_b_vals - sigma2_a

    def kl_gaussian(mu_q, sigma2_q, mu_p, sigma2_p):
        return 0.5 * (
            (mu_q - mu_p)**2 / sigma2_p
            + sigma2_q / sigma2_p
            - 1
            - np.log(sigma2_q / sigma2_p)
        )

    kl_a = kl_gaussian(mu_a, sigma2_a, mu_star, sigma_star**2)
    kl_b = kl_gaussian(mu_b, sigma2_b_vals, mu_star, sigma_star**2)

    delta_kl  = kl_a - kl_b   # positive = EFE prefers a
    delta_ehd = np.zeros_like(delta_sigma2)  # always 0

    fig, ax = plt.subplots(figsize=(6.5, 4))

    ax.axhline(0, color=GRAY, lw=0.8, ls=":")
    ax.fill_between(delta_sigma2, delta_ehd, delta_kl,
                    color=PLUM, alpha=0.08)
    ax.plot(delta_sigma2, delta_ehd, color=NAVY, lw=2.2,
            label=r"EHD pragmatic term $\Delta V_{\mathrm{prag}}=0$")
    ax.plot(delta_sigma2, delta_kl, color=PLUM, lw=2.2,
            label=r"EFE KL term $\Delta\mathrm{KL}$")

    ax.annotate("EHD indifferent",
                xy=(0.06, 0.002), fontsize=9, color=NAVY)
    ax.annotate("EFE penalises higher variance",
                xy=(0.05, delta_kl[50] + 0.002),
                fontsize=9, color=PLUM)

    ax.set_xlabel(
        r"Variance gap $\sigma^2_{\theta_t}(b)-\sigma^2_{\theta_t}(a)$")
    ax.set_ylabel(r"Score difference $(a)-(b)$")
    ax.set_title(
        "Ranking divergence: EHD vs single-step EFE\n"
        "(Proposition 5, mechanism ii)")
    ax.legend(fontsize=9, frameon=False, loc="lower left")

    fig.tight_layout()
    fig.savefig("figures/fig_ranking_divergence.pdf", dpi=300)
    fig.savefig("figures/fig_ranking_divergence.png", dpi=300)
    plt.close(fig)
    print("fig_ranking_divergence saved.")


# ------------------------------------------------------------------ #
# FIGURE 3 — Section 7: 24-month welfare trajectory
# ------------------------------------------------------------------ #
def generate_fig3():
    t = np.arange(0, 25, dtype=float)

    # External trend and welfare
    noise  = np.random.normal(0, 0.01, len(t))
    g_raw  = 0.08 * np.sin(2 * np.pi * t / 24) + 0.04 + noise
    g_smooth = np.zeros_like(g_raw)
    g_smooth[0] = g_raw[0]
    for i in range(1, len(t)):
        g_smooth[i] = 0.3 * g_raw[i] + 0.7 * g_smooth[i - 1]

    W_ext      = 1 / (1 + np.exp(3 * g_smooth))
    theta_ext  = 0.45

    # Hope term
    B = np.zeros_like(t)
    for i, ti in enumerate(t):
        if ti < 3:
            B[i] = W_ext[i]
        elif ti == 3:
            B[i] = 0.62
        elif ti < 16:
            B[i] = 0.62 * np.exp(-0.08 * (ti - 3))
        else:
            B[i] = W_ext[i] + 0.03

    # Endocentric
    x2 = 0.80 * np.exp(-0.02 * t)
    x2[6:] += 0.12 * np.exp(-0.02 * (t[6:] - 6))
    x2 = np.clip(x2, 0, 1)
    x3 = 0.72 * np.exp(-0.01 * t)

    p1 = 0.42
    x1 = 0.70 * W_ext + 0.20 * B + 0.10 * p1
    V  = 0.55 * x1 + 0.25 * x2 + 0.20 * x3

    fig, axes = plt.subplots(
        3, 1, figsize=(6.5, 7),
        sharex=True,
        gridspec_kw={"height_ratios": [2.5, 1, 1]}
    )
    fig.suptitle(
        "EHD welfare trajectory — 24-month simulation (Section 7)",
        fontsize=11)

    # --- Subplot 1 ---
    ax = axes[0]
    ax.plot(t, W_ext, color=PLUM, lw=2,
            label=r"$W_{\mathrm{ext}}(t)$")
    ax.plot(t, B, color=GOLD, lw=1.8, ls="--",
            label=r"$B_t(a^*)$")
    ax.axhline(theta_ext, color=GRAY, lw=1, ls=":",
               label=r"$\theta_{\mathrm{ext}}=0.45$")
    ax.fill_between(t, 0, 1,
                    where=(W_ext < theta_ext),
                    color=RED, alpha=0.10,
                    label="Trigger active")
    ax.annotate("", xy=(3, 0.25), xytext=(3, 0.18),
                arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.6))
    ax.text(3.2, 0.17, "Action selected", fontsize=8, color=GREEN)
    ax.set_ylabel("Welfare signal")
    ax.set_ylim(0.1, 0.85)
    ax.legend(fontsize=8, frameon=False, loc="upper right",
              ncol=2)

    # --- Subplot 2 ---
    ax = axes[1]
    ax.plot(t, x2, color=NAVY, lw=1.8,
            label=r"Budget $x_{t,2}$")
    ax.plot(t, x3, color=GREEN, lw=1.8, ls="--",
            label=r"Knowledge $x_{t,3}$")
    ax.plot(6, x2[6], marker="^", color=NAVY, ms=7,
            label="Replenishment")
    ax.set_ylabel("Endocentric")
    ax.legend(fontsize=8, frameon=False, loc="upper right")

    # --- Subplot 3 ---
    ax = axes[2]
    ax.plot(t, V, color="black", lw=2,
            label=r"$V(x_t)$")
    ax.axhline(0.50, color=GRAY, lw=1, ls=":",
               label=r"$\theta=0.50$")
    ax.set_ylabel(r"$V(x_t)$")
    ax.set_xlabel(r"Time $t$ (months)")
    ax.legend(fontsize=8, frameon=False, loc="upper right")

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.savefig("figures/fig_welfare_trajectory.pdf", dpi=300)
    fig.savefig("figures/fig_welfare_trajectory.png", dpi=300)
    plt.close(fig)
    print("fig_welfare_trajectory saved.")


# ------------------------------------------------------------------ #
def main():
    print("Generating EHD simulation figures...")
    generate_fig1()
    generate_fig2()
    generate_fig3()
    print("Done. Files saved in ./figures/")

if __name__ == "__main__":
    main()
