FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements-server.txt .

# Create virtual environment and install dependencies
RUN python -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install -r requirements-server.txt

# Copy application files
COPY download_model.py .
COPY server.py .
COPY .env* ./

# Set default port
ENV CLASSIFIER_PORT=8069

# Create an entrypoint script that checks for model and runs server
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Activate virtual environment\n\
source /app/.venv/bin/activate\n\
\n\
# Check if model exists\n\
if [ -d "/app/spare_parts_model" ] && [ -f "/app/spare_parts_model/config.json" ]; then\n\
    echo "✓ Model already exists, skipping download..."\n\
else\n\
    echo "Model not found, downloading..."\n\
    python download_model.py\n\
fi\n\
\n\
# Run the server\n\
echo "Starting server..."\n\
python server.py\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose the port
EXPOSE 8069

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
