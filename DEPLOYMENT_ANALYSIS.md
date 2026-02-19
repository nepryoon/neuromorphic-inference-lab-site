# Deployment Analysis: HTML File Changes Not Reflecting Live

**Date:** 2026-02-19  
**Repository:** nepryoon/neuromorphic-inference-lab-site  
**Issue:** Local changes to HTML files (`demos/visual-inspector/index.html` and root `index.html`) are committed and pushed, but do not reflect on the live deployment at https://www.neuromorphicinference.com/

---

## Executive Summary

**Root Cause:** The repository is deployed to **Cloudflare Pages**, which likely deploys from the **`main` branch** by default. Changes made to the **`copilot/analyze-html-file-changes` branch** (or any other feature branch) are **not automatically deployed** to production.

**Key Finding:** This is not a build, caching, or configuration issue—it is a **branch deployment workflow** issue.

---

## 1. Build Process Analysis

### Findings

**✅ No Build Tools or Static Site Generators Detected**

The repository uses **static HTML** with no build step:
- ❌ No `package.json` (no npm build scripts)
- ❌ No `astro.config.*` (not using Astro)
- ❌ No `webpack.config.*` (no Webpack)
- ❌ No `Makefile` at root (only in `infra/terraform/`)
- ❌ No build scripts (`build.sh`, `deploy.sh`)

**Source Files Are Production Files**

- HTML files in the root directory (`index.html`) and subdirectories (`demos/visual-inspector/index.html`) are **hand-written source files**.
- They are **not auto-generated outputs**.
- Developers should **edit these files directly**.

**Documentation Confirmation**

From `README.md` (lines 134-143):
```markdown
## Deployment (Cloudflare Pages)

This repo is connected to Cloudflare Pages (git-driven deploy).

Typical setup:
- Build command: none / empty (static)
- Output directory: `/` (repo root)
- Functions directory: `functions/` (auto-detected)

After pushing to `main`, Cloudflare Pages deploys automatically.
```

**Verdict:** HTML files are source files. No build step required.

---

## 2. Deployment Configuration Analysis

### Cloudflare Pages Setup

**Deployment Platform:** Cloudflare Pages (confirmed in README.md line 9 and lines 134-143)

**Configuration Location:** 
- ❌ No `wrangler.toml` found
- ❌ No `.github/workflows/` directory (no CI/CD workflows)
- ❌ No `_headers` or `_redirects` files
- ✅ Configuration exists **in Cloudflare dashboard** (not in repository)

**Deployment Settings** (from README.md):
- **Build command:** none / empty (static)
- **Output directory:** `/` (repo root)
- **Functions directory:** `functions/` (auto-detected)
- **Branch:** `main` (stated: "After pushing to `main`, Cloudflare Pages deploys automatically")

**Related Configuration:**
- `render.yaml` exists but only configures a **Docker service** (`nil-rag-copilot`) for a separate backend API—not relevant to the static HTML site deployment.

### Current Branch Analysis

```bash
$ git branch -a
* copilot/analyze-html-file-changes
  remotes/origin/copilot/analyze-html-file-changes
```

**Critical Issue:** The repository is currently on a **feature branch** (`copilot/analyze-html-file-changes`), not `main`. 

**Cloudflare Pages Deployment Behaviour:**
- Production deployments trigger automatically on pushes to the **production branch** (typically `main`)
- Preview deployments may be created for other branches, but they have **different URLs** (e.g., `<branch-name>.<project>.pages.dev`)
- Changes pushed to feature branches **do not update the production URL** (`www.neuromorphicinference.com`)

---

## 3. Caching Mechanisms Analysis

### Browser-Side Caching

**Service Workers:** ❌ None detected (`find . -name "sw.js"` returned no results)

**Manifest Files:** ❌ None detected (`find . -name "manifest.json"` returned no results)

**Cache-Control Headers:**
- Not explicitly defined in repository (no `_headers` file)
- Cloudflare Pages applies default caching headers
- However, Cloudflare typically caches static assets (HTML, CSS, JS) aggressively

**Build Provenance API:**
- `/api/build` endpoint (served by `functions/api/build.js`) uses `"cache-control": "no-store"` to prevent caching of build metadata
- This does **not** affect HTML file caching

### Cloudflare-Side Caching

**Cloudflare Edge Caching:**
- Cloudflare Pages caches static files at the edge by default
- HTML files may be cached for several minutes to hours
- After deployment, cached content may persist until cache TTL expires or manual purge is performed

**Potential Caching Issue:**
Even if the correct branch is deployed, **cached HTML files** at the edge may serve stale content temporarily.

**Mitigation:**
- Cloudflare Pages typically purges cache automatically on new deployments
- Manual cache purge is available in Cloudflare dashboard: Cache → Purge Everything

---

## 4. Developer Workflow Analysis

### Current Incorrect Workflow

Based on the current repository state, the likely workflow being followed is:

1. ✅ Edit HTML files locally (e.g., `demos/visual-inspector/index.html`)
2. ✅ Commit changes to a feature branch (e.g., `copilot/analyze-html-file-changes`)
3. ✅ Push changes to GitHub
4. ❌ **Problem:** Changes are pushed to a feature branch, not `main`
5. ❌ **Result:** Cloudflare Pages does not deploy these changes to production

### Correct Workflow

To successfully deploy HTML changes to production:

#### For Direct Changes (Small Updates)

```bash
# 1. Switch to main branch
git checkout main

# 2. Pull latest changes
git pull origin main

# 3. Edit HTML files
# (e.g., vim demos/visual-inspector/index.html)

# 4. Stage changes
git add demos/visual-inspector/index.html

# 5. Commit changes
git commit -m "Update visual inspector demo"

# 6. Push to main
git push origin main

# 7. Wait for Cloudflare Pages deployment (1-2 minutes)
# Monitor deployment in Cloudflare Pages dashboard

# 8. Verify changes at https://www.neuromorphicinference.com/demos/visual-inspector/

# 9. If changes not visible, check for caching:
#    - Hard refresh browser: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
#    - Or purge Cloudflare cache in dashboard
```

#### For Feature Branch Workflow (Best Practice)

```bash
# 1. Create and switch to feature branch
git checkout -b feature/update-visual-inspector

# 2. Edit HTML files
# (e.g., vim demos/visual-inspector/index.html)

# 3. Commit changes
git add demos/visual-inspector/index.html
git commit -m "Update visual inspector demo"

# 4. Push feature branch
git push origin feature/update-visual-inspector

# 5. Create Pull Request on GitHub
#    - Base branch: main
#    - Compare branch: feature/update-visual-inspector

# 6. Review preview deployment (if Cloudflare Pages preview enabled)
#    - URL format: feature-update-visual-inspector.<project>.pages.dev

# 7. Merge Pull Request to main via GitHub UI

# 8. Cloudflare Pages automatically deploys merged changes to production

# 9. Verify changes at production URL

# 10. Clean up
git checkout main
git pull origin main
git branch -d feature/update-visual-inspector
```

---

## 5. Specific Issue: Why Current Changes Are Not Live

### Branch Analysis

```bash
$ git branch -a
* copilot/analyze-html-file-changes
  remotes/origin/copilot/analyze-html-file-changes
```

**Issue:** The repository is on the `copilot/analyze-html-file-changes` branch, **not `main`**.

**Missing Branch:**
- The `main` branch is **not visible** in the local repository
- The repository may have been cloned with `--single-branch` or with a grafted history
- `git log` shows: `7103299 (grafted)` indicating a shallow clone or grafted commit

### Git History Anomaly

```bash
$ git log --all --oneline -30
0b1d36e (HEAD -> copilot/analyze-html-file-changes, origin/copilot/analyze-html-file-changes) Initial plan
7103299 (grafted) Merge pull request #23 from nepryoon/copilot/retrieve-original-file
```

**Observation:**
- Only 2 commits visible in history
- Commit `7103299` is marked as `(grafted)`, indicating this is a **shallow clone**
- The `main` branch is **not present locally**

**Implication:**
- Any changes made on this branch will **not** be deployed to production
- To deploy changes, they must be merged into `main` (or the production branch configured in Cloudflare)

---

## 6. Cloudflare Pages Configuration (Inferred)

Since configuration is not in the repository, the following settings are **inferred** from README documentation:

| Setting | Inferred Value | Source |
|---------|----------------|--------|
| **Production Branch** | `main` | README.md line 143: "After pushing to `main`, Cloudflare Pages deploys automatically" |
| **Build Command** | (empty) | README.md line 139: "Build command: none / empty (static)" |
| **Output Directory** | `/` | README.md line 140: "Output directory: `/` (repo root)" |
| **Functions Directory** | `functions/` | README.md line 141: "Functions directory: `functions/` (auto-detected)" |
| **Root Directory** | (empty / repo root) | Implied by output directory `/` |

**Preview Deployments:**
- Cloudflare Pages may generate preview deployments for non-production branches
- Preview URL format: `<branch-name>.<project-name>.pages.dev`
- Preview deployments **do not** affect the production domain (`www.neuromorphicinference.com`)

---

## 7. Recommendations

### Immediate Actions

1. **Verify Production Branch**
   - Check Cloudflare Pages dashboard: Settings → Builds & Deployments → Production Branch
   - Confirm it is set to `main` (or identify the actual production branch)

2. **Merge Feature Branch to Main**
   - Create a Pull Request from `copilot/analyze-html-file-changes` to `main`
   - Review and merge the PR
   - Cloudflare Pages will automatically deploy the merged changes

3. **Check Deployment Status**
   - Monitor the deployment in Cloudflare Pages dashboard
   - Wait for deployment to complete (typically 1-2 minutes)

4. **Verify Changes**
   - Visit production URL: https://www.neuromorphicinference.com/demos/visual-inspector/
   - If changes not visible, perform hard refresh (Ctrl+Shift+R)
   - If still not visible, purge Cloudflare cache in dashboard

### Long-Term Process Improvements

1. **Document Branch Strategy**
   - Add to README.md: clarify that only `main` branch deploys to production
   - Document preview deployment URL format for feature branches

2. **Add Deployment Status Badge**
   - Consider adding Cloudflare Pages deployment status badge to README
   - Provides visual feedback on deployment status

3. **Enable Preview Deployments**
   - Ensure Cloudflare Pages is configured to create preview deployments for PRs
   - Allows testing changes before merging to production

4. **Add Pre-Commit Checks**
   - Consider adding HTML validation via pre-commit hooks
   - Prevents pushing broken HTML to any branch

5. **Document Cache Purging**
   - Add to README: instructions for manual cache purge if needed
   - Location: Cloudflare dashboard → Caching → Configuration → Purge Cache

---

## 8. Technical Details: Cloudflare Pages Functions

The repository includes **Cloudflare Pages Functions** in the `functions/` directory:

```
functions/
└── api/
    ├── build.js         # Returns build metadata (commit SHA, branch, timestamp)
    ├── health.js        # Health check endpoint
    ├── version.js       # Version information
    └── mvgrid/          # Additional API routes
```

**Function Deployment:**
- Functions are deployed **alongside HTML files** on every Cloudflare Pages deployment
- They run on Cloudflare's edge network
- They are **not affected by browser caching** (they execute server-side on each request)

**Build Metadata Endpoint:**
- `functions/api/build.js` returns build information from Cloudflare environment variables:
  - `CF_PAGES_COMMIT_SHA` - Git commit SHA of deployed code
  - `CF_PAGES_BRANCH` - Git branch deployed
  - `CF_PAGES_URL` - Deployment URL
- The `build-info.js` script (loaded in HTML pages) fetches this endpoint to display build provenance in the page footer
- This can be used to **verify which commit is currently deployed**

**Verification Method:**
```bash
# Check currently deployed commit
curl https://www.neuromorphicinference.com/api/build | jq .

# Expected output format:
# {
#   "sha": "abc123...",
#   "shaShort": "abc123",
#   "branch": "main",
#   "builtAt": "2026-02-19T08:00:00.000Z",
#   "commitUrl": "https://github.com/nepryoon/neuromorphic-inference-lab-site/commit/abc123..."
# }
```

If the `sha` in the response does not match your latest commit on `main`, the deployment has not yet completed or failed.

---

## 9. Troubleshooting Checklist

If changes are still not reflecting after following the correct workflow:

- [ ] **Verify branch:** Confirm changes are merged to `main` (or production branch)
- [ ] **Check deployment logs:** Review Cloudflare Pages dashboard for deployment errors
- [ ] **Verify commit SHA:** Check `/api/build` endpoint to confirm deployed commit
- [ ] **Clear browser cache:** Hard refresh (Ctrl+Shift+R) or test in incognito mode
- [ ] **Purge edge cache:** Use Cloudflare dashboard to purge cache manually
- [ ] **Check HTML syntax:** Validate HTML files for syntax errors that might break deployment
- [ ] **Review git history:** Ensure commits are actually in `main` branch history
- [ ] **Check Cloudflare status:** Verify Cloudflare Pages service is operational (status.cloudflare.com)

---

## 10. Conclusion

**Primary Issue:** Changes are pushed to a feature branch (`copilot/analyze-html-file-changes`) instead of the production branch (`main`).

**Solution:** Merge feature branch to `main` via Pull Request. Cloudflare Pages will automatically deploy the changes.

**Build Process:** Not applicable—this is a static HTML site with no build step.

**Caching:** May cause brief delay (1-5 minutes) even after deployment. Hard refresh or cache purge resolves this.

**Developer Workflow:** Always merge to `main` for production deployment. Use feature branches for development, then merge via Pull Request.

---

## Appendix: Files Analysed

### Configuration Files
- `README.md` - Deployment documentation (Cloudflare Pages setup)
- `render.yaml` - Render.com config (only for `nil-rag-copilot` Docker service, not HTML site)
- `.gitignore` - Standard ignore rules (no build directories ignored)

### HTML Files (Sample)
- `index.html` - Root landing page
- `demos/visual-inspector/index.html` - Demo page (mentioned in issue)

### JavaScript Files
- `build-info.js` - Fetches `/api/build` to display footer provenance
- `functions/api/build.js` - Cloudflare Pages Function returning build metadata

### Directories
- `functions/` - Cloudflare Pages Functions
- `demos/` - Individual demo pages (static HTML)
- `infra/terraform/` - AWS infrastructure code (unrelated to site deployment)

### Not Found (Confirming No Build Process)
- ❌ `package.json`
- ❌ `astro.config.*`
- ❌ `webpack.config.*`
- ❌ Build scripts (`build.sh`, `deploy.sh`)
- ❌ `wrangler.toml`
- ❌ `.github/workflows/`
- ❌ Service workers (`sw.js`)
- ❌ Manifest files (`manifest.json`)
- ❌ Caching headers files (`_headers`)

---

**Generated:** 2026-02-19T08:15:31Z  
**Agent:** GitHub Copilot Workspace Analysis
