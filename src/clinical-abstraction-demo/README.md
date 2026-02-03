# Clinical Abstraction Demo

Custom Workbench application for demonstrating AI-powered clinical variable extraction from medical notes using OpenAI GPT-4.

## Overview

This custom app combines:
- **JupyterLab** (port 8888) - for data analysis and notebook development
- **Flask Backend** (port 5000) - OpenAI API integration for clinical extraction
- **Web UI** (port 8000) - Clinical abstraction workstation interface

Both the Flask backend and HTTP server start automatically when the container launches.

## Building and Deploying

### Prerequisites

- [Workbench CLI](https://support.workbench.verily.com/docs/guides/cli/cli_install_and_run/) installed
- Docker with colima (Mac) or Docker Desktop
- git

### Step 1: Create Artifact Registry

```bash
wb gcloud artifacts repositories create clinical-demo-repo \
  --repository-format=docker --location=us-central1

export REGISTRY_URI=`wb gcloud artifacts repositories describe clinical-demo-repo \
  --location us-central1 --format json | jq -r '.registryUri'`
echo ${REGISTRY_URI}
```

### Step 2: Build Container Image

```bash
cd ~/repos/workbench-app-devcontainers/src/clinical-abstraction-demo

export CONTAINER_TAG=${REGISTRY_URI}/clinical-abstraction-demo:`date +'%Y%m%d'`
echo ${CONTAINER_TAG}

# Build the image
docker build -t ${CONTAINER_TAG} .
```

### Step 3: Push to Artifact Registry

```bash
# Authenticate Docker
gcloud auth print-access-token | docker login -u oauth2accesstoken \
  --password-stdin https://us-central1-docker.pkg.dev

# Push the image
docker push ${CONTAINER_TAG}

# Confirm upload
wb gcloud artifacts docker tags list $REGISTRY_URI
```

### Step 4: Update docker-compose.yaml

Replace the `build` section in `docker-compose.yaml` with your pushed image:

```yaml
services:
  app:
    container_name: "application-server"
    image: "${CONTAINER_TAG}"  # Use your actual tag
    user: "jupyter"
    ...
```

### Step 5: Deploy to Workbench

1. In Workbench UI, go to Apps tab
2. Click "New app instance" → "Custom"
3. Fill in:
   - **Repository URL**: `git@github.com:verily-src/workbench-app-devcontainers.git`
   - **Repository branch**: `main` (or your branch name)
   - **Repository folder path**: `src/clinical-abstraction-demo`

## Using the App

Once deployed:

1. **JupyterLab**: Access at the default app URL
   - `https://workbench.verily.com/app/YOUR-WORKSPACE-ID/`

2. **Clinical Abstraction UI**: Navigate to port 8000
   - `https://workbench.verily.com/app/YOUR-WORKSPACE-ID/proxy/8000/index.html`

3. **Set OpenAI API Key**: In the web UI settings panel

4. **Start Extracting**: Upload clinical notes and extract variables with AI

## Features

- **Protocol Management**: Create and manage extraction rules
- **AI Extraction**: GPT-4 powered variable extraction from clinical text
- **Evidence Highlighting**: See exactly where AI found each value
- **Sample Data**: Includes example heart failure clinical notes
- **Statistics Dashboard**: Track extraction accuracy and patterns

## Supported Clinical Variables

- NYHA Functional Class
- Ejection Fraction (LVEF)
- Blood Pressure
- Heart Rate
- Heart Failure Diagnosis Type
- BNP/NT-proBNP levels

## Development

The demo application files are located at:
`/home/jupyter/clinical-abstraction-demo/`

All Flask backend logs: `/var/log/supervisor/flask-backend.out.log`
HTTP server logs: `/var/log/supervisor/http-server.out.log`

## Troubleshooting

- **Services not running**: Check supervisor logs in `/var/log/supervisor/`
- **Flask errors**: Verify OpenAI API key is set
- **Port conflicts**: Ensure ports 5000, 8000, 8888 are available

## Options

| Option | Description | Type | Default |
|--------|-------------|------|---------|
| cloud  | VM cloud environment | string | gcp |
| login  | Whether to log in to workbench CLI | string | false |
