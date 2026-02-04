FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY src/clinical-abstraction-demo/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/clinical-abstraction-demo/app/ .

EXPOSE 8080

CMD ["python", "extraction_backend_openai.py"]
