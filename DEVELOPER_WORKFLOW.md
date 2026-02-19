# Developer Workflow: Deploying HTML Changes

**Quick Reference Guide for Contributors**

---

## Prerequisites

- Git installed and configured
- Access to the repository
- Understanding: **Only the `main` branch deploys to production**

---

## Workflow 1: Direct Changes (Quick Updates)

Use this for small, low-risk changes (typos, copy updates, styling tweaks).

```bash
# 1. Switch to main branch
git checkout main

# 2. Pull latest changes
git pull origin main

# 3. Edit HTML files
vim demos/visual-inspector/index.html
# or use your preferred editor

# 4. Stage changes
git add demos/visual-inspector/index.html
# or use: git add .

# 5. Commit with descriptive message
git commit -m "Update visual inspector demo: fix typo in hero section"

# 6. Push to main
git push origin main

# 7. Wait 1-2 minutes for Cloudflare Pages deployment

# 8. Verify changes
# Visit: https://www.neuromorphicinference.com/demos/visual-inspector/
# Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
```

---

## Workflow 2: Feature Branch (Recommended for Larger Changes)

Use this for substantial changes, new features, or when you want review before production.

```bash
# 1. Ensure you're on main and up to date
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/improve-visual-inspector

# 3. Make changes
vim demos/visual-inspector/index.html
# Edit files as needed

# 4. Commit changes (can make multiple commits)
git add demos/visual-inspector/index.html
git commit -m "Improve visual inspector UI: add file size display"

# 5. Push feature branch to remote
git push origin feature/improve-visual-inspector

# 6. Create Pull Request on GitHub
# - Go to: https://github.com/nepryoon/neuromorphic-inference-lab-site
# - Click "Compare & pull request" button
# - Base branch: main
# - Compare branch: feature/improve-visual-inspector
# - Add description of changes
# - Click "Create pull request"

# 7. Optional: Check preview deployment
# If Cloudflare Pages preview is enabled, preview URL will be:
# https://feature-improve-visual-inspector.<project>.pages.dev

# 8. Request review (if working with team)

# 9. Merge Pull Request via GitHub UI
# Click "Merge pull request" → "Confirm merge"

# 10. Cloudflare Pages automatically deploys merged changes
# Deployment starts immediately after merge
# Takes 1-2 minutes to complete

# 11. Verify changes in production
# Visit: https://www.neuromorphicinference.com/demos/visual-inspector/

# 12. Clean up local branches
git checkout main
git pull origin main
git branch -d feature/improve-visual-inspector
```

---

## Verification: Confirm Your Changes Are Live

### Method 1: Check Build Provenance API

```bash
# Fetch deployed commit information
curl https://www.neuromorphicinference.com/api/build | jq .
```

**Expected output:**
```json
{
  "sha": "abc1234567890...",
  "shaShort": "abc1234",
  "branch": "main",
  "builtAt": "2026-02-19T08:30:00.000Z",
  "commitUrl": "https://github.com/nepryoon/neuromorphic-inference-lab-site/commit/abc1234..."
}
```

**Verify:**
- `shaShort` matches your latest commit on `main`
- `branch` is `main`
- `builtAt` timestamp is recent (within last few minutes)

### Method 2: Check Commit SHA on Page Footer

1. Visit any page (e.g., https://www.neuromorphicinference.com/)
2. Scroll to footer
3. Check "commit: abc1234" value
4. Compare with your latest commit: `git log --oneline -1`

### Method 3: Inspect HTML Source

```bash
# Fetch live HTML
curl https://www.neuromorphicinference.com/demos/visual-inspector/ | grep "your-unique-text"
```

If your change included unique text, search for it in the fetched HTML.

---

## Troubleshooting

### Changes Not Visible After 5 Minutes

**1. Clear browser cache**
```bash
# Hard refresh
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)

# Or use incognito/private mode
```

**2. Check deployed commit SHA**
```bash
curl https://www.neuromorphicinference.com/api/build | jq .shaShort
git log --oneline -1
```
If they don't match, deployment may have failed.

**3. Check Cloudflare Pages dashboard**
- Go to Cloudflare dashboard
- Navigate to Pages → neuromorphic-inference-lab-site (or your project name)
- Check "Deployments" tab for status
- Review logs for errors

**4. Verify branch**
```bash
# On GitHub, check which branch your commit is on
git branch -r --contains <commit-sha>
```
If not on `main`, your changes won't deploy to production.

**5. Purge Cloudflare cache (last resort)**
- Cloudflare dashboard → Caching → Configuration
- Click "Purge Everything"
- Wait 30 seconds
- Hard refresh browser

---

## Common Mistakes

### ❌ Pushing to Wrong Branch
```bash
# You're on feature branch
git push origin feature/my-changes
```
**Problem:** Feature branches don't deploy to production.  
**Solution:** Merge to `main` via Pull Request.

### ❌ Forgetting to Pull Before Editing
```bash
# You edit old version of main
git checkout main
vim index.html  # ❌ Without git pull first
```
**Problem:** Creates merge conflicts.  
**Solution:** Always `git pull origin main` before editing.

### ❌ Editing Files on Detached HEAD
```bash
git checkout abc1234  # ❌ Detached HEAD
vim index.html
git commit -m "Update"  # ❌ Commit not on any branch
```
**Problem:** Commits are lost when switching branches.  
**Solution:** Always work on a named branch.

---

## File Structure

### Files You Can Edit
- `index.html` - Homepage
- `demos/*/index.html` - Individual demo pages
- `evidence/index.html` - Proof Ledger
- `about/index.html` - About page
- `research/index.html` - Research archive
- `style.css` - Shared styles
- `nil.css` - Additional styles

### Files You Should NOT Edit Directly
- `functions/api/*.js` - Cloudflare Pages Functions (edit only if you understand serverless functions)

### Directories
```
/
├── index.html              # Homepage
├── style.css               # Shared CSS
├── build-info.js           # Footer build provenance script
├── demos/                  # Individual demo pages
│   ├── visual-inspector/
│   │   └── index.html
│   ├── rag-copilot/
│   │   └── index.html
│   └── ...
├── evidence/               # Proof Ledger
│   └── index.html
├── about/                  # Identity page
│   └── index.html
├── functions/              # Cloudflare Pages Functions (API routes)
│   └── api/
│       ├── build.js       # /api/build endpoint
│       └── ...
└── infra/                  # Infrastructure code (unrelated to site)
```

---

## No Build Step Required

**Important:** This is a static HTML site. There is:
- ❌ No `npm run build`
- ❌ No `npm install`
- ❌ No compilation step
- ❌ No transpilation

**What you see is what gets deployed.**

HTML files are source files. Edit them directly.

---

## Local Development (Optional)

To preview changes before deploying:

### Option 1: Simple Static Server
```bash
# Python
python -m http.server 8080

# Node
npx serve .

# Open: http://localhost:8080
```

**Note:** Cloudflare Pages Functions (e.g., `/api/build`) won't work in a static server.

### Option 2: Wrangler (With Functions)
```bash
# Run Cloudflare Pages locally with Functions support
npx wrangler pages dev .

# Open: http://localhost:8787
```

---

## Summary

**Key Points:**
1. ✅ **Only `main` branch deploys to production**
2. ✅ **No build step required** (static HTML)
3. ✅ **Use feature branches** for larger changes
4. ✅ **Always pull before editing** `main`
5. ✅ **Verify deployment** using `/api/build` endpoint
6. ✅ **Hard refresh** if changes not visible immediately

**Typical Timeline:**
- Commit pushed to `main`: ~0s
- Cloudflare Pages starts build: ~5-10s
- Deployment completes: ~1-2 minutes
- Cache propagation: ~1-5 minutes (may require hard refresh)

**Total time from push to visible changes: 2-7 minutes**

---

**Last Updated:** 2026-02-19  
**Questions?** See [DEPLOYMENT_ANALYSIS.md](DEPLOYMENT_ANALYSIS.md) for full technical details.
