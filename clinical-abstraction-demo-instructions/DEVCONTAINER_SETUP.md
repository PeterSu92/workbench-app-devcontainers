# Devcontainer Setup Documentation

This document details how the Workbench custom app devcontainer configuration was created for the Clinical Abstraction Demo.

## Overview

The Clinical Abstraction Demo custom app combines:
1. **JupyterLab** (port 8888) - Base Workbench Jupyter environment
2. **Flask Backend** (port 5000) - OpenAI API integration for clinical extraction
3. **HTTP Server** (port 8000) - Serves the web UI (index.html)

All three services run simultaneously in the container, with Flask and HTTP server starting automatically via supervisor.

---

## File Structure

```
workbench-app-devcontainers/
├── clinical-abstraction-demo/               # Demo application directory
│   ├── clinical-abstraction-demo/           # Extracted v4 zip contents
│   │   ├── index.html                       # Main web UI
│   │   ├── extraction_backend_openai.py     # Flask backend
│   │   ├── requirements.txt                 # Python dependencies (flask, flask-cors, openai)
│   │   ├── sample_notes/                    # Example clinical notes
│   │   ├── synthetic_data/                  # Synthetic note generator
│   │   ├── start_demo.sh                    # Manual startup script (not used in container)
│   │   └── ...
│   ├── DEVCONTAINER_SETUP.md                # This file
│   └── custom_app_instructions.md           # Reference instructions (GATK example)
│
└── src/
    └── clinical-abstraction-demo/           # Devcontainer configuration
        ├── .devcontainer.json               # Devcontainer config
        ├── devcontainer-template.json       # Template metadata
        ├── docker-compose.yaml              # Docker Compose config
        ├── Dockerfile                       # Container build instructions
        └── README.md                        # Deployment guide
```

---

## What Was Done

### Step 1: Extracted v4 Demo Files

The `clinical-abstraction-demo v4.zip` file was extracted to:
`clinical-abstraction-demo/clinical-abstraction-demo/`

This contains:
- **index.html** - Single-file web application (299KB)
- **extraction_backend_openai.py** - Flask API server (29KB)
- **requirements.txt** - Dependencies: flask==3.0.0, flask-cors==4.0.0, openai==2.16.0, tiktoken==0.5.2, tenacity==8.2.3
- **sample_notes/** - 3 example heart failure clinical notes
- **synthetic_data/** - Generator and 100+ synthetic clinical notes
- Various documentation files (README.md, SETUP_GUIDE.md, etc.)

### Step 2: Created Devcontainer Config in `src/clinical-abstraction-demo/`

Following the pattern from `custom_app_instructions.md` (GATK example), I created devcontainer files based on the `custom-workbench-jupyter-template`.

#### Files Created:

1. **`.devcontainer.json`**
   - Copied from: `src/custom-workbench-jupyter-template/.devcontainer.json`
   - Modified:
     - Changed name to "Clinical Abstraction Demo"
     - Kept all Jupyter-specific settings
     - Added file extensions: .html, .txt, .json, .csv
     - Uses Workbench startup scripts (post-startup.sh, remount-on-restart.sh)

2. **`devcontainer-template.json`**
   - Copied from: `src/custom-workbench-jupyter-template/devcontainer-template.json`
   - Modified:
     - Changed id to "clinical-abstraction-demo"
     - Updated description to describe the app
     - Kept standard options (cloud, login)

3. **`docker-compose.yaml`**
   - Copied from: `src/custom-workbench-jupyter-template/docker-compose.yaml`
   - Modified:
     - Build context set to `../..` (repo root)
     - Dockerfile path: `src/clinical-abstraction-demo/Dockerfile`
     - Added ports: 5000 (Flask), 8000 (HTTP server)
     - Kept port 8888 (JupyterLab)
     - Includes comment about replacing build section with image reference after pushing

4. **`Dockerfile`**
   - Based on: `src/custom-workbench-jupyter-template/Dockerfile`
   - Base image: `us-central1-docker.pkg.dev/verily-workbench-public/apps/workbench-jupyter:latest`
   - **Key additions:**
     - Installed supervisor (for managing multiple processes)
     - Copied demo files from `clinical-abstraction-demo/clinical-abstraction-demo/` to `/home/jupyter/clinical-abstraction-demo/`
     - Installed Python dependencies from requirements.txt
     - Created supervisor config (see Startup Commands section below)

5. **`README.md`**
   - Created comprehensive deployment guide
   - Includes artifact registry setup instructions
   - Container build and push commands
   - Workbench deployment steps

---

## Startup Commands - How Services Auto-Start

### The Problem

The demo requires THREE services running simultaneously:
1. JupyterLab (already handled by base image)
2. Flask backend (extraction_backend_openai.py)
3. HTTP server (to serve index.html)

### The Solution: Supervisor

**Supervisor** is a process control system that manages multiple processes in a container. It was installed in the Dockerfile and configured to auto-start the Flask backend and HTTP server.

### Supervisor Configuration

Located in the Dockerfile, lines creating `/etc/supervisor/conf.d/clinical-demo.conf`:

```ini
[supervisord]
nodaemon=false

[program:flask-backend]
command=python extraction_backend_openai.py
directory=/home/jupyter/clinical-abstraction-demo
user=jupyter
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/flask-backend.err.log
stdout_logfile=/var/log/supervisor/flask-backend.out.log

[program:http-server]
command=python -m http.server 8000
directory=/home/jupyter/clinical-abstraction-demo
user=jupyter
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/http-server.err.log
stdout_logfile=/var/log/supervisor/http-server.out.log
```

### What Each Section Does

**`[supervisord]`**
- `nodaemon=false` - Runs in background (not blocking)

**`[program:flask-backend]`**
- `command=python extraction_backend_openai.py` - Starts Flask API server
- `directory=/home/jupyter/clinical-abstraction-demo` - Working directory
- `user=jupyter` - Runs as jupyter user (not root)
- `autostart=true` - Starts automatically when supervisor starts
- `autorestart=true` - Restarts if it crashes
- Logs to `/var/log/supervisor/flask-backend.out.log`

**`[program:http-server]`**
- `command=python -m http.server 8000` - Starts simple HTTP server on port 8000
- Serves index.html and all static files
- Same auto-start and restart behavior as Flask

### Container Startup Sequence

When the container starts, this is what happens:

1. **Workbench starts the container**
2. **CMD in Dockerfile executes:**
   ```bash
   sudo /usr/bin/supervisord && /home/jupyter/.local/bin/jupyter lab
   ```
3. **Supervisor starts in background:**
   - Reads `/etc/supervisor/conf.d/clinical-demo.conf`
   - Starts `flask-backend` process
   - Starts `http-server` process
4. **JupyterLab starts in foreground:**
   - Main container process
   - Accessible on port 8888

All three services are now running!

---

## Key Differences from Original Demo

### Original Local Setup (start_demo.sh)

The original demo used `start_demo.sh` which:
```bash
# Terminal 1
python extraction_backend_openai.py

# Terminal 2
python -m http.server 8000
```

Required user to manually start both servers and keep terminals open.

### Workbench Container Setup

In the Workbench container:
- **Supervisor automatically starts both servers**
- No manual intervention needed
- Services restart automatically if they crash
- All logging goes to `/var/log/supervisor/`
- User just accesses the URLs

---

## Port Mapping

| Service | Port | Access URL |
|---------|------|------------|
| JupyterLab | 8888 | `https://workbench.verily.com/app/WORKSPACE-ID/` |
| Web UI | 8000 | `https://workbench.verily.com/app/WORKSPACE-ID/proxy/8000/index.html` |
| Flask Backend | 5000 | `https://workbench.verily.com/app/WORKSPACE-ID/proxy/5000/` (internal only) |

**Note:** The Flask backend (port 5000) is called internally by the web UI on port 8000. Users don't access it directly.

---

## Build Context Explanation

### Why `context: ../..` in docker-compose.yaml?

The build context is set to the repository root (`../..` from `src/clinical-abstraction-demo/`) because:

1. **Dockerfile is at:** `src/clinical-abstraction-demo/Dockerfile`
2. **Demo files are at:** `clinical-abstraction-demo/clinical-abstraction-demo/`
3. **COPY command in Dockerfile:**
   ```dockerfile
   COPY clinical-abstraction-demo/clinical-abstraction-demo/ /home/jupyter/clinical-abstraction-demo/
   ```

The COPY path is relative to the build context (repo root), so it can access files outside the `src/` directory.

### Directory Layout During Build

```
. (build context = repo root)
├── clinical-abstraction-demo/
│   └── clinical-abstraction-demo/     <- COPY source
│       ├── index.html
│       ├── extraction_backend_openai.py
│       └── ...
└── src/
    └── clinical-abstraction-demo/
        └── Dockerfile                  <- Build file
```

---

## What Was Copied vs. What Was Modified

### Copied Directly (Minimal Changes)

1. **`.devcontainer.json`**
   - Source: `src/custom-workbench-jupyter-template/.devcontainer.json`
   - Changes: Name, file extensions only

2. **`devcontainer-template.json`**
   - Source: `src/custom-workbench-jupyter-template/devcontainer-template.json`
   - Changes: id, name, description

### Modified Significantly

1. **`Dockerfile`**
   - Source: `src/custom-workbench-jupyter-template/Dockerfile`
   - Added: supervisor installation, demo file copy, supervisor config, Python deps
   - Added: Custom CMD to start supervisor + JupyterLab

2. **`docker-compose.yaml`**
   - Source: `src/custom-workbench-jupyter-template/docker-compose.yaml`
   - Added: Ports 5000 and 8000
   - Changed: Build context to `../..`

### Created from Scratch

1. **`README.md`** - Deployment guide specific to this app
2. **`DEVCONTAINER_SETUP.md`** - This documentation file

---

## Dependencies Installed

### System Packages (via apt)
- `supervisor` - Process control system

### Python Packages (via pip)
All from `requirements.txt`:
- `flask==3.0.0` - Web framework for backend API
- `flask-cors==4.0.0` - CORS support for frontend-backend communication
- `openai==2.16.0` - OpenAI API client
- `tiktoken==0.5.2` - Token counting for OpenAI
- `tenacity==8.2.3` - Retry logic

---

## Reference: custom_app_instructions.md Pattern

The setup followed the GATK example pattern from `custom_app_instructions.md`:

### Key Steps from Instructions:
1. ✅ Start from Workbench Jupyter base image
2. ✅ Copy template from `custom-workbench-jupyter-template`
3. ✅ Create custom Dockerfile with additional software
4. ✅ Build and push to artifact registry
5. ✅ Update docker-compose.yaml with image reference
6. ✅ Deploy via Workbench UI

### Key Differences:
- GATK example: Added GATK 4.3.0.0
- This app: Added Flask backend + HTTP server with supervisor

---

## Deployment Process

### For First-Time Deployment:

1. **Create artifact registry:**
   ```bash
   wb gcloud artifacts repositories create clinical-demo-repo \
     --repository-format=docker --location=us-central1
   ```

2. **Build container:**
   ```bash
   cd ~/repos/workbench-app-devcontainers/src/clinical-abstraction-demo
   export CONTAINER_TAG=${REGISTRY_URI}/clinical-abstraction-demo:$(date +'%Y%m%d')
   docker build -t ${CONTAINER_TAG} .
   ```

3. **Push to registry:**
   ```bash
   docker push ${CONTAINER_TAG}
   ```

4. **Update docker-compose.yaml:**
   Replace the `build:` section with:
   ```yaml
   image: "${CONTAINER_TAG}"  # Your actual image tag
   ```

5. **Deploy in Workbench UI:**
   - Repository URL: `git@github.com:verily-src/workbench-app-devcontainers.git`
   - Branch: `main` (or your branch)
   - Folder path: `src/clinical-abstraction-demo`

---

## Troubleshooting

### Check if services are running:
```bash
# SSH into the container, then:
sudo supervisorctl status
```

Should show:
```
flask-backend                    RUNNING   pid 123, uptime 0:05:00
http-server                      RUNNING   pid 124, uptime 0:05:00
```

### View logs:
```bash
# Flask backend logs
tail -f /var/log/supervisor/flask-backend.out.log

# HTTP server logs
tail -f /var/log/supervisor/http-server.out.log

# All supervisor logs
tail -f /var/log/supervisor/*.log
```

### Restart services:
```bash
sudo supervisorctl restart flask-backend
sudo supervisorctl restart http-server
```

---

## Files NOT Used in Container

These files exist in the demo but are NOT used in the containerized version:

- **`start_demo.sh`** - Manual startup script (replaced by supervisor)
- **`flask.log`** - Local log file (container uses supervisor logs)
- **`.venv/`** - Local virtual environment (container uses global pip)

These are for local development only.

---

## Issues Encountered & Solutions

### Issue 1: Files Not in Git Repository

**Error:**
```
failed to calculate checksum of ref: "/clinical-abstraction-demo/": not found
```

**Problem:** Workbench builds containers from the git repository, not local filesystem. The COPY command in Dockerfile referenced files that weren't committed to git.

**Solution:**
- All app files must be in the `src/clinical-abstraction-demo/` directory
- Structure: `src/clinical-abstraction-demo/app/` contains all application code
- Dockerfile COPY path: `COPY src/clinical-abstraction-demo/app/ /home/jupyter/clinical-abstraction-demo/`
- Commit and push all files before deploying

### Issue 2: Pip Dependency Conflict (blinker)

**Error:**
```
Cannot uninstall blinker 1.4
It is a distutils installed project and thus we cannot accurately determine which files belong to it
```

**Problem:** Base Jupyter image has `blinker 1.4` installed via distutils. Flask wants to upgrade it but can't uninstall the old version.

**Solution:**
```dockerfile
# Install blinker with --ignore-installed, then install other deps normally
RUN pip install --no-cache-dir --ignore-installed blinker && \
    pip install --no-cache-dir -r /home/jupyter/clinical-abstraction-demo/requirements.txt
```

**DON'T** use `--ignore-installed` for everything - it reinstalls all dependencies and makes builds very slow.

### Issue 3: Jupyter Startup Failure

**Error:**
```
[C] `root_dir` and `file_to_run` are incompatible. They don't share the same subtrees.
```

**Problem:** Overriding CMD breaks Workbench's Jupyter startup configuration.

**BAD (doesn't work):**
```dockerfile
CMD sudo /usr/bin/supervisord && /home/jupyter/.local/bin/jupyter lab
```

**BETTER (but still problematic):**
```dockerfile
ENTRYPOINT ["/usr/local/bin/start-script.sh"]
# Script runs supervisor then exec "$@"
```

**Problem with ENTRYPOINT approach:** Base image may use its own ENTRYPOINT, causing conflicts.

**BEST SOLUTION:** Override CMD to start supervisor then Jupyter directly:
```dockerfile
RUN echo '#!/bin/bash' | sudo tee /usr/local/bin/start-all.sh && \
    echo 'sudo /usr/bin/supervisord &' | sudo tee -a /usr/local/bin/start-all.sh && \
    echo 'sleep 2' | sudo tee -a /usr/local/bin/start-all.sh && \
    echo 'exec /home/jupyter/.local/bin/jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root' | sudo tee -a /usr/local/bin/start-all.sh && \
    sudo chmod +x /usr/local/bin/start-all.sh

CMD ["/usr/local/bin/start-all.sh"]
```

### Issue 4: Container Restart Loop

**Symptom:** Container keeps restarting, logs show supervisor starting but then container exits.

**Causes:**
1. Main process exits (supervisor with `nodaemon=false` runs in background and exits)
2. JupyterLab crashes due to configuration issues
3. Port 8888 not binding, causing Workbench health checks to fail

**Debug Commands (on VM):**
```bash
# Check container status
docker ps -a

# View logs
docker logs application-server --tail 200

# Check what's actually running in container
docker exec application-server ps aux

# Check supervisor status
docker exec application-server sudo supervisorctl status

# View supervisor logs
docker exec application-server sudo tail -f /var/log/supervisor/*.log
```

### Issue 5: Build vs. Image Deployment Speed

**Build Approach (slow):**
```yaml
build:
  context: ../..
  dockerfile: src/clinical-abstraction-demo/Dockerfile
```
- Builds on VM every deployment
- 30-40 minutes per instance
- Good for development/testing only

**GAR Image Approach (fast):**
```yaml
image: "us-central1-docker.pkg.dev/PROJECT/REPO/NAME:TAG"
```
- Build once locally or in CI
- Push to Google Artifact Registry
- 2-5 minute deployments
- **Required for production**

**How to Switch to GAR:**
```bash
cd src/clinical-abstraction-demo

# Build using docker-compose (handles additional_contexts)
docker compose build

# Tag the image
export CONTAINER_TAG="us-central1-docker.pkg.dev/PROJECT/REPO/NAME:$(date +'%Y%m%d')"
docker tag clinical-abstraction-demo-app:latest ${CONTAINER_TAG}

# Push to GAR
docker push ${CONTAINER_TAG}

# Update docker-compose.yaml to use image: instead of build:
# Then commit and push
```

---

## Best Practices for Workbench Custom Apps

### 1. File Organization

```
src/YOUR-APP-NAME/
├── .devcontainer.json          # Devcontainer config
├── devcontainer-template.json  # Template metadata
├── docker-compose.yaml         # Docker Compose config
├── Dockerfile                  # Container build
├── README.md                   # Deployment guide
└── app/                        # All application files
    ├── your_app_files_here
    └── requirements.txt
```

### 2. Dockerfile Structure

```dockerfile
FROM us-central1-docker.pkg.dev/verily-workbench-public/apps/workbench-jupyter:latest

# Install jupyter extensions (required)
RUN --mount=type=bind,from=jupyter-extension-builder,source=/dist,target=/tmp/extensions \
    /tmp/extensions/setup.sh

# Install system dependencies
RUN sudo apt-get update && sudo apt-get install -y \
    your-packages-here \
    && sudo rm -rf /var/lib/apt/lists/*

# Copy application files
COPY src/YOUR-APP-NAME/app/ /home/jupyter/your-app/

# Install Python dependencies
RUN pip install --no-cache-dir -r /home/jupyter/your-app/requirements.txt

# Expose additional ports (8888 is default for Jupyter)
EXPOSE 5000 8000 8888

# IMPORTANT: Only override CMD, not ENTRYPOINT
CMD ["/path/to/your/startup-script.sh"]
```

### 3. Supervisor Configuration

If you need background services, supervisor is the right approach:

```dockerfile
# Install supervisor
RUN sudo apt-get update && sudo apt-get install -y supervisor

# Create supervisor config
RUN echo '[supervisord]' | sudo tee /etc/supervisor/conf.d/myapp.conf && \
    echo 'nodaemon=false' | sudo tee -a /etc/supervisor/conf.d/myapp.conf && \
    echo '' | sudo tee -a /etc/supervisor/conf.d/myapp.conf && \
    echo '[program:my-service]' | sudo tee -a /etc/supervisor/conf.d/myapp.conf && \
    echo 'command=/path/to/service' | sudo tee -a /etc/supervisor/conf.d/myapp.conf && \
    echo 'directory=/home/jupyter/app' | sudo tee -a /etc/supervisor/conf.d/myapp.conf && \
    echo 'user=jupyter' | sudo tee -a /etc/supervisor/conf.d/myapp.conf && \
    echo 'autostart=true' | sudo tee -a /etc/supervisor/conf.d/myapp.conf && \
    echo 'autorestart=true' | sudo tee -a /etc/supervisor/conf.d/myapp.conf
```

### 4. Testing Before Deployment

**Local Testing:**
```bash
# Build locally
cd src/your-app
docker compose build

# Run locally
docker compose up

# Test that all services start
docker ps
docker logs application-server

# Check ports
curl http://localhost:8888  # Jupyter
curl http://localhost:5000  # Your service
```

**Deploy to GAR:**
Only after local testing succeeds, push to GAR for Workbench deployment.

### 5. Deployment Checklist

- [ ] All files in `src/YOUR-APP/` committed to git
- [ ] Dockerfile COPY paths relative to repo root
- [ ] Python dependencies handle distutils conflicts
- [ ] Ports exposed in Dockerfile and docker-compose.yaml
- [ ] CMD/ENTRYPOINT doesn't break base image startup
- [ ] Built and pushed to GAR (for production)
- [ ] docker-compose.yaml uses `image:` not `build:` (for production)
- [ ] README.md has deployment instructions

---

## Common Mistakes to Avoid

### ❌ DON'T: Override ENTRYPOINT carelessly
```dockerfile
# This can break base image startup logic
ENTRYPOINT ["/my/script.sh"]
```

### ✅ DO: Override CMD or use ENTRYPOINT wrapper carefully
```dockerfile
CMD ["/my/startup-script.sh"]
# OR wrap ENTRYPOINT and preserve base with exec "$@"
```

### ❌ DON'T: Use --ignore-installed for all packages
```dockerfile
RUN pip install --no-cache-dir --ignore-installed -r requirements.txt
# This reinstalls EVERYTHING, very slow
```

### ✅ DO: Only ignore specific problematic packages
```dockerfile
RUN pip install --no-cache-dir --ignore-installed blinker && \
    pip install --no-cache-dir -r requirements.txt
```

### ❌ DON'T: Reference files outside src/ in COPY
```dockerfile
COPY ../other-dir/files /app/
# Won't work - files must be in src/YOUR-APP/ or subdirectories
```

### ✅ DO: Keep all files in src/YOUR-APP/
```dockerfile
COPY src/YOUR-APP/app/ /home/jupyter/app/
```

### ❌ DON'T: Deploy with build: in production
```yaml
build:
  context: ../..
  dockerfile: src/YOUR-APP/Dockerfile
# 30-40 min deployments
```

### ✅ DO: Use GAR images in production
```yaml
image: "us-central1-docker.pkg.dev/PROJECT/REPO/NAME:TAG"
# 2-5 min deployments
```

---

## Debugging Tips

### Check Container Status
```bash
# On the VM
docker ps -a
docker logs application-server --tail 100
```

### Inspect Running Container
```bash
docker exec application-server ps aux
docker exec application-server ls -la /home/jupyter/
docker exec application-server cat /var/log/supervisor/flask-backend.err.log
```

### Verify Ports
```bash
docker exec application-server netstat -tlnp
# Should show 8888 (Jupyter), 5000, 8000, etc.
```

### Check Supervisor
```bash
docker exec application-server sudo supervisorctl status
docker exec application-server sudo supervisorctl restart all
```

### Common Error Patterns

**"Port is empty"** → Jupyter not starting on 8888
**"root_dir and file_to_run incompatible"** → CMD/ENTRYPOINT override broke Jupyter config
**Container restart loop** → Main process exiting, check logs
**"failed to calculate checksum"** → Files not in git repo

---

## Summary

This devcontainer configuration:
1. Extends the Workbench Jupyter base image
2. Installs the clinical abstraction demo into `/home/jupyter/clinical-abstraction-demo/`
3. Uses supervisor to auto-start Flask backend and HTTP server
4. Exposes three ports: 8888 (Jupyter), 5000 (Flask), 8000 (Web UI)
5. Follows the official Workbench custom app pattern
6. **Must be built and pushed to GAR for production use**

The key innovation is using **supervisor** to run multiple background services (Flask + HTTP server) alongside the main JupyterLab process, making the demo fully self-contained and automatically starting.

### Quick Start for Production

1. **Build locally:**
   ```bash
   cd src/clinical-abstraction-demo
   docker compose build
   export TAG="us-central1-docker.pkg.dev/PROJECT/REPO/NAME:$(date +'%Y%m%d')"
   docker tag clinical-abstraction-demo-app:latest ${TAG}
   docker push ${TAG}
   ```

2. **Update docker-compose.yaml:**
   Replace `build:` section with `image: "${TAG}"`

3. **Commit and push to git**

4. **Deploy in Workbench UI:**
   - Repository URL: `git@github.com:verily-src/workbench-app-devcontainers.git`
   - Branch: `your-branch`
   - Folder path: `src/clinical-abstraction-demo`

5. **Access:**
   - JupyterLab: `https://workbench.verily.com/app/WORKSPACE-ID/`
   - Web UI: `https://workbench.verily.com/app/WORKSPACE-ID/proxy/8000/index.html`
