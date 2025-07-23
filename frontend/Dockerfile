# Frontend Dockerfile for Streamlit - Production Ready
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_PORT=8501

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Create Streamlit config directory
RUN mkdir -p /home/appuser/.streamlit

# Create optimized Streamlit config
RUN echo '[server]\n\
headless = true\n\
port = 8501\n\
address = "0.0.0.0"\n\
maxUploadSize = 200\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
showErrorDetails = false\n\
\n\
[theme]\n\
primaryColor = "#1f77b4"\n\
backgroundColor = "#ffffff"\n\
secondaryBackgroundColor = "#f0f2f6"' > /home/appuser/.streamlit/config.toml

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--server.headless", "true"]
