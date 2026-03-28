# Docker Deployment Guide

## Quick Start with Docker Compose

### Start the monitoring toolkit:
```bash
docker-compose up -d
```

### View logs:
```bash
docker-compose logs -f tomcat-monitor
```

### Stop:
```bash
docker-compose down
```

## Manual Docker Commands

### Build the image:
```bash
docker build -t tomcat-monitor:latest .
```

### Run the container:
```bash
docker run -d \
  --name tomcat-monitor \
  -p 5000:5000 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v /path/to/tomcat/logs:/var/log/tomcat:ro \
  tomcat-monitor:latest
```

### Run with custom config:
```bash
docker run -d \
  --name tomcat-monitor \
  -p 5000:5000 \
  -v /path/to/custom/config.yaml:/app/config.yaml:ro \
  tomcat-monitor:latest
```

## Environment Variables

The toolkit primarily uses the config.yaml file, but you can override specific settings:

```bash
docker run -d \
  --name tomcat-monitor \
  -p 5000:5000 \
  -e PYTHONUNBUFFERED=1 \
  tomcat-monitor:latest
```

## Volume Mounts

### Required Mounts:

1. **Configuration** (read-only recommended):
   ```
   -v $(pwd)/config.yaml:/app/config.yaml:ro
   ```

2. **Tomcat Access Logs** (read-only):
   ```
   -v /var/log/tomcat:/var/log/tomcat:ro
   ```

3. **Monitor Logs** (optional, for persistence):
   ```
   -v tomcat-monitor-logs:/var/log/tomcat-monitor
   ```

## Health Check

The container includes a health check that runs every 30 seconds:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' tomcat-monitor
```

## Network Configuration

### Connect to existing Tomcat network:
```bash
docker run -d \
  --name tomcat-monitor \
  --network tomcat-network \
  -p 5000:5000 \
  tomcat-monitor:latest
```

### With custom JMX host (in config.yaml):
```yaml
jmx:
  host: tomcat-container  # Use container name or service name
  port: 9999
```

## Resource Limits

### Set memory and CPU limits:
```bash
docker run -d \
  --name tomcat-monitor \
  -p 5000:5000 \
  --memory="512m" \
  --cpus="0.5" \
  tomcat-monitor:latest
```

### In docker-compose.yml:
```yaml
services:
  tomcat-monitor:
    # ... other config
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## Security

### Running as non-root (default):
The Dockerfile creates and uses a non-root user `tomcat-monitor`.

### Read-only filesystem (optional):
```bash
docker run -d \
  --name tomcat-monitor \
  -p 5000:5000 \
  --read-only \
  --tmpfs /tmp \
  tomcat-monitor:latest
```

### Drop capabilities:
```bash
docker run -d \
  --name tomcat-monitor \
  -p 5000:5000 \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  tomcat-monitor:latest
```

## Troubleshooting

### View container logs:
```bash
docker logs tomcat-monitor
```

### Access container shell:
```bash
docker exec -it tomcat-monitor /bin/bash
```

### Test configuration:
```bash
docker exec tomcat-monitor python -c "from config_manager import load_config; config = load_config('config.yaml'); print('Config OK')"
```

### Check API endpoints:
```bash
# Health check
curl http://localhost:5000/api/health

# Full status
curl http://localhost:5000/api/status | jq
```

## Production Deployment

### With docker-compose in production:

```yaml
version: '3.8'

services:
  tomcat-monitor:
    image: tomcat-monitor:latest
    container_name: tomcat-monitor
    restart: always
    ports:
      - "5000:5000"
    volumes:
      - ./config.yaml:/app/config.yaml:ro
      - /var/log/tomcat:/var/log/tomcat:ro
      - monitor-logs:/var/log/tomcat-monitor
    networks:
      - monitoring
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5000/api/health', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  monitor-logs:

networks:
  monitoring:
    external: true
```

### Start in production:
```bash
docker-compose -f docker-compose.prod.yml up -d
```
