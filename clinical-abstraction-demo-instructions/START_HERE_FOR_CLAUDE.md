# Guide for Next Claude: Setting Up Clinical Abstraction Demo as Workbench Custom App

## Context

You're helping convert a local Flask+HTML clinical abstraction demo into a **Verily Workbench custom app**. The user may start from the `clinical-abstraction-demo v4.zip` file or the existing files in this repo.

## Essential Files to Read (In Order)

### 1. Understanding Workbench Custom Apps

**Read First:**
- `clinical-abstraction-demo-instructions/custom_app_instructions.md`
  - This is the OFFICIAL Workbench guide using GATK as an example
  - Shows the pattern for creating custom apps
  - Key insight: Use `custom-workbench-jupyter-template` as base

**Read Second:**
- `README.md` (repo root)
  - Explains the workbench-app-devcontainers repo structure
  - Shows how custom app templates are organized

### 2. Understanding the Clinical Abstraction Demo

**Read:**
- `clinical-abstraction-demo-instructions/README.md`
  - What the demo does (AI-powered clinical data extraction)
  - Architecture: Flask backend + HTML frontend
  - Requires TWO servers: Flask (port 5000) + HTTP server (port 8000)

- `clinical-abstraction-demo-instructions/ANALYSIS.md` (Optional)
  - Technical deep-dive into the app
  - Known security issues (debug mode, CORS, etc.)
  - Good for understanding what you're deploying

### 3. Lessons Learned & Troubleshooting

**MUST READ:**
- `clinical-abstraction-demo-instructions/DEVCONTAINER_SETUP.md`
  - **THIS IS THE MOST IMPORTANT FILE**
  - Documents all issues hit during initial implementation
  - Solutions to: pip conflicts, Jupyter startup, restart loops
  - Best practices for Workbench custom apps
  - Debugging tips
  - Read the "Issues Encountered & Solutions" section carefully

## Current State of the Repo

### What's Already Done

```
src/clinical-abstraction-demo/
├── .devcontainer.json          ✅ Created
├── devcontainer-template.json  ✅ Created
├── docker-compose.yaml         ✅ Created (uses GAR image)
├── Dockerfile                  ⚠️ HAS BUGS (restart loop issue)
├── README.md                   ✅ Created
└── app/                        ✅ All demo files copied here
    ├── extraction_backend_openai.py
    ├── index.html
    ├── requirements.txt
    ├── sample_notes/
    └── ...
```

### What's Broken

**The Dockerfile CMD/ENTRYPOINT approach causes container restart loops.**

See `DEVCONTAINER_SETUP.md` → "Issue 3: Jupyter Startup Failure" for details and solutions.

### GAR Image Status

- ✅ Built: `us-central1-docker.pkg.dev/wb-twinkly-turnip-8149/clin-abs-repo/test1:20260203`
- ⚠️ Image has the broken Dockerfile, so it doesn't work
- Need to fix Dockerfile, rebuild, push new tag

## Quick Reference: Key Insights

### 1. File Structure

**All files MUST be in `src/YOUR-APP-NAME/`**
- Workbench builds from git, not local filesystem
- COPY paths in Dockerfile are relative to repo root
- Structure: `src/clinical-abstraction-demo/app/` contains application code

### 2. Supervisor is Required

The demo needs **three services running simultaneously**:
- JupyterLab (port 8888) - provided by base image
- Flask backend (port 5000) - needs to auto-start
- HTTP server (port 8000) - needs to auto-start

Use **supervisor** to manage Flask + HTTP server.

### 3. Don't Break Jupyter Startup

The `workbench-jupyter` base image has its own startup logic. **DO NOT override ENTRYPOINT or CMD carelessly.**

**Working approaches:**
- Override CMD with a script that starts supervisor then Jupyter
- Use supervisor as a system service
- See DEVCONTAINER_SETUP.md "Issue 3" for details

### 4. Deployment Speed Matters

**Build on VM (slow):**
```yaml
build:
  context: ../..
  dockerfile: src/clinical-abstraction-demo/Dockerfile
```
→ 30-40 minutes per deployment

**Pre-built GAR image (fast):**
```yaml
image: "us-central1-docker.pkg.dev/PROJECT/REPO/NAME:TAG"
```
→ 2-5 minutes per deployment

**Always use GAR for production.**

### 5. Common Pitfalls

❌ Files not committed to git → build fails
❌ `pip install --ignore-installed` for everything → very slow
❌ Overriding ENTRYPOINT → breaks Jupyter
❌ `nodaemon=false` for supervisor without proper exec → container exits
❌ Using `build:` in production → slow deployments

See DEVCONTAINER_SETUP.md → "Common Mistakes to Avoid" for full list.

## If Starting from v4.zip

The `clinical-abstraction-demo v4.zip` contains:
- `extraction_backend_openai.py` - Flask backend
- `index.html` - Web UI
- `requirements.txt` - Python dependencies
- `sample_notes/` - Example data
- `start_demo.sh` - Local startup script (not used in container)

**Steps:**
1. Extract to `src/clinical-abstraction-demo/app/`
2. Follow the custom app pattern from `custom_app_instructions.md`
3. Apply lessons from `DEVCONTAINER_SETUP.md`

## Recommended Approach

### Step 1: Understand the Pattern
Read `custom_app_instructions.md` to understand how GATK was converted to a custom app.

### Step 2: Review Current Implementation
Read `DEVCONTAINER_SETUP.md` to understand:
- What was tried
- What failed
- What the solutions are

### Step 3: Fix the Dockerfile
The main issue is in the Dockerfile's CMD section. See "Issue 3" solutions in DEVCONTAINER_SETUP.md.

### Step 4: Build Locally & Test
```bash
cd src/clinical-abstraction-demo
docker compose build
docker compose up
# Test that all services start
```

### Step 5: Push to GAR
```bash
export TAG="us-central1-docker.pkg.dev/PROJECT/REPO/NAME:$(date +'%Y%m%d')"
docker tag clinical-abstraction-demo-app:latest ${TAG}
docker push ${TAG}
```

### Step 6: Update docker-compose.yaml
Replace `build:` with `image: "${TAG}"`

### Step 7: Deploy in Workbench
- Repository: `git@github.com:verily-src/workbench-app-devcontainers.git`
- Branch: `yp_ac_clin`
- Folder: `src/clinical-abstraction-demo`

## Key Questions to Ask the User

1. **"Are you starting from scratch or from the existing `src/clinical-abstraction-demo/`?"**
   - If scratch: Extract v4.zip to `src/clinical-abstraction-demo/app/`
   - If existing: Fix the Dockerfile CMD issue

2. **"Do you have a GAR repository set up?"**
   - If no: Help create one with `wb gcloud artifacts repositories create`
   - If yes: Get the registry URI for tagging images

3. **"Do you want to test locally first or deploy directly?"**
   - Local testing with `docker compose build && docker compose up` is recommended
   - Faster iteration than deploying to Workbench each time

## Expected End Result

When working, the user should be able to:
1. Deploy app instance in Workbench (2-5 min with GAR image)
2. Access JupyterLab at `https://workbench.verily.com/app/WORKSPACE-ID/`
3. Access clinical abstraction UI at `https://workbench.verily.com/app/WORKSPACE-ID/proxy/8000/index.html`
4. All three services (Jupyter, Flask, HTTP) running automatically

## Files You DON'T Need to Read

- `SETUP_GUIDE.md` - Local setup, not relevant for containerization
- `CHECKLIST.md` - Pre-distribution checklist for the demo itself
- `DISTRIBUTION_GUIDE.md` - How to share the demo locally
- Files in `clinical-abstraction-demo-instructions/clinical-abstraction-demo/` - These are the source files, already copied to `src/clinical-abstraction-demo/app/`

## Good Luck!

The main challenge is getting the supervisor + Jupyter startup sequence right without breaking the base image's configuration. Everything else follows the standard custom app pattern.

Key success criteria:
- ✅ Container starts without restart loop
- ✅ Supervisor manages Flask + HTTP server
- ✅ JupyterLab accessible on port 8888
- ✅ Web UI accessible on port 8000
