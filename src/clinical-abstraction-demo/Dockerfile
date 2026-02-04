FROM us-central1-docker.pkg.dev/verily-workbench-public/apps/workbench-jupyter:latest

# Install jupyter extensions (required for workbench-jupyter template)
RUN --mount=type=bind,from=jupyter-extension-builder,source=/dist,target=/tmp/extensions \
    /tmp/extensions/setup.sh

# Install supervisor for background services
RUN sudo apt-get update && sudo apt-get install -y \
    supervisor \
    && sudo rm -rf /var/lib/apt/lists/*

# Create app directory
RUN mkdir -p /home/jupyter/clinical-abstraction-demo

# Copy the clinical abstraction demo application
COPY src/clinical-abstraction-demo/app/ /home/jupyter/clinical-abstraction-demo/

# Install Python dependencies
# Use --ignore-installed for blinker only (distutils-installed in base image)
RUN pip install --no-cache-dir --ignore-installed blinker && \
    pip install --no-cache-dir -r /home/jupyter/clinical-abstraction-demo/requirements.txt

# Create supervisor configuration for Flask and HTTP server (background services)
RUN sudo mkdir -p /var/log/supervisor && \
    echo '[program:flask-backend]' | sudo tee /etc/supervisor/conf.d/clinical-demo.conf && \
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

# Expose ports
EXPOSE 5000 8000 8888

# Create startup script per DEVCONTAINER_SETUP.md "BEST SOLUTION"
# - Start supervisor in background
# - Clear file_to_run to avoid config conflict with base image
# - Start Jupyter as main process
RUN echo '#!/bin/bash' | sudo tee /usr/local/bin/start-all.sh && \
    echo 'sudo /usr/bin/supervisord &' | sudo tee -a /usr/local/bin/start-all.sh && \
    echo 'sleep 2' | sudo tee -a /usr/local/bin/start-all.sh && \
    echo 'exec /home/jupyter/.local/bin/jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --ServerApp.file_to_run="" --ServerApp.root_dir=/home/jupyter' | sudo tee -a /usr/local/bin/start-all.sh && \
    sudo chmod +x /usr/local/bin/start-all.sh

CMD ["/usr/local/bin/start-all.sh"]
