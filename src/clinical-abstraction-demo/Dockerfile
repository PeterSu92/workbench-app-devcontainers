FROM python:3.11-slim

# Create user with sudo (needed for Workbench startup scripts)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo curl fuse \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 -s /bin/bash appuser \
    && echo "appuser ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/appuser

WORKDIR /home/appuser/clinical-abstraction-demo

# Copy and install dependencies
COPY src/clinical-abstraction-demo/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/clinical-abstraction-demo/app/ .

RUN chown -R appuser:appuser /home/appuser

USER appuser

EXPOSE 8000

CMD ["python", "extraction_backend_openai.py"]
