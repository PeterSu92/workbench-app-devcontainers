FROM us-central1-docker.pkg.dev/verily-workbench-public/apps/workbench-jupyter:latest

# Install jupyter extensions
RUN --mount=type=bind,from=jupyter-extension-builder,source=/dist,target=/tmp/extensions \
    /tmp/extensions/setup.sh

# Install additional system dependencies
RUN sudo apt-get update && sudo apt-get install -y \
    supervisor \
    && sudo rm -rf /var/lib/apt/lists/*

# Create app directory
RUN mkdir -p /home/jupyter/clinical-abstraction-demo

# Copy the clinical abstraction demo application
# Build context is repo root (../..), so path is relative to that
COPY src/clinical-abstraction-demo/app/ /home/jupyter/clinical-abstraction-demo/

# Install Python dependencies
# Use --ignore-installed to handle distutils-installed packages like blinker
RUN pip install --no-cache-dir --ignore-installed -r /home/jupyter/clinical-abstraction-demo/requirements.txt

# Create supervisor configuration to run both Flask and HTTP servers
RUN echo '[supervisord]' | sudo tee /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'nodaemon=false' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo '' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo '[program:flask-backend]' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'command=python extraction_backend_openai.py' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'directory=/home/jupyter/clinical-abstraction-demo' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'user=jupyter' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'autostart=true' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'autorestart=true' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'stderr_logfile=/var/log/supervisor/flask-backend.err.log' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'stdout_logfile=/var/log/supervisor/flask-backend.out.log' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo '' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo '[program:http-server]' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'command=python -m http.server 8000' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'directory=/home/jupyter/clinical-abstraction-demo' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'user=jupyter' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'autostart=true' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'autorestart=true' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'stderr_logfile=/var/log/supervisor/http-server.err.log' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'stdout_logfile=/var/log/supervisor/http-server.out.log' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf

# Expose ports (Flask backend on 5000, HTTP server on 8000, JupyterLab on 8888)
EXPOSE 5000 8000 8888

# Start supervisor in background and then start jupyter
CMD sudo /usr/bin/supervisord && /home/jupyter/.local/bin/jupyter lab
