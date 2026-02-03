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

## Summary

This devcontainer configuration:
1. Extends the Workbench Jupyter base image
2. Installs the clinical abstraction demo into `/home/jupyter/clinical-abstraction-demo/`
3. Uses supervisor to auto-start Flask backend and HTTP server
4. Exposes three ports: 8888 (Jupyter), 5000 (Flask), 8000 (Web UI)
5. Follows the official Workbench custom app pattern
6. Requires building and pushing to artifact registry before deployment

The key innovation is using **supervisor** to run multiple background services (Flask + HTTP server) alongside the main JupyterLab process, making the demo fully self-contained and automatically starting.
