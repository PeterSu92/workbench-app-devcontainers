# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository stores Verily Workbench devcontainer app templates. Each template defines a containerized application (Jupyter, RStudio, VS Code, etc.) that runs in the Workbench platform. Users fork this repo to create custom applications.

## Repository Structure

- `src/` - App templates (each subdirectory is a complete app with `.devcontainer.json`, `docker-compose.yaml`, startup scripts)
- `features/src/` - Reusable devcontainer features (workbench-tools, jupyter, java, postgres-client)
- `startupscript/` - VM provisioning scripts for Workbench environments (GCP, AWS, Vertex AI, Dataproc)
- `scripts/` - Development utilities including `create-custom-app.sh`

## Common Commands

### Create a new app template
```bash
./scripts/create-custom-app.sh <app-name> <docker-image> <port> [username] [home-dir]
# Example: ./scripts/create-custom-app.sh example quay.io/jupyter/base-notebook 8888 jovyan /home/jovyan
```

### Run BATS tests
```bash
cd scripts/test
bats .                                    # All tests
bats create-custom-app.bats               # Specific file
bats create-custom-app.bats --filter "shows usage"  # Specific test
```

### Local development
```bash
docker network create app-network         # Required external network
cd src/<app-name>
devcontainer up --workspace-folder .      # Start the app
# Access at localhost:<port>
```

### Lint shell scripts
```bash
shellcheck src/**/*.sh
# Configure locally: echo "disable=SC1090,SC1091" > ~/.shellcheckrc
```

## Creating Custom Apps

**Workbench apps do NOT have to be Jupyter-based.** Look at existing examples in `src/`:
- `src/vscode/` - VS Code Server (just a pre-built image + port 8443)
- `src/r-analysis/` - RStudio (pre-built image + port 8787)
- `src/example/` - Jupyter-based example

For a simple web app (Flask, FastAPI, etc.), follow the `vscode` or `r-analysis` pattern:
1. Simple Dockerfile with your app
2. Expose your port in docker-compose.yaml
3. No need for Jupyter, supervisor, or complex startup scripts

The `workbench-jupyter` base image is only needed if you actually want JupyterLab. Using it for non-Jupyter apps adds unnecessary complexity (Jupyter config conflicts, supervisor for multiple processes, etc.).

## Current Work: Clinical Abstraction Demo (branch: yp_ac_clin)

Simplified Flask app deployment. Key files:
- `src/clinical-abstraction-demo/Dockerfile` - Simple python:3.11-slim, single Flask process
- `src/clinical-abstraction-demo/app/extraction_backend_openai.py` - Serves UI + API on port 8000

**Status:** Fixed CORS error. Ready to test deploy.

**To test:** Deploy in Workbench UI with:
- Repository: `git@github.com:verily-src/workbench-app-devcontainers.git`
- Branch: `yp_ac_clin`
- Folder: `src/clinical-abstraction-demo`

**If it fails:** Check logs on VM: `docker logs application-server`

## Playground Template Pattern (public repo)

Location: `~/repos/public-workbench-app-devcontainers/workbench-app-devcontainers/src/playground/`

This is a **clean, working pattern** for Workbench custom apps:

**Architecture:**
- `caddy:2.11-alpine` as main `application-server` on port 8080 (reverse proxy)
- Separate service containers on internal networks
- Postgres for state (optional)
- No devcontainer features (avoids apt-key and other issues)

**Key .devcontainer.json pattern (minimal):**
```json
{
  "name": "App Name",
  "dockerComposeFile": "docker-compose.yaml",
  "service": "app",
  "shutdownAction": "none",
  "workspaceFolder": "/workspace",
  "remoteUser": "root"
}
```

**To port clinical-abstraction-demo to this pattern:**
1. Use Caddy or direct Flask as `application-server` on port 8080
2. Remove all devcontainer features from .devcontainer.json
3. Remove postCreateCommand/postStartCommand (they use startup scripts that may fail)
4. Self-contained Dockerfile with all dependencies

## Known Issues

### Google Cloud CLI feature fails on newer Debian
The `ghcr.io/dhoeric/features/google-cloud-cli` feature uses deprecated `apt-key` which doesn't exist in Debian 13+ (e.g., `python:3.11-slim` based on bookworm/trixie). Error: `apt-key: command not found`.

**Workarounds:**
1. Remove the feature from `.devcontainer.json` if gcloud isn't needed
2. Install gcloud directly in Dockerfile using the modern approach (no apt-key)
3. Use a base image that already has gcloud (like workbench-jupyter)

### Devcontainer features may conflict with slim images
Features like `workbench-tools` expect certain system packages. When using minimal base images like `python:3.11-slim`, some features may fail. Either install dependencies in your Dockerfile first, or skip features that aren't essential.

## Workbench-Specific Requirements

All apps must follow these conventions:
1. Container name must be `application-server`
2. Container must connect to external Docker network `app-network`
3. Port exposed on `0.0.0.0` (localhost)
4. For gcsfuse support: `--cap-add SYS_ADMIN --device /dev/fuse --security-opt apparmor:unconfined`
5. Cloud storage mounts at `${homedir}/workspaces`, GitHub repos at `${homedir}/repos`

## Shell Script Conventions

- Mark variables `readonly` to prevent overrides
- For command output assignments, separate `readonly` declaration (to avoid masking errors per SC2155):
  ```bash
  FOO="$(command)"
  readonly FOO
  ```
- Mark functions `readonly -f function_name`
- Use `set -o errexit -o nounset -o pipefail` for error handling

## CI/CD

- Pull requests trigger: ShellCheck linting, smoke tests for changed app templates
- `test-scripts.yaml` runs BATS tests when `scripts/` changes
- `release.yaml` (manual, master only) publishes templates to devcontainers registry

## Testing Changes to Startup Scripts

For complex changes, point a VM to your branch's script:

**Vertex AI:**
```bash
wb resource create gcp-notebook --id=test --post-startup-script=https://raw.githubusercontent.com/verily-src/workbench-app-devcontainers/<branch>/startupscript/vertex-ai-user-managed-notebook/post-startup.sh
```

**Dataproc:**
```bash
wb resource create dataproc-cluster --name=test --metadata=startup-script-url=https://raw.githubusercontent.com/verily-src/workbench-app-devcontainers/<branch>/startupscript/dataproc/startup.sh
```

Debug logs: `/home/<user>/.workbench/post-startup-output.txt`
