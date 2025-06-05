# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (no system packages needed for basic FastAPI)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY models/ ./models/
COPY sentinel_pipeline/ ./sentinel_pipeline/

# Create empty dashboard directory (API handles missing dashboard gracefully)
RUN mkdir -p dashboard/dist

# Expose port
EXPOSE 8000

# Simple health check using Python built-ins
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} 