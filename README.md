# Neuromorphic Inference Lab — Site

> **Live site:** [https://www.neuromorphicinference.com/](https://www.neuromorphicinference.com/)
> **Demos hub:** [https://www.neuromorphicinference.com/demos](https://www.neuromorphicinference.com/demos)
> **Evidence index:** [https://www.neuromorphicinference.com/evidence](https://www.neuromorphicinference.com/evidence)
> **Build metadata (commit/branch):** [https://www.neuromorphicinference.com/api/build](https://www.neuromorphicinference.com/api/build)

## What this repo is

This repository contains the **source of the Neuromorphic Inference Lab website** (static pages + lightweight Cloudflare Pages Functions).
The site is designed as an **applied AI portfolio** with *evidence-based competence*: every claim should be verifiable through:

* **Live docs** hosted on the domain (this site)
* **Exact source code** hosted in dedicated GitHub repos (e.g., EdgePulse / nil-* repos)

## Principles

* **Evidence-based competence:** no “skill listing” without a clickable proof (live + code).
* **Production-first framing:** demos are described as *systems* (ingest → store → score → operate), not papers.
* **Stable URLs:** `/demos/*` and `/evidence#*` are intended to be referenced from the CV.

## How the portfolio is structured

* `/demos` → catalog of projects (each has Live/Docs + Code)
* `/demos/<project>` → “live documentation” (case study / roadmap / verification path)
* `/evidence` → skill-to-proof index (anchors meant to be linked from CV)
* `/about` → positioning
* `/research` → archive (kept for continuity, intentionally secondary)

## Repo layout (high level)

* `index.html` → home
* `style.css` → shared styling (optional if used)
* `build-info.js` → client script that populates footer build provenance by calling `/api/build`
* `demos/` → demo pages (live docs)
* `evidence/`, `about/`, `research/` → section pages
* `functions/api/build.js` → Cloudflare Pages Function returning build metadata as JSON

## Build provenance (commit + branch)

Cloudflare Pages exposes build information as environment variables (e.g., commit SHA, branch).
Since these variables are not directly available in the browser, the site uses:

* **Function endpoint:** `/api/build` (served by `functions/api/build.js`)
* **Client script:** `build-info.js` fetches `/api/build` and updates the footer

This provides a lightweight “build provenance” signal recruiters/engineers can audit.

## Local development

This site is static HTML. You can run it locally with any static server. Examples:

* Python:

  * `python -m http.server 8080`
* Node:

  * `npx serve .`

Then open: `http://localhost:8080`

> Note: Cloudflare Pages Functions won’t run in a plain static server. To test Functions locally, use Cloudflare tooling (Wrangler) or test on the deployed environment.

## Deployment (Cloudflare Pages)

This repo is connected to **Cloudflare Pages** (git-driven deploy). Typical setup:

* **Build command:** none / empty (static)
* **Output directory:** `/` (repo root)
* **Functions directory:** `functions/` (auto-detected by Pages)

After pushing to the main branch, Cloudflare Pages deploys automatically.

## Adding a new demo (standard)

When adding a new project, do all of the following:

1. Create a **live docs page** under `/demos/<slug>/index.html`
2. Create a **code repo** on GitHub (or link an existing one)
3. Update:

   * `/demos/index.html` (add card with Live/Docs + Code)
   * `/evidence/index.html` (add/update proofs for relevant skills)
4. Ensure **bidirectional links**:

   * Demo page links to GitHub repo
   * GitHub README links back to the live docs page + `/evidence`

## Related repos (code)

This site links to dedicated repositories for each demo/system, e.g.:

* `edgepulse` (case study + system implementation)
* `nil-rag-copilot`, `nil-forecast-studio`, `nil-tabular-risk`, `nil-visual-inspector`
* `nil-infra-template`

(See `/demos` for the authoritative list.)

## License

Choose a license appropriate for how you want the site content reused (MIT is common for code; content may require a separate policy).
If you intend open reuse, add a `LICENSE` file and reference it here.

## Contact

GitHub: [https://github.com/nepryoon](https://github.com/nepryoon)
