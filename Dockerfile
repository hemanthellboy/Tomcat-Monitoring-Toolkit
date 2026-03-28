FROM python:3.10-slim

# Create non-root user
RUN groupadd -r tomcat-monitor && useradd -r -g tomcat-monitor tomcat-monitor

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./
COPY templates ./templates/
COPY config.yaml .

# Create directories for logs (with proper permissions)
RUN mkdir -p /var/log/tomcat-monitor && \
    chown -R tomcat-monitor:tomcat-monitor /var/log/tomcat-monitor && \
    chown -R tomcat-monitor:tomcat-monitor /app

# Switch to non-root user
USER tomcat-monitor

# Expose Flask port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health', timeout=5)" || exit 1

# Run the application
CMD ["python", "app.py"]
