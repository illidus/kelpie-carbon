FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Install poetry and dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only=main --no-interaction --no-ansi

# Copy application code
COPY api/ ./api/
COPY sentinel_pipeline/ ./sentinel_pipeline/
COPY models/ ./models/
COPY dashboard/dist/ ./dashboard/dist/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash kelpie
RUN chown -R kelpie:kelpie /app
USER kelpie

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"] 