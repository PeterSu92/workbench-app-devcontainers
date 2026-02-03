# GATK on Jupyter Custom App

This workspace demonstrates how to create a custom app: a JupyterLab image with GATK 4.3.0.0 installed.

We have tested these instructions on a Mac laptop running macOS 15.1.

## Setup

Ensure the following is installed on your laptop or local machine:

* [homebrew](https://brew.sh/)
* [Workbench CLI](https://support.workbench.verily.com/docs/guides/cli/cli_install_and_run/) and dependencies (described in link)
* docker
	* [colima](https://github.com/abiosoft/colima) for the container runtime
	* [docker](https://formulae.brew.sh/formula/docker) for the executable
* git

## Configure Workbench CLI

In a terminal on your local machine, log in to Workbench:

```
wb auth login
```

Create a workspace either in the Workbench Web UI or in a terminal via the CLI, like so:

```
wb workspace create –name=<your-workspace-name>
```

Then, point the `wb` CLI to that workspace as follows (note `your-workspace-id` does not necessarily equal `your-workspace-name`.  `your-workspace-id` is available in the web UI, or it should have been returned when the workspace was created using the CLI):

```
wb workspace set –id=<your-workspace-id>
```

## Create artifact registry

You'll need to create an [artifact registry](https://cloud.google.com/artifact-registry/docs/overview) repository for the Docker container image.  Here, we name the repository `gatk-demo-repo`.

```
wb gcloud artifacts repositories create gatk-demo-repo \
--repository-format=docker --location=us-central1
```

Confirm the repository was created successfully by `describe`-ing it and exporting its URI to an environment variable named `REGISTRY_URI`.

```
export REGISTRY_URI=`wb gcloud artifacts repositories describe gatk-demo-repo \
--location us-central1 --format json | jq -r '.registryUri'`; \
echo ${REGISTRY_URI}
```

## Build and push container image

First, create a tag for the container image:

```
export CONTAINER_TAG=${REGISTRY_URI}/test1:`date +'%Y%m%d'`; \
echo ${CONTAINER_TAG}
```

Then, create a directory for the `docker` build and go to that directory:

```
mkdir ~/docker; cd ~/docker
```

Then, create a new `Dockerfile` in `~/docker` with these contents:

```
FROM us-central1-docker.pkg.dev/verily-workbench-public/apps/workbench-jupyter:latest

# Install GATK 4.3.0.0
RUN wget -O /tmp/gatk-4.3.0.0.zip https://github.com/broadinstitute/gatk/releases/download/4.3.0.0/gatk-4.3.0.0.zip
RUN sudo unzip /tmp/gatk-4.3.0.0.zip -d /opt
RUN rm /tmp/gatk-4.3.0.0.zip
RUN sudo ln -s /opt/gatk-4.3.0.0/gatk /usr/local/bin/gatk

# Make sure python points to python3
RUN sudo ln -s /usr/bin/python3 /usr/bin/python
```

Start `colima` container runtime.  You'll see quite a bit of text - that's normal:

```
colima start
```

Build the container image from within the `~/docker` directory:

```
docker build -t ${CONTAINER_TAG} .
```

Authenticate docker using gcloud credentials:

```
gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://us-central1-docker.pkg.dev
```

Push the container image to the workspace's artifact registry.  This will take a while depending on your upload speed.

```
docker push ${CONTAINER_TAG}
```

Confirm the container image has been pushed to `REGISTRY_URI`:

```
wb gcloud artifacts docker tags list $REGISTRY_URI
```
## Build devcontainer

We strongly encourage following the devcontainer templates in the [verily-src/workbench-app-devcontainers](https://github.com/verily-src/workbench-app-devcontainers) GitHub repo.  Rather than walk you through the process of cloning a repo and creating a pull request, here's a link to the [pull request](https://github.com/verily-src/workbench-app-devcontainers/pull/155) we used to create the `jupyter-gatk` custom app.

In this PR, we:

* Copied `src/custom-workbench-jupyter-template` to `src/jupyter-gatk`
* Changed the various ids and descriptions
* Changed the default container image in in the template file to `$CONTAINER_TAG`
* Explicitly copied the default container tag and port information to the `docker-compose.yaml` because **templating does not appear to work at the moment**.  Instance creation fails in prod with an opaque error message.

Create a directory for github repositories and `cd` to that directory:

```
mkdir ~/repos; cd ~/repos
```

Clone the [verily-src/workbench-app-devcontainers](https://github.com/verily-src/workbench-app-devcontainers) GitHub repo:

```
git clone git@github.com:verily-src/workbench-app-devcontainers.git
```

## Launch custom app

In the Apps tab of your workspace, click the "New app instance" button, then click the "Custom" app chip at the bottom of the app menu.

Give your app a name - we're using `jupyter-gatk` in this instance - and a description.

Then, in the "Container Setup" section, fill in the fields as follows:

| field                  | value                                                       |
| ---------------------- | ----------------------------------------------------------- |
| Repository URL         | `git@github.com:verily-src/workbench-app-devcontainers.git` |
| Repository branch      | `jupyter-gatk`                                              |
| Repository folder path | `src/jupyter-gatk`                                          |

The rest of the app instance configuration flow behaves exactly like that of the other apps.  You won't need to enter all of this configuration information when creating subsequent app instances - a `jupyter-gatk` chip will be added to the app instance menu.

