# Stage 1: Download the model
FROM python:3.11-slim AS model-downloader

WORKDIR /app

# Copy download script
COPY download_model.py .
COPY .env* ./

# Install only what's needed for downloading (transformers and huggingface-hub)
RUN pip install transformers huggingface-hub python-dotenv

# Download the model
RUN echo "========================================" && \
    echo "Starting model download..." && \
    echo "========================================" && \
    python download_model.py && \
    echo "========================================" && \
    echo "Download script completed, checking files..." && \
    ls -la /app/ && \
    echo "========================================" && \
    if [ -d "/app/spare_parts_model" ]; then \
        echo "Model directory exists, listing contents:"; \
        ls -la /app/spare_parts_model/; \
    else \
        echo "❌ Model directory does not exist!"; \
        exit 1; \
    fi && \
    if [ -f "/app/spare_parts_model/config.json" ]; then \
        echo "✓ Model files verified in build stage!"; \
    else \
        echo "❌ config.json not found!"; \
        exit 1; \
    fi

# Stage 2: Runtime server
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements-server.txt .

# Create virtual environment and install dependencies
RUN python -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install -r requirements-server.txt

# Copy application files
COPY server.py .
COPY .env* ./

# Copy the downloaded model from the first stage
COPY --from=model-downloader /app/spare_parts_model ./spare_parts_model

# Verify model was copied to runtime stage
RUN echo "Verifying model in runtime stage..." && \
    ls -la /app/spare_parts_model/ && \
    test -f /app/spare_parts_model/config.json && \
    echo "✓ Model files verified in runtime stage!" || \
    (echo "❌ Model copy failed!" && exit 1)

# Set default port
ENV CLASSIFIER_PORT=8069

# Create an entrypoint script to run server
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Activate virtual environment\n\
source /app/.venv/bin/activate\n\
\n\
echo "✓ Model already in image"\n\
\n\
# Run the server\n\
echo "Starting server..."\n\
python server.py\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose the port
EXPOSE 8069

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
