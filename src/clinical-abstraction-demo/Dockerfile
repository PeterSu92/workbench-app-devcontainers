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
# Use --ignore-installed for blinker only (distutils-installed in base image)
RUN pip install --no-cache-dir --ignore-installed blinker && \
    pip install --no-cache-dir -r /home/jupyter/clinical-abstraction-demo/requirements.txt

# Create supervisor configuration for all services
# nodaemon=true keeps supervisor in foreground as PID 1
# Jupyter is managed by supervisor to preserve proper startup
RUN sudo mkdir -p /var/log/supervisor && \
    echo '[supervisord]' | sudo tee /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'nodaemon=true' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'logfile=/var/log/supervisor/supervisord.log' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'pidfile=/var/run/supervisord.pid' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo '' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo '[program:jupyter]' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'command=/home/jupyter/.local/bin/jupyter lab --ip=0.0.0.0 --port=8888 --no-browser' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'directory=/home/jupyter' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'user=jupyter' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'autostart=true' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'autorestart=true' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'priority=10' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'stdout_logfile=/var/log/supervisor/jupyter.out.log' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'stderr_logfile=/var/log/supervisor/jupyter.err.log' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo '' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo '[program:flask-backend]' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'command=python extraction_backend_openai.py' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'directory=/home/jupyter/clinical-abstraction-demo' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'user=jupyter' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'autostart=true' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'autorestart=true' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'priority=20' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'stderr_logfile=/var/log/supervisor/flask-backend.err.log' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'stdout_logfile=/var/log/supervisor/flask-backend.out.log' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo '' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo '[program:http-server]' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'command=python -m http.server 8000' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'directory=/home/jupyter/clinical-abstraction-demo' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'user=jupyter' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'autostart=true' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'autorestart=true' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'priority=20' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'stderr_logfile=/var/log/supervisor/http-server.err.log' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf && \
    echo 'stdout_logfile=/var/log/supervisor/http-server.out.log' | sudo tee -a /etc/supervisor/conf.d/clinical-demo.conf

# Expose ports (Flask backend on 5000, HTTP server on 8000, JupyterLab on 8888)
EXPOSE 5000 8000 8888

# Run supervisor as the main process (nodaemon=true keeps it in foreground)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
